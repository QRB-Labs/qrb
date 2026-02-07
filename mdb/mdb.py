import argparse
import sqlite3
import pandas as pd
import glob
import os
import re


def parse_location(loc_str):
    """
    Supports:
    1. Parentheses format: Co3-B(5,4)
    2. Standard format:    C01-A-1-6
    3. Pipe format:        C02-B | 5-0
    """
    if pd.isna(loc_str) or not isinstance(loc_str, str):
        return None, None, None, None
    # Regex Breakdown:
    # C?(\d+)             -> Container (Optional 'C')
    # [-\s]+              -> Separator (dash or space)
    # ([A-Z])             -> Side (Single letter)
    # [\( \-|]+           -> Bridge: handles '(', ' | ', '-', or spaces
    # (\d+)               -> Shelf
    # [,\s\-|]+           -> Separator: handles ',', ' ', '-', or '|'
    # (\d+)               -> Position
    # \)?                 -> Optional closing parenthesis

    pattern = r"Co?0?(\d+)[-\s]+([A-Z])[\( \-|]+(\d+)[,\s\-|]+(\d+)\)?"

    match = re.search(pattern, loc_str, re.IGNORECASE)

    if match:
        container = int(match.group(1))
        side = match.group(2).upper()
        row = int(match.group(3))
        pos = int(match.group(4))
        return container, side, row, pos

    return None, None, None, None


def build_db(files, db_name, table_name):
    df_list = []
    for f in files:
        print(f"Reading and mapping {f}...")
        df = pd.read_csv(f)

        # Apply the parsing logic if 'location' exists
        if 'location' in df.columns:
            # Expand into 4 new columns
            loc_data = df['location'].apply(lambda x: pd.Series(parse_location(x)))
            loc_data.columns = ['container', 'side', 'shelf', 'position']
            # Join the new columns back to the main dataframe
            df = pd.concat([df, loc_data], axis=1)

        df_list.append(df)

    final_df = pd.concat(df_list, ignore_index=True)
    final_df = final_df.drop_duplicates()

    # Write to SQLite
    conn = sqlite3.connect(db_name)
    final_df.to_sql(table_name, conn, if_exists='replace', index=False)

    if 'mac_address' in final_df.columns:
        conn.execute(f"CREATE INDEX IF NOT EXISTS idx_host ON {table_name} (mac_address)")

    conn.close()
    print(f"✅ Created {db_name} with columns: {list(final_df.columns)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--src', type=str, default="data/*.csv")
    parser.add_argument('--out', type=str, default="mdb.sqlite")
    parser.add_argument('--table', type=str, default="machines")
    args = parser.parse_args()

    build_db(glob.glob(args.src), args.out, args.table)
