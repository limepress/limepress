from __future__ import annotations

from bs4 import BeautifulSoup

from limepress.unit import LimepressUnit


class LimepressHtmlParser:
    def handle_unit_meta_data(self, unit: LimepressUnit) -> None:
        if unit.get_file_extension() != 'html':
            return

        unit.set_default_template()
        unit.load_meta_data()

    def render_unit(self, unit: LimepressUnit) -> None:
        if not unit.get_file_extension() == 'html':
            return

        body = unit.read_body()
        soup = BeautifulSoup(body, features='html.parser')

        if soup.h1:
            unit.body_title = soup.h1.getText()

            soup.h1.decompose()

        unit.body_text = str(soup)
