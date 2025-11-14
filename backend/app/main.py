from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import tempfile
import os
import logging
from app.parsers import IOL700Parser
from app.excel_handler import merge_excel_data, create_excel_from_rows

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Ophthalmology PDF Data Extractor")

# Add CORS middleware for frontend
# Get frontend URL from environment variable, fallback to localhost for development
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        FRONTEND_URL,
        "http://localhost:3000",
        "http://localhost:5173",  # Vite default port
        "*"  # Allow all in development, restrict in production
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/extract")
async def extract_data(
    machine_type: str = Form(...),
    pdf_files: List[UploadFile] = File(...),
    excel_file: Optional[UploadFile] = File(None)
):
    """
    Extract data from PDF files and merge with existing Excel file.
    
    Args:
        machine_type: Type of machine (e.g., "IOL700")
        pdf_files: List of PDF files to process
        excel_file: Optional existing Excel file to merge with
        
    Returns:
        Updated Excel file as downloadable response
    """
    logger.info(f"Extract endpoint called with machine_type={machine_type}, {len(pdf_files)} PDF files, excel_file={'provided' if excel_file else 'not provided'}")
    
    if not pdf_files:
        raise HTTPException(status_code=400, detail="At least one PDF file is required")
    
    # Select parser based on machine type
    parser = None
    if machine_type == "IOL700":
        parser = IOL700Parser()
        logger.info("Using IOL700Parser")
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported machine type: {machine_type}")
    
    # Create temporary directory for processing
    with tempfile.TemporaryDirectory() as temp_dir:
        all_rows = []
        
        # Process each PDF file
        for pdf_file in pdf_files:
            logger.info(f"Processing PDF: {pdf_file.filename}")
            # Save uploaded PDF to temp file
            pdf_path = os.path.join(temp_dir, pdf_file.filename)
            with open(pdf_path, "wb") as f:
                content = await pdf_file.read()
                f.write(content)
            logger.info(f"PDF saved to {pdf_path}, size: {len(content)} bytes")
            
            # Parse PDF
            try:
                rows = parser.parse(pdf_path)
                logger.info(f"Parsed PDF {pdf_file.filename}: extracted {len(rows)} rows")
                for idx, row in enumerate(rows):
                    logger.debug(f"  Row {idx}: {row}")
                all_rows.extend(rows)
            except Exception as e:
                logger.error(f"Error parsing PDF {pdf_file.filename}: {str(e)}", exc_info=True)
                raise HTTPException(
                    status_code=500,
                    detail=f"Error parsing PDF {pdf_file.filename}: {str(e)}"
                )
        
        logger.info(f"Total rows extracted: {len(all_rows)}")
        
        # Handle Excel file if provided
        existing_excel_path = None
        if excel_file:
            logger.info(f"Excel file provided: {excel_file.filename}")
            existing_excel_path = os.path.join(temp_dir, excel_file.filename)
            with open(existing_excel_path, "wb") as f:
                content = await excel_file.read()
                f.write(content)
            logger.info(f"Excel file saved to {existing_excel_path}, size: {len(content)} bytes")
        else:
            logger.info("No Excel file provided")
        
        # Create output Excel file
        output_path = os.path.join(temp_dir, "output.xlsx")
        logger.info(f"Output path: {output_path}")
        
        try:
            if existing_excel_path:
                logger.info("Calling merge_excel_data")
                merge_excel_data(existing_excel_path, all_rows, output_path)
            else:
                logger.info("Calling create_excel_from_rows")
                create_excel_from_rows(all_rows, output_path)
            
            # Verify file exists and has content
            if not os.path.exists(output_path):
                raise HTTPException(status_code=500, detail="Failed to create output Excel file")
            
            # Read the file content before temp directory is deleted
            with open(output_path, "rb") as f:
                file_content = f.read()
            
            if len(file_content) == 0:
                raise HTTPException(status_code=500, detail="Output Excel file is empty")
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(status_code=500, detail=f"Error creating Excel file: {str(e)}")
        
        # Return file as downloadable response
        return Response(
            content=file_content,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment; filename=extracted_data.xlsx"}
        )

