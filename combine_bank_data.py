import argparse
import sys
from pathlib import Path
from typing import List

import pandas as pd


def list_data_files(root: Path) -> List[Path]:
    exts = {".csv", ".tsv", ".xlsx", ".xls", ".xlsb"}
    return [p for p in root.rglob("*") if p.suffix.lower() in exts and p.is_file()]


def read_any(path: Path) -> pd.DataFrame:
    suffix = path.suffix.lower()
    if suffix in {".csv", ".tsv"}:
        sep = "," if suffix == ".csv" else "\t"
        try:
            return pd.read_csv(path, sep=sep, dtype_backend="pyarrow")
        except TypeError:
            # Older pandas without dtype_backend
            return pd.read_csv(path, sep=sep)
    if suffix == ".xlsx":
        # Prefer openpyxl
        try:
            return pd.read_excel(path, engine="openpyxl")
        except Exception:
            # Fallback to auto engine
            return pd.read_excel(path)
    if suffix == ".xls":
        # xlrd is needed for legacy xls. Try with xlrd, fall back if unavailable.
        try:
            return pd.read_excel(path, engine="xlrd")
        except Exception:
            return pd.read_excel(path)
    if suffix == ".xlsb":
        # Requires pyxlsb if available
        try:
            return pd.read_excel(path, engine="pyxlsb")
        except Exception as e:
            raise RuntimeError(f"Reading .xlsb requires pyxlsb. Install it and retry. File: {path}") from e
    raise ValueError(f"Unsupported file type: {suffix}")


def main():
    parser = argparse.ArgumentParser(description="Merge all Excel/CSV files in a folder into one dataset.")
    parser.add_argument(
        "folder",
        nargs="?",
        default=r"C:\\Users\\HP\\Desktop\\bankExcel",
        help="Folder containing Excel/CSV files (default: C:/Users/HP/Desktop/bankExcel)",
    )
    parser.add_argument(
        "--recursive",
        action="store_true",
        help="Search subfolders recursively (default: True if not set, but kept for explicitness)",
    )
    parser.add_argument(
        "--out",
        default="combined_bank_data.parquet",
        help="Output file path (.parquet or .csv). Default: combined_bank_data.parquet",
    )

    args = parser.parse_args()

    root = Path(args.folder).expanduser()
    if not root.exists() or not root.is_dir():
        print(f"Folder not found: {root}", file=sys.stderr)
        sys.exit(1)

    files = list_data_files(root)
    if not files:
        print(f"No data files found in {root}")
        sys.exit(2)

    frames: List[pd.DataFrame] = []
    read_ok = 0
    for fp in files:
        try:
            df = read_any(fp)
            df["source_file"] = str(fp)
            frames.append(df)
            read_ok += 1
        except Exception as e:
            print(f"WARN: Skipped {fp} due to error: {e}", file=sys.stderr)

    if not frames:
        print("No files could be read successfully.", file=sys.stderr)
        sys.exit(3)

    combined = pd.concat(frames, ignore_index=True, sort=False)

    total_rows = len(combined)
    total_cols = len(combined.columns)
    print(f"Read {read_ok}/{len(files)} files. Combined shape: {total_rows} rows x {total_cols} columns")

    out_path = Path(args.out)
    if out_path.suffix.lower() == ".csv":
        combined.to_csv(out_path, index=False)
        print(f"Saved CSV -> {out_path.resolve()}")
    else:
        # Default to parquet for speed/size; requires pyarrow or fastparquet
        try:
            combined.to_parquet(out_path, index=False)
            print(f"Saved Parquet -> {out_path.resolve()}")
        except Exception as e:
            print(f"Parquet write failed ({e}); falling back to CSV.")
            csv_fallback = out_path.with_suffix(".csv")
            combined.to_csv(csv_fallback, index=False)
            print(f"Saved CSV -> {csv_fallback.resolve()}")


if __name__ == "__main__":
    main()
