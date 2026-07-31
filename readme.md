# AI Financial Research Report Generator

An AI-powered application that automatically generates a professional equity research report from raw company financial documents (PDF, CSV, or TXT). The output PDF is styled to closely match Geojit's "Retail Equity Research" report format.

This is a deterministic, **Vectorless RAG** pipeline — no embeddings, no FAISS/Pinecone/Chroma, no agent frameworks. Retrieval is done via a keyword + heading-weighted page index, and extraction uses task-specific LLM prompts (not one giant prompt).

---

## What it does

1. Accepts a company name + a financial document (any company, any format — PDF/CSV/TXT).
2. Parses the document (via Docling) into structured pages with headings, paragraphs, and tables.
3. Builds a deterministic **page index** — mapping report sections (e.g. "quarterly financials", "balance sheet") to the pages most likely to contain them, using weighted heading/keyword/table scoring.
4. Runs 7 specialized extractors, each scoped only to its relevant pages, calling an LLM to return structured JSON for its section.
5. Merges all extractor outputs into one validated Pydantic schema.
6. Generates Revenue/EBITDA/PAT charts (Matplotlib) from the extracted data.
7. Renders everything into an HTML template styled after the Geojit report, then converts it to a downloadable PDF (WeasyPrint).

The Geojit PDF is **not** the input — it's the visual/structural template the output is designed to resemble. Input documents can be of any company (ICICI, JSW Energy, LTM, etc.) in any of the supported formats.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI |
| Document Parsing | Docling |
| Retrieval | Deterministic keyword + heading weighted Page Index (no vector DB) |
| LLM | Qwen2.5-7B-Instruct via Hugging Face Inference API |
| Validation | Pydantic |
| Charts | Matplotlib |
| Templating | Jinja2 |
| PDF Rendering | WeasyPrint |
| Storage | None — fully in-memory / stateless per request |

**Explicitly not used:** LangChain, LangGraph, CrewAI, FAISS, Pinecone, ChromaDB, Milvus, vector embeddings, hybrid search, rerankers, agent frameworks.

---

## Architecture / Flow

```
Upload (Company Name + Document)
            │
            ▼
     Docling Parser
   (pages, headings, tables)
            │
            ▼
     Page Index Builder
 (weighted heading/keyword/table scoring)
            │
            ▼
   ┌────────┴─────────┐
   │  7 Extractors    │  → company, financials (shareholding +
   │  (task-specific  │     price performance), quarterly, annual
   │   LLM prompts)   │     (+ P&L/BS/CF/ratios), highlights,
   └────────┬─────────┘     outlook, valuation
            │
            ▼
     Merged Report JSON
     (validated via Pydantic)
            │
            ▼
     Chart Generator
    (Matplotlib — Revenue/EBITDA/PAT)
            │
            ▼
   Jinja2 HTML Template
  (Geojit-style layout)
            │
            ▼
      WeasyPrint
            │
            ▼
    Final Downloadable PDF
```

**Key principle:** extractors never touch charts/HTML; the renderer never calls the LLM. Each component has one responsibility.

---

## Folder Structure

```
app/
├── parser/
│   └── docling_parser.py       # PDF/CSV/TXT → structured ParsedDocument (pages/headings/tables)
├── retrieval/
│   └── page_index.py           # Weighted section → page-number scoring
├── extractors/
│   ├── llm_client.py           # Hugging Face Inference API client
│   ├── prompt_builder.py       # ParsedPage list → LLM prompt text
│   ├── base.py                 # Shared run_extraction() + field filtering
│   ├── company.py
│   ├── financials.py           # shareholding + price performance
│   ├── quarterly.py
│   ├── annual.py                # annual estimates + P&L + balance sheet + cashflow + ratios
│   ├── highlights.py
│   ├── outlook.py
│   ├── valuation.py
│   └── merge.py                # Combines all extractors into one ReportSchema
├── prompts/                     # One .txt system prompt per extractor
├── renderer/
│   ├── charts.py                # Matplotlib chart generation (no LLM calls)
│   ├── template.html            # Geojit-style Jinja2 template
│   └── pdf_generator.py         # Jinja2 render → WeasyPrint PDF (no LLM calls)
├── schemas/
│   └── report_schema.py         # Pydantic ReportSchema (single source of truth)
├── static/                      # Generated charts + PDFs served from here
├── templates/
│   └── index.html               # Upload UI
├── uploads/                      # Temp storage for uploaded documents
├── api.py                        # FastAPI routes
└── main.py                       # FastAPI app entrypoint
```

---

## How to Run

### 1. Clone and set up environment

```bash
git clone https://github.com/UtkarshMaurya1/AI-Financial-Report-Generator.git
cd ai_financial_report
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure environment variables

Create a `.env` file in the project root:

```
HF_API_TOKEN=your_huggingface_token_here
HF_MODEL=Qwen/Qwen2.5-7B-Instruct
```

Get a token from [huggingface.co](https://huggingface.co) → Settings → Access Tokens (read scope is sufficient).

### 3. Run the server

```bash
uvicorn app.main:app --reload
```

### 4. Use the app

Open `http://localhost:8000` in your browser:
- Enter a company name
- Upload a financial document (PDF, CSV, or TXT)
- Click **Generate Report**
- The generated PDF downloads automatically

---

## Notes

- All schema fields are `Optional` — missing data in the source document is handled gracefully
- Fiscal years in extracted tables use generic keys (`fy_minus_2` … `fy_plus_2`) instead of hardcoded years, so the schema works across any company's reporting calendar.
- The page index returns confidence scores alongside page numbers, so extractors/future logic can detect low-confidence retrieval and adjust.