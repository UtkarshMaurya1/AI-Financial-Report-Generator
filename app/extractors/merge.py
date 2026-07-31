from app.parser.docling_parser import ParsedDocument
from app.schemas.report_schema import ReportSchema, Financials

from app.extractors.company import extract_company
from app.extractors.financials import extract_financials
from app.extractors.quarterly import extract_quarterly
from app.extractors.annual import extract_annual
from app.extractors.highlights import extract_highlights
from app.extractors.outlook import extract_outlook
from app.extractors.valuation import extract_valuation
from app.renderer.charts import generate_all_charts


def run_all_extractors(document: ParsedDocument, page_index: dict) -> ReportSchema:
    company_info, company_data = extract_company(document, page_index)
    shareholding, price_performance = extract_financials(document, page_index)
    quarterly = extract_quarterly(document, page_index)
    annual, ratios = extract_annual(document, page_index)
    highlights = extract_highlights(document, page_index)
    outlook = extract_outlook(document, page_index)
    valuation = extract_valuation(document, page_index)

    charts = generate_all_charts(quarterly)

    return ReportSchema(
        company=company_info,
        company_data=company_data,
        financials=Financials(
            shareholding=shareholding,
            price_performance=price_performance,
            quarterly=quarterly,
            annual=annual,
            ratios=ratios,
        ),
        charts=charts,
        highlights=highlights,
        outlook=outlook,
        valuation=valuation,
    )