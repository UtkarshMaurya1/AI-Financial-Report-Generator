from docling.document_converter import DocumentConverter
from dataclasses import dataclass, field
from typing import Literal, Optional


BlockType = Literal["heading", "paragraph", "table", "caption"]


@dataclass
class TableData:
    """Structured table representation — preserves rows/columns."""
    rows: list[list[str]] = field(default_factory=list)
    markdown: str = ""   # rendered form, used only when building LLM prompts


@dataclass
class Block:
    type: BlockType
    text: str
    table_data: Optional[TableData] = None


@dataclass
class ParsedPage:
    page_number: int
    blocks: list[Block] = field(default_factory=list)

    @property
    def headings(self) -> list[str]:
        return [b.text for b in self.blocks if b.type == "heading"]

    @property
    def tables(self) -> list[TableData]:
        return [b.table_data for b in self.blocks if b.type == "table" and b.table_data]

    @property
    def body_text(self) -> str:
        """Paragraphs + captions only (excludes headings/tables)."""
        return "\n".join(b.text for b in self.blocks if b.type in ("paragraph", "caption"))

    @property
    def full_text(self) -> str:
        """Everything, including table markdown — used for final LLM prompt content."""
        parts = []
        for b in self.blocks:
            if b.type == "table" and b.table_data:
                parts.append(b.table_data.markdown)
            else:
                parts.append(b.text)
        return "\n".join(parts)

    def has_table(self) -> bool:
        return len(self.tables) > 0


@dataclass
class ParsedDocument:
    pages: list[ParsedPage]

    def get_page(self, page_number: int) -> Optional[ParsedPage]:
        return next((p for p in self.pages if p.page_number == page_number), None)

    def get_pages(self, page_numbers: list[int]) -> list[ParsedPage]:
        return [p for p in self.pages if p.page_number in page_numbers]


def parse_document(file_path: str) -> ParsedDocument:
    """Parses a PDF using Docling into structured per-page blocks."""
    converter = DocumentConverter()
    result = converter.convert(file_path)
    doc = result.document

    pages: dict[int, ParsedPage] = {}

    for item, _level in doc.iterate_items():
        page_no = _get_page_number(item)
        if page_no is None:
            continue

        if page_no not in pages:
            pages[page_no] = ParsedPage(page_number=page_no)

        label = getattr(item, "label", "")
        item_text = getattr(item, "text", "") or ""

        if label in ("section_header", "title"):
            pages[page_no].blocks.append(Block(type="heading", text=item_text))
        elif label == "table":
            table_data = _extract_table_data(item)
            pages[page_no].blocks.append(
                Block(type="table", text=table_data.markdown, table_data=table_data)
            )
        elif label == "caption":
            pages[page_no].blocks.append(Block(type="caption", text=item_text))
        else:
            if item_text.strip():
                pages[page_no].blocks.append(Block(type="paragraph", text=item_text))

    ordered_pages = [pages[k] for k in sorted(pages.keys())]
    return ParsedDocument(pages=ordered_pages)


def parse_plain_document(file_path: str, chunk_size: int = 3000) -> ParsedDocument:
    """
    Fallback for CSV/TXT — no real pages/headings/tables exist, so each
    chunk becomes a pseudo-page with a single paragraph block.
    (CSV rows could optionally be parsed into a TableData block — see note below.)
    """
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    chunks = [content[i:i + chunk_size] for i in range(0, len(content), chunk_size)]
    pages = [
        ParsedPage(page_number=i + 1, blocks=[Block(type="paragraph", text=chunk)])
        for i, chunk in enumerate(chunks)
    ]
    return ParsedDocument(pages=pages)


def _get_page_number(item) -> Optional[int]:
    prov = getattr(item, "prov", None)
    if prov and len(prov) > 0:
        return getattr(prov[0], "page_no", None)
    return None


def _extract_table_data(item) -> TableData:
    """Extracts structured rows if Docling exposes them, else falls back to markdown only."""
    rows: list[list[str]] = []
    try:
        table_obj = item.export_to_dataframe()  # Docling TableItem → pandas DataFrame
        rows = [list(table_obj.columns)] + table_obj.values.tolist()
    except Exception:
        pass

    try:
        markdown = item.export_to_markdown()
    except Exception:
        markdown = getattr(item, "text", "[table]")

    return TableData(rows=rows, markdown=markdown)