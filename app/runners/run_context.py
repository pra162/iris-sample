import json
import shutil
from datetime import datetime
from pathlib import Path

from app.config.paths import DataPaths


class RunContext:
    """
    Represents one complete IRIS ETL execution.

    Each run has an isolated workspace:

        data/runs/<run_id>/

    A successful run can be promoted to:

        data/current/

    The current dataset is never modified until
    the complete pipeline succeeds.
    """

    def __init__(
        self,
        run_id: str | None = None,
        data_root: Path | str = "data",
    ):

        self.data_root = Path(data_root)

        if run_id is None:

            run_id = datetime.now().strftime(
                "%Y-%m-%d_%H%M%S"
            )

        self.run_id = run_id

        # =================================================
        # ISOLATED RUN
        # =================================================

        self.run_root = (
            self.data_root
            / "runs"
            / self.run_id
        )

        self.paths = DataPaths(
            self.run_root
        )

        # =================================================
        # CURRENT PRODUCTION DATA
        # =================================================

        self.current_root = (
            self.data_root
            / "current"
        )

        self.current_paths = DataPaths(
            self.current_root
        )

    # =====================================================
    # START
    # =====================================================

    def initialize(self):

        self.paths.create_directories()

        print("--------------------------------")
        print("IRIS Pipeline Run")

        print(
            f"Run ID : {self.run_id}"
        )

        print(
            f"Root   : {self.run_root}"
        )

        print("--------------------------------")

    # =====================================================
    # STATUS FILE
    # =====================================================

    @property
    def status_file(self) -> Path:

        return (
            self.run_root
            / "run_status.json"
        )

    # =====================================================
    # WRITE STATUS
    # =====================================================

    def write_status(
        self,
        status: str,
        **extra,
    ):

        payload = {
            "run_id": self.run_id,
            "status": status,
            "run_root": str(
                self.run_root
            ),
            "timestamp": datetime.now().isoformat(),
            **extra,
        }

        self.run_root.mkdir(
            parents=True,
            exist_ok=True,
        )

        with self.status_file.open(
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                payload,
                file,
                indent=2,
                ensure_ascii=False,
            )

    # =====================================================
    # CURRENT DATA EXISTS
    # =====================================================

    def has_current_data(self) -> bool:
        """
        Return True when a previously successful
        current dataset exists.
        """

        return (
            self.current_root.exists()
            and any(
                self.current_root.iterdir()
            )
        )

    # =====================================================
    # PROMOTE
    # =====================================================

    def promote_to_current(self):
        """
        Promote this successful run to current.

        Existing current data is replaced only after
        the complete pipeline succeeds.
        """

        if not self.run_root.exists():

            raise FileNotFoundError(
                f"Run directory does not exist: "
                f"{self.run_root}"
            )

        temporary_current = (
            self.data_root
            / f".current_{self.run_id}"
        )

        # -------------------------------------------------
        # Remove stale temporary directory
        # -------------------------------------------------

        if temporary_current.exists():

            shutil.rmtree(
                temporary_current
            )

        # -------------------------------------------------
        # Copy completed run
        # -------------------------------------------------

        shutil.copytree(
            self.run_root,
            temporary_current,
        )

        # -------------------------------------------------
        # Remove run status from production dataset
        # -------------------------------------------------

        temporary_status = (
            temporary_current
            / "run_status.json"
        )

        if temporary_status.exists():

            temporary_status.unlink()

        # -------------------------------------------------
        # Replace current
        # -------------------------------------------------

        if self.current_root.exists():

            shutil.rmtree(
                self.current_root
            )

        temporary_current.rename(
            self.current_root
        )

        print("--------------------------------")
        print(
            "Current dataset promoted successfully."
        )

        print(
            f"Current : {self.current_root}"
        )

        print("--------------------------------")

    # =====================================================
    # SUCCESS
    # =====================================================

    def mark_success(self):

        self.write_status(
            "SUCCESS",
        )

    # =====================================================
    # FAILED
    # =====================================================

    def mark_failed(
        self,
        error: Exception,
    ):

        self.write_status(
            "FAILED",
            error_type=type(error).__name__,
            error=str(error),
        )