from app.parser.docling_parser import ParsedDocument
from app.retrieval.page_index import get_relevant_pages
from app.extractors.prompt_builder import build_prompt_text
from app.extractors.llm_client import call_llm


def run_extraction(
    document: ParsedDocument,
    page_index: dict,
    section: str,
    prompt_path: str,
    top_n: int = 3,
) -> dict:
    """
    Shared extraction flow used by every extractor:
    relevant pages -> prompt text -> LLM call -> raw dict.
    Returns {} if no relevant pages found or LLM call fails.
    """
    pages = get_relevant_pages(document, page_index, section, top_n=top_n)
    if not pages:
        return {}

    prompt_text = build_prompt_text(pages)

    with open(prompt_path, "r") as f:
        system_prompt = f.read()

    return call_llm(system_prompt, prompt_text)


def filter_valid_fields(data: dict, model) -> dict:
    """Keeps only keys that exist on a Pydantic model, avoiding validation errors."""
    valid_keys = model.model_fields.keys()
    return {k: v for k, v in data.items() if k in valid_keys}