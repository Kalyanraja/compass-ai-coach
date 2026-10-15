"""Shared test setup: an isolated data dir and a live server on a random port."""

import json
import os
import tempfile
import threading
import urllib.error
import urllib.request

_TMP = tempfile.mkdtemp(prefix="compass-test-")
os.environ["COMPASS_DATA_DIR"] = _TMP

from compass import config, db  # noqa: E402  (env must be set first)
from compass.server import Handler  # noqa: E402
from http.server import ThreadingHTTPServer  # noqa: E402

db.init(reset=True)

_server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
threading.Thread(target=_server.serve_forever, daemon=True).start()
BASE = f"http://127.0.0.1:{_server.server_address[1]}"


def call(method, path, body=None, token=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(BASE + path, data=data, method=method)
    req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", "Bearer " + token)
    try:
        with urllib.request.urlopen(req) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read() or b"{}")


def login(role, subject=None):
    s, b = call("POST", "/api/session", {"role": role, "subject": subject})
    assert s == 200, b
    return b["token"]
