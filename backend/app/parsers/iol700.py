import pdfplumber
import re
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import logging
from .base import BaseParser

logger = logging.getLogger(__name__)


class IOL700Parser(BaseParser):
    """Parser for IOLMaster 700 PDF reports."""
    
    # Field mapping: PDF field name -> Excel column name
    FIELD_MAPPING = {
        "ID Patient": "ID Patient",
        "Né(e) le": "Âge",  # Will calculate age from birth date
        "AL": "AL",
        "CCT": "PACHY (mm)",
        "ACD": "ACD epit",
        "LT": "LT",
        "K1": "K1",
        "K2": "K2",
        "WTW": "WTW (mm)",
        "Modèle implanté": "Axe"
    }
    
    def parse(self, pdf_path: str) -> List[Dict[str, any]]:
        """
        Parse IOL700 PDF and extract data for both eyes.
        
        Returns:
            List of 2 dictionaries: [OD_data, OS_data]
        """
        logger.info(f"Parsing PDF: {pdf_path}")
        with pdfplumber.open(pdf_path) as pdf:
            logger.info(f"PDF opened, {len(pdf.pages)} pages")
            # Try to extract tables first (for columnar data)
            tables = []
            full_text = ""
            for page_idx, page in enumerate(pdf.pages):
                page_tables = page.extract_tables()
                if page_tables:
                    tables.extend(page_tables)
                    logger.info(f"Page {page_idx + 1}: Found {len(page_tables)} tables")
                page_text = page.extract_text() or ""
                full_text += page_text
                logger.debug(f"Page {page_idx + 1}: Extracted {len(page_text)} characters of text")
            
            logger.info(f"Total tables found: {len(tables)}, Total text length: {len(full_text)}")
            
            # Extract patient demographics (common to both eyes)
            patient_id = self._extract_field(full_text, r"ID\s+Patient[:\s]+([A-Z0-9_\-\s]+)", "ID Patient")
            if not patient_id:
                # Try alternative patterns
                patient_id = self._extract_field(full_text, r"Patient[:\s]+ID[:\s]+([A-Z0-9_\-\s]+)", "ID Patient")
            if not patient_id:
                # Try from table (ID patient)
                patient_id = self._extract_field(full_text, r"ID\s+patient[:\s]+([A-Z0-9_\-\s]+)", "ID Patient")
            # Clean Patient ID - extract only digits
            if patient_id:
                import re
                # Extract only digits from the patient ID
                digits_only = re.sub(r'\D', '', patient_id)
                patient_id = digits_only if digits_only else patient_id.strip()
            logger.info(f"Extracted Patient ID: '{patient_id}'")
            
            birth_date_str = self._extract_field(full_text, r"Né\(e\)\s+le[:\s]+(\d{1,2}[/\-\.]\d{1,2}[/\-\.]\d{2,4})", "Né(e) le")
            if not birth_date_str:
                # Try alternative patterns
                birth_date_str = self._extract_field(full_text, r"Date\s+de\s+naissance[:\s]+(\d{1,2}[/\-\.]\d{1,2}[/\-\.]\d{2,4})", "Né(e) le")
            # Also try extracting from tables (format: "Né(e) le", "", "17.08.2010")
            if not birth_date_str and tables:
                for table in tables:
                    for row in table:
                        if row and len(row) >= 3:
                            # Check if first cell contains "Né(e) le"
                            first_cell = str(row[0] if row[0] else "").strip()
                            if "Né(e) le" in first_cell or "Né" in first_cell:
                                # Birth date is usually in the 3rd column (index 2)
                                if len(row) > 2 and row[2]:
                                    birth_date_str = str(row[2]).strip()
                                    logger.info(f"Extracted Birth Date from table: '{birth_date_str}'")
                                    break
                        if birth_date_str:
                            break
                    if birth_date_str:
                        break
            logger.info(f"Extracted Birth Date: '{birth_date_str}'")
            
            # Calculate age from birth date
            age = self._calculate_age(birth_date_str) if birth_date_str else ""
            logger.info(f"Calculated Age: '{age}'")
            
            # Try to extract from tables if available
            if tables:
                logger.info("Attempting to extract data from tables")
                od_data, os_data = self._extract_from_tables(tables, patient_id, age)
                if od_data and os_data:
                    logger.info("Successfully extracted data from tables")
                    logger.info(f"OD data: {od_data}")
                    logger.info(f"OS data: {os_data}")
                    return [od_data, os_data]
                else:
                    logger.warning("Table extraction returned None, falling back to text extraction")
                    logger.warning(f"od_data: {od_data}, os_data: {os_data}")
            
            # Fallback to text extraction
            logger.info("Extracting data from text (fallback method)")
            # Extract OD (right eye, left column) values
            od_data = self._extract_eye_data(full_text, "OD")
            od_data["ID Patient"] = patient_id
            od_data["Âge"] = age
            od_data["Œil"] = "OD"
            # Ensure K1, K2, and Axe are always present
            if "K1" not in od_data:
                od_data["K1"] = ""
            if "K2" not in od_data:
                od_data["K2"] = ""
            if "Axe" not in od_data:
                od_data["Axe"] = ""
            logger.debug(f"OD data extracted: {od_data}")
            
            # Extract OS (left eye, right column) values
            os_data = self._extract_eye_data(full_text, "OS")
            os_data["ID Patient"] = patient_id
            os_data["Âge"] = age
            os_data["Œil"] = "OS"
            # Ensure K1, K2, and Axe are always present
            if "K1" not in os_data:
                os_data["K1"] = ""
            if "K2" not in os_data:
                os_data["K2"] = ""
            if "Axe" not in os_data:
                os_data["Axe"] = ""
            logger.debug(f"OS data extracted: {os_data}")
            
            logger.info(f"Returning {len([od_data, os_data])} rows")
            return [od_data, os_data]
    
    def _extract_from_tables(self, tables: List, patient_id: str, age: str) -> Tuple[Optional[Dict[str, any]], Optional[Dict[str, any]]]:
        """Extract data from PDF tables (columnar structure)."""
        logger.info(f"_extract_from_tables called with {len(tables)} tables, patient_id='{patient_id}', age='{age}'")
        od_data = {}
        os_data = {}
        
        for table_idx, table in enumerate(tables):
            logger.info(f"Processing table {table_idx + 1}/{len(tables)}, rows: {len(table) if table else 0}")
            if not table or len(table) < 2:
                logger.debug(f"  Skipping table {table_idx + 1}: too small")
                continue
            
            # Log table structure for debugging
            logger.info(f"  Table {table_idx + 1} structure (first 10 rows, first 8 columns):")
            for r_idx, r in enumerate(table[:10]):  # Log first 10 rows
                row_preview = [str(cell)[:20] if cell else "" for cell in (r[:8] if len(r) > 8 else r)]
                logger.info(f"    Row {r_idx}: {row_preview}")
            
            # Look for OD/OS headers or column structure
            # First, try to find a header row with OD/OS
            header_row_idx = None
            od_col_idx = None
            os_col_idx = None
            
            for row_idx, row in enumerate(table):
                if not row:
                    continue
                
                row_text = " ".join([str(cell) if cell else "" for cell in row]).upper()
                
                # Check if this row contains OD/OS indicators
                has_od = "OD" in row_text
                has_os = "OS" in row_text
                
                if has_od or has_os:
                    logger.info(f"  Found OD/OS header in row {row_idx}: {row[:10]}")
                    header_row_idx = row_idx
                    # Find which columns contain OD and OS
                    # Look for separate columns - OD is usually left, OS is usually right
                    for col_idx, cell in enumerate(row):
                        if not cell:
                            continue
                        cell_text = str(cell).upper()
                        # Check if this cell contains OD (and not OS)
                        if "OD" in cell_text and "OS" not in cell_text and od_col_idx is None:
                            od_col_idx = col_idx
                            logger.info(f"    OD column found at index {col_idx}")
                        # Check if this cell contains OS (and not OD, or if it's clearly separate)
                        elif "OS" in cell_text and os_col_idx is None:
                            # If cell has both OD and OS, check if we can determine separate columns
                            if "OD" not in cell_text:
                                os_col_idx = col_idx
                                logger.info(f"    OS column found at index {col_idx}")
                    
                    # If both found in same cell, try to find separate columns by looking at data rows
                    if od_col_idx == os_col_idx and od_col_idx is not None:
                        logger.info(f"    OD and OS both in column {od_col_idx}, searching for separate columns")
                        # Look at next few rows to find where values are
                        for check_row_idx in range(row_idx + 1, min(row_idx + 10, len(table))):
                            check_row = table[check_row_idx]
                            if not check_row or len(check_row) < 2:
                                continue
                            
                            # Look for pattern like "AL: X.XX" which indicates data columns
                            for col_idx in range(len(check_row)):
                                cell_val = str(check_row[col_idx]) if col_idx < len(check_row) and check_row[col_idx] else ""
                                cell_upper = cell_val.upper()
                                
                                # Check for "AL:" pattern - OD typically has higher values (24+), OS has lower (23+)
                                if "AL:" in cell_upper:
                                    # Extract the AL value to determine which eye
                                    import re
                                    al_match = re.search(r"AL:\s*([\d,\.]+)", cell_upper)
                                    if al_match:
                                        al_val_str = al_match.group(1).replace(",", ".")
                                        try:
                                            al_val = float(al_val_str)
                                            # OD is usually right eye, might have different values
                                            # But we can use column position: left columns = OD, right columns = OS
                                            if col_idx < len(check_row) // 2:
                                                if od_col_idx is None or col_idx < od_col_idx:
                                                    od_col_idx = col_idx
                                                    logger.info(f"    OD column determined from AL value at index {col_idx} (AL={al_val})")
                                            else:
                                                if os_col_idx is None or col_idx > (od_col_idx or 0):
                                                    os_col_idx = col_idx
                                                    logger.info(f"    OS column determined from AL value at index {col_idx} (AL={al_val})")
                                        except ValueError:
                                            pass
                            
                            # Also check for multiline cells with measurement labels
                            for col_idx in range(len(check_row)):
                                cell_val = str(check_row[col_idx]) if col_idx < len(check_row) and check_row[col_idx] else ""
                                if "\n" in cell_val and ("AL" in cell_val.upper() or "CCT" in cell_val.upper()):
                                    # This is likely a measurement column
                                    if col_idx < len(check_row) // 2:
                                        if od_col_idx is None or col_idx < od_col_idx:
                                            od_col_idx = col_idx
                                            logger.info(f"    OD column determined from multiline cell at index {col_idx}")
                                    else:
                                        if os_col_idx is None or col_idx > (od_col_idx or 0):
                                            os_col_idx = col_idx
                                            logger.info(f"    OS column determined from multiline cell at index {col_idx}")
                            
                            if od_col_idx is not None and os_col_idx is not None and od_col_idx != os_col_idx:
                                break
                    
                    # If still not found separately, use column position heuristic
                    if od_col_idx == os_col_idx and od_col_idx is not None:
                        # Assume OD is left half, OS is right half
                        max_cols = max(len(row) for row in table if row) if table else 0
                        if max_cols >= 4:
                            od_col_idx = 0
                            os_col_idx = 4  # Based on logs, OS is at column 4
                            logger.info(f"    Using heuristic: OD at {od_col_idx}, OS at {os_col_idx}")
                        else:
                            od_col_idx = 0
                            os_col_idx = max_cols - 1 if max_cols > 1 else 1
                            logger.info(f"    Using heuristic: OD at {od_col_idx}, OS at {os_col_idx}")
                    
                    break
            
            # If we found OD/OS columns, extract data from rows below
            # Also extract even if columns weren't detected separately (use position-based extraction)
            if header_row_idx is not None:
                # Ensure we have column indices (use defaults if not detected)
                if od_col_idx is None:
                    od_col_idx = 0
                if os_col_idx is None:
                    # Try to find OS column from data, default to column 4
                    for check_row_idx in range(header_row_idx + 1, min(header_row_idx + 6, len(table))):
                        check_row = table[check_row_idx]
                        if check_row and len(check_row) > 4:
                            # Check if column 4 has "AL:" pattern
                            if check_row[4] and "AL:" in str(check_row[4]).upper():
                                os_col_idx = 4
                                break
                    if os_col_idx is None:
                        os_col_idx = 4  # Default based on logs
                
                logger.info(f"  Extracting data from rows after header row {header_row_idx}, OD col={od_col_idx}, OS col={os_col_idx}")
                # Look for measurement rows after the header
                for row_idx in range(header_row_idx + 1, min(header_row_idx + 20, len(table))):
                    row = table[row_idx]
                    if not row:
                        continue
                    
                    # Get all cell text for this row
                    row_text_all = " ".join([str(cell) if cell else "" for cell in row]).upper()
                    row_first_col = str(row[0]).upper() if len(row) > 0 and row[0] else ""
                    
                    # Extract measurements from cells that contain labels and values
                    # Pattern 1: "AL: 24,18 mm" format (like row 4)
                    for col_idx, cell in enumerate(row):
                        if not cell:
                            continue
                        cell_text = str(cell)
                        cell_text_upper = cell_text.upper()
                        
                        # Check for pattern like "AL: 24,18 mm" or "AL: 24.18 mm"
                        for meas_label, excel_col in [("AL", "AL"), ("CCT", "PACHY (mm)"), 
                                                      ("ACD", "ACD epit"), ("LT", "LT"),
                                                      ("K1", "K1"), ("K2", "K2"),
                                                      ("WTW", "WTW (mm)")]:
                            if f"{meas_label}:" in cell_text_upper:
                                # Extract value after the colon
                                val = self._extract_value_from_text(cell_text, meas_label)
                                if val:
                                    # Determine if this is OD or OS based on column position
                                    # Column 0-3 are typically OD, column 4+ are OS (based on logs)
                                    if od_col_idx is not None and col_idx == od_col_idx:
                                        if excel_col not in od_data:  # Don't overwrite
                                            od_data[excel_col] = val
                                            logger.info(f"    OD: {excel_col} = {val} (from pattern match, col {col_idx})")
                                    elif os_col_idx is not None and col_idx == os_col_idx:
                                        if excel_col not in os_data:  # Don't overwrite
                                            os_data[excel_col] = val
                                            logger.info(f"    OS: {excel_col} = {val} (from pattern match, col {col_idx})")
                                    elif col_idx < 4:  # Left side = OD (columns 0-3)
                                        if excel_col not in od_data:
                                            od_data[excel_col] = val
                                            logger.info(f"    OD: {excel_col} = {val} (from position, col {col_idx})")
                                    elif col_idx >= 4:  # Right side = OS (columns 4+)
                                        if excel_col not in os_data:
                                            os_data[excel_col] = val
                                            logger.info(f"    OS: {excel_col} = {val} (from position, col {col_idx})")
                    
                    # Pattern 2: Multi-line cells with label and values (like row 5)
                    # Cell format: "AL\n24,18mm\n24,18mm\n..."
                    for col_idx, cell in enumerate(row):
                        if not cell:
                            continue
                        cell_str = str(cell)
                        # Check if cell has newlines (multi-line)
                        if "\n" in cell_str:
                            lines = [line.strip() for line in cell_str.split("\n") if line.strip()]
                            if len(lines) >= 2:
                                # First line might be label, second line might be value
                                first_line = lines[0].upper()
                                second_line = lines[1] if len(lines) > 1 else ""
                                
                                # Check if first line is a measurement label
                                for meas_label, excel_col in [("AL", "AL"), ("CCT", "PACHY (mm)"), 
                                                              ("ACD", "ACD epit"), ("LT", "LT"),
                                                              ("K1", "K1"), ("K2", "K2"),
                                                              ("WTW", "WTW (mm)")]:
                                    if meas_label in first_line:
                                        # Extract value from second line (remove units)
                                        val = self._extract_value_from_text(second_line, meas_label)
                                        if not val:
                                            # Try extracting from the whole cell
                                            val = self._extract_value_from_text(cell_str, meas_label)
                                        
                                        if val:
                                            # Determine OD/OS based on column position
                                            # Columns 0-3 = OD, columns 4+ = OS
                                            if col_idx < 4:
                                                if excel_col not in od_data:  # Don't overwrite
                                                    od_data[excel_col] = val
                                                    logger.info(f"    OD: {excel_col} = {val} (from multiline cell, col {col_idx})")
                                            else:
                                                if excel_col not in os_data:  # Don't overwrite
                                                    os_data[excel_col] = val
                                                    logger.info(f"    OS: {excel_col} = {val} (from multiline cell, col {col_idx})")
                    
                    # Pattern 3: Extract from specific OD/OS columns if we have them
                    # Also extract from adjacent columns (OD: cols 0-3, OS: cols 4-7)
                    for col_idx in range(len(row)):
                        if col_idx < 4:  # OD columns
                            cell = row[col_idx]
                            if cell:
                                cell_text = str(cell)
                                cell_text_upper = cell_text.upper()
                                for meas_label, excel_col in [("AL", "AL"), ("CCT", "PACHY (mm)"), 
                                                              ("ACD", "ACD epit"), ("LT", "LT"),
                                                              ("K1", "K1"), ("K2", "K2"),
                                                              ("WTW", "WTW (mm)")]:
                                    if meas_label in cell_text_upper and excel_col not in od_data:
                                        val = self._extract_value_from_text(cell_text, meas_label)
                                        if val:
                                            od_data[excel_col] = val
                                            logger.info(f"    OD: {excel_col} = {val} (from column {col_idx})")
                                
                                # Extract "Modèle implanté" - look for "@" followed by number and degree symbol
                                # Check if K1 is in this cell (since "@" is next to K1)
                                if "K1" in cell_text_upper and "Axe" not in od_data:
                                    modele_val = self._extract_modele_implante(cell_text, row, col_idx)
                                    if modele_val:
                                        od_data["Axe"] = modele_val
                                        logger.info(f"    OD: Axe = {modele_val} (from column {col_idx})")
                        else:  # OS columns (4+)
                            cell = row[col_idx]
                            if cell:
                                cell_text = str(cell)
                                cell_text_upper = cell_text.upper()
                                for meas_label, excel_col in [("AL", "AL"), ("CCT", "PACHY (mm)"), 
                                                              ("ACD", "ACD epit"), ("LT", "LT"),
                                                              ("K1", "K1"), ("K2", "K2"),
                                                              ("WTW", "WTW (mm)")]:
                                    if meas_label in cell_text_upper and excel_col not in os_data:
                                        val = self._extract_value_from_text(cell_text, meas_label)
                                        if val:
                                            os_data[excel_col] = val
                                            logger.info(f"    OS: {excel_col} = {val} (from column {col_idx})")
                                
                                # Extract "Modèle implanté" - look for "@" followed by number and degree symbol
                                # Check if K1 is in this cell (since "@" is next to K1)
                                if "K1" in cell_text_upper and "Axe" not in os_data:
                                    modele_val = self._extract_modele_implante(cell_text, row, col_idx)
                                    if modele_val:
                                        os_data["Axe"] = modele_val
                                        logger.info(f"    OS: Axe = {modele_val} (from column {col_idx})")
            
            # Fallback: try the original method if no structured extraction worked
            if not od_data and not os_data:
                logger.info(f"  Fallback: trying original extraction method for table {table_idx + 1}")
                for row_idx, row in enumerate(table):
                    if not row:
                        continue
                    
                    row_text = " ".join([str(cell) if cell else "" for cell in row]).upper()
                    has_od = "OD" in row_text
                    has_os = "OS" in row_text
                    
                    if has_od or has_os:
                        for col_idx, cell in enumerate(row):
                            cell_text = str(cell).upper() if cell else ""
                            
                            # Look for measurement labels and values
                            if "AL" in cell_text:
                                val = self._extract_value_from_cell(row, col_idx, table, row_idx)
                                if has_od and col_idx < len(row) // 2:
                                    od_data["AL"] = val
                                    logger.info(f"    Found AL for OD: {val}")
                                elif has_os and col_idx >= len(row) // 2:
                                    os_data["AL"] = val
                                    logger.info(f"    Found AL for OS: {val}")
                            
                            # Similar patterns for other fields
                            for field_key, field_label in [("CCT", "CCT"), ("ACD", "ACD"), ("LT", "LT"), 
                                                           ("K1", "K1"), ("K2", "K2"), ("WTW", "WTW")]:
                                if field_label in cell_text:
                                    val = self._extract_value_from_cell(row, col_idx, table, row_idx)
                                    excel_col = self.FIELD_MAPPING.get(field_label, field_label)
                                    if has_od and col_idx < len(row) // 2:
                                        od_data[excel_col] = val
                                        logger.info(f"    Found {excel_col} for OD: {val}")
                                    elif has_os and col_idx >= len(row) // 2:
                                        os_data[excel_col] = val
                                        logger.info(f"    Found {excel_col} for OS: {val}")
        
        logger.info(f"After table processing - OD data keys: {list(od_data.keys())}, OS data keys: {list(os_data.keys())}")
        
        if od_data or os_data:
            if not od_data:
                od_data = {"Œil": "OD", "ID Patient": patient_id, "Âge": age, "K1": "", "K2": "", "Axe": ""}
                logger.info("OD data was empty, creating default")
            else:
                od_data["Œil"] = "OD"
                od_data["ID Patient"] = patient_id
                od_data["Âge"] = age
                # Ensure K1, K2, and Axe are always present
                if "K1" not in od_data:
                    od_data["K1"] = ""
                if "K2" not in od_data:
                    od_data["K2"] = ""
                if "Axe" not in od_data:
                    od_data["Axe"] = ""
                logger.info(f"OD data populated: {od_data}")
            
            if not os_data:
                os_data = {"Œil": "OS", "ID Patient": patient_id, "Âge": age, "K1": "", "K2": "", "Axe": ""}
                logger.info("OS data was empty, creating default")
            else:
                os_data["Œil"] = "OS"
                os_data["ID Patient"] = patient_id
                os_data["Âge"] = age
                # Ensure K1, K2, and Axe are always present
                if "K1" not in os_data:
                    os_data["K1"] = ""
                if "K2" not in os_data:
                    os_data["K2"] = ""
                if "Axe" not in os_data:
                    os_data["Axe"] = ""
                logger.info(f"OS data populated: {os_data}")
            
            return od_data, os_data
        
        logger.warning("No data extracted from tables")
        return None, None
    
    def _extract_value_from_cell(self, row: List, col_idx: int, table: List, row_idx: int) -> str:
        """Extract numeric value from a table cell or adjacent cells."""
        # Try current cell
        if col_idx < len(row) and row[col_idx]:
            val = str(row[col_idx]).strip()
            # Remove common units and clean
            val = val.replace("mm", "").replace("D", "").replace("°", "").strip()
            if self._is_numeric(val):
                return val
        
        # Try next cell in same row
        if col_idx + 1 < len(row) and row[col_idx + 1]:
            val = str(row[col_idx + 1]).strip()
            val = val.replace("mm", "").replace("D", "").replace("°", "").strip()
            if self._is_numeric(val):
                return val
        
        # Try cell below
        if row_idx + 1 < len(table) and col_idx < len(table[row_idx + 1]) and table[row_idx + 1][col_idx]:
            val = str(table[row_idx + 1][col_idx]).strip()
            val = val.replace("mm", "").replace("D", "").replace("°", "").strip()
            if self._is_numeric(val):
                return val
        
        return ""
    
    def _extract_value_from_text(self, text: str, label: str) -> str:
        """Extract numeric value from text that contains a measurement label."""
        import re
        text_upper = text.upper()
        
        # Pattern 1: "AL: 24,18 mm" or "AL: 24.18 mm" - extract value after colon
        pattern1 = rf"{label}\s*[:=]\s*([\d,\.]+)"
        match = re.search(pattern1, text_upper)
        if match:
            val = match.group(1).strip()
            # Clean the value: remove units and convert comma to dot
            val = val.replace("mm", "").replace("µm", "").replace("µ", "").replace("D", "").replace("°", "").strip()
            val = val.replace(",", ".")
            if self._is_numeric(val):
                logger.debug(f"      Extracted {label} value '{val}' from pattern1: '{text[:50]}'")
                return val
        
        # Pattern 2: Label followed by number (for multiline cells like "AL\n24,18mm")
        # Look for label, then any text, then a number
        pattern2 = rf"{label}.*?([\d,\.]+)"
        match = re.search(pattern2, text_upper, re.DOTALL)
        if match:
            val = match.group(1).strip()
            # Clean the value
            val = val.replace("mm", "").replace("µm", "").replace("µ", "").replace("D", "").replace("°", "").strip()
            val = val.replace(",", ".")
            if self._is_numeric(val):
                logger.debug(f"      Extracted {label} value '{val}' from pattern2: '{text[:50]}'")
                return val
        
        # Pattern 3: Extract first valid number found in text (for cells with just numbers)
        # Look for numbers that could be measurements (typically 1.0 to 50.0 range for these measurements)
        numbers = re.findall(r"[\d,\.]+", text)
        for num_str in numbers:
            val = num_str.replace(",", ".").strip()
            if self._is_numeric(val):
                num_val = float(val)
                # Filter out invalid ranges (like single digits that might be row numbers)
                if num_val > 0.5 and num_val < 100:  # Reasonable range for measurements
                    logger.debug(f"      Extracted {label} value '{val}' from pattern3: '{text[:50]}'")
                    return val
        
        logger.debug(f"      Failed to extract {label} value from: '{text[:50]}'")
        return ""
    
    def _extract_modele_implante(self, cell_text: str, row: List, col_idx: int) -> str:
        """Extract 'Modèle implanté' value - looks for '@' followed by number and degree symbol."""
        import re
        # Pattern: "@" followed by optional spaces, then number, then degree symbol (°)
        # Look in current cell first
        pattern = r"@\s*(\d+)\s*°"
        match = re.search(pattern, cell_text)
        if match:
            return match.group(1)
        
        # If not found, check adjacent cells (next column)
        if col_idx + 1 < len(row) and row[col_idx + 1]:
            next_cell_text = str(row[col_idx + 1])
            match = re.search(pattern, next_cell_text)
            if match:
                return match.group(1)
        
        # Also try without degree symbol (just number after @)
        pattern2 = r"@\s*(\d+)"
        match = re.search(pattern2, cell_text)
        if match:
            return match.group(1)
        
        if col_idx + 1 < len(row) and row[col_idx + 1]:
            next_cell_text = str(row[col_idx + 1])
            match = re.search(pattern2, next_cell_text)
            if match:
                return match.group(1)
        
        return ""
    
    def _is_numeric(self, value: str) -> bool:
        """Check if a string represents a numeric value."""
        try:
            float(value.replace(",", "."))
            return True
        except (ValueError, AttributeError):
            return False
    
    def _extract_eye_data(self, text: str, eye: str) -> Dict[str, any]:
        """Extract measurements for a specific eye (OD or OS)."""
        data = {}
        
        # Try to find eye-specific sections
        # Look for patterns like "OD:" or "OS:" followed by measurements
        eye_pattern = rf"{eye}[:\s]*"
        
        # Extract AL (Axial Length)
        # Try multiple patterns for better extraction
        al = self._extract_numeric_field(text, rf"{eye_pattern}.*?AL[:\s]+([\d.,]+)", "AL")
        if not al:
            al = self._extract_numeric_field(text, rf"AL[:\s]+([\d.,]+).*?{eye}", "AL")
        if not al:
            # Try pattern with mm unit
            al = self._extract_numeric_field(text, rf"{eye_pattern}.*?AL[:\s]+([\d.,]+)\s*mm", "AL")
        data["AL"] = al.replace(",", ".") if al else ""
        
        # Extract CCT (Central Corneal Thickness) -> PACHY (mm)
        cct = self._extract_numeric_field(text, rf"{eye_pattern}.*?CCT[:\s]+([\d.,]+)", "CCT")
        if not cct:
            cct = self._extract_numeric_field(text, rf"CCT[:\s]+([\d.,]+).*?{eye}", "CCT")
        if not cct:
            # Try PACHY pattern
            cct = self._extract_numeric_field(text, rf"{eye_pattern}.*?PACHY[:\s]+([\d.,]+)", "CCT")
        data["PACHY (mm)"] = cct.replace(",", ".") if cct else ""
        
        # Extract ACD (Anterior Chamber Depth) -> ACD epit
        acd = self._extract_numeric_field(text, rf"{eye_pattern}.*?ACD[:\s]+([\d.,]+)", "ACD")
        if not acd:
            acd = self._extract_numeric_field(text, rf"ACD[:\s]+([\d.,]+).*?{eye}", "ACD")
        if not acd:
            # Try ACD epit pattern
            acd = self._extract_numeric_field(text, rf"{eye_pattern}.*?ACD\s+epit[:\s]+([\d.,]+)", "ACD")
        data["ACD epit"] = acd.replace(",", ".") if acd else ""
        
        # Extract LT (Lens Thickness)
        lt = self._extract_numeric_field(text, rf"{eye_pattern}.*?LT[:\s]+([\d.,]+)", "LT")
        if not lt:
            lt = self._extract_numeric_field(text, rf"LT[:\s]+([\d.,]+).*?{eye}", "LT")
        data["LT"] = lt.replace(",", ".") if lt else ""
        
        # Extract K1 -> K1
        k1 = self._extract_numeric_field(text, rf"{eye_pattern}.*?K1[:\s]+([\d.,]+)", "K1")
        if not k1:
            k1 = self._extract_numeric_field(text, rf"K1[:\s]+([\d.,]+).*?{eye}", "K1")
        data["K1"] = k1.replace(",", ".") if k1 else ""
        
        # Extract K2 -> K2
        k2 = self._extract_numeric_field(text, rf"{eye_pattern}.*?K2[:\s]+([\d.,]+)", "K2")
        if not k2:
            k2 = self._extract_numeric_field(text, rf"K2[:\s]+([\d.,]+).*?{eye}", "K2")
        data["K2"] = k2.replace(",", ".") if k2 else ""
        
        # Extract WTW (White-to-White)
        wtw = self._extract_numeric_field(text, rf"{eye_pattern}.*?WTW[:\s]+([\d.,]+)", "WTW")
        if not wtw:
            wtw = self._extract_numeric_field(text, rf"WTW[:\s]+([\d.,]+).*?{eye}", "WTW")
        data["WTW (mm)"] = wtw.replace(",", ".") if wtw else ""
        
        # Extract Axe (Modèle implanté) - look for "@" followed by number and degree symbol
        # Try to find it near K1 in the text
        axe_pattern = rf"{eye_pattern}.*?@\s*(\d+)\s*°"
        axe_match = re.search(axe_pattern, text, re.IGNORECASE | re.MULTILINE | re.DOTALL)
        if not axe_match:
            # Try without eye pattern
            axe_pattern = r"@\s*(\d+)\s*°"
            axe_match = re.search(axe_pattern, text, re.IGNORECASE | re.MULTILINE | re.DOTALL)
        if not axe_match:
            # Try without degree symbol
            axe_pattern = rf"{eye_pattern}.*?@\s*(\d+)"
            axe_match = re.search(axe_pattern, text, re.IGNORECASE | re.MULTILINE | re.DOTALL)
        if not axe_match:
            axe_pattern = r"@\s*(\d+)"
            axe_match = re.search(axe_pattern, text, re.IGNORECASE | re.MULTILINE | re.DOTALL)
        data["Axe"] = axe_match.group(1) if axe_match else ""
        
        return data
    
    def _extract_field(self, text: str, pattern: str, field_name: str) -> Optional[str]:
        """Extract a text field using regex."""
        match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
        if match:
            return match.group(1).strip()
        return ""
    
    def _extract_numeric_field(self, text: str, pattern: str, field_name: str) -> Optional[str]:
        """Extract a numeric field using regex."""
        match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE | re.DOTALL)
        if match:
            value = match.group(1).strip()
            # Replace comma with dot for decimal separator
            value = value.replace(",", ".")
            # Try to convert to float to validate, but return as string
            try:
                float(value)
                return value
            except ValueError:
                return ""
        return ""
    
    def _calculate_age(self, birth_date_str: str) -> str:
        """Calculate age from birth date string."""
        if not birth_date_str:
            return ""
        
        # Try different date formats (including dots)
        date_formats = [
            "%d.%m.%Y",  # 17.08.2010
            "%d/%m/%Y",
            "%d-%m-%Y",
            "%d.%m.%y",  # 17.08.10
            "%d/%m/%y",
            "%d-%m-%y",
            "%Y.%m.%d",  # 2010.08.17
            "%Y/%m/%d",
            "%Y-%m-%d"
        ]
        
        birth_date = None
        for fmt in date_formats:
            try:
                birth_date = datetime.strptime(birth_date_str, fmt)
                # If 2-digit year, assume 1900s if > 50, else 2000s
                if fmt.endswith("%y") and birth_date.year < 1950:
                    birth_date = birth_date.replace(year=birth_date.year + 100)
                break
            except ValueError:
                continue
        
        if not birth_date:
            return ""
        
        today = datetime.now()
        age = today.year - birth_date.year
        if (today.month, today.day) < (birth_date.month, birth_date.day):
            age -= 1
        
        return str(age)

