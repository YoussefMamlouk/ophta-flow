"""
Simple test script for the IOL700 parser.
Run this after installing dependencies to test PDF parsing.
"""
import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.parsers import IOL700Parser

def test_parser(pdf_path: str):
    """Test the IOL700 parser with a sample PDF."""
    if not os.path.exists(pdf_path):
        print(f"Error: PDF file not found: {pdf_path}")
        return
    
    parser = IOL700Parser()
    try:
        results = parser.parse(pdf_path)
        print(f"Successfully parsed PDF: {pdf_path}")
        print(f"Number of rows extracted: {len(results)}")
        for i, row in enumerate(results):
            print(f"\nRow {i+1} ({row.get('Œil', 'Unknown')}):")
            for key, value in row.items():
                print(f"  {key}: {value}")
    except Exception as e:
        print(f"Error parsing PDF: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Test with the sample PDF if it exists
    sample_pdf = "../2510935381_RAJESWARAN_Tharani_20251111113828.pdf"
    if len(sys.argv) > 1:
        sample_pdf = sys.argv[1]
    
    test_parser(sample_pdf)

