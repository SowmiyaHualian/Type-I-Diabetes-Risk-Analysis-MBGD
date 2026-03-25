from __future__ import annotations

import http.server
import os
import socketserver
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent
PORT = 8000


class StaticHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT_DIR), **kwargs)

    def do_GET(self) -> None:
        if self.path in ("/", ""):
            self.path = "/index.html"
        return super().do_GET()


def run_server(port: int = PORT) -> None:
    os.chdir(ROOT_DIR)
    with socketserver.TCPServer(("", port), StaticHandler) as httpd:
        print(f"Serving static site at http://localhost:{port}")
        print("Press Ctrl+C to stop")
        httpd.serve_forever()


if __name__ == "__main__":
    run_server()
