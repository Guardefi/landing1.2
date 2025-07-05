"""
Filesystem Utilities Module
---------------------------
Provides utilities for file operations, archiving, and exports without Git internals.
Replaces the previous implementation that mixed Git operations with zip exports.
"""
import os
import zipfile
import tarfile
import shutil
import logging
from typing import List, Optional, Dict, Union, Callable
from pathlib import Path
import fnmatch
import hashlib
from datetime import datetime

logger = logging.getLogger("core.filesystem")

class ExportFilter:
    """Filter class for excluding unwanted files from exports"""
    
    DEFAULT_EXCLUDES = [
        ".git",
        ".git/**",
        "__pycache__",
        "**/__pycache__/**",
        "*.pyc",
        "*.pyo",
        ".pytest_cache",
        "**/.pytest_cache/**",
        "node_modules",
        "**/node_modules/**",
        ".env",
        ".env.*",
        "*.log",
        ".DS_Store",
        "Thumbs.db",
        "*.tmp",
        "*.temp",
        ".vscode",
        ".idea",
        "*.swp",
        "*.swo",
        "*~"
    ]
    
    def __init__(self, excludes: List[str] = None, includes_only: List[str] = None):
        """
        Initialize filter with exclude and include patterns
        
        Args:
            excludes: List of patterns to exclude (defaults to DEFAULT_EXCLUDES)
            includes_only: If provided, only include files matching these patterns
        """
        self.excludes = excludes if excludes is not None else self.DEFAULT_EXCLUDES.copy()
        self.includes_only = includes_only
    
    def should_include(self, file_path: str, relative_path: str) -> bool:
        """
        Check if a file should be included in the export
        
        Args:
            file_path: Absolute path to the file
            relative_path: Relative path from the export root
            
        Returns:
            True if file should be included, False otherwise
        """
        # Check includes_only first (if specified)
        if self.includes_only:
            included = any(fnmatch.fnmatch(relative_path, pattern) for pattern in self.includes_only)
            if not included:
                return False
        
        # Check excludes
        for pattern in self.excludes:
            if fnmatch.fnmatch(relative_path, pattern):
                logger.debug(f"Excluding {relative_path} (matches pattern: {pattern})")
                return False
        
        return True


class FileSystemExporter:
    """Handles file system exports without Git internals"""
    
    def __init__(self, export_filter: Optional[ExportFilter] = None):
        """
        Initialize the exporter
        
        Args:
            export_filter: Filter to use for excluding files
        """
        self.filter = export_filter or ExportFilter()
    
    def create_zip_export(self, 
                         source_path: str, 
                         output_path: str,
                         compression: int = zipfile.ZIP_DEFLATED,
                         exclude_git: bool = True) -> Dict[str, Union[str, int]]:
        """
        Create a ZIP archive of the specified directory, excluding Git internals
        
        Args:
            source_path: Path to the directory to archive
            output_path: Path for the output ZIP file
            compression: Compression method to use
            exclude_git: Whether to exclude Git directories (default: True)
            
        Returns:
            Dictionary with export statistics
        """
        source_path = Path(source_path).resolve()
        output_path = Path(output_path).resolve()
        
        if not source_path.exists():
            raise FileNotFoundError(f"Source path does not exist: {source_path}")
        
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        stats = {
            "files_processed": 0,
            "files_included": 0,
            "files_excluded": 0,
            "total_size": 0,
            "compressed_size": 0,
            "output_file": str(output_path)
        }
        
        logger.info(f"Creating ZIP export from {source_path} to {output_path}")
        
        with zipfile.ZipFile(output_path, 'w', compression=compression) as zipf:
            for root, dirs, files in os.walk(source_path):
                # Remove excluded directories from dirs list to prevent walking into them
                dirs[:] = [d for d in dirs if self._should_include_dir(os.path.join(root, d), source_path)]
                
                for file in files:
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, source_path)
                    
                    stats["files_processed"] += 1
                    
                    if self.filter.should_include(file_path, relative_path):
                        try:
                            # Get file info
                            file_size = os.path.getsize(file_path)
                            stats["total_size"] += file_size
                            
                            # Add to archive
                            zipf.write(file_path, relative_path)
                            stats["files_included"] += 1
                            
                            logger.debug(f"Added to archive: {relative_path}")
                            
                        except Exception as e:
                            logger.warning(f"Failed to add {relative_path} to archive: {str(e)}")
                            stats["files_excluded"] += 1
                    else:
                        stats["files_excluded"] += 1
        
        # Get compressed size
        stats["compressed_size"] = output_path.stat().st_size
        
        logger.info(f"ZIP export completed: {stats['files_included']} files, "
                   f"{stats['total_size']} bytes -> {stats['compressed_size']} bytes")
        
        return stats
    
    def create_tar_export(self,
                         source_path: str,
                         output_path: str,
                         compression: str = "gz") -> Dict[str, Union[str, int]]:
        """
        Create a TAR archive of the specified directory
        
        Args:
            source_path: Path to the directory to archive
            output_path: Path for the output TAR file
            compression: Compression method ("", "gz", "bz2", "xz")
            
        Returns:
            Dictionary with export statistics
        """
        source_path = Path(source_path).resolve()
        output_path = Path(output_path).resolve()
        
        if not source_path.exists():
            raise FileNotFoundError(f"Source path does not exist: {source_path}")
        
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Determine mode based on compression
        mode = "w"
        if compression == "gz":
            mode = "w:gz"
        elif compression == "bz2":
            mode = "w:bz2"
        elif compression == "xz":
            mode = "w:xz"
        
        stats = {
            "files_processed": 0,
            "files_included": 0,
            "files_excluded": 0,
            "total_size": 0,
            "compressed_size": 0,
            "output_file": str(output_path)
        }
        
        logger.info(f"Creating TAR export from {source_path} to {output_path}")
        
        with tarfile.open(output_path, mode) as tarf:
            for root, dirs, files in os.walk(source_path):
                # Remove excluded directories from dirs list
                dirs[:] = [d for d in dirs if self._should_include_dir(os.path.join(root, d), source_path)]
                
                for file in files:
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, source_path)
                    
                    stats["files_processed"] += 1
                    
                    if self.filter.should_include(file_path, relative_path):
                        try:
                            # Get file info
                            file_size = os.path.getsize(file_path)
                            stats["total_size"] += file_size
                            
                            # Add to archive
                            tarf.add(file_path, arcname=relative_path)
                            stats["files_included"] += 1
                            
                            logger.debug(f"Added to archive: {relative_path}")
                            
                        except Exception as e:
                            logger.warning(f"Failed to add {relative_path} to archive: {str(e)}")
                            stats["files_excluded"] += 1
                    else:
                        stats["files_excluded"] += 1
        
        # Get compressed size
        stats["compressed_size"] = output_path.stat().st_size
        
        logger.info(f"TAR export completed: {stats['files_included']} files, "
                   f"{stats['total_size']} bytes -> {stats['compressed_size']} bytes")
        
        return stats
    
    def _should_include_dir(self, dir_path: str, base_path: str) -> bool:
        """
        Check if a directory should be included (walked into)
        
        Args:
            dir_path: Absolute path to the directory
            base_path: Base path for the export
            
        Returns:
            True if directory should be included
        """
        relative_path = os.path.relpath(dir_path, base_path)
        return self.filter.should_include(dir_path, relative_path)
    
    def calculate_directory_hash(self, directory_path: str) -> str:
        """
        Calculate a hash of all files in a directory (excluding Git internals)
        
        Args:
            directory_path: Path to the directory
            
        Returns:
            SHA256 hash of the directory contents
        """
        directory_path = Path(directory_path).resolve()
        
        if not directory_path.exists():
            raise FileNotFoundError(f"Directory does not exist: {directory_path}")
        
        hash_obj = hashlib.sha256()
        
        # Get all files in sorted order for consistent hashing
        files_to_hash = []
        
        for root, dirs, files in os.walk(directory_path):
            # Remove excluded directories from dirs list
            dirs[:] = [d for d in dirs if self._should_include_dir(os.path.join(root, d), directory_path)]
            
            for file in sorted(files):
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, directory_path)
                
                if self.filter.should_include(file_path, relative_path):
                    files_to_hash.append(file_path)
        
        # Hash each file
        for file_path in sorted(files_to_hash):
            try:
                # Hash the relative path first
                relative_path = os.path.relpath(file_path, directory_path)
                hash_obj.update(relative_path.encode('utf-8'))
                
                # Hash the file contents
                with open(file_path, 'rb') as f:
                    while chunk := f.read(8192):
                        hash_obj.update(chunk)
                        
            except Exception as e:
                logger.warning(f"Failed to hash {file_path}: {str(e)}")
        
        return hash_obj.hexdigest()
    
    def clean_directory(self, directory_path: str, dry_run: bool = True) -> Dict[str, List[str]]:
        """
        Clean a directory by removing excluded files and directories
        
        Args:
            directory_path: Path to the directory to clean
            dry_run: If True, only report what would be cleaned
            
        Returns:
            Dictionary with lists of files and directories that were/would be removed
        """
        directory_path = Path(directory_path).resolve()
        
        if not directory_path.exists():
            raise FileNotFoundError(f"Directory does not exist: {directory_path}")
        
        result = {
            "files_removed": [],
            "directories_removed": [],
            "errors": []
        }
        
        logger.info(f"Cleaning directory: {directory_path} (dry_run={dry_run})")
        
        # First pass: collect all items to remove
        items_to_remove = []
        
        for root, dirs, files in os.walk(directory_path, topdown=False):
            # Check files
            for file in files:
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, directory_path)
                
                if not self.filter.should_include(file_path, relative_path):
                    items_to_remove.append(("file", file_path, relative_path))
            
            # Check directories
            for dir_name in dirs:
                dir_path = os.path.join(root, dir_name)
                relative_path = os.path.relpath(dir_path, directory_path)
                
                if not self.filter.should_include(dir_path, relative_path):
                    items_to_remove.append(("dir", dir_path, relative_path))
        
        # Second pass: remove items
        for item_type, full_path, relative_path in items_to_remove:
            try:
                if dry_run:
                    logger.info(f"Would remove {item_type}: {relative_path}")
                else:
                    if item_type == "file":
                        os.remove(full_path)
                        logger.info(f"Removed file: {relative_path}")
                    else:  # directory
                        shutil.rmtree(full_path)
                        logger.info(f"Removed directory: {relative_path}")
                
                if item_type == "file":
                    result["files_removed"].append(relative_path)
                else:
                    result["directories_removed"].append(relative_path)
                    
            except Exception as e:
                error_msg = f"Failed to remove {relative_path}: {str(e)}"
                logger.error(error_msg)
                result["errors"].append(error_msg)
        
        logger.info(f"Cleaning completed: {len(result['files_removed'])} files, "
                   f"{len(result['directories_removed'])} directories, "
                   f"{len(result['errors'])} errors")
        
        return result


def create_clean_export(source_path: str, 
                       output_path: str, 
                       format_type: str = "zip",
                       custom_excludes: List[str] = None) -> Dict[str, Union[str, int]]:
    """
    Convenience function to create a clean export without Git internals
    
    Args:
        source_path: Path to the directory to export
        output_path: Path for the output archive
        format_type: Archive format ("zip" or "tar")
        custom_excludes: Additional patterns to exclude
        
    Returns:
        Dictionary with export statistics
    """
    # Create filter with custom excludes if provided
    excludes = ExportFilter.DEFAULT_EXCLUDES.copy()
    if custom_excludes:
        excludes.extend(custom_excludes)
    
    export_filter = ExportFilter(excludes=excludes)
    exporter = FileSystemExporter(export_filter)
    
    if format_type.lower() == "zip":
        return exporter.create_zip_export(source_path, output_path)
    elif format_type.lower() == "tar":
        return exporter.create_tar_export(source_path, output_path)
    else:
        raise ValueError(f"Unsupported format: {format_type}")
