# Setup and operations

## Requirements

- Python 3.9 or newer. Nothing else: no pip packages, no Node, no database server, no internet access, no API keys.
- Any modern browser (Edge, Chrome, Firefox).

## Start

| Platform | Command |
|---|---|
| Windows | Double-click `Start-Coach.bat`, or run `py -3 -m compass` |
| macOS / Linux | `./start-coach.sh` or `python3 -m compass` |

The first start creates `var/signals.db` (synthetic data) and `var/private.db` (empty). The browser opens at `http://127.0.0.1:8765/`.

## Command reference

| Command | Purpose |
|---|---|
| `python -m compass` | Start the server and open the browser |
| `python -m compass --no-browser` | Start without opening a browser |
| `python -m compass --port 9000` | Use a different port |
| `python -m compass --reset` | Rebuild synthetic data, clear private data and audit log |
| `python -m compass eval` | Run the quality evaluation and write `reports/` (exits non-zero below 80%) |
| `python -m compass compliance` | Run data-minimization checks |
| `python -m compass export-data` | Write the synthetic dataset to `data/synthetic/*.csv` |
| `python -m unittest discover -s tests -t . -v` | Run the acceptance tests |

## Configuration (environment variables)

| Variable | Default | Meaning |
|---|---|---|
| `COMPASS_HOST` | `127.0.0.1` | Bind address. Keep it local for the demo. |
| `COMPASS_PORT` | `8765` | Port |
| `COMPASS_K_ANON` | `5` | Minimum group size for any aggregated number |
| `COMPASS_DATA_DIR` | `./var` | Where the two SQLite files and the audit log live |
| `COMPASS_SECRET` | random per start | Session signing key. Set it to keep sessions across restarts. |
| `COMPASS_LLM_URL`, `COMPASS_LLM_MODEL` | empty (off) | Optional approved OpenAI-compatible endpoint used only to polish prompt wording |

## Running under strict corporate restrictions

- **No admin rights:** Python from the company software center is enough. Nothing is installed.
- **No internet:** the UI has no CDN, web fonts or external calls. Source links in recommendations only open when clicked.
- **Port blocked:** use `--port` with any free local port.
- **`file://` only:** not needed. The UI is served by the local Python server, so browser file restrictions don't apply.
- **Python missing:** the coaching logic needs Python. The agent kit (`agent-kit/`) is plain files and works without Python.

## Install the agent kit into a project

```
agent-kit\install-kit.bat C:\path\to\your-repo
./agent-kit/install-kit.sh /path/to/your-repo
```

The installer never overwrites existing files. It skips them and lists them. See [agent-kit/README.md](../agent-kit/README.md).

## Troubleshooting

| Symptom | Fix |
|---|---|
| "Python 3 was not found" | Install Python 3.9+ and re-run. On Windows, the `py` launcher is detected automatically. |
| Port already in use | `python -m compass --port 8780` |
| Signed out after restart | Expected, because the signing key is regenerated. Set `COMPASS_SECRET` to keep sessions. |
| Want a clean demo | `python -m compass --reset` |
