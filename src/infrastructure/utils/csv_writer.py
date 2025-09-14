"""
DataConta - CSV Writer Utility
Utility class for efficient CSV writing operations for Business Intelligence exports.
"""

import csv
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

from src.application.ports.interfaces import Logger


class CSVWriter:
    """
    Utility class for writing CSV files efficiently for BI exports.
    Handles file creation, directory management, and data validation.
    """
    
    def __init__(self, logger: Logger, base_output_dir: str = "outputs/bi"):
        """Initialize CSVWriter with logger and base output directory."""
        self._logger = logger
        self._base_output_dir = Path(base_output_dir)
        self._project_root = Path(__file__).parent.parent.parent.parent
        self._full_output_dir = self._project_root / self._base_output_dir
    
    def ensure_output_directory(self) -> bool:
        """
        Ensure the BI output directory exists.
        
        Returns:
            True if directory exists or was created successfully
        """
        try:
            self._full_output_dir.mkdir(parents=True, exist_ok=True)
            self._logger.debug(f"BI output directory ensured: {self._full_output_dir}")
            return True
        
        except Exception as e:
            self._logger.error(f"Error creating BI output directory {self._full_output_dir}: {e}")
            return False
    
    def write_csv_file(
        self, 
        filename: str, 
        headers: List[str], 
        rows: List[Dict[str, Any]], 
        validate_headers: bool = True
    ) -> bool:
        """
        Write data to CSV file in the BI output directory.
        
        Args:
            filename: Name of the CSV file
            headers: List of column headers
            rows: List of row data as dictionaries
            validate_headers: Whether to validate that all rows have required headers
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Ensure output directory exists
            if not self.ensure_output_directory():
                return False
            
            file_path = self._full_output_dir / filename
            
            # Validate data if requested
            if validate_headers and rows:
                if not self._validate_row_headers(headers, rows):
                    return False
            
            # Write CSV file
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=headers, quoting=csv.QUOTE_MINIMAL)
                
                # Write headers
                writer.writeheader()
                
                # Write data rows
                for row in rows:
                    # Filter row to only include headers (remove extra fields)
                    filtered_row = {k: row.get(k, '') for k in headers}
                    writer.writerow(filtered_row)
            
            self._logger.info(f"BI CSV file written successfully: {filename} ({len(rows)} rows)")
            return True
        
        except Exception as e:
            self._logger.error(f"Error writing BI CSV file {filename}: {e}")
            return False
    
    def _validate_row_headers(self, headers: List[str], rows: List[Dict[str, Any]]) -> bool:
        """
        Validate that all rows contain the required headers.
        
        Args:
            headers: Expected headers
            rows: Data rows to validate
            
        Returns:
            True if validation passes
        """
        try:
            missing_fields_count = 0
            
            for i, row in enumerate(rows[:10]):  # Check first 10 rows for performance
                missing_fields = [h for h in headers if h not in row]
                if missing_fields:
                    self._logger.warning(f"Row {i} missing fields: {missing_fields}")
                    missing_fields_count += 1
            
            if missing_fields_count > 0:
                self._logger.warning(f"{missing_fields_count} rows have missing fields (checked first 10)")
            
            return True  # Allow processing even with warnings
        
        except Exception as e:
            self._logger.error(f"Error validating row headers: {e}")
            return False
    
    def write_multiple_csvs(self, csv_data: Dict[str, Dict[str, Any]]) -> Dict[str, bool]:
        """
        Write multiple CSV files in a single operation.
        
        Args:
            csv_data: Dictionary where key is filename and value contains 'headers' and 'rows'
            
        Returns:
            Dictionary with filename as key and success status as value
        """
        results = {}
        
        for filename, data in csv_data.items():
            headers = data.get('headers', [])
            rows = data.get('rows', [])
            
            if not headers:
                self._logger.error(f"No headers provided for {filename}")
                results[filename] = False
                continue
            
            results[filename] = self.write_csv_file(filename, headers, rows)
        
        return results
    
    def get_output_directory(self) -> str:
        """Get the full path to the BI output directory."""
        return str(self._full_output_dir)
    
    def get_file_info(self, filename: str) -> Dict[str, Any]:
        """
        Get information about a file in the BI output directory.
        
        Args:
            filename: Name of the file
            
        Returns:
            Dictionary with file information
        """
        try:
            file_path = self._full_output_dir / filename
            
            if not file_path.exists():
                return {"exists": False}
            
            stat = file_path.stat()
            return {
                "exists": True,
                "size": stat.st_size,
                "created": datetime.fromtimestamp(stat.st_ctime),
                "modified": datetime.fromtimestamp(stat.st_mtime),
                "size_kb": round(stat.st_size / 1024, 2),
                "full_path": str(file_path)
            }
        
        except Exception as e:
            self._logger.error(f"Error getting file info for {filename}: {e}")
            return {"exists": False, "error": str(e)}
    
    def list_bi_files(self) -> List[Dict[str, Any]]:
        """
        List all CSV files in the BI output directory.
        
        Returns:
            List of file information dictionaries
        """
        try:
            if not self._full_output_dir.exists():
                return []
            
            files = []
            for file_path in self._full_output_dir.glob("*.csv"):
                info = self.get_file_info(file_path.name)
                if info.get("exists", False):
                    info["name"] = file_path.name
                    files.append(info)
            
            return sorted(files, key=lambda x: x.get("modified", datetime.min), reverse=True)
        
        except Exception as e:
            self._logger.error(f"Error listing BI files: {e}")
            return []