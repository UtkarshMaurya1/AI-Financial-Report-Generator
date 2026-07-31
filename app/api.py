import os
import shutil
from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.requests import Request

from app.parser.docling_parser import parse_document, parse_plain_document
from app.retrieval.page_index import build_page_index
from app.extractors.merge import run_all_extractors
from app.renderer.pdf_generator import render_report

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

UPLOAD_DIR = "app/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@router.get("/health")
def health_check():
    return {"status": "ok"}


@router.post("/generate-report")
async def generate_report(company_name: str = Form(...), file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    ext = file.filename.lower().split(".")[-1]
    if ext == "pdf":
        document = parse_document(file_path)
    else:
        document = parse_plain_document(file_path)

    page_index = build_page_index(document)
    report = run_all_extractors(document, page_index)

    if not report.company.company_name:
        report.company.company_name = company_name

    output_filename = f"{company_name.replace(' ', '_')}_report.pdf"
    pdf_path = render_report(report, output_filename)

    return FileResponse(pdf_path, media_type="application/pdf", filename=output_filename)