from abc import ABC, abstractmethod
from typing import List, Dict


class BaseParser(ABC):
    """Base interface for PDF parsers."""
    
    @abstractmethod
    def parse(self, pdf_path: str) -> List[Dict[str, any]]:
        """
        Parse a PDF file and extract structured data.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            List of dictionaries, each representing one row of data.
            For ophthalmology reports, typically 2 dicts per PDF (OD and OS).
        """
        pass

