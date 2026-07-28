from app.parser.docling_parser import ParsedPage


def build_prompt_text(pages: list[ParsedPage]) -> str:
    """
    Converts structured ParsedPage objects into a single text block
    for the LLM prompt — preserving headings and table markdown,
    separated by page for clarity.
    """
    if not pages:
        return ""

    sections = []
    for page in pages:
        header = f"--- Page {page.page_number} ---"
        headings = "\n".join(f"# {h}" for h in page.headings)
        body = page.body_text
        tables = "\n\n".join(t.markdown for t in page.tables)

        parts = [header]
        if headings:
            parts.append(headings)
        if body:
            parts.append(body)
        if tables:
            parts.append(tables)

        sections.append("\n".join(parts))

    return "\n\n".join(sections)