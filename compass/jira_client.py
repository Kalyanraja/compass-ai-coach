"""Optional, read-only Jira fetch (off by default).

* Only GET requests to the single base URL the user configured and approved.
* Token comes from an environment variable (default COMPASS_JIRA_TOKEN) or is
  typed for the current session; it is never written to disk or logs.
* Data Center/Server: personal access token as Bearer. Cloud: email + API token
  (basic auth). Uses the REST API v2 issue endpoint (plain-text description).
* Fetched text is shown to the user for review; it is processed in memory only.
* Without Jira access, the CSV export import keeps working.
"""

from __future__ import annotations

import base64
import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request

from . import settings

KEY_RX = re.compile(r"^[A-Z][A-Z0-9_]{1,19}-\d{1,9}$")
TIMEOUT = 20


class JiraError(Exception):
    pass


def status() -> dict:
    j = settings.load()["jira"]
    return {"mode": j["mode"], "base_url": j["base_url"], "approved": j["approved"],
            "token_present": bool(os.environ.get(j.get("token_env") or "COMPASS_JIRA_TOKEN")),
            "token_env": j.get("token_env") or "COMPASS_JIRA_TOKEN",
            "ready": j["mode"] != "off" and j["approved"] and bool(j["base_url"])}


def _headers(j: dict, token: str | None) -> dict:
    tok = token or os.environ.get(j.get("token_env") or "COMPASS_JIRA_TOKEN")
    if not tok:
        raise JiraError(f"No Jira token. Set the {j.get('token_env') or 'COMPASS_JIRA_TOKEN'} environment variable or enter it for this session.")
    h = {"Accept": "application/json", "User-Agent": "compass-coach"}
    if j["mode"] == "cloud":
        if not j.get("email"):
            raise JiraError("Jira Cloud needs your account email in Settings.")
        h["Authorization"] = "Basic " + base64.b64encode(f"{j['email']}:{tok}".encode()).decode()
    else:
        h["Authorization"] = "Bearer " + tok
    return h


def _get(path: str, params: dict, token: str | None) -> dict:
    j = settings.load()["jira"]
    if j["mode"] == "off" or not j["approved"] or not j["base_url"]:
        raise JiraError("Jira is off. Configure and approve it in Settings, or import a Jira CSV export instead.")
    base = j["base_url"].rstrip("/")
    if not base.startswith("https://"):
        raise JiraError("Jira base URL must use https.")
    url = base + path + ("?" + urllib.parse.urlencode(params) if params else "")
    if urllib.parse.urlparse(url).netloc != urllib.parse.urlparse(base).netloc:
        raise JiraError("refusing to call a different host")
    req = urllib.request.Request(url, headers=_headers(j, token), method="GET")
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:  # noqa: S310 - https base URL enforced above
            return json.loads(r.read(2_000_000))
    except urllib.error.HTTPError as e:
        raise JiraError({401: "Jira rejected the credentials (401).", 403: "No permission for this issue (403).",
                         404: "Issue not found (404)."}.get(e.code, f"Jira returned HTTP {e.code}."))
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        raise JiraError(f"Could not reach Jira: {getattr(e, 'reason', e)}")
    except ValueError:
        raise JiraError("Jira returned something that is not JSON.")


def _text(v) -> str:
    if v is None:
        return ""
    if isinstance(v, str):
        return v
    if isinstance(v, dict):  # Atlassian document format (v3) fallback
        parts = []

        def walk(n):
            if isinstance(n, dict):
                if n.get("type") == "text":
                    parts.append(n.get("text", ""))
                for c in n.get("content", []) or []:
                    walk(c)
                if n.get("type") in ("paragraph", "heading", "listItem"):
                    parts.append("\n")
            elif isinstance(n, list):
                for c in n:
                    walk(c)
        walk(v)
        return "".join(parts).strip()
    return str(v)


def fetch_issue(key: str, token: str | None = None) -> dict:
    key = (key or "").strip().upper()
    if not KEY_RX.match(key):
        raise JiraError("That does not look like a Jira key (for example ABC-123).")
    j = settings.load()["jira"]
    fields = "summary,description,issuetype,priority,status,labels,components"
    if j.get("acceptance_field"):
        if not re.match(r"^customfield_\d+$", j["acceptance_field"]):
            raise JiraError("acceptance_field must look like customfield_12345")
        fields += "," + j["acceptance_field"]
    data = _get(f"/rest/api/2/issue/{key}", {"fields": fields}, token)
    f = data.get("fields", {})
    ac = _text(f.get(j.get("acceptance_field"))) if j.get("acceptance_field") else ""
    text = (f.get("summary") or "") + "\n" + _text(f.get("description")) + (("\nAcceptance criteria:\n" + ac) if ac else "")
    return {"key": data.get("key", key), "summary": f.get("summary", ""), "issue_type": (f.get("issuetype") or {}).get("name", ""),
            "status": (f.get("status") or {}).get("name", ""), "priority": (f.get("priority") or {}).get("name", ""),
            "text": text.strip()[:20000], "source": "jira-rest-v2", "stored": False}


def search(jql: str | None = None, token: str | None = None, limit: int = 20) -> list[dict]:
    j = settings.load()["jira"]
    q = (jql or j.get("default_jql") or "").strip()
    if len(q) > 500:
        raise JiraError("JQL too long")
    params = {"jql": q, "maxResults": max(1, min(50, limit)), "fields": "summary,issuetype,status"}
    path = "/rest/api/3/search/jql" if j["mode"] == "cloud" else "/rest/api/2/search"
    data = _get(path, params, token)
    return [{"key": i.get("key"), "summary": (i.get("fields") or {}).get("summary", ""),
             "issue_type": ((i.get("fields") or {}).get("issuetype") or {}).get("name", ""),
             "status": ((i.get("fields") or {}).get("status") or {}).get("name", "")} for i in data.get("issues", [])]
