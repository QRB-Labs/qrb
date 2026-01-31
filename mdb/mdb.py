import argparse
import sqlite3
import pandas as pd
import glob
import os
import re


# Define your "Source of Truth" mapping here
# Format: 'Current CSV Header': 'Standardized Name'
COLUMN_MAP = {
    'Worker 1': 'worker',
    'IP': 'ip_address',
    'MAC Address': 'mac_address',
    'MAC Addr': 'mac_address',
    'MAC': 'mac_address',
    'Miner Type': 'type',
    'Type': 'type',
    'Location': 'location',
    'SN': 'serial_number',
    'Miner SN': 'serial_number',
    'Serial Number': 'serial_number',
    'Power SN': 'psu_serial_number'
}


def parse_location(loc_str):
    """
    Parses strings like 'Co3-B(5,4)' or 'C01-A-1-6' 
    into (container, side, row, position)
    """
    if pd.isna(loc_str) or not isinstance(loc_str, str):
        return None, None, None, None
        
    # Pattern explanation:
    # Co?(\d+) -> 'C' then optional 'o', capture digits (Container)
    # -([A-Z]) -> hyphen then capture one letter (Side)
    # [-(]\(?  -> separator is either hyphen or parenthesis
    # (\d+)    -> capture digits (Row)
    # [,/ -]+  -> separator (comma, space, or hyphen)
    # (\d+)    -> capture digits (Position)
    pattern = r"Co?(\d+)-([A-Z])[-(]\(?(\d+)[,-]?(\d+)\)?"
    
    match = re.search(pattern, loc_str, re.IGNORECASE)
    if match:
        container = int(match.group(1))
        side = match.group(2).upper()
        row = int(match.group(3))
        pos = int(match.group(4))
        return container, side, row, pos
    
    return None, None, None, None


def build_standardized_db(pattern, db_name, table_name):
    files = glob.glob(pattern)
    if not files:
        print(f"No files found for: {pattern}")
        return

    df_list = []
    for f in sorted(files):
        print(f"Reading and mapping {f}...")
        df = pd.read_csv(f)
        
        # Standardize columns
        # We use errors='ignore' so it only renames what it finds
        df = df.rename(columns=COLUMN_MAP, errors='ignore')

        # Keep only the columns we actually want in our web app
        standard_columns = list(set(COLUMN_MAP.values()))
        valid_cols = [c for c in standard_columns if c in df.columns]
        df = df[valid_cols]

        # Apply the parsing logic if 'location' exists
        if 'location' in df.columns:
            print("Parsing location strings into components...")
            # Apply the function and expand into 4 new columns
            loc_data = df['location'].apply(lambda x: pd.Series(parse_location(x)))
            loc_data.columns = ['container', 'side', 'shelf', 'position']
            # Join the new columns back to the main dataframe
            df = pd.concat([df, loc_data], axis=1)

        
        df_list.append(df)

    # Combine everything
    print("Merging dataframes...")
    final_df = pd.concat(df_list, ignore_index=True)
    
    # Final cleanup: drop full duplicates
    final_df = final_df.drop_duplicates()

    # Write to SQLite
    conn = sqlite3.connect(db_name)
    final_df.to_sql(table_name, conn, if_exists='replace', index=False)
    
    # Index the hostname for fast JS searches
    if 'hostname' in final_df.columns:
        conn.execute(f"CREATE INDEX IF NOT EXISTS idx_host ON {table_name} (mac_address)")
    
    conn.close()
    print(f"✅ Created {db_name} with standardized columns: {list(final_df.columns)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--src', type=str, default="*.csv")
    parser.add_argument('--out', type=str, default="mdb.sqlite")
    parser.add_argument('--table', type=str, default="machines")
    args = parser.parse_args()
    
    build_standardized_db(args.src, args.out, args.table)
