import json

from bs4 import BeautifulSoup


class NextDataParser:

    def parse(self, html: str):

        soup = BeautifulSoup(html, "html.parser")

        script = soup.find("script", id="__NEXT_DATA__")

        if script is None:
            raise Exception("__NEXT_DATA__ not found")

        return json.loads(script.string)