import os
import mimetypes
from http.server import HTTPServer, SimpleHTTPRequestHandler

PORT = 8000
BASE_DIR = os.path.abspath(os.path.dirname(os.path.abspath(__file__))+"/../")
class CustomHTTPRequestHandler(SimpleHTTPRequestHandler):

    def do_GET(self):
        # Normalize request path
        req_path = self.path.split('?')[0]  # Remove query parameters if present

        # Route 1: Root "/" -> Serve client/index.html
        if req_path == "/" or req_path == "/index.html":
            file_path = os.path.join(BASE_DIR, "client", "index.html")

        # Route 2: /js or /js/ -> Serve client/js directory/files
        elif req_path.startswith("/js") or req_path.startswith("/JS"):
            # Strip leading '/js' and map to 'client/js'
            relative_path = req_path[3:].lstrip("/")
            file_path = os.path.join(BASE_DIR, "client", "js", relative_path)

        # Route 3: /css or /css/ -> Serve client/css directory/files
        elif req_path.startswith("/css") or req_path.startswith("/CSS"):
            relative_path = req_path[4:].lstrip("/")
            file_path = os.path.join(BASE_DIR, "client", "css", relative_path)

        # Route 4: /assets -> Serve files directly under assets directory
        elif req_path.startswith("/assets") or req_path.startswith("/Assets"):
            relative_path = req_path[7:].lstrip("/")
            file_path = os.path.join(BASE_DIR, "assets", relative_path)

        # Fallback: Serve anything requested under /client/ or /assets/

        else:
            file_path = os.path.join(BASE_DIR, req_path.lstrip("/"))

        # Check if the target is a directory without index.html or doesn't exist
        if os.path.isdir(file_path):
            file_path = os.path.join(file_path, "index.html")

        # Serve the requested static file
        self.serve_file(file_path)

    def serve_file(self, file_path):
        if os.path.exists(file_path) and os.path.isfile(file_path):
            self.send_response(200)
            
            # Auto-detect Content-Type (HTML, JS, CSS, PNG, JSON, etc.)
            mime_type, _ = mimetypes.guess_type(file_path)
            if mime_type:
                self.send_header("Content-Type", mime_type)
            else:
                self.send_header("Content-Type", "application/octet-stream")

            # Enable CORS (Allows WebGL/Unity or frontend JS to fetch assets without block)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "*")
            self.end_headers()

            # Read and write file binary content
            with open(file_path, "rb") as f:
                self.wfile.write(f.read())
        else:
            self.send_error(404, f"File Not Found: {self.path}")

    def do_OPTIONS(self):
        # Handle CORS preflight requests
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.end_headers()

def run_server():
    server_address = ("", PORT)
    httpd = HTTPServer(server_address, CustomHTTPRequestHandler)
    print(f"🚀 Static HTTP Server running at http://localhost:{PORT}/")
    print(f"Routes active:")
    print(f"  - http://localhost:{PORT}/            -> client/index.html")
    print(f"  - http://localhost:{PORT}/js/         -> client/js/")
    print(f"  - http://localhost:{PORT}/css/        -> client/css/")
    print(f"  - http://localhost:{PORT}/assets/     -> assets/")
    httpd.serve_forever()

if __name__ == "__main__":
    run_server()