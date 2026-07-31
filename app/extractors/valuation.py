from app.parser.docling_parser import ParsedDocument
from app.extractors.base import run_extraction

PROMPT_PATH = "app/prompts/valuation.txt"


def extract_valuation(document: ParsedDocument, page_index: dict) -> str | None:
    result = run_extraction(document, page_index, "outlook_valuation", PROMPT_PATH, top_n=2)
    return result.get("valuation")