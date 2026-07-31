from app.parser.docling_parser import ParsedDocument
from app.extractors.base import run_extraction

PROMPT_PATH = "app/prompts/highlights.txt"


def extract_highlights(document: ParsedDocument, page_index: dict) -> list[str]:
    result = run_extraction(document, page_index, "highlights", PROMPT_PATH, top_n=2)
    return [str(h) for h in result.get("highlights", []) or []]