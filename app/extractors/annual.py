from app.parser.docling_parser import ParsedDocument
from app.extractors.base import run_extraction, filter_valid_fields
from app.schemas.report_schema import AnnualFinancialEntry, RatioEntry

PROMPT_PATH = "app/prompts/annual.txt"

SECTIONS = ["annual_estimates", "profit_and_loss", "balance_sheet", "cashflow", "ratios"]


def extract_annual(document: ParsedDocument, page_index: dict) -> tuple[list[AnnualFinancialEntry], list[RatioEntry]]:
    annual_entries: list[AnnualFinancialEntry] = []
    ratio_entries: list[RatioEntry] = []

    for section in SECTIONS:
        result = run_extraction(document, page_index, section, PROMPT_PATH, top_n=2)
        if not result:
            continue

        annual_entries.extend(
            AnnualFinancialEntry(**filter_valid_fields(e, AnnualFinancialEntry))
            for e in result.get("annual", []) or []
        )
        ratio_entries.extend(
            RatioEntry(**filter_valid_fields(e, RatioEntry))
            for e in result.get("ratios", []) or []
        )

    return annual_entries, ratio_entries