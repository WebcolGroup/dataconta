"""
DataConta - CSV File Adapter
Infrastructure adapter for CSV file operations.
"""

import csv
import os
from pathlib import Path
from typing import List
from datetime import datetime

from src.application.ports.interfaces import CSVExporter, Logger


class CSVFileAdapter(CSVExporter):
    """
    Adapter for CSV file export operations.
    Handles file system operations and CSV writing.
    """
    
    def __init__(self, logger: Logger):
        """Initialize the adapter with required dependencies."""
        self._logger = logger
        # Get project root directory (3 levels up from this file)
        self._project_root = Path(__file__).parent.parent.parent.parent
        self._outputs_dir = self._project_root / "outputs"
    
    def write_csv(self, file_path: str, headers: List[str], rows: List[List[str]]) -> bool:
        """
        Write data to CSV file in the outputs directory.
        
        Args:
            file_path: Filename (will be placed in outputs directory)
            headers: List of column headers
            rows: List of data rows (each row is a list of values)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Ensure outputs directory exists
            if not self.ensure_output_directory(str(self._outputs_dir)):
                return False
            
            # Create full path in outputs directory
            full_path = self._outputs_dir / file_path
            
            # Write CSV file
            with open(full_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL)
                
                # Write headers
                writer.writerow(headers)
                
                # Write data rows
                for row in rows:
                    writer.writerow(row)
            
            self._logger.info(f"CSV file written successfully: {full_path} ({len(rows)} rows)")
            return True
        
        except Exception as e:
            self._logger.error(f"Error writing CSV file {file_path}: {e}")
            return False
    
    def ensure_output_directory(self, directory_path: str) -> bool:
        """
        Ensure output directory exists.
        
        Args:
            directory_path: Path to the output directory
            
        Returns:
            True if directory exists or was created successfully
        """
        try:
            Path(directory_path).mkdir(parents=True, exist_ok=True)
            self._logger.debug(f"Output directory ensured: {directory_path}")
            return True
        
        except Exception as e:
            self._logger.error(f"Error creating output directory {directory_path}: {e}")
            return False
    
    def generate_timestamped_filename(self, base_name: str, extension: str = "csv") -> str:
        """
        Generate a filename with timestamp.
        
        Args:
            base_name: Base name for the file
            extension: File extension (without dot)
            
        Returns:
            Filename with timestamp
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{base_name}_{timestamp}.{extension}"
    
    def get_file_info(self, file_path: str) -> dict:
        """
        Get information about a file in outputs directory.
        
        Args:
            file_path: Filename (will be looked for in outputs directory)
            
        Returns:
            Dictionary with file information
        """
        try:
            full_path = self._outputs_dir / file_path
            
            if not full_path.exists():
                return {"exists": False}
            
            stat = full_path.stat()
            return {
                "exists": True,
                "size": stat.st_size,
                "created": datetime.fromtimestamp(stat.st_ctime),
                "modified": datetime.fromtimestamp(stat.st_mtime),
                "size_kb": round(stat.st_size / 1024, 2),
                "full_path": str(full_path)
            }
        
        except Exception as e:
            self._logger.error(f"Error getting file info for {file_path}: {e}")
            return {"exists": False, "error": str(e)}
    
    def get_outputs_directory(self) -> str:
        """
        Get the outputs directory path.
        
        Returns:
            Path to outputs directory
        """
        return str(self._outputs_dir)