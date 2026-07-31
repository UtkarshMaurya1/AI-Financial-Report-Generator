from app.parser.docling_parser import ParsedDocument
from app.extractors.base import run_extraction, filter_valid_fields
from app.schemas.report_schema import QuarterlyFinancialEntry

PROMPT_PATH = "app/prompts/quarterly.txt"


def extract_quarterly(document: ParsedDocument, page_index: dict) -> list[QuarterlyFinancialEntry]:
    result = run_extraction(document, page_index, "quarterly_financials", PROMPT_PATH, top_n=2)

    return [
        QuarterlyFinancialEntry(**filter_valid_fields(e, QuarterlyFinancialEntry))
        for e in result.get("quarterly", []) or []
    ]