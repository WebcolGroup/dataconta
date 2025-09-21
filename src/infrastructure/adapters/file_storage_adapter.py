"""
File storage adapter - Implementation of FileStorage port.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

from src.application.ports.interfaces import FileStorage, Logger


class FileStorageAdapter(FileStorage):
    """Adapter for file storage operations."""
    
    def __init__(self, output_directory: str, logger: Logger):
        self._output_directory = Path(output_directory)
        self._logger = logger
        self._ensure_output_directory()
    
    def save_data(self, data: Dict[str, Any], filename: str) -> str:
        """Save data to file and return the file path."""
        try:
            # Handle subdirectories in filename
            if '/' in filename:
                filename_parts = filename.split('/')
                subdirs = filename_parts[:-1]
                base_filename = filename_parts[-1]
                
                # Create subdirectories if they don't exist
                subdir_path = self._output_directory
                for subdir in subdirs:
                    subdir_path = subdir_path / subdir
                    subdir_path.mkdir(parents=True, exist_ok=True)
                
                filename_for_timestamp = base_filename
                target_directory = subdir_path
            else:
                filename_for_timestamp = filename
                target_directory = self._output_directory
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            full_filename = f"{filename_for_timestamp}_{timestamp}.json"
            file_path = target_directory / full_filename
            
            # Save data as JSON
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)
            
            self._logger.info(f"Data saved to: {file_path}")
            return str(file_path)
            
        except Exception as e:
            self._logger.error(f"Failed to save data to file: {e}")
            raise Exception(f"File save error: {e}")
    
    def list_files(self) -> List[str]:
        """List all saved files."""
        try:
            if not self._output_directory.exists():
                return []
            
            files = []
            for file_path in self._output_directory.glob("*"):
                if file_path.is_file():
                    files.append(file_path.name)
            
            return sorted(files)
            
        except Exception as e:
            self._logger.error(f"Failed to list files: {e}")
            raise Exception(f"File listing error: {e}")
    
    def get_file_info(self, filename: str) -> Dict[str, Any]:
        """Get information about a specific file."""
        try:
            file_path = self._output_directory / filename
            
            if not file_path.exists():
                return {
                    "exists": False,
                    "size": 0,
                    "modified": None
                }
            
            stat = file_path.stat()
            modified_time = datetime.fromtimestamp(stat.st_mtime)
            
            return {
                "exists": True,
                "size": stat.st_size,
                "modified": modified_time.strftime('%Y-%m-%d %H:%M:%S'),
                "path": str(file_path)
            }
            
        except Exception as e:
            self._logger.error(f"Failed to get file info for {filename}: {e}")
            return {
                "exists": False,
                "size": 0,
                "modified": None,
                "error": str(e)
            }
    
    def _ensure_output_directory(self) -> None:
        """Ensure the output directory exists."""
        try:
            self._output_directory.mkdir(parents=True, exist_ok=True)
            self._logger.debug(f"Output directory ready: {self._output_directory}")
        except Exception as e:
            self._logger.error(f"Failed to create output directory: {e}")
            raise Exception(f"Directory creation error: {e}")