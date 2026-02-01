import argparse
import http.server
import socketserver
import urllib.parse
import get_data
import mdb

PORT = 8000
server_args = None

class MDBServer(http.server.SimpleHTTPRequestHandler):
        
    def do_GET(self):
        # 1. Custom endpoint to trigger the update pipeline
        if self.path == '/update':
            try:
                print("🔄 Syncing from Google Sheets...")
                filenames = get_data.sync_sheets(server_args.key_file, server_args.sheet_url, server_args.worksheets)
                print("🔨 Rebuilding SQLite Database...")
                mdb.build_db(filenames, 'mdb.sqlite', 'machines')
                
                self.send_response(200)
                self.send_header("Content-type", "text/plain")
                self.end_headers()
                self.wfile.write(b"Update Successful! SQLite rebuilt.")
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(f"Update Failed: {str(e)}".encode())
                raise e
        
        # 2. Otherwise, serve files normally (index.html, sqlite file, etc.)
        else:
            super().do_GET()



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--key_file', type=str, default="qrb-labs-mdb.json")
    parser.add_argument('--sheet_url', type=str, help="Google spreadsheet url")
    parser.add_argument('--worksheets', nargs='+',
                        help='list of worksheet names eg --worksheets "Miners" "Other miners"',  default=["Miners"])
    server_args = parser.parse_args()
    handler = lambda *args, **kwargs: MDBServer(server_args.key_file, server_args.sheet_url, server_args.worksheets, *args, **kwargs)
    
    with socketserver.TCPServer(("", PORT), MDBServer) as httpd:
        print(f"🚀 Server running at http://localhost:{PORT}")
        print(f"🔗 Visit http://localhost:{PORT}/update to refresh data")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server...")
            httpd.server_close()
