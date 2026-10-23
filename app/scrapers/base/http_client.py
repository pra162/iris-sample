import random
import time

import requests


class HttpClient:
    """
    Shared HTTP client for external data sources.

    Provides:
    - Persistent HTTP session
    - Project-specific User-Agent
    - Retry handling for transient failures
    - Configurable HTTP 429 handling
    - Retry-After header support
    - Exponential backoff with jitter
    - Configurable request timeout
    - Useful error messages for debugging
    """

    MAX_RETRIES = 3

    BASE_DELAY = 5

    RATE_LIMIT_BASE_DELAY = 60

    DEFAULT_TIMEOUT = 60

    def __init__(self):

        self.session = requests.Session()

        self.session.headers.update(
            {
                "User-Agent": (
                    "NRW-DataCenter-BI/1.0 "
                    "(research/ETL project)"
                ),
                "Accept": (
                    "application/json,"
                    "text/plain,"
                    "*/*"
                ),
            }
        )

    # =====================================================
    # GET
    # =====================================================

    def get(
        self,
        url: str,
        **kwargs,
    ):

        return self._request(
            "GET",
            url,
            **kwargs,
        )

    # =====================================================
    # POST
    # =====================================================

    def post(
        self,
        url: str,
        **kwargs,
    ):

        return self._request(
            "POST",
            url,
            **kwargs,
        )

    # =====================================================
    # REQUEST
    # =====================================================

    def _request(
        self,
        method: str,
        url: str,
        **kwargs,
    ):

        timeout = kwargs.pop(
            "timeout",
            self.DEFAULT_TIMEOUT,
        )

        max_retries = kwargs.pop(
            "max_retries",
            self.MAX_RETRIES,
        )

        retry_on_rate_limit = kwargs.pop(
            "retry_on_rate_limit",
            True,
        )

        rate_limit_delay = kwargs.pop(
            "rate_limit_delay",
            self.RATE_LIMIT_BASE_DELAY,
        )

        for attempt in range(
            max_retries + 1
        ):

            try:

                response = self.session.request(
                    method,
                    url,
                    timeout=timeout,
                    **kwargs,
                )

                # -----------------------------------------
                # SUCCESS
                # -----------------------------------------

                if response.ok:

                    return response

                # -----------------------------------------
                # HTTP 429 - RATE LIMITED
                # -----------------------------------------

                if response.status_code == 429:

                    if not retry_on_rate_limit:

                        raise requests.HTTPError(
                            "HTTP 429 Too Many Requests "
                            f"for {url}",
                            response=response,
                        )

                    if attempt >= max_retries:

                        print(
                            f"HTTP 429 received from {url}. "
                            "Maximum retries reached."
                        )

                        response.raise_for_status()

                    delay = self._get_rate_limit_delay(
                        response=response,
                        attempt=attempt,
                        base_delay=rate_limit_delay,
                    )

                    print(
                        f"HTTP 429 received from {url}. "
                        f"Waiting {delay:.1f}s before retry "
                        f"({attempt + 1}/{max_retries})..."
                    )

                    time.sleep(delay)

                    continue

                # -----------------------------------------
                # SERVER ERRORS
                # -----------------------------------------

                if response.status_code in (
                    500,
                    502,
                    503,
                    504,
                ):

                    if attempt >= max_retries:

                        response.raise_for_status()

                    delay = self._get_backoff_delay(
                        attempt=attempt,
                        base_delay=self.BASE_DELAY,
                    )

                    print(
                        f"HTTP {response.status_code} "
                        f"received from {url}. "
                        f"Retrying in {delay:.1f}s "
                        f"({attempt + 1}/{max_retries})..."
                    )

                    time.sleep(delay)

                    continue

                # -----------------------------------------
                # OTHER HTTP ERRORS
                # -----------------------------------------

                response.raise_for_status()

            # =============================================
            # TIMEOUT
            # =============================================

            except requests.Timeout as exc:

                if attempt >= max_retries:

                    print(
                        f"HTTP timeout for {url} "
                        f"after "
                        f"{max_retries + 1} attempts."
                    )

                    raise

                delay = self._get_backoff_delay(
                    attempt=attempt,
                    base_delay=self.BASE_DELAY,
                )

                print(
                    f"HTTP timeout for {url}: "
                    f"{type(exc).__name__}: {exc}. "
                    f"Retrying in {delay:.1f}s "
                    f"({attempt + 1}/{max_retries})..."
                )

                time.sleep(delay)

            # =============================================
            # CONNECTION ERROR
            # =============================================

            except requests.ConnectionError as exc:

                if attempt >= max_retries:

                    print(
                        f"HTTP connection error for {url} "
                        f"after "
                        f"{max_retries + 1} attempts."
                    )

                    raise

                delay = self._get_backoff_delay(
                    attempt=attempt,
                    base_delay=self.BASE_DELAY,
                )

                print(
                    f"HTTP connection failed for {url}: "
                    f"{type(exc).__name__}: {exc}. "
                    f"Retrying in {delay:.1f}s "
                    f"({attempt + 1}/{max_retries})..."
                )

                time.sleep(delay)

            # =============================================
            # OTHER REQUEST ERRORS
            # =============================================

            except requests.RequestException as exc:

                print(
                    f"HTTP request failed for {url}: "
                    f"{type(exc).__name__}: {exc}"
                )

                raise

        raise RuntimeError(
            f"HTTP request failed after "
            f"{max_retries + 1} attempts: "
            f"{url}"
        )

    # =====================================================
    # RATE LIMIT DELAY
    # =====================================================

    def _get_rate_limit_delay(
        self,
        response: requests.Response,
        attempt: int,
        base_delay: float,
    ) -> float:
        """
        Determine the delay after HTTP 429.

        Priority:

        1. Retry-After response header
        2. Exponential backoff with jitter
        """

        retry_after = response.headers.get(
            "Retry-After"
        )

        if retry_after:

            try:

                delay = float(
                    retry_after
                )

                if delay >= 0:

                    return delay

            except ValueError:

                pass

        return self._get_backoff_delay(
            attempt=attempt,
            base_delay=base_delay,
        )

    # =====================================================
    # EXPONENTIAL BACKOFF
    # =====================================================

    @staticmethod
    def _get_backoff_delay(
        attempt: int,
        base_delay: float,
    ) -> float:
        """
        Calculate exponential backoff with jitter.

        Example:

            60s
            120s
            240s

        plus a small random jitter.
        """

        delay = (
            base_delay
            * (2 ** attempt)
        )

        jitter = random.uniform(
            0,
            min(
                30,
                delay * 0.25,
            ),
        )

        return delay + jitter