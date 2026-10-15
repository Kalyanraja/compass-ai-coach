"""Safe, read-only access to a selected project folder, and fact detection.

Boundaries:
* Only folders under the user's allowed roots (Settings) can be opened.
* Paths are resolved and must stay inside the project root (no traversal, no
  symlink escapes; symlinks are skipped entirely).
* Credential-like files and VCS/dependency folders are never read.
* File size and count limits keep scans bounded.

Every fact carries a status (detected, inferred, confirmed, unknown) and a source
{path, line} when it came from a file. Nothing is invented: when a fact cannot be
found it is "unknown", and stacks the detectors don't support are reported as such.
"""

from __future__ import annotations

import hashlib
import os
import re
from pathlib import Path

MAX_FILE_BYTES = 256 * 1024
MAX_FILES = 3000
SKIP_DIRS = {".git", ".hg", ".svn", "node_modules", ".venv", "venv", "__pycache__", "target", "build", "dist",
             ".idea", ".vs", "bin", "obj", ".gradle", ".mypy_cache", ".pytest_cache", ".tox"}
BLOCKED_NAMES = re.compile(
    r"(^\.env(\..*)?$|^id_(rsa|dsa|ecdsa|ed25519)(\.pub)?$|\.(pem|key|p12|pfx|jks|keystore|kdbx|ppk)$|^\.npmrc$|^\.pypirc$|"
    r"^\.netrc$|^credentials(\.json)?$|^secrets?\.(json|ya?ml|txt)$|^\.git-credentials$|^known_hosts$|^\.docker(cfg)?$)",
    re.I)
BLOCKED_DIR_PARTS = {".ssh", ".aws", ".azure", ".gnupg", ".kube", ".docker"}
TEXT_EXT = {".java", ".kt", ".py", ".ts", ".tsx", ".js", ".jsx", ".cs", ".go", ".rb", ".php", ".sql", ".yaml", ".yml",
            ".json", ".xml", ".md", ".txt", ".toml", ".ini", ".cfg", ".gradle", ".properties", ".csproj", ".sln",
            ".html", ".css", ".sh", ".bat", ".ps1", ".diff", ".cbl", ".jcl", ".feature"}


class WorkspaceError(Exception):
    pass


class Workspace:
    def __init__(self, root: str, allowed_roots: list[str]):
        if not root:
            raise WorkspaceError("choose a project folder")
        p = Path(root).expanduser()
        if not p.is_absolute():
            raise WorkspaceError("use an absolute project path")
        if p.is_symlink():
            raise WorkspaceError("the project folder cannot be a symbolic link")
        rp = p.resolve()
        if not rp.is_dir():
            raise WorkspaceError("project folder not found")
        allowed = [Path(a).resolve() for a in allowed_roots]
        if not any(rp == a or a in rp.parents for a in allowed):
            raise WorkspaceError("this folder is not in your allowed project folders (Settings)")
        if any(part in BLOCKED_DIR_PARTS for part in rp.parts):
            raise WorkspaceError("this folder is a credential location and cannot be read")
        self.root = rp

    # ------------------------------------------------------------------ paths
    def safe_path(self, rel: str) -> Path:
        if not rel or "\x00" in rel:
            raise WorkspaceError("invalid path")
        candidate = (self.root / rel)
        # reject symlinks anywhere along the way
        cur = self.root
        for part in Path(rel).parts:
            if part in ("..",):
                raise WorkspaceError("path traversal is not allowed")
            cur = cur / part
            if cur.is_symlink():
                raise WorkspaceError("symbolic links are not followed")
        resolved = candidate.resolve()
        if resolved != self.root and self.root not in resolved.parents:
            raise WorkspaceError("path escapes the project folder")
        if BLOCKED_NAMES.search(resolved.name) or any(p in BLOCKED_DIR_PARTS for p in resolved.parts):
            raise WorkspaceError("credential-like files are never read")
        return resolved

    def files(self) -> list[str]:
        out = []
        for dirpath, dirnames, filenames in os.walk(self.root, followlinks=False):
            dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS and d not in BLOCKED_DIR_PARTS
                                 and not (Path(dirpath) / d).is_symlink())
            for f in sorted(filenames):
                fp = Path(dirpath) / f
                if fp.is_symlink() or BLOCKED_NAMES.search(f):
                    continue
                if fp.suffix.lower() not in TEXT_EXT and f not in ("Dockerfile", "Jenkinsfile", "Makefile", "AGENTS.md", "CLAUDE.md"):
                    continue
                try:
                    if fp.stat().st_size > MAX_FILE_BYTES:
                        continue
                except OSError:
                    continue
                out.append(fp.relative_to(self.root).as_posix())
                if len(out) >= MAX_FILES:
                    return out
        return out

    def read(self, rel: str) -> str:
        p = self.safe_path(rel)
        if not p.is_file():
            raise WorkspaceError(f"not a file: {rel}")
        if p.stat().st_size > MAX_FILE_BYTES:
            raise WorkspaceError(f"file too large: {rel}")
        return p.read_text(encoding="utf-8", errors="replace")

    def lines(self, rel: str) -> list[str]:
        return self.read(rel).splitlines()

    def snapshot_hash(self, rels: list[str] | None = None) -> str:
        h = hashlib.sha256()
        for rel in sorted(rels if rels is not None else self.files()):
            try:
                h.update(rel.encode())
                h.update(hashlib.sha256(self.safe_path(rel).read_bytes()).digest())
            except (OSError, WorkspaceError):
                continue
        return h.hexdigest()


# ---------------------------------------------------------------------- facts

def fact(fid, label, value, status, path=None, line=None, note=None):
    f = {"id": fid, "label": label, "value": value, "status": status}
    if path:
        f["source"] = {"path": path, "line": line}
    if note:
        f["note"] = note
    return f


def _find(ws: Workspace, rel: str, pattern: str, flags=re.I):
    try:
        for i, ln in enumerate(ws.lines(rel), start=1):
            if re.search(pattern, ln, flags):
                return i, ln.strip()
    except WorkspaceError:
        return None
    return None


SUPPORTED_STACKS = {
    "java-maven": "Java with Maven (pom.xml)",
    "java-gradle": "Java/Kotlin with Gradle",
    "python": "Python (pyproject.toml / requirements.txt / setup.py)",
    "node": "JavaScript/TypeScript with npm (package.json)",
    "dotnet": ".NET (*.csproj)",
}


def detect_facts(ws: Workspace) -> dict:
    files = ws.files()
    fs = set(files)
    facts: dict[str, dict] = {}

    def put(f):
        facts[f["id"]] = f

    # stack + build file
    stack = None
    if "pom.xml" in fs:
        stack = "java-maven"
        hit = _find(ws, "pom.xml", r"<artifactId>spring-boot") or _find(ws, "pom.xml", r"<artifactId>")
        put(fact("build_file", "Build file", "pom.xml", "detected", "pom.xml", hit[0] if hit else 1))
    elif any(f.endswith("build.gradle") or f.endswith("build.gradle.kts") for f in files):
        stack = "java-gradle"
        bf = next(f for f in files if f.endswith(("build.gradle", "build.gradle.kts")))
        put(fact("build_file", "Build file", bf, "detected", bf, 1))
    elif "pyproject.toml" in fs or "requirements.txt" in fs or "setup.py" in fs:
        stack = "python"
        bf = "pyproject.toml" if "pyproject.toml" in fs else ("requirements.txt" if "requirements.txt" in fs else "setup.py")
        hit = _find(ws, bf, r"requires-python|^name\s*=") if bf == "pyproject.toml" else None
        put(fact("build_file", "Build file", bf, "detected", bf, hit[0] if hit else 1))
    elif "package.json" in fs:
        stack = "node"
        put(fact("build_file", "Build file", "package.json", "detected", "package.json", 1))
    elif any(f.endswith(".csproj") for f in files):
        stack = "dotnet"
        bf = next(f for f in files if f.endswith(".csproj"))
        put(fact("build_file", "Build file", bf, "detected", bf, 1))
    else:
        put(fact("build_file", "Build file", None, "unknown", note="No supported build file found."))

    if stack:
        src = facts["build_file"]["source"]
        put(fact("stack", "Stack", SUPPORTED_STACKS[stack], "detected", src["path"], src["line"]))
    else:
        exts = sorted({Path(f).suffix for f in files if Path(f).suffix})
        put(fact("stack", "Stack", None, "unknown",
                 note=("Automatic framework detection is unavailable for this project (" + ", ".join(exts[:6]) +
                       "). Supported for deep detection: " + ", ".join(SUPPORTED_STACKS.values()) +
                       ". Select your workflow and confirm the facts and commands yourself.")))
    facts["stack"]["stack_id"] = stack

    # test framework + command
    tf = None
    if stack == "java-maven":
        hit = _find(ws, "pom.xml", r"junit-jupiter|<artifactId>junit")
        if hit:
            tf = fact("test_framework", "Test framework", "JUnit 5", "detected", "pom.xml", hit[0])
        put(fact("test_command", "Test command", "mvn -q test", "inferred", "pom.xml", facts["build_file"]["source"]["line"],
                 note="Maven convention; confirm the exact command."))
    elif stack == "python":
        tfile = next((f for f in files if re.match(r"(.*/)?tests?/.*test.*\.py$", f)), None)
        if tfile:
            hit = _find(ws, tfile, r"import unittest|unittest\.TestCase")
            if hit:
                tf = fact("test_framework", "Test framework", "unittest", "detected", tfile, hit[0])
            else:
                hit = _find(ws, tfile, r"import pytest|def test_")
                if hit:
                    tf = fact("test_framework", "Test framework", "pytest", "detected", tfile, hit[0])
        cmd_src = None
        for doc in ("AGENTS.md", "README.md"):
            if doc in fs:
                h = _find(ws, doc, r"python -m (unittest|pytest)[^`\n]*")
                if h:
                    m = re.search(r"python -m (unittest|pytest)[^`\n]*", h[1])
                    cmd_src = (doc, h[0], m.group(0).strip())
                    break
        if cmd_src:
            put(fact("test_command", "Test command", cmd_src[2], "detected", cmd_src[0], cmd_src[1]))
        else:
            put(fact("test_command", "Test command", "python -m unittest discover -s tests -t .", "inferred",
                     note="Python convention; confirm the exact command."))
    elif stack == "node":
        h = _find(ws, "package.json", r'"test"\s*:')
        if h:
            put(fact("test_command", "Test command", "npm test", "detected", "package.json", h[0]))
        h2 = _find(ws, "package.json", r"@playwright/test|\"jest\"|vitest|mocha")
        if h2:
            name = re.search(r"@playwright/test|jest|vitest|mocha", h2[1]).group(0)
            tf = fact("test_framework", "Test framework", name, "detected", "package.json", h2[0])
    elif stack == "dotnet":
        bf = facts["build_file"]["value"]
        h = _find(ws, bf, r"xunit|nunit|mstest")
        if h:
            tf = fact("test_framework", "Test framework", re.search(r"xunit|nunit|mstest", h[1], re.I).group(0), "detected", bf, h[0])
        put(fact("test_command", "Test command", "dotnet test", "inferred", bf, 1, note=".NET convention; confirm."))
    elif stack == "java-gradle":
        put(fact("test_command", "Test command", "gradle test", "inferred", facts["build_file"]["value"], 1, note="Gradle convention; confirm."))
    put(tf or fact("test_framework", "Test framework", None, "unknown"))
    if "test_command" not in facts:
        put(fact("test_command", "Test command", None, "unknown"))

    # API spec
    specs = [f for f in files if re.search(r"(^|/)(openapi|swagger)[^/]*\.(ya?ml|json)$", f, re.I)]
    spec = min(specs, key=lambda f: (f.count("/"), f)) if specs else None  # prefer the project's own, shallowest spec
    if spec:
        h = _find(ws, spec, r"^\s*\"?(openapi|swagger)\"?\s*:")
        put(fact("api_spec", "API specification", spec, "detected", spec, h[0] if h else 1))
        sec = _find(ws, spec, r"securitySchemes")
        if sec:
            put(fact("auth_scheme", "Authentication scheme", "declared in spec", "detected", spec, sec[0]))
        else:
            put(fact("auth_scheme", "Authentication scheme", None, "unknown", note=f"No securitySchemes in {spec}."))
    else:
        put(fact("api_spec", "API specification", None, "unknown"))
        put(fact("auth_scheme", "Authentication scheme", None, "unknown"))

    # standards
    stds = [f for f in files if re.search(r"(^|/)standards?/.*\.md$|standard.*\.md$", f, re.I)]
    std = min(stds, key=lambda f: (f.count("/"), f)) if stds else None
    if std:
        put(fact("api_standard", "Project standard", std, "detected", std, 1))
        for fid, label, rx in (("standard_header_rule", "Standard: required header", r"X-Correlation-Id"),
                               ("standard_error_rule", "Standard: error responses", r"\b400\b"),
                               ("standard_auth_rule", "Standard: authentication", r"bearer|auth")):
            h = _find(ws, std, rx)
            if h:
                ident = re.search(r"STD-[A-Z]+-\d+", h[1])
                text = re.sub(r"[*`]", "", h[1])
                if ident:
                    text = text.replace(ident.group(0), "")
                text = text.strip(" -:.0123456789\t")
                put(fact(fid, label, (ident.group(0) + ": " if ident else "") + text[:160], "detected", std, h[0]))
    else:
        put(fact("api_standard", "Project standard", None, "unknown", note="No standards document found."))

    # agent instructions
    ai = next((f for f in ("AGENTS.md", ".github/copilot-instructions.md", "CLAUDE.md") if f in fs), None)
    put(fact("agent_instructions", "Agent instructions file", ai, "detected" if ai else "unknown",
             ai, 1 if ai else None, note=None if ai else "No AGENTS.md / copilot-instructions.md / CLAUDE.md."))

    # CI
    ci = next((f for f in files if f.startswith(".github/workflows/") or f in ("Jenkinsfile", "azure-pipelines.yml")), None)
    put(fact("ci", "CI configuration", ci, "detected" if ci else "unknown", ci, 1 if ci else None))

    # existing tests
    tests = [f for f in files if (re.search(r"(^|/)(tests?|__tests__|src/test)/", f) or re.search(r"(Test|_test|\.test|\.spec)\.\w+$", f))
             and Path(f).suffix.lower() in (".py", ".java", ".kt", ".ts", ".tsx", ".js", ".cs", ".go", ".feature")
             and not f.endswith("__init__.py") and not f.startswith("recorded/")]
    put(fact("existing_tests", "Existing test files", tests[:12], "detected" if tests else "unknown",
             tests[0] if tests else None, 1 if tests else None))

    # stories / defect reports shipped with fixtures
    stories = [f for f in files if re.search(r"(^|/)docs/(stories/|uat-defect)", f)]
    if stories:
        put(fact("documents", "Story / defect documents", stories, "detected", stories[0], 1))

    return {"root": str(ws.root), "name": ws.root.name, "file_count": len(files), "stack": stack,
            "supported_stack": bool(stack), "facts": facts}


def project_map(ws: Workspace, limit: int = 400) -> list[dict]:
    """Small structural map for navigation (not proof): file, size, top-level symbols."""
    out = []
    sym_rx = {
        ".py": r"^\s*(def|class)\s+([A-Za-z_]\w*)",
        ".java": r"^\s*(?:public|private|protected)?\s*(?:static\s+)?(?:class|interface|record|enum|[\w<>\[\]]+)\s+([A-Za-z_]\w*)\s*[({]",
        ".ts": r"^\s*(?:export\s+)?(?:async\s+)?(?:function|class|const)\s+([A-Za-z_]\w*)",
        ".js": r"^\s*(?:export\s+)?(?:async\s+)?(?:function|class|const)\s+([A-Za-z_]\w*)",
        ".cs": r"^\s*(?:public|private|internal)\s+.*?(?:class|void|Task|[\w<>]+)\s+([A-Za-z_]\w*)\s*[({]",
    }
    for rel in ws.files()[:limit]:
        p = ws.safe_path(rel)
        entry = {"path": rel, "bytes": p.stat().st_size}
        rx = sym_rx.get(Path(rel).suffix.lower())
        if rx:
            syms = []
            for i, ln in enumerate(ws.lines(rel), start=1):
                m = re.search(rx, ln)
                if m:
                    syms.append({"name": m.groups()[-1], "line": i})
                if len(syms) >= 15:
                    break
            entry["symbols"] = syms
        out.append(entry)
    return out
