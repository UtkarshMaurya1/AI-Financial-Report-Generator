from app.parser.docling_parser import ParsedDocument
from app.extractors.base import run_extraction, filter_valid_fields
from app.schemas.report_schema import CompanyInfo, CompanyData

PROMPT_PATH = "app/prompts/company.txt"


def extract_company(document: ParsedDocument, page_index: dict) -> tuple[CompanyInfo, CompanyData]:
    result = run_extraction(document, page_index, "company_overview", PROMPT_PATH, top_n=2)

    company_dict = result.get("company", {}) or {}
    company_data_dict = result.get("company_data", {}) or {}

    return (
        CompanyInfo(**filter_valid_fields(company_dict, CompanyInfo)),
        CompanyData(**filter_valid_fields(company_data_dict, CompanyData)),
    )