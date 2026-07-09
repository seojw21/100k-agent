#!/usr/bin/env python3
"""Force num_ctx on Ollama /api/chat and /api/generate (raw stream tunnel).

Connect hardcodes num_ctx=8192. Point Connect at this proxy so every request
is rewritten to NUM_CTX even if the extension process still has old JS.

  connectAiLab.ollamaUrl = http://127.0.0.1:11435

Env:
  OLLAMA_HOST  default http://127.0.0.1:11434
  PROXY_HOST   default 127.0.0.1
  PROXY_PORT   default 11435
  NUM_CTX      default 32768

Usage:
  python3 scripts/ollama_num_ctx_proxy.py
  nohup python3 scripts/ollama_num_ctx_proxy.py >/tmp/ollama_num_ctx_proxy.log 2>&1 &
"""
from __future__ import annotations

import json
import os
import socket
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

UPSTREAM = os.environ.get("OLLAMA_HOST", "http://127.0.0.1:11434").rstrip("/")
LISTEN_HOST = os.environ.get("PROXY_HOST", "127.0.0.1")
LISTEN_PORT = int(os.environ.get("PROXY_PORT", "11435"))
FORCE_CTX = int(os.environ.get("NUM_CTX", "32768"))
MUTATE_PATHS = {"/api/chat", "/api/generate"}


def _upstream_parts():
    u = urlparse(UPSTREAM)
    return u.hostname or "127.0.0.1", u.port or 80


def _rewrite_body(path: str, body: bytes) -> bytes:
    if path not in MUTATE_PATHS or not body:
        return body
    try:
        data = json.loads(body.decode("utf-8"))
    except Exception:
        return body
    if not isinstance(data, dict):
        return body
    opts = data.get("options")
    if not isinstance(opts, dict):
        opts = {}
        data["options"] = opts
    old = opts.get("num_ctx")
    opts["num_ctx"] = FORCE_CTX
    print(f"[proxy] {path} num_ctx {old} -> {FORCE_CTX}", flush=True)
    return json.dumps(data, ensure_ascii=False).encode("utf-8")


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, fmt: str, *args) -> None:
        sys.stderr.write("[proxy] " + (fmt % args) + "\n")

    def _proxy(self) -> None:
        host, port = _upstream_parts()
        length = int(self.headers.get("Content-Length") or 0)
        body = self.rfile.read(length) if length else b""
        path_only = self.path.split("?", 1)[0]
        body = _rewrite_body(path_only, body)

        # Build upstream request
        lines = [f"{self.command} {self.path} HTTP/1.1", f"Host: {host}:{port}"]
        skip = {
            "host",
            "content-length",
            "connection",
            "proxy-connection",
            "transfer-encoding",
            "keep-alive",
            "expect",
        }
        for k, v in self.headers.items():
            if k.lower() in skip:
                continue
            lines.append(f"{k}: {v}")
        lines.append(f"Content-Length: {len(body)}")
        lines.append("Connection: close")
        req = ("\r\n".join(lines) + "\r\n\r\n").encode("utf-8") + body

        up = socket.create_connection((host, port), timeout=600)
        try:
            up.sendall(req)
            # Tunnel raw HTTP response bytes straight to the client socket.
            # Do NOT re-parse headers (preserves chunked streaming).
            client = self.connection
            while True:
                chunk = up.recv(65536)
                if not chunk:
                    break
                try:
                    client.sendall(chunk)
                except BrokenPipeError:
                    break
        finally:
            try:
                up.close()
            except Exception:
                pass
            # Prevent BaseHTTPRequestHandler from trying to write a second response
            self.close_connection = True

    def do_GET(self) -> None:
        self._proxy()

    def do_POST(self) -> None:
        self._proxy()

    def do_HEAD(self) -> None:
        self._proxy()

    def do_PUT(self) -> None:
        self._proxy()

    def do_DELETE(self) -> None:
        self._proxy()

    def handle_one_request(self) -> None:
        """Override to allow raw tunnel without BaseHTTP response framing."""
        try:
            self.raw_requestline = self.rfile.readline(65537)
            if not self.raw_requestline:
                self.close_connection = True
                return
            if not self.parse_request():
                return
            mname = "do_" + self.command
            if not hasattr(self, mname):
                self.send_error(501, f"Unsupported method ({self.command})")
                return
            getattr(self, mname)()
        except Exception:
            self.close_connection = True
            raise


def main() -> None:
    print(
        f"ollama num_ctx proxy: listen http://{LISTEN_HOST}:{LISTEN_PORT} "
        f"-> {UPSTREAM} force num_ctx={FORCE_CTX}",
        flush=True,
    )
    print(
        f"Set Connect: connectAiLab.ollamaUrl = http://{LISTEN_HOST}:{LISTEN_PORT}",
        flush=True,
    )
    # Avoid slow DNS / dual-stack weirdness on localhost
    httpd = ThreadingHTTPServer((LISTEN_HOST, LISTEN_PORT), Handler)
    httpd.daemon_threads = True
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nbye", flush=True)


if __name__ == "__main__":
    main()
