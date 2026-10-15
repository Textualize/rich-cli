import http.server
import subprocess
import sys
import threading

import pytest


@pytest.fixture
def resource_server():
    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path == "/redirect":
                self.send_response(302)
                self.send_header("Location", "/ok.txt")
                self.end_headers()
            elif self.path == "/ok.txt":
                self.send_response(200)
                self.send_header("Content-Type", "text/plain")
                self.end_headers()
                self.wfile.write(b"successful resource\n")
            else:
                self.send_response(int(self.path.strip("/")))
                self.send_header("Content-Type", "text/plain")
                self.end_headers()
                self.wfile.write(b"ERROR_BODY_MUST_NOT_RENDER")

        def log_message(self, *args):
            pass

    with http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler) as server:
        thread = threading.Thread(target=server.serve_forever)
        thread.start()
        try:
            yield f"http://127.0.0.1:{server.server_port}"
        finally:
            server.shutdown()
            thread.join()


def invoke(*args):
    return subprocess.run(
        [sys.executable, "-m", "rich_cli", *args],
        capture_output=True,
        text=True,
        timeout=10,
    )


@pytest.mark.parametrize("status", [404, 500])
@pytest.mark.parametrize(
    "mode", ["--syntax", "--markdown", "--json", "--csv", "--rst", "--ipynb"]
)
def test_http_error_is_reported_before_rendering(resource_server, status, mode):
    result = invoke(f"{resource_server}/{status}", mode)
    assert result.returncode != 0
    assert str(status) in result.stderr
    assert "127.0.0.1" in result.stderr
    assert "Traceback" not in result.stderr
    assert "ERROR_BODY_MUST_NOT_RENDER" not in result.stdout


@pytest.mark.parametrize("path", ["/ok.txt", "/redirect"])
def test_http_success_and_redirects(resource_server, path):
    result = invoke(resource_server + path, "--syntax")
    assert result.returncode == 0
    assert "successful resource" in result.stdout
    assert result.stderr == ""


def test_connection_error_is_reported_without_traceback():
    with http.server.ThreadingHTTPServer(
        ("127.0.0.1", 0), http.server.BaseHTTPRequestHandler
    ) as server:
        url = f"http://127.0.0.1:{server.server_port}/unavailable"
    result = invoke(url, "--markdown")
    assert result.returncode != 0
    assert "127.0.0.1" in result.stderr
    assert "Traceback" not in result.stderr
