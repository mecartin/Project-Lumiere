# inspect_data.py

import os
import glob
import zipfile
import pandas as pd

# Set pandas to display all columns
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)

def inspect_csv_from_zip(zip_path, csv_filename):
    """Inspects a single CSV file from within a zip archive."""
    print("-" * 50)
    print(f"File: {csv_filename}")
    print("-" * 50)
    
    try:
        with zipfile.ZipFile(zip_path, 'r') as zf:
            with zf.open(csv_filename) as f:
                # Use engine='python' for robustness against parsing errors
                df = pd.read_csv(f, engine='python')
                
                print("Columns:")
                print(df.columns.tolist())
                print("\nSample Rows:")
                print(df.head(3))
                print("\n")

    except Exception as e:
        print(f"Could not read or process {csv_filename}. Error: {e}\n")


def inspect_standalone_csv(csv_path):
    """Inspects a single standalone CSV file."""
    print("=" * 70)
    print(f"Standalone File: {os.path.basename(csv_path)}")
    print("=" * 70)
    
    try:
        # Use engine='python' for robustness
        df = pd.read_csv(csv_path, engine='python')
        
        print("Columns:")
        print(df.columns.tolist())
        print("\nSample Rows:")
        print(df.head(3))
        print("\n")

    except Exception as e:
        print(f"Could not read or process {os.path.basename(csv_path)}. Error: {e}\n")


def main():
    """Main function to find and inspect all relevant CSV files."""
    
    # --- Inspect CSVs inside the Letterboxd ZIP file ---
    zip_files = glob.glob('letterboxd-*.zip')
    if not zip_files:
        print("No Letterboxd ZIP file ('letterboxd-*.zip') found in this folder.")
    else:
        zip_path = zip_files[0]
        print(f"Inspecting contents of: {zip_path}\n")
        with zipfile.ZipFile(zip_path, 'r') as zf:
            csv_in_zip = [name for name in zf.namelist() if name.endswith('.csv')]
            for csv_file in csv_in_zip:
                inspect_csv_from_zip(zip_path, csv_file)

    # --- Inspect standalone CSVs in the folder ---
    standalone_csv_files = glob.glob('*.csv')
    if not standalone_csv_files:
        print("No standalone CSV files ('*.csv') found in this folder.")
    else:

        for csv_path in standalone_csv_files:
            # We don't want to re-inspect the files from the uploaded profile.csv
            if 'profile.csv' not in csv_path:
                 inspect_standalone_csv(csv_path)


if __name__ == "__main__":
    main()