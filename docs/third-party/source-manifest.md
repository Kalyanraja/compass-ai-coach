# Source manifest: 37 reviewed candidates

Generated from `catalog/tools.json` (checked 2026-10-15) by `scripts/build_source_manifest.py`. Metadata only. Not executable plugin definitions. Every entry is inactive (enabled=false, approval_state=not-requested) until reviewed and approved through your enterprise process.

Revisions come from `git ls-remote` (HEAD of the default branch). Licenses come from each repository's LICENSE file at that revision. Compass does not install, vendor or enable any of these unless *What Compass actually reuses* says so.

| Tool | Category | Status | License (code) | Content / rules / model license | Latest release | Reviewed commit | Selected workflows | Notes |
|---|---|---|---|---|---|---|---|---|
| [AI-Engineering-Coach](https://github.com/microsoft/AI-Engineering-Coach) | workflow | adapted-content | MIT |  | none | `8c78e96316a8` | feature-api, uat-defect, test-creation | Community project by Microsoft employees, not an official product. Compass does not ingest session logs. |
| [ECC](https://github.com/affaan-m/ECC) | workflow | reference | MIT |  | v2.2.3 | `b92f181b3b74` | security-review | Host-specific behavior: full hook support only in Claude Code; Copilot gets instructions/prompts only. Do not assume Claude hooks work in Copilot. |
| [spec-kit](https://github.com/github/spec-kit) | workflow | adapted-content | MIT |  | v1.2.0 | `6e7348de375f` | feature-api |  |
| [superpowers](https://github.com/obra/superpowers) | workflow | adapted-content | MIT |  | v7.0.0 | `bb92a7774141` | uat-defect, test-creation |  |
| [BMAD-METHOD](https://github.com/bmad-code-org/BMAD-METHOD) | workflow | reference | MIT |  | v6.12.4 | `8f0d50e1817f` | - |  |
| [OpenSpec](https://github.com/Fission-AI/OpenSpec) | workflow | reference | MIT |  | v1.14.2 | `f80d860fc510` | feature-api |  |
| [megalinter](https://github.com/oxsecurity/megalinter) | security | optional-capability | AGPL-3.0 |  | v10.1.0 | `f3b843634946` | - | AGPL-3.0: review obligations before redistribution or modification. |
| [security-audit-skill](https://github.com/cloudflare/security-audit-skill) | security | reference | MIT |  | none | `c1c8a8c14710` | security-review | Agent-guided audit methodology, NOT an offline vulnerability scanner. |
| [skills](https://github.com/trailofbits/skills) | security | reference | see content license | CC-BY-SA-4.0 | none | `1f68e03536f7` | security-review | CC-BY-SA-4.0 share-alike: any adapted text must carry attribution and the same license, so Compass paraphrases ideas only and copies no text. |
| [skill-scanner](https://github.com/cisco-ai-defense/skill-scanner) | security | optional-capability | Apache-2.0 |  | 2.3.0 | `8554b119bd11` | security-review | A scanner approval is not a trust guarantee; human review still required. |
| [gitleaks](https://github.com/gitleaks/gitleaks) | security | runtime-adapter-candidate | MIT |  | v8.30.1 | `b58d3f102cf3` | security-review, feature-api, uat-defect, test-creation | Adapter implemented; runs only if an approved binary is configured. Verified fixture output: v8.30.1. |
| [semgrep](https://github.com/semgrep/semgrep) | security | runtime-adapter-candidate | LGPL-2.1 | Semgrep Rules License (registry rules); not used | v1.181.0 | `51602ad27f09` | security-review | Engine LGPL-2.1; Semgrep Registry rules have their own Semgrep Rules License; Compass ships its own local rules. Verified fixture output: v1.181.0. |
| [trivy](https://github.com/aquasecurity/trivy) | security | optional-capability | Apache-2.0 |  | v0.76.0 | `032ac48ccfa5` | security-review | Report DB date and staleness; never fetch during offline runs. |
| [osv-scanner](https://github.com/google/osv-scanner) | security | optional-capability | Apache-2.0 |  | v2.7.0 | `f45535354688` | security-review | OSV data has its own terms; record DB date. |
| [syft](https://github.com/anchore/syft) | security | optional-capability | Apache-2.0 |  | v1.54.1 | `30200f1d691d` | - |  |
| [checkov](https://github.com/bridgecrewio/checkov) | security | optional-capability | Apache-2.0 |  | 3.3.29 | `7a6782e3d81e` | - |  |
| [zizmor](https://github.com/zizmorcore/zizmor) | security | optional-capability | MIT |  | v1.31.0 | `5eb37696bbf1` | security-review |  |
| [ASVS](https://github.com/OWASP/ASVS) | security | adapted-content | see content license | CC-BY-SA-4.0 | Latest stable release is 5.0.0 (May 2025) per the project README; newest semver-style git tag found was v4.0.1, so tag naming differs. | `2b47a9dd1676` | security-review | Content CC-BY-SA-4.0. Compass cites requirement IDs and paraphrases; latest stable 5.0.0 (May 2025); ID format v5.0.0-<chapter>.<section>.<req>. |
| [rtk](https://github.com/rtk-ai/rtk) | context | optional-capability | Apache-2.0 |  | v1.0.1 | `5eb0509690a6` | context-packaging | No separate 'rtk-oss' edition found in the README (checked 2026-10-15); marked unverified. Do not enable any API proxy. |
| [repomix](https://github.com/yamadashy/repomix) | context | optional-capability | MIT |  | v1.18.1 | `55c6de6aebde` | context-packaging |  |
| [ripgrep](https://github.com/BurntSushi/ripgrep) | context | runtime-adapter-candidate | MIT OR Unlicense |  | 15.2.0 | `3fce3b5bb023` | context-packaging | Dual MIT/Unlicense. |
| [ast-grep](https://github.com/ast-grep/ast-grep) | context | optional-capability | MIT |  | 0.51.0 | `48b54b3120b7` | context-packaging |  |
| [aider](https://github.com/Aider-AI/aider) | context | reference | Apache-2.0 |  | v0.86.2 | `5dc9490bb35f` | context-packaging |  |
| [LLMLingua](https://github.com/microsoft/LLMLingua) | context | optional-capability | MIT | Model weights carry their own licenses; review separately. | v0.2.2 | `5a4c78ae18ab` | - | Never applied to decisive code by default. |
| [playwright](https://github.com/microsoft/playwright) | testing | reference | Apache-2.0 |  | v1.64.1 | `5ad202df4f48` | test-creation |  |
| [spectral](https://github.com/stoplightio/spectral) | testing | runtime-adapter-candidate | Apache-2.0 |  | v6.17.0 | `95ab37eeea1f` | feature-api | Adapter implemented; Compass also ships a built-in OpenAPI lite check. Verified fixture output: v6.17.0. |
| [schemathesis](https://github.com/schemathesis/schemathesis) | testing | optional-capability | MIT |  | v4.31.1 | `da53539eec32` | feature-api |  |
| [axe-core](https://github.com/dequelabs/axe-core) | testing | optional-capability | MPL-2.0 |  | v4.14.0 | `f01bf5ce56ff` | - | MPL-2.0. |
| [stryker-js](https://github.com/stryker-mutator/stryker-js) | testing | optional-capability | Apache-2.0 |  | v10.0.0 | `c931a9323781` | test-creation |  |
| [ruff](https://github.com/astral-sh/ruff) | testing | optional-capability | MIT |  | 0.17.1 | `4683270c69cb` | - |  |
| [biome](https://github.com/biomejs/biome) | testing | optional-capability | Apache-2.0 OR MIT |  | none | `49bc11cc0e98` | - | Dual MIT/Apache-2.0. |
| [pre-commit](https://github.com/pre-commit/pre-commit) | testing | reference | MIT |  | v4.7.0 | `20b1e7cb12b8` | - | Do not install hooks automatically. |
| [awesome-copilot](https://github.com/github/awesome-copilot) | host-model | adapted-content | MIT |  | none | `36e95dfda721` | feature-api, uat-defect, test-creation |  |
| [vscode-extension-samples](https://github.com/microsoft/vscode-extension-samples) | host-model | reference | MIT |  | none | `65c1c44800ee` | - |  |
| [promptfoo](https://github.com/promptfoo/promptfoo) | host-model | optional-capability | MIT |  | 0.124.1 | `8570ed47327c` | - |  |
| [llama.cpp](https://github.com/ggml-org/llama.cpp) | host-model | optional-capability | MIT | Model weights carry their own licenses; review separately. | Releases use bNNNN build tags; no current semver release tag. | `620d2225cc43` | - | Disabled by default. |
| [web-llm](https://github.com/mlc-ai/web-llm) | host-model | optional-capability | Apache-2.0 | Model weights carry their own licenses; review separately. | v0.2.86 | `c42c36670cfc` | - | Disabled by default. |

## What Compass actually reuses

| Source | How | Where |
|---|---|---|
| obra/superpowers (MIT) | Adapted text (debugging, TDD, verification) plus a vendored copy with its LICENSE | `agent-kit/.claude/skills/`, `agent-kit/vendor/superpowers/` |
| github/awesome-copilot (MIT) | Adapted instructions and prompts; a reviewed subset is vendored with its LICENSE | `agent-kit/`, `agent-kit/vendor/awesome-copilot-selected/` |
| github/spec-kit (MIT) | Ideas from the spec/plan/tasks templates; templates vendored with their LICENSE | `agent-kit/vendor/spec-kit-templates/`, work package structure |
| microsoft/AI-Engineering-Coach (MIT) | Prompt anti-pattern rules paraphrased; rules vendored with their LICENSE | `agent-kit/prompt-library/anti-patterns.json`, `agent-kit/vendor/ai-engineering-coach-rules/` |
| cloudflare/security-audit-skill (MIT) | Idea only: the candidate / needs-validation / confirmed / rejected claim states | `compass/workflow/evidence.py` |
| OWASP/ASVS (CC-BY-SA-4.0) | Cited by version and chapter only (v5.0.0 V1, V2, V4, V6, V8, V13, V16); no text copied | `workflows/packs/security-review.json` |
| trailofbits/skills (CC-BY-SA-4.0) | Ideas only. No text is copied, because share-alike would apply to adapted text | - |
| gitleaks (MIT), Semgrep CE (LGPL-2.1), Spectral (Apache-2.0) | Runtime adapters that call a binary you installed and approved; nothing is bundled. Compass ships its own local rules (`compass_rules/`) | `compass/workflow/runner.py`, `compass/workflow/evidence.py` |

Everything else is reference-only and inactive. The optional capabilities are listed so a reviewer can approve them later: Trivy, OSV-Scanner, Syft, Checkov, zizmor, MegaLinter, skill-scanner, Repomix, RTK, ast-grep, Ruff, Biome, Stryker, Schemathesis, axe-core, promptfoo, llama.cpp, WebLLM and LLMLingua. Until an adapter is implemented and verified, none of them is ever reported as passing.

## Special review notes

- **Cloudflare security-audit-skill** is an agent methodology, not an offline vulnerability scanner.
- **ECC** behaves differently by host: full hooks only work in Claude Code, and Copilot gets instructions and prompts only. Compass never assumes Claude hooks work in Copilot.
- **RTK:** the README (checked 2026-10-15) mentions no separate `rtk-oss` edition, so this is marked partially verified. Telemetry is opt-in, and `RTK_TELEMETRY_DISABLED=1` blocks it. No proxy mode is enabled.
- **Trail of Bits skills and OWASP ASVS** are CC-BY-SA-4.0. Adapted text would have to carry attribution and the same license, so Compass cites and paraphrases instead.
- **Semgrep:** the engine is LGPL-2.1. Registry rules carry the separate Semgrep Rules License and are not used. Compass runs only `compass_rules/semgrep-local.yaml` with `--metrics off`; Semgrep sends no metrics without registry configs.
- **Trivy / OSV-Scanner:** the vulnerability databases need a separate, approved preparation step. Record the database date and how stale it is, and never fetch updates during an offline run.
- **MegaLinter** is AGPL-3.0, so review the obligations before modifying or redistributing it.
- **LLMLingua, llama.cpp, WebLLM:** model weights carry their own licenses. All three are disabled, and lossy compression is never applied to decisive code.
