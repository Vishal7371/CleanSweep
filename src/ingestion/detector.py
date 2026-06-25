"""
detector.py — File Type & Encoding Detector

This is the FIRST step of CleanSweep's ingestion layer.
For every incoming supplier file, it detects:
  1. File type (CSV, XLSX)
  2. File encoding (UTF-8, Latin-1, etc.)
  3. Basic diagnostics (row count, column names)

WHY THIS MATTERS:
  Suppliers send files in different formats and encodings.
  If we try to read a Latin-1 encoded file as UTF-8, we get garbled text.
  chardet library sniffs the encoding automatically.
"""

import os
import chardet
from pathlib import Path
from loguru import logger


def detect_file_type(filepath: str) -> str:
    """
    Detect if a file is CSV, XLSX, TSV, or unknown.
    
    Args:
        filepath: path to the file
    Returns:
        'csv', 'xlsx', 'tsv', or 'unknown'
    """
    ext = Path(filepath).suffix.lower()
    
    type_map = {
        ".csv": "csv",
        ".xlsx": "xlsx",
        ".xls": "xlsx",
        ".tsv": "tsv",
    }
    
    file_type = type_map.get(ext, "unknown")
    logger.info(f"File type detected: {file_type} for {Path(filepath).name}")
    return file_type


def detect_encoding(filepath: str) -> str:
    """
    Detect the character encoding of a file using chardet.
    
    Args:
        filepath: path to the file
    Returns:
        encoding string e.g. 'utf-8', 'ISO-8859-1'
    
    WHY: Some suppliers save CSVs with Latin-1 encoding (common in older 
    Windows systems or when content has special characters like é, ñ, ü).
    Reading with wrong encoding causes UnicodeDecodeError or garbled text.
    """
    with open(filepath, "rb") as f:
        raw_data = f.read(10000)  # Read first 10KB is enough to detect
    
    result = chardet.detect(raw_data)
    encoding = result.get("encoding", "utf-8") or "utf-8"
    confidence = result.get("confidence", 0)
    
    logger.info(
        f"Encoding detected: {encoding} "
        f"(confidence: {confidence:.0%}) "
        f"for {Path(filepath).name}"
    )
    return encoding


def get_file_diagnostics(filepath: str) -> dict:
    """
    Get basic diagnostics about a file before ingestion.
    
    Returns a dict with:
        - file_name: name of the file
        - file_type: csv/xlsx/tsv
        - encoding: detected encoding
        - file_size_kb: size in KB
        - supplier_name: guessed from filename (e.g. 'supplier_a')
    """
    path = Path(filepath)
    file_type = detect_file_type(filepath)
    
    diagnostics = {
        "file_name": path.name,
        "file_path": str(filepath),
        "file_type": file_type,
        "file_size_kb": round(path.stat().st_size / 1024, 2),
        "supplier_name": path.stem,  # filename without extension
        "encoding": None,
    }
    
    # Only detect encoding for text-based files
    if file_type in ("csv", "tsv"):
        diagnostics["encoding"] = detect_encoding(filepath)
    else:
        diagnostics["encoding"] = "N/A (binary format)"
    
    return diagnostics


def scan_supplier_drops(drop_folder: str) -> list[dict]:
    """
    Scan the supplier_drops folder and return diagnostics for all files.
    Skips .py files and other non-data files.
    
    Args:
        drop_folder: path to the folder containing supplier files
    Returns:
        List of diagnostics dicts, one per file
    """
    supported_extensions = {".csv", ".xlsx", ".xls", ".tsv"}
    drop_path = Path(drop_folder)
    
    if not drop_path.exists():
        logger.error(f"Supplier drops folder not found: {drop_folder}")
        return []
    
    files = [
        f for f in drop_path.iterdir()
        if f.is_file() and f.suffix.lower() in supported_extensions
    ]
    
    logger.info(f"Found {len(files)} supplier files in {drop_folder}")
    
    results = []
    for file_path in sorted(files):
        diag = get_file_diagnostics(str(file_path))
        results.append(diag)
        logger.success(
            f"✅ {diag['file_name']} | "
            f"Type: {diag['file_type']} | "
            f"Size: {diag['file_size_kb']} KB | "
            f"Encoding: {diag['encoding']}"
        )
    
    return results


# ── Quick test when running this file directly ──────────────────────────────
if __name__ == "__main__":
    import sys
    
    # Get the project root (2 levels up from this file)
    project_root = Path(__file__).parent.parent.parent
    drop_folder = project_root / "data" / "supplier_drops"
    
    print("\n" + "="*60)
    print("  CleanSweep — File Detector")
    print("="*60 + "\n")
    
    results = scan_supplier_drops(str(drop_folder))
    
    print("\n" + "="*60)
    print(f"  Total files detected: {len(results)}")
    print("="*60)
    
    for r in results:
        print(f"\n  📄 {r['file_name']}")
        print(f"     Type     : {r['file_type']}")
        print(f"     Encoding : {r['encoding']}")
        print(f"     Size     : {r['file_size_kb']} KB")
        print(f"     Supplier : {r['supplier_name']}")
