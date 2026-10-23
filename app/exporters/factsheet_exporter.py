from __future__ import annotations

from pathlib import Path
from typing import Any

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    Image,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
    KeepTogether,
)

from app.database.session import SessionLocal
from app.services.site_intelligence_service import SiteIntelligenceService
from app.exporters.map_renderer import MapRenderer


class FactsheetExporter:
    """
    Generates a two-page IRIS Site Intelligence PDF factsheet.

    The exporter intentionally uses the existing SiteIntelligenceService
    and MapRenderer instead of duplicating spatial/business logic.

    Output:
        data/exports/factsheets/<facility_id>.pdf
    """

    OUTPUT_DIRECTORY = (
        Path("data")
        / "exports"
        / "factsheets"
    )

    PAGE_WIDTH, PAGE_HEIGHT = A4

    def __init__(
        self,
        session,
        output_directory: Path | None = None,
    ):
        self.session = session
        self.output_directory = (
            output_directory
            or self.OUTPUT_DIRECTORY
        )

        self.site_service = SiteIntelligenceService(
            session
        )

        self.map_renderer = MapRenderer(
            session
        )

        self.styles = self._build_styles()

    # ==========================================================
    # PUBLIC API
    # ==========================================================

    def export_facility(
        self,
        facility_id: str,
        radius_km: float = 10,
    ) -> Path:
        """
        Generate the complete two-page factsheet.
        """

        facility = (
            self.map_renderer._get_facility(
                facility_id
            )
        )

        if facility is None:
            raise ValueError(
                f"Facility not found: {facility_id}"
            )

        intelligence = (
            self.site_service.analyze_facility(
                facility_id
            )
        )

        if intelligence is None:
            raise ValueError(
                f"Could not analyze facility: {facility_id}"
            )

        print("--------------------------------")
        print("Generating IRIS factsheet")
        print("--------------------------------")
        print(
            f"Facility : {facility.name}"
        )
        print(
            f"Company  : {facility.company}"
        )
        print(
            f"City     : {facility.city}"
        )

        # ------------------------------------------------------
        # Map
        # ------------------------------------------------------

        map_path = (
            self.map_renderer.render_facility(
                facility_id,
                radius_km=radius_km,
            )
        )

        # ------------------------------------------------------
        # Infrastructure summary
        # ------------------------------------------------------

        infrastructure = (
            self._collect_infrastructure(
                facility,
                radius_km,
            )
        )

        # ------------------------------------------------------
        # Output
        # ------------------------------------------------------

        self.output_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        output_path = (
            self.output_directory
            / f"{facility_id}.pdf"
        )

        self._build_pdf(
            output_path=output_path,
            facility=facility,
            intelligence=intelligence,
            infrastructure=infrastructure,
            map_path=Path(map_path),
            radius_km=radius_km,
        )

        print("--------------------------------")
        print("Factsheet generated successfully:")
        print(output_path)
        print("--------------------------------")

        return output_path

    # ==========================================================
    # DATA
    # ==========================================================

    def _collect_infrastructure(
        self,
        facility,
        radius_km: float,
    ) -> dict[str, Any]:
        """
        Collect the same nearby infrastructure used by the map.

        We intentionally reuse MapRenderer's filtering logic so that
        the numbers printed in the PDF correspond to the map.
        """

        substations = (
            self.map_renderer
            .power_repository
            .get_high_voltage_substations()
        )

        lines = (
            self.map_renderer
            .power_repository
            .get_high_voltage_lines()
        )

        transformers = (
            self.map_renderer
            .power_repository
            .get_strategic_transformers()
        )

        nearby_substations = (
            self.map_renderer._filter_power_rows(
                substations,
                facility,
                radius_km,
            )
        )

        nearby_lines = (
            self.map_renderer._filter_power_rows(
                lines,
                facility,
                radius_km,
            )
        )

        nearby_transformers = (
            self.map_renderer._filter_power_rows(
                transformers,
                facility,
                radius_km,
            )
        )

        voltage_counts = {
            "380 kV": 0,
            "220 kV": 0,
            "110 kV": 0,
        }

        for row in nearby_lines:
            level = (
                self.map_renderer._voltage_level(
                    row.get("voltage")
                )
            )

            if level in (
                "380",
                "220",
                "110",
            ):
                voltage_counts[
                    f"{level} kV"
                ] += 1

        return {
            "lines": nearby_lines,
            "substations": nearby_substations,
            "transformers": nearby_transformers,
            "voltage_counts": voltage_counts,
        }

    # ==========================================================
    # PDF
    # ==========================================================

    def _build_pdf(
        self,
        output_path: Path,
        facility,
        intelligence: dict[str, Any],
        infrastructure: dict[str, Any],
        map_path: Path,
        radius_km: float,
    ) -> None:

        document = BaseDocTemplate(
            str(output_path),
            pagesize=A4,
            rightMargin=14 * mm,
            leftMargin=14 * mm,
            topMargin=13 * mm,
            bottomMargin=13 * mm,
            title=(
                f"IRIS Site Intelligence - "
                f"{facility.name}"
            ),
            author="IRIS",
        )

        frame = Frame(
            document.leftMargin,
            document.bottomMargin,
            document.width,
            document.height,
            id="normal",
        )

        document.addPageTemplates(
            [
                PageTemplate(
                    id="IRIS",
                    frames=[frame],
                    onPage=self._draw_page_header,
                )
            ]
        )

        story = []

        # ======================================================
        # PAGE 1
        # ======================================================

        story.append(
            Paragraph(
                "IRIS SITE INTELLIGENCE",
                self.styles["title"],
            )
        )

        subtitle = (
            f"{facility.name or 'Selected Site'}"
        )

        if facility.city:
            subtitle += (
                f"  •  {facility.city}"
            )

        story.append(
            Paragraph(
                subtitle,
                self.styles["subtitle"],
            )
        )

        if facility.company:
            story.append(
                Paragraph(
                    facility.company,
                    self.styles["company"],
                )
            )

        story.append(
            Spacer(1, 5 * mm)
        )

        # Score card
        score = intelligence.get(
            "site_score",
            {},
        )

        score_table = self._score_card(
            score
        )

        story.append(score_table)
        story.append(
            Spacer(1, 5 * mm)
        )

        # Large map
        if map_path.exists():
            map_image = Image(
                str(map_path),
            )

            available_width = (
                document.width
            )

            available_height = (
                154 * mm
            )

            image_width = available_width
            image_height = (
                map_image.imageHeight
                * image_width
                / map_image.imageWidth
            )

            if image_height > available_height:
                image_height = available_height
                image_width = (
                    map_image.imageWidth
                    * image_height
                    / map_image.imageHeight
                )

            map_image.drawWidth = image_width
            map_image.drawHeight = image_height

            story.append(
                map_image
            )

        story.append(
            Spacer(1, 2 * mm)
        )

        story.append(
            Paragraph(
                (
                    f"Analysis radius: "
                    f"{radius_km:g} km  •  "
                    f"Selected site: "
                    f"{facility.latitude:.6f}, "
                    f"{facility.longitude:.6f}"
                ),
                self.styles["caption"],
            )
        )

        story.append(
            PageBreak()
        )

        # ======================================================
        # PAGE 2
        # ======================================================

        story.append(
            Paragraph(
                "SITE INTELLIGENCE",
                self.styles["section"],
            )
        )

        story.append(
            Spacer(1, 2 * mm)
        )

        # ------------------------------------------------------
        # Infrastructure
        # ------------------------------------------------------

        story.append(
            Paragraph(
                "POWER INFRASTRUCTURE",
                self.styles["subsection"],
            )
        )

        voltage_counts = (
            infrastructure[
                "voltage_counts"
            ]
        )

        power_data = [
            [
                "Metric",
                "Value",
            ],
            [
                "HV transmission lines",
                str(
                    len(
                        infrastructure["lines"]
                    )
                ),
            ],
            [
                "380 kV",
                str(
                    voltage_counts["380 kV"]
                ),
            ],
            [
                "220 kV",
                str(
                    voltage_counts["220 kV"]
                ),
            ],
            [
                "110 kV",
                str(
                    voltage_counts["110 kV"]
                ),
            ],
            [
                "HV substations",
                str(
                    len(
                        infrastructure[
                            "substations"
                        ]
                    )
                ),
            ],
            [
                "Strategic transformers",
                str(
                    len(
                        infrastructure[
                            "transformers"
                        ]
                    )
                ),
            ],
        ]

        story.append(
            self._data_table(
                power_data
            )
        )

        story.append(
            Spacer(1, 6 * mm)
        )

        # ------------------------------------------------------
        # Nearest infrastructure
        # ------------------------------------------------------

        story.append(
            Paragraph(
                "NEAREST INFRASTRUCTURE",
                self.styles["subsection"],
            )
        )

        power = intelligence.get(
            "power",
            {},
        )

        nearest_line = power.get(
            "nearest_high_voltage_line"
        )

        nearest_substation = power.get(
            "nearest_substation"
        )

        nearest_transformer = power.get(
            "nearest_transformer"
        )

        nearest_data = [
            [
                "Infrastructure",
                "Distance",
                "Details",
            ],
            self._nearest_row(
                "HV transmission line",
                nearest_line,
                voltage=True,
            ),
            self._nearest_row(
                "HV substation",
                nearest_substation,
                voltage=True,
            ),
            self._nearest_row(
                "Transformer",
                nearest_transformer,
                voltage=True,
            ),
        ]

        story.append(
            self._data_table(
                nearest_data
            )
        )

        story.append(
            Spacer(1, 6 * mm)
        )

        # ------------------------------------------------------
        # Land
        # ------------------------------------------------------

        story.append(
            Paragraph(
                "LAND INTELLIGENCE",
                self.styles["subsection"],
            )
        )

        land = intelligence.get(
            "land",
            {},
        )

        land_data = [
            [
                "Metric",
                "Value",
            ],
            [
                "Municipality",
                self._safe(
                    land.get("municipality")
                ),
            ],
            [
                "District",
                self._safe(
                    land.get("district")
                ),
            ],
            [
                "Postal code",
                self._safe(
                    land.get("postal_code")
                ),
            ],
            [
                "Land value",
                self._format_eur_m2(
                    land.get(
                        "land_value_eur_m2"
                    )
                ),
            ],
            [
                "Land-value reference distance",
                self._format_distance(
                    land.get("distance_km")
                ),
            ],
        ]

        story.append(
            self._data_table(
                land_data
            )
        )

        story.append(
            Spacer(1, 6 * mm)
        )

        # ------------------------------------------------------
        # Renewable energy
        # ------------------------------------------------------

        story.append(
            Paragraph(
                "RENEWABLE ENERGY",
                self.styles["subsection"],
            )
        )

        renewable = intelligence.get(
            "renewable_energy",
            {},
        )

        renewable_data = [
            [
                "Metric",
                "Value",
            ],
            [
                "Assets within analysis area",
                str(
                    renewable.get(
                        "asset_count",
                        0,
                    )
                ),
            ],
            [
                "Solar capacity",
                self._format_kw(
                    renewable.get(
                        "solar_kw",
                        0,
                    )
                ),
            ],
            [
                "Wind capacity",
                self._format_kw(
                    renewable.get(
                        "wind_kw",
                        0,
                    )
                ),
            ],
        ]

        story.append(
            self._data_table(
                renewable_data
            )
        )

        story.append(
            Spacer(1, 6 * mm)
        )

        # ------------------------------------------------------
        # Site score breakdown
        # ------------------------------------------------------

        story.append(
            Paragraph(
                "SITE SCORE BREAKDOWN",
                self.styles["subsection"],
            )
        )

        score_data = [
            [
                "Category",
                "Score",
                "Maximum",
            ],
            [
                "Grid",
                str(
                    score.get(
                        "grid_score",
                        0,
                    )
                ),
                "25",
            ],
            [
                "Transmission",
                str(
                    score.get(
                        "transmission_score",
                        0,
                    )
                ),
                "20",
            ],
            [
                "Transformer",
                str(
                    score.get(
                        "transformer_score",
                        0,
                    )
                ),
                "15",
            ],
            [
                "Renewable",
                str(
                    score.get(
                        "renewable_score",
                        0,
                    )
                ),
                "10",
            ],
            [
                "Land",
                str(
                    score.get(
                        "land_score",
                        0,
                    )
                ),
                "15",
            ],
            [
                "Expansion",
                str(
                    score.get(
                        "expansion_score",
                        0,
                    )
                ),
                "15",
            ],
        ]

        story.append(
            self._data_table(
                score_data
            )
        )

        story.append(
            Spacer(1, 5 * mm)
        )

        # ------------------------------------------------------
        # Cadastre status
        # ------------------------------------------------------

        story.append(
            Paragraph(
                "CADASTRE",
                self.styles["subsection"],
            )
        )

        story.append(
            Paragraph(
                (
                    "Parcel identifier: "
                    "<b>Pending cadastre "
                    "integration</b>"
                ),
                self.styles["body"],
            )
        )

        story.append(
            Spacer(1, 4 * mm)
        )

        story.append(
            Paragraph(
                (
                    "Note: the current IRIS database does not "
                    "contain a dedicated cadastre/parcel dataset. "
                    "The parcel identifier is therefore not "
                    "inferred from BORIS land-value data."
                ),
                self.styles["note"],
            )
        )

        document.build(
            story
        )

    # ==========================================================
    # COMPONENTS
    # ==========================================================

    def _score_card(
        self,
        score: dict[str, Any],
    ) -> Table:

        overall = score.get(
            "overall_score",
            0,
        )

        rating = score.get(
            "rating",
            "Unknown",
        )

        data = [
            [
                Paragraph(
                    "IRIS SITE SCORE",
                    self.styles["card_label"],
                ),
                Paragraph(
                    f"<b>{overall}</b> / 100",
                    self.styles["score"],
                ),
                Paragraph(
                    rating.upper(),
                    self.styles["rating"],
                ),
            ]
        ]

        table = Table(
            data,
            colWidths=[
                50 * mm,
                50 * mm,
                65 * mm,
            ],
            rowHeights=[
                17 * mm
            ],
        )

        table.setStyle(
            TableStyle(
                [
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, -1),
                        colors.HexColor(
                            "#F8FAFC"
                        ),
                    ),
                    (
                        "BOX",
                        (0, 0),
                        (-1, -1),
                        1,
                        colors.HexColor(
                            "#CBD5E1"
                        ),
                    ),
                    (
                        "VALIGN",
                        (0, 0),
                        (-1, -1),
                        "MIDDLE",
                    ),
                    (
                        "ALIGN",
                        (1, 0),
                        (-1, -1),
                        "CENTER",
                    ),
                    (
                        "LEFTPADDING",
                        (0, 0),
                        (-1, -1),
                        5 * mm,
                    ),
                    (
                        "RIGHTPADDING",
                        (0, 0),
                        (-1, -1),
                        5 * mm,
                    ),
                ]
            )
        )

        return table

    def _data_table(
        self,
        data: list[list[str]],
    ) -> Table:

        table = Table(
            data,
            colWidths=[
                78 * mm,
                48 * mm,
                48 * mm,
            ]
            if len(data[0]) == 3
            else [
                92 * mm,
                82 * mm,
            ],
            repeatRows=1,
        )

        style_commands = [
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.HexColor(
                    "#0F172A"
                ),
            ),
            (
                "TEXTCOLOR",
                (0, 0),
                (-1, 0),
                colors.white,
            ),
            (
                "FONTNAME",
                (0, 0),
                (-1, 0),
                "Helvetica-Bold",
            ),
            (
                "FONTSIZE",
                (0, 0),
                (-1, 0),
                8.5,
            ),
            (
                "FONTSIZE",
                (0, 1),
                (-1, -1),
                8.5,
            ),
            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.HexColor(
                    "#CBD5E1"
                ),
            ),
            (
                "ROWBACKGROUNDS",
                (0, 1),
                (-1, -1),
                [
                    colors.white,
                    colors.HexColor(
                        "#F8FAFC"
                    ),
                ],
            ),
            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "MIDDLE",
            ),
            (
                "LEFTPADDING",
                (0, 0),
                (-1, -1),
                3 * mm,
            ),
            (
                "RIGHTPADDING",
                (0, 0),
                (-1, -1),
                3 * mm,
            ),
            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                2.2 * mm,
            ),
            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                2.2 * mm,
            ),
        ]

        table.setStyle(
            TableStyle(
                style_commands
            )
        )

        return table

    def _nearest_row(
        self,
        title: str,
        item: dict | None,
        voltage: bool = False,
    ) -> list[str]:

        if not item:
            return [
                title,
                "—",
                "No data",
            ]

        distance = self._format_distance(
            item.get("distance_km")
        )

        details = (
            item.get("name")
            or item.get("operator")
            or "Unnamed infrastructure"
        )

        if voltage:
            voltage_value = item.get(
                "voltage"
            )

            if voltage_value:
                details += (
                    f" • {voltage_value}"
                )

        return [
            title,
            distance,
            details,
        ]

    # ==========================================================
    # STYLES
    # ==========================================================

    @staticmethod
    def _build_styles():

        styles = getSampleStyleSheet()

        return {
            "title": ParagraphStyle(
                "IRISTitle",
                parent=styles["Title"],
                fontName="Helvetica-Bold",
                fontSize=21,
                leading=24,
                textColor=colors.HexColor(
                    "#0F172A"
                ),
                alignment=TA_LEFT,
                spaceAfter=2 * mm,
            ),
            "subtitle": ParagraphStyle(
                "IRISSubtitle",
                parent=styles["Normal"],
                fontName="Helvetica",
                fontSize=11,
                leading=14,
                textColor=colors.HexColor(
                    "#475569"
                ),
            ),
            "company": ParagraphStyle(
                "IRISCompany",
                parent=styles["Normal"],
                fontName="Helvetica-Bold",
                fontSize=9,
                leading=12,
                textColor=colors.HexColor(
                    "#64748B"
                ),
                spaceBefore=1 * mm,
            ),
            "section": ParagraphStyle(
                "IRISSection",
                parent=styles["Heading1"],
                fontName="Helvetica-Bold",
                fontSize=15,
                leading=18,
                textColor=colors.HexColor(
                    "#0F172A"
                ),
                spaceAfter=3 * mm,
            ),
            "subsection": ParagraphStyle(
                "IRISSubsection",
                parent=styles["Heading2"],
                fontName="Helvetica-Bold",
                fontSize=9.5,
                leading=12,
                textColor=colors.HexColor(
                    "#1E293B"
                ),
                spaceAfter=2 * mm,
            ),
            "body": ParagraphStyle(
                "IRISBody",
                parent=styles["BodyText"],
                fontName="Helvetica",
                fontSize=8.5,
                leading=12,
                textColor=colors.HexColor(
                    "#334155"
                ),
            ),
            "note": ParagraphStyle(
                "IRISNote",
                parent=styles["BodyText"],
                fontName="Helvetica",
                fontSize=7.5,
                leading=10,
                textColor=colors.HexColor(
                    "#64748B"
                ),
            ),
            "caption": ParagraphStyle(
                "IRISCaption",
                parent=styles["Normal"],
                fontName="Helvetica",
                fontSize=7,
                leading=9,
                textColor=colors.HexColor(
                    "#64748B"
                ),
            ),
            "card_label": ParagraphStyle(
                "IRISCardLabel",
                parent=styles["Normal"],
                fontName="Helvetica-Bold",
                fontSize=8,
                leading=10,
                textColor=colors.HexColor(
                    "#475569"
                ),
            ),
            "score": ParagraphStyle(
                "IRISScore",
                parent=styles["Normal"],
                fontName="Helvetica-Bold",
                fontSize=19,
                leading=22,
                textColor=colors.HexColor(
                    "#0F172A"
                ),
                alignment=TA_CENTER,
            ),
            "rating": ParagraphStyle(
                "IRISRating",
                parent=styles["Normal"],
                fontName="Helvetica-Bold",
                fontSize=10,
                leading=12,
                textColor=colors.HexColor(
                    "#2563EB"
                ),
                alignment=TA_CENTER,
            ),
        }

    # ==========================================================
    # HEADER
    # ==========================================================

    @staticmethod
    def _draw_page_header(
        canvas,
        document,
    ) -> None:

        canvas.saveState()

        canvas.setFont(
            "Helvetica-Bold",
            6.5,
        )

        canvas.setFillColor(
            colors.HexColor(
                "#94A3B8"
            )
        )

        canvas.drawRightString(
            A4[0] - 14 * mm,
            A4[1] - 8 * mm,
            "IRIS",
        )

        canvas.setStrokeColor(
            colors.HexColor(
                "#E2E8F0"
            )
        )

        canvas.setLineWidth(
            0.5
        )

        canvas.line(
            14 * mm,
            A4[1] - 10 * mm,
            A4[0] - 14 * mm,
            A4[1] - 10 * mm,
        )

        canvas.setFont(
            "Helvetica",
            6.5,
        )

        canvas.setFillColor(
            colors.HexColor(
                "#94A3B8"
            )
        )

        canvas.drawString(
            14 * mm,
            8 * mm,
            "IRIS Site Intelligence",
        )

        canvas.drawRightString(
            A4[0] - 14 * mm,
            8 * mm,
            f"Page {document.page}",
        )

        canvas.restoreState()

    # ==========================================================
    # FORMATTERS
    # ==========================================================

    @staticmethod
    def _safe(value) -> str:
        if value is None:
            return "—"

        text = str(value).strip()

        return text or "—"

    @staticmethod
    def _format_distance(
        value,
    ) -> str:

        if value is None:
            return "—"

        try:
            return f"{float(value):.2f} km"
        except (
            TypeError,
            ValueError,
        ):
            return "—"

    @staticmethod
    def _format_eur_m2(
        value,
    ) -> str:

        if value is None:
            return "—"

        try:
            return f"€{float(value):,.2f} / m²"
        except (
            TypeError,
            ValueError,
        ):
            return "—"

    @staticmethod
    def _format_kw(
        value,
    ) -> str:

        if value is None:
            return "0 kW"

        try:
            return f"{float(value):,.0f} kW"
        except (
            TypeError,
            ValueError,
        ):
            return "0 kW"


# ==========================================================
# Convenience function
# ==========================================================

def generate_factsheet(
    facility_id: str,
    radius_km: float = 10,
) -> Path:
    """
    Convenience function for scripts/CLI usage.
    """

    session = SessionLocal()

    try:
        exporter = FactsheetExporter(
            session
        )

        return exporter.export_facility(
            facility_id,
            radius_km=radius_km,
        )

    finally:
        session.close()


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print(
            "Usage: python -m app.exporters.factsheet_exporter "
            "<facility_id> [radius_km]"
        )
        raise SystemExit(1)

    facility_id = sys.argv[1]

    radius = (
        float(sys.argv[2])
        if len(sys.argv) > 2
        else 10.0
    )

    output = generate_factsheet(
        facility_id,
        radius_km=radius,
    )

    print(
        f"OUTPUT: {output}"
    )