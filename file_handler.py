"""
Efficient file handling for large matrix data
Supports .txt and .csv files with memory-optimized loading
"""

import os
import numpy as np
import pandas as pd
from typing import Optional, Tuple, Union, List
from pathlib import Path
import mmap
import csv

class MatrixFileHandler:
    """Handles loading of large matrix files efficiently"""
    
    def __init__(self):
        self.supported_extensions = {'.txt', '.csv', '.tsv'}
    
    def detect_file_type(self, file_path: str) -> str:
        """Detect file type from extension"""
        path = Path(file_path)
        extension = path.suffix.lower()
        
        if extension not in self.supported_extensions:
            raise ValueError(f"Unsupported file type: {extension}. Supported: {self.supported_extensions}")
        
        return extension
    
    def detect_delimiter(self, file_path: str, sample_lines: int = 5) -> str:
        """Detect delimiter by sampling first few lines"""
        common_delimiters = [',', '\t', ' ', ';', '|']
        delimiter_counts = {delim: 0 for delim in common_delimiters}
        
        with open(file_path, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f):
                if i >= sample_lines:
                    break
                line = line.strip()
                if line:
                    for delim in common_delimiters:
                        delimiter_counts[delim] += line.count(delim)
        
        # Return the delimiter with highest count
        best_delimiter = max(delimiter_counts, key=delimiter_counts.get)
        
        # If comma has highest count, it's likely CSV
        if best_delimiter == ',' and delimiter_counts[','] > 0:
            return ','
        # If tab has highest count, it's likely TSV
        elif best_delimiter == '\t' and delimiter_counts['\t'] > 0:
            return '\t'
        # If space has highest count and others are low, it's space-separated
        elif best_delimiter == ' ' and delimiter_counts[' '] > delimiter_counts[','] + delimiter_counts['\t']:
            return ' '
        # Default fallback
        elif delimiter_counts[','] > 0:
            return ','
        else:
            return '\t'
    
    def get_file_info(self, file_path: str) -> dict:
        """Get basic file information without loading full content"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        file_stats = os.stat(file_path)
        file_type = self.detect_file_type(file_path)
        
        # Sample first few lines to estimate structure
        with open(file_path, 'r', encoding='utf-8') as f:
            sample_lines = []
            for i, line in enumerate(f):
                if i >= 10:  # Sample first 10 lines
                    break
                sample_lines.append(line.strip())
        
        delimiter = self.detect_delimiter(file_path)
        
        # Estimate dimensions from first non-empty line
        first_data_line = None
        for line in sample_lines:
            if line and not line.startswith('#'):  # Skip comments
                first_data_line = line
                break
        
        estimated_cols = 0
        if first_data_line:
            if delimiter == ' ':
                # For space-separated, split on any whitespace
                estimated_cols = len(first_data_line.split())
            else:
                estimated_cols = len(first_data_line.split(delimiter))
        
        return {
            'file_path': file_path,
            'file_type': file_type,
            'file_size_bytes': file_stats.st_size,
            'file_size_mb': file_stats.st_size / (1024 * 1024),
            'delimiter': delimiter,
            'estimated_columns': estimated_cols,
            'sample_lines': sample_lines[:3]  # First 3 lines as preview
        }
    
    def load_matrix_chunked(self, file_path: str, max_memory_mb: int = 500) -> np.ndarray:
        """Load matrix in chunks for memory efficiency"""
        file_info = self.get_file_info(file_path)
        
        if file_info['file_size_mb'] < max_memory_mb:
            # Small file, load directly
            return self.load_matrix_direct(file_path)
        else:
            # Large file, use chunked loading
            return self.load_matrix_pandas_chunked(file_path)
    
    def load_matrix_direct(self, file_path: str) -> np.ndarray:
        """Load matrix directly into memory (for smaller files)"""
        file_info = self.get_file_info(file_path)
        delimiter = file_info['delimiter']
        
        try:
            if delimiter == ' ':
                # For space-separated files, use numpy's loadtxt with any whitespace
                matrix = np.loadtxt(file_path, dtype=float)
            else:
                # For CSV/TSV files, use pandas for better handling
                df = pd.read_csv(file_path, sep=delimiter, header=None, dtype=float)
                matrix = df.values
            
            return matrix
            
        except Exception as e:
            # Fallback: try to parse manually
            return self._manual_parse(file_path, delimiter)
    
    def load_matrix_pandas_chunked(self, file_path: str, chunk_size: int = 1000) -> np.ndarray:
        """Load large matrix using pandas chunking"""
        file_info = self.get_file_info(file_path)
        delimiter = file_info['delimiter']
        
        chunks = []
        total_rows = 0
        
        try:
            chunk_iter = pd.read_csv(
                file_path, 
                sep=delimiter, 
                header=None, 
                dtype=float,
                chunksize=chunk_size,
                na_values=['', 'NA', 'NaN', 'null'],
                keep_default_na=True
            )
            
            for chunk in chunk_iter:
                # Drop rows/columns that are entirely NaN
                chunk = chunk.dropna(how='all', axis=0)  # Drop empty rows
                chunk = chunk.dropna(how='all', axis=1)  # Drop empty columns
                
                if not chunk.empty:
                    chunks.append(chunk.values)
                    total_rows += len(chunk)
            
            if chunks:
                matrix = np.vstack(chunks)
                return matrix
            else:
                raise ValueError("No valid data found in file")
                
        except Exception as e:
            print(f"Pandas chunked loading failed: {e}")
            # Fallback to direct loading
            return self.load_matrix_direct(file_path)
    
    def _manual_parse(self, file_path: str, delimiter: str) -> np.ndarray:
        """Manual parsing fallback for problematic files"""
        rows = []
        
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f):
                line = line.strip()
                if not line or line.startswith('#'):  # Skip empty lines and comments
                    continue
                
                try:
                    if delimiter == ' ':
                        # Split on any whitespace
                        values = [float(x) for x in line.split()]
                    else:
                        values = [float(x.strip()) for x in line.split(delimiter)]
                    
                    if values:  # Only add non-empty rows
                        rows.append(values)
                        
                except ValueError as e:
                    print(f"Warning: Could not parse line {line_num + 1}: {line[:50]}...")
                    continue
        
        if not rows:
            raise ValueError("No valid numeric data found in file")
        
        # Convert to numpy array, handling different row lengths
        max_cols = max(len(row) for row in rows)
        
        # Pad shorter rows with NaN
        padded_rows = []
        for row in rows:
            if len(row) < max_cols:
                padded_row = row + [np.nan] * (max_cols - len(row))
                padded_rows.append(padded_row)
            else:
                padded_rows.append(row)
        
        matrix = np.array(padded_rows, dtype=float)
        return matrix
    
    def get_matrix_metadata(self, matrix: np.ndarray) -> dict:
        """Get comprehensive metadata about loaded matrix"""
        return {
            'shape': matrix.shape,
            'dtype': matrix.dtype,
            'size_elements': matrix.size,
            'memory_usage_mb': matrix.nbytes / (1024 * 1024),
            'has_nan': np.isnan(matrix).any(),
            'nan_count': np.isnan(matrix).sum(),
            'min_value': np.nanmin(matrix) if not np.isnan(matrix).all() else np.nan,
            'max_value': np.nanmax(matrix) if not np.isnan(matrix).all() else np.nan,
            'mean_value': np.nanmean(matrix) if not np.isnan(matrix).all() else np.nan,
        }
    
    def preview_matrix(self, matrix: np.ndarray, max_rows: int = 5, max_cols: int = 8) -> str:
        """Create a formatted preview of the matrix"""
        rows, cols = matrix.shape
        
        # Determine preview size
        preview_rows = min(max_rows, rows)
        preview_cols = min(max_cols, cols)
        
        preview = matrix[:preview_rows, :preview_cols]
        
        preview_str = f"Matrix Preview ({preview_rows}x{preview_cols} of {rows}x{cols}):\n"
        preview_str += np.array2string(preview, precision=3, suppress_small=True, separator=', ')
        
        if rows > max_rows or cols > max_cols:
            preview_str += "\n... (truncated)"
        
        return preview_str
    
    def load_and_analyze(self, file_path: str, max_memory_mb: int = 500) -> Tuple[np.ndarray, dict]:
        """Complete workflow: load matrix and return with metadata"""
        print(f"Loading matrix from: {file_path}")
        
        # Get file info first
        file_info = self.get_file_info(file_path)
        print(f"File type: {file_info['file_type']}")
        print(f"File size: {file_info['file_size_mb']:.2f} MB")
        print(f"Detected delimiter: '{file_info['delimiter']}'")
        print(f"Estimated columns: {file_info['estimated_columns']}")
        
        # Load matrix
        matrix = self.load_matrix_chunked(file_path, max_memory_mb)
        
        # Get metadata
        metadata = self.get_matrix_metadata(matrix)
        
        print(f"\nMatrix loaded successfully!")
        print(f"Shape: {metadata['shape']}")
        print(f"Data type: {metadata['dtype']}")
        print(f"Memory usage: {metadata['memory_usage_mb']:.2f} MB")
        
        if metadata['has_nan']:
            print(f"Warning: Matrix contains {metadata['nan_count']} NaN values")
        
        print(f"Value range: [{metadata['min_value']:.3f}, {metadata['max_value']:.3f}]")
        print(f"Mean value: {metadata['mean_value']:.3f}")
        
        # Show preview
        print(f"\n{self.preview_matrix(matrix)}")
        
        return matrix, {**file_info, **metadata}

def create_sample_files():
    """Create sample matrix files for testing"""
    # Create a sample CSV file
    csv_data = np.random.randn(100, 50)
    np.savetxt('sample_matrix.csv', csv_data, delimiter=',', fmt='%.6f')
    
    # Create a sample TXT file  
    txt_data = np.random.randn(50, 30)
    np.savetxt('sample_matrix.txt', txt_data, delimiter=' ', fmt='%.6f')
    
    print("Sample files created:")
    print("- sample_matrix.csv (100x50)")
    print("- sample_matrix.txt (50x30)")

if __name__ == "__main__":
    # Demo usage
    handler = MatrixFileHandler()
    
    # Create sample files for testing
    create_sample_files()
    
    # Test loading
    try:
        matrix, metadata = handler.load_and_analyze('sample_matrix.csv')
        print(f"\nLoaded CSV matrix: {matrix.shape}")
        
        matrix2, metadata2 = handler.load_and_analyze('sample_matrix.txt')
        print(f"\nLoaded TXT matrix: {matrix2.shape}")
        
    except Exception as e:
        print(f"Error: {e}")