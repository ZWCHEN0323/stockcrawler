from __future__ import annotations

import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Tuple

from app.utils.logger import logger


class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # type: ignore[override]
        if self.path != "/health":
            self.send_response(404)
            self.end_headers()
            return
        payload = json.dumps({"status": "ok"}).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, format: str, *args) -> None:  # noqa: A003
        logger.info("HealthServer - " + format, *args)


def start_health_server(
    host: str = "0.0.0.0", port: int = 8000
) -> Tuple[HTTPServer, threading.Thread]:
    server = HTTPServer((host, port), HealthHandler)

    def run() -> None:
        logger.info("Starting health server on %s:%d", host, port)
        server.serve_forever()

    thread = threading.Thread(target=run, daemon=True)
    thread.start()
    return server, thread

