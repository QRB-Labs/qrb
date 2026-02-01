import argparse
import gspread
import os
import pandas as pd
import tempfile


def sync_sheets(json_key, spreadsheet_url, tab_names):
    gc = gspread.service_account(filename=json_key)
    sh = gc.open_by_url(spreadsheet_url)

    for name in tab_names:
        worksheet = sh.worksheet(name)
        records = worksheet.get_all_records()
        df = pd.DataFrame(records)
        df = df.dropna(how='all')

        temp_dir = tempfile.gettempdir()
        output_file = os.path.join(temp_dir, f'{name}.csv')
        df.to_csv(output_file)
        yield output_file


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--key_file', type=str, default="qrb-labs-mdb.json")
    parser.add_argument('--sheet_url', type=str, help="Google spreadsheet url")
    parser.add_argument('--worksheets', nargs='+',
                        help='list of worksheet names eg --worksheets "Miners" "Other miners"',  default=["Miners"])
    args = parser.parse_args()
    
    filenames = sync_sheets(args.key_file, args.sheet_url, args.worksheets)
    print(list(filenames))
