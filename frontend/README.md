# Frontend - Ophthalmology PDF Data Extractor

React + TypeScript frontend for the ophthalmology PDF data extraction application.

## Setup

1. Install dependencies:
```bash
npm install
```

## Running the Development Server

```bash
npm run dev
```

The application will be available at `http://localhost:3000`

## Building for Production

```bash
npm run build
```

## Project Structure

- `src/App.tsx`: Main application component
- `src/components/`: React components
  - `MachineSelector.tsx`: Machine type selection dropdown
  - `PDFUploader.tsx`: Multiple PDF file uploader
  - `ExcelUploader.tsx`: Optional Excel file uploader
  - `ProcessButton.tsx`: Process button with loading state
  - `StatusDisplay.tsx`: Status messages and download link

## Configuration

The frontend is configured to proxy API requests to `http://localhost:8000` (backend server).

