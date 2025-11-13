# Backend - Ophthalmology PDF Data Extractor

FastAPI backend for extracting structured data from ophthalmology PDF reports.

## Setup

1. Create a virtual environment (recommended):
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Server

```bash
uvicorn app.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`

## API Endpoint

### POST /extract

Extract data from PDF files and merge with existing Excel file.

**Request:**
- `machine_type` (form field): Machine type (e.g., "IOL700")
- `pdf_files` (file upload): One or multiple PDF files
- `excel_file` (file upload, optional): Existing Excel file to merge with

**Response:**
- Excel file (.xlsx) as downloadable attachment

## Architecture

- `app/main.py`: FastAPI application and `/extract` endpoint
- `app/parsers/`: Parser implementations for different machine types
  - `base.py`: Base parser interface
  - `iol700.py`: IOL700 parser implementation
- `app/excel_handler.py`: Excel file merging and duplicate detection logic

