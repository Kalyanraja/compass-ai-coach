"""Regenerate docs/third-party/source-manifest.md from catalog/tools.json (offline)."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
d = json.loads((ROOT / "catalog" / "tools.json").read_text(encoding="utf-8"))
L = ["# Source manifest: 37 reviewed candidates", "",
     f"Generated from `catalog/tools.json` (checked {d['generated']}) by `scripts/build_source_manifest.py`. {d['note']}", "",
     "Revisions come from `git ls-remote` (HEAD of the default branch). Licenses come from each repository's LICENSE file at that revision. "
     "Compass does not install, vendor or enable any of these unless *What Compass actually reuses* says so.", "",
     "| Tool | Category | Status | License (code) | Content / rules / model license | Latest release | Reviewed commit | Selected workflows | Notes |",
     "|---|---|---|---|---|---|---|---|---|"]
for t in d["tools"]:
    r, l = t["reviewed_revision"], t["license"]
    L.append(f"| [{t['name']}]({t['repository_url']}) | {t['category']} | {t['integration_status']} | {l['code_spdx'] or 'see content license'} | "
             f"{l['rules_or_content_license'] or l['model_license_note'] or ''} | {r.get('latest_release_tag') or r.get('latest_release_note') or 'none'} | "
             f"`{(r['commit'] or '')[:12]}` | {', '.join(t['selected_workflows']) or '-'} | {t['review_notes']} |")
L += ["", "## What Compass actually reuses", "", "| Source | How | Where |", "|---|---|---|",
      "| obra/superpowers (MIT) | Adapted text (debugging, TDD, verification) plus a vendored copy with its LICENSE | `agent-kit/.claude/skills/`, `agent-kit/vendor/superpowers/` |",
      "| github/awesome-copilot (MIT) | Adapted instructions and prompts; a reviewed subset is vendored with its LICENSE | `agent-kit/`, `agent-kit/vendor/awesome-copilot-selected/` |",
      "| github/spec-kit (MIT) | Ideas from the spec/plan/tasks templates; templates vendored with their LICENSE | `agent-kit/vendor/spec-kit-templates/`, work package structure |",
      "| microsoft/AI-Engineering-Coach (MIT) | Prompt anti-pattern rules paraphrased; rules vendored with their LICENSE | `agent-kit/prompt-library/anti-patterns.json`, `agent-kit/vendor/ai-engineering-coach-rules/` |",
      "| cloudflare/security-audit-skill (MIT) | Idea only: the candidate / needs-validation / confirmed / rejected claim states | `compass/workflow/evidence.py` |",
      "| OWASP/ASVS (CC-BY-SA-4.0) | Cited by version and chapter only (v5.0.0 V1, V2, V4, V6, V8, V13, V16); no text copied | `workflows/packs/security-review.json` |",
      "| trailofbits/skills (CC-BY-SA-4.0) | Ideas only. No text is copied, because share-alike would apply to adapted text | - |",
      "| gitleaks (MIT), Semgrep CE (LGPL-2.1), Spectral (Apache-2.0) | Runtime adapters that call a binary you installed and approved; nothing is bundled. Compass ships its own local rules (`compass_rules/`) | `compass/workflow/runner.py`, `compass/workflow/evidence.py` |",
      "", "Everything else is reference-only and inactive. The optional capabilities are listed so a reviewer can approve them later: Trivy, OSV-Scanner, Syft, Checkov, zizmor, MegaLinter, skill-scanner, Repomix, RTK, ast-grep, Ruff, Biome, Stryker, Schemathesis, axe-core, promptfoo, llama.cpp, WebLLM and LLMLingua. Until an adapter is implemented and verified, none of them is ever reported as passing.",
      "", "## Special review notes", "",
      "- **Cloudflare security-audit-skill** is an agent methodology, not an offline vulnerability scanner.",
      "- **ECC** behaves differently by host: full hooks only work in Claude Code, and Copilot gets instructions and prompts only. Compass never assumes Claude hooks work in Copilot.",
      "- **RTK:** the README (checked 2026-10-15) mentions no separate `rtk-oss` edition, so this is marked partially verified. Telemetry is opt-in, and `RTK_TELEMETRY_DISABLED=1` blocks it. No proxy mode is enabled.",
      "- **Trail of Bits skills and OWASP ASVS** are CC-BY-SA-4.0. Adapted text would have to carry attribution and the same license, so Compass cites and paraphrases instead.",
      "- **Semgrep:** the engine is LGPL-2.1. Registry rules carry the separate Semgrep Rules License and are not used. Compass runs only `compass_rules/semgrep-local.yaml` with `--metrics off`; Semgrep sends no metrics without registry configs.",
      "- **Trivy / OSV-Scanner:** the vulnerability databases need a separate, approved preparation step. Record the database date and how stale it is, and never fetch updates during an offline run.",
      "- **MegaLinter** is AGPL-3.0, so review the obligations before modifying or redistributing it.",
      "- **LLMLingua, llama.cpp, WebLLM:** model weights carry their own licenses. All three are disabled, and lossy compression is never applied to decisive code.", ""]
out = ROOT / "docs" / "third-party" / "source-manifest.md"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text("\n".join(L), encoding="utf-8")
print(f"wrote {out}")
