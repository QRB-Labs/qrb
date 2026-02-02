#!/usr/bin/python3
import argparse
import http.server
import os
import socketserver
import urllib.parse

import get_data
import mdb

PORT = 8000
server_args = None

class MDBServer(http.server.SimpleHTTPRequestHandler):

    def do_GET(self):
        # Custom endpoint to trigger the update pipeline
        if self.path == '/update':
            try:
                print("🔄 Syncing from Google Sheets...")
                filenames = get_data.sync_sheets(server_args.key_file, server_args.sheet_url, server_args.worksheets)
                print("🔨 Rebuilding database...")
                mdb.build_db(filenames, server_args.db_file, 'machines')

                self.send_response(200)
                self.send_header("Content-type", "text/plain")
                self.end_headers()
                self.wfile.write(b"Update successful, database rebuilt.")
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(f"Update failed: {str(e)}".encode())
                raise e

        # When serving db file, force update cache if the file changed
        elif server_args.db_file in self.path:
            full_path = self.translate_path(self.path)
            stats = os.stat(full_path)
            self.send_response(200)
            self.send_header('Content-type', 'application/x-sqlite3')
            self.send_header('Last-Modified', self.date_time_string(stats.st_mtime))
            self.end_headers()
            # Manually serve the file content
            with open(full_path, 'rb') as f:
                self.wfile.write(f.read())

        # Otherwise, serve files normally (index.html, etc.)
        else:
            super().do_GET()



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--key_file', type=str, default="qrb-labs-mdb.json")
    parser.add_argument('--sheet_url', type=str, help="Google spreadsheet url")
    parser.add_argument('--worksheets', nargs='+',
                        help='list of worksheet names eg --worksheets "Miners" "Other miners"',  default=["Miners"])
    parser.add_argument('--db_file', type=str, default="mdb.sqlite")
    server_args = parser.parse_args()

    with socketserver.TCPServer(("", PORT), MDBServer) as httpd:
        print(f"🚀 Server running at http://localhost:{PORT}")
        print(f"🔗 Visit http://localhost:{PORT}/update to refresh data")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server...")
            httpd.server_close()
