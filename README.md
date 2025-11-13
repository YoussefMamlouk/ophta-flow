# Ophthalmology PDF Data Extractor

A complete web application for extracting structured ophthalmology data from medical PDF reports and merging with existing Excel files.

## Features

- Extract data from IOLMaster 700 PDF reports
- Support for multiple PDF files
- Merge with existing Excel files
- Automatic duplicate detection (by Patient ID + Eye)
- Clean, modern web interface
- Two rows per PDF (OD and OS eyes)

## Project Structure

```
aleksandra/
├── backend/          # FastAPI backend
│   ├── app/
│   │   ├── main.py              # FastAPI app
│   │   ├── parsers/             # PDF parsers
│   │   └── excel_handler.py     # Excel operations
│   └── requirements.txt
├── frontend/         # React frontend
│   ├── src/
│   │   ├── App.tsx
│   │   └── components/
│   └── package.json
└── README.md
```

## Quick Start

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Create virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the server:
```bash
uvicorn app.main:app --reload --port 8000
```

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Run the development server:
```bash
npm run dev
```

4. Open `http://localhost:3000` in your browser

## Usage

1. Select machine type (currently only "IOL700")
2. Upload one or multiple PDF files
3. Optionally upload an existing Excel file
4. Click "Process PDFs"
5. Download the resulting Excel file

## Field Mapping

The application extracts the following fields from PDFs:

- ID Patient → ID Patient
- Birth Date (Né(e) le) → Age (calculated)
- AL → AL
- CCT → PACHY (mm)
- ACD → ACD epit
- LT → LT
- K1 → PUISSANCE IOL
- K2 → TORIQUE PROG EDOF
- WTW → WTW (mm)
- Eye → Œil (OD or OS)

## Notes

- Each PDF produces two rows: one for OD (right eye) and one for OS (left eye)
- Duplicate rows (same Patient ID + Eye) are automatically skipped
- Excel structure is preserved (row 1 + column headers in row 2)

