from dataclasses import dataclass, field
from app.parser.docling_parser import ParsedDocument, ParsedPage


@dataclass
class SectionDefinition:
    canonical_name: str
    heading_aliases: list[str]      # strong signal — different report styles, same meaning
    body_keywords: list[str]        # weak signal
    requires_table: bool = False    # bonus score if page has a table


# Weights — tune these based on real-world testing
HEADING_MATCH_WEIGHT = 10
BODY_KEYWORD_WEIGHT = 1
TABLE_KEYWORD_WEIGHT = 3
TABLE_PRESENCE_BONUS = 5


SECTION_DEFINITIONS: list[SectionDefinition] = [
    SectionDefinition(
        canonical_name="company_overview",
        heading_aliases=["company data", "key data", "stock data"],
        body_keywords=["market cap", "bloomberg code", "nse code", "bse code", "face value"],
    ),
    SectionDefinition(
        canonical_name="shareholding",
        heading_aliases=["shareholding", "shareholding pattern"],
        body_keywords=["promoters", "fii", "public shareholding", "institutions", "dii"],
    ),
    SectionDefinition(
        canonical_name="price_performance",
        heading_aliases=["price performance", "stock performance"],
        body_keywords=["absolute return", "relative return", "sensex", "nifty"],
    ),
    SectionDefinition(
        canonical_name="quarterly_financials",
        heading_aliases=["quarterly financials", "quarterly results", "quarterly performance"],
        body_keywords=["q1fy", "q2fy", "q3fy", "q4fy", "qoq"],
        requires_table=True,
    ),
    SectionDefinition(
        canonical_name="annual_estimates",
        heading_aliases=["annual estimates", "financial snapshot", "key financials"],
        body_keywords=["y.e march", "fy25", "fy26", "fy27", "estimates"],
        requires_table=True,
    ),
    SectionDefinition(
        canonical_name="profit_and_loss",
        heading_aliases=["profit & loss", "profit and loss", "income statement", "statement of operations"],
        body_keywords=["sales", "ebitda", "pbt", "net profit", "revenue from operations"],
        requires_table=True,
    ),
    SectionDefinition(
        canonical_name="balance_sheet",
        heading_aliases=["balance sheet", "statement of assets and liabilities"],
        body_keywords=["total assets", "total liabilities", "shareholder funds", "net worth"],
        requires_table=True,
    ),
    SectionDefinition(
        canonical_name="cashflow",
        heading_aliases=["cash flow", "cashflow", "statement of cash flows"],
        body_keywords=["operating activities", "investing activities", "financing activities"],
        requires_table=True,
    ),
    SectionDefinition(
        canonical_name="ratios",
        heading_aliases=["ratio analysis", "key ratios", "financial ratios"],
        body_keywords=["roe", "roce", "ev/ebitda", "p/e", "current ratio", "debt/equity"],
        requires_table=True,
    ),
    SectionDefinition(
        canonical_name="highlights",
        heading_aliases=["key highlights", "highlights", "investment rationale"],
        body_keywords=["highlight"],
    ),
    SectionDefinition(
        canonical_name="outlook_valuation",
        heading_aliases=["outlook", "valuation", "outlook & valuation", "management discussion"],
        body_keywords=["target price", "recommend", "rating rationale"],
    ),
]


def _normalize(text: str) -> str:
    return text.lower().strip()


def _score_page(page: ParsedPage, section: SectionDefinition) -> int:
    score = 0

    normalized_headings = [_normalize(h) for h in page.headings]
    for alias in section.heading_aliases:
        if any(alias in h for h in normalized_headings):
            score += HEADING_MATCH_WEIGHT

    body = _normalize(page.body_text)
    for kw in section.body_keywords:
        score += body.count(kw) * BODY_KEYWORD_WEIGHT

    table_text = _normalize(" ".join(t.markdown for t in page.tables))
    for kw in section.body_keywords:
        score += table_text.count(kw) * TABLE_KEYWORD_WEIGHT

    if section.requires_table and page.has_table():
        score += TABLE_PRESENCE_BONUS

    return score


def build_page_index(document: ParsedDocument) -> dict[str, list[tuple[int, int]]]:
    """
    Returns {canonical_section_name: [(page_number, score), ...]} sorted by score desc.
    Score included so extractors can gauge retrieval confidence.
    """
    index: dict[str, list[tuple[int, int]]] = {s.canonical_name: [] for s in SECTION_DEFINITIONS}

    for page in document.pages:
        for section in SECTION_DEFINITIONS:
            score = _score_page(page, section)
            if score > 0:
                index[section.canonical_name].append((page.page_number, score))

    for section_name in index:
        index[section_name].sort(key=lambda x: x[1], reverse=True)

    return index


def get_relevant_pages(
    document: ParsedDocument,
    page_index: dict[str, list[tuple[int, int]]],
    section: str,
    top_n: int = 3,
    min_score: int = 1,
) -> list[ParsedPage]:
    """
    Returns actual ParsedPage objects (not a flattened string) for the
    top-N scoring pages of a section. Caller (extractor) decides how to
    build its own prompt text from page.full_text / headings / tables.
    """
    scored = page_index.get(section, [])
    qualifying = [(pg, sc) for pg, sc in scored if sc >= min_score][:top_n]
    page_numbers = [pg for pg, _ in qualifying]
    return document.get_pages(page_numbers)