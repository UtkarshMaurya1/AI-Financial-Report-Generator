from app.parser.docling_parser import ParsedDocument
from app.extractors.base import run_extraction, filter_valid_fields
from app.schemas.report_schema import ShareholdingEntry, PricePerformanceEntry

PROMPT_PATH = "app/prompts/financials.txt"


def extract_financials(
    document: ParsedDocument, page_index: dict
) -> tuple[list[ShareholdingEntry], list[PricePerformanceEntry]]:
    shareholding_result = run_extraction(document, page_index, "shareholding", PROMPT_PATH, top_n=2)
    price_result = run_extraction(document, page_index, "price_performance", PROMPT_PATH, top_n=2)

    merged = {**shareholding_result, **price_result}

    shareholding = [
        ShareholdingEntry(**filter_valid_fields(e, ShareholdingEntry))
        for e in merged.get("shareholding", []) or []
    ]
    price_performance = [
        PricePerformanceEntry(**filter_valid_fields(e, PricePerformanceEntry))
        for e in merged.get("price_performance", []) or []
    ]

    return shareholding, price_performance