#!/usr/bin/env python3
"""
DeepSweep Mock API Server

Mock server for testing /v1/signal endpoint locally.
Validates request format and returns proper 202 Accepted response.

Usage:
    python test-mock-server.py

Then in another terminal:
    export DEEPSWEEP_INTEL_ENDPOINT=http://localhost:8080/v1/signal
    deepsweep validate .
"""

import hashlib
import json
import time
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any


class MockSignalHandler(BaseHTTPRequestHandler):
    """Mock handler for /v1/signal endpoint."""

    def log_message(self, format: str, *args: Any) -> None:
        """Override to add timestamps and colors."""
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {format % args}")

    def do_POST(self) -> None:  # noqa: N802
        """Handle POST requests to /v1/signal."""
        if self.path == "/v1/signal":
            self._handle_signal()
        else:
            self._send_error_response(404, "Not Found", "Endpoint not found")

    def _handle_signal(self) -> None:
        """Process threat signal POST request."""
        try:
            # Read request body
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length)
            data = json.loads(body)

            # Validate required fields
            required_fields = [
                "event",
                "version",
                "install_id",
                "cli_version",
                "timestamp",
            ]

            missing = [f for f in required_fields if f not in data]
            if missing:
                self._send_error_response(
                    400,
                    "Bad Request",
                    f"Missing required fields: {', '.join(missing)}",
                )
                return

            # Validate event type
            if data.get("event") != "threat_signal":
                self._send_error_response(
                    400, "Bad Request", "Invalid event type (expected: threat_signal)"
                )
                return

            # Validate version
            if data.get("version") != "1":
                self._send_error_response(400, "Bad Request", "Invalid version (expected: 1)")
                return

            # Log received signal
            self._log_signal(data)

            # Generate signal_id (matches backend format)
            signal_id = f"sig_{hashlib.sha256(str(time.time()).encode()).hexdigest()[:12]}"

            # Return 202 Accepted (API contract v1.0.0)
            self.send_response(202)
            self.send_header("Content-Type", "application/json")
            self.send_header("X-DeepSweep-Version", "1.0.0")
            self.end_headers()

            response = {
                "status": "accepted",  # NOT "ok"
                "signal_id": signal_id,
                "message": "Threat signal received",
            }

            self.wfile.write(json.dumps(response, indent=2).encode())

            print(f"[PASS] Signal accepted - ID: {signal_id}")

        except json.JSONDecodeError:
            self._send_error_response(400, "Bad Request", "Invalid JSON")
        except Exception as e:
            self._send_error_response(500, "Internal Server Error", str(e))

    def _send_error_response(self, status: int, title: str, message: str) -> None:
        """Send error response."""
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()

        response = {"status": "error", "error": title, "message": message}

        self.wfile.write(json.dumps(response, indent=2).encode())
        print(f"[FAIL] {status} {title}: {message}")

    def _log_signal(self, data: dict[str, Any]) -> None:
        """Log signal details for verification."""
        print("\n" + "=" * 60)
        print("THREAT SIGNAL RECEIVED")
        print("=" * 60)
        print(f"Event:         {data.get('event')}")
        print(f"Version:       {data.get('version')}")
        print(f"CLI Version:   {data.get('cli_version')}")
        print(f"Install ID:    {data.get('install_id')}")
        print(f"Session ID:    {data.get('session_id')}")
        print(f"Timestamp:     {data.get('timestamp')}")
        print(f"---")
        print(f"Finding Count: {data.get('finding_count')}")
        print(f"Score:         {data.get('score')}")
        print(f"Grade:         {data.get('grade')}")
        print(f"Duration:      {data.get('duration_ms')}ms")
        print(f"---")
        print(f"Pattern IDs:   {len(data.get('pattern_ids', []))}")
        print(f"CVE Matches:   {data.get('cve_matches', [])}")
        print(f"Severity:      {data.get('severity_counts', {})}")
        print(f"---")
        print(f"OS:            {data.get('os_type')}")
        print(f"Python:        {data.get('python_version')}")
        print(f"CI:            {data.get('is_ci')} ({data.get('ci_provider')})")
        print("=" * 60 + "\n")


def main() -> None:
    """Run mock server."""
    host = "localhost"
    port = 8080

    server = HTTPServer((host, port), MockSignalHandler)

    print("=" * 60)
    print("DeepSweep Mock API Server")
    print("=" * 60)
    print(f"Listening on: http://{host}:{port}")
    print(f"Endpoint:     http://{host}:{port}/v1/signal")
    print("")
    print("To test:")
    print(f"  export DEEPSWEEP_INTEL_ENDPOINT=http://{host}:{port}/v1/signal")
    print("  deepsweep validate .")
    print("")
    print("Press Ctrl+C to stop")
    print("=" * 60 + "\n")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\n[INFO] Server stopped")
        server.shutdown()


if __name__ == "__main__":
    main()
