import os
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
from app.schemas.report_schema import ReportSchema

TEMPLATE_DIR = "app/renderer"
TEMPLATE_FILE = "template.html"
OUTPUT_DIR = "app/static/reports"


def render_report(report: ReportSchema, output_filename: str = "report.pdf") -> str:
    """
    Renders ReportSchema into HTML via Jinja2, then converts to PDF via WeasyPrint.
    Does NOT call the LLM — pure templating + file conversion.
    Returns the path to the generated PDF.
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    template = env.get_template(TEMPLATE_FILE)

    html_content = template.render(
        company=report.company,
        company_data=report.company_data,
        financials=report.financials,
        charts=report.charts,
        highlights=report.highlights,
        outlook=report.outlook,
        valuation=report.valuation,
    )

    output_path = os.path.join(OUTPUT_DIR, output_filename)
    HTML(string=html_content, base_url=".").write_pdf(output_path)

    return output_path