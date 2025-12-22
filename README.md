<div align="center">

# DeepSweep

**The #1 Security Gateway for Agentic AI Code Assistants**

Intercept prompt injection, MCP poisoning, and supply chain attacks before your AI assistant loads them.

[![PyPI](https://img.shields.io/pypi/v/deepsweep-ai?color=0066cc&style=flat-square)](https://pypi.org/project/deepsweep-ai/)
[![Downloads](https://img.shields.io/pypi/dm/deepsweep-ai?color=0066cc&style=flat-square)](https://pypi.org/project/deepsweep-ai/)
[![License](https://img.shields.io/badge/license-MIT-0066cc?style=flat-square)](LICENSE)
[![OWASP](https://img.shields.io/badge/OWASP-Agentic%20AI%20Top%2010-0066cc?style=flat-square)](https://genai.owasp.org)

```bash
pip install deepsweep-ai
```

</div>

---

## Why a Security Gateway?

| Approach | Traditional Scanners | DeepSweep Gateway |
|----------|---------------------|-------------------|
| **Timing** | After commit | Before IDE loads config |
| **Action** | Reports findings | Blocks threats |
| **Integration** | Separate CI step | Inline protection |
| **Posture** | Reactive | Preventive |

DeepSweep validates AI assistant configurations **before** your IDE executes them—not after you've already been compromised.

---

## Overview

December 2025: OWASP releases Top 10 for Agentic AI Applications. 100% of AI coding assistants are vulnerable. 30+ CVEs disclosed across GitHub Copilot, Cursor, Claude Code, Amazon Q, and Windsurf.

DeepSweep is the security gateway that intercepts these threats at the configuration layer—before your AI assistant can act on malicious instructions.

### OWASP Agentic AI Top 10 Coverage

| OWASP Risk | Code | DeepSweep Coverage |
|------------|------|-------------------|
| Agent Goal Hijack | ASI01 | Prompt injection detection |
| Tool Misuse & Exploitation | ASI02 | MCP tool validation |
| Identity & Privilege Abuse | ASI03 | Credential exposure detection |
| Supply Chain Vulnerabilities | ASI04 | Dependency validation |
| Unexpected Code Execution | ASI05 | Auto-execute pattern detection |
| Memory & Context Poisoning | ASI06 | Memory store validation |
| Insecure Inter-Agent Comm | ASI07 | MCP server isolation checks |
| Cascading Failures | ASI08 | Chain detection |
| Human-Agent Trust Exploitation | ASI09 | YOLO mode detection |
| Rogue Agents | ASI10 | Behavioral baseline deviation |

### Detection Coverage

| Category | Patterns | CVEs |
|----------|----------|------|
| Prompt Injection | 8 | 3 |
| Data Exfiltration | 6 | 1 |
| Destructive Operations | 7 | 1 |
| Supply Chain | 5 | 1 |
| MCP Poisoning | 7 | 4 |
| Extension Risk | 6 | 1 |
| **Total** | **39** | **10+** |

Full pattern database: [deepsweep.ai/coverage](https://deepsweep.ai/coverage)

---

## Installation

```bash
pip install deepsweep-ai
```

The package name is `deepsweep-ai`. The CLI command is `deepsweep`.

---

## Usage

### Validate Directory

```bash
# Observe mode (default) - report only, exit 0
deepsweep scan .

# Enforce mode - exit 1 on critical/high findings
deepsweep scan . --enforce
```

### Output Formats

```bash
deepsweep scan . --format text      # Human-readable (default)
deepsweep scan . --format json      # Structured JSON
deepsweep scan . --format sarif     # GitHub Security integration
```

### Example Output

```
DeepSweep v0.1.0

Target     ./project
Mode       OBSERVE

────────────────────────────────────────────────────────────────────────

FINDINGS

● CRITICAL  DS-PI-001  Instruction Override Pattern
            .cursorrules:14
            "Ignore all previous instructions..."
            CVE-2025-53773

● HIGH      DS-MCP-001  MCP Server Auto-Start Enabled
            .cursor/mcp.json:8
            "autoStart": true
            CVE-2025-54135

────────────────────────────────────────────────────────────────────────

┌────────────┬─────────────────────────────────────────────────────────┐
│ Status     │ FAIL                                                    │
│ Score      │ 65/100                                                  │
│ Findings   │ 2 (1 critical, 1 high)                                  │
│ Files      │ 8 validated                                               │
│ Duration   │ 42ms                                                    │
└────────────┴─────────────────────────────────────────────────────────┘

OBSERVE MODE: Findings reported, exit code 0.
Use --enforce to exit 1 on critical/high findings.
```

---

## Files Validated

| Assistant | Configuration Files |
|-----------|---------------------|
| Cursor | `.cursorrules`, `.cursor/rules/`, `.cursor/mcp.json` |
| GitHub Copilot | `.github/copilot-instructions.md` |
| Claude Code | `CLAUDE.md`, `.claude/settings.json` |
| Windsurf | `.windsurfrules` |
| Amazon Q | `.amazonq/` |
| Universal | `AGENTS.md`, `mcp.json`, `mcp-config.json` |

---

## CI/CD Integration

### GitHub Action

```yaml
name: Security Gateway
on: [push, pull_request]

jobs:
  deepsweep:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: deepsweep-ai/deepsweep-action@v1
        with:
          fail-on-critical: true
          upload-sarif: true
```

### Manual Integration

```yaml
- run: pip install deepsweep-ai
- run: deepsweep scan . --enforce --format sarif > results.sarif
- uses: github/codeql-action/upload-sarif@v3
  with:
    sarif_file: results.sarif
```

---

## CVE Coverage

| CVE | CVSS | Target | Attack Vector |
|-----|------|--------|---------------|
| CVE-2025-53773 | 7.8 | GitHub Copilot | YOLO mode activation via rules file |
| CVE-2025-54135 | 8.6 | Cursor | MCP server auto-execution |
| CVE-2025-55284 | 7.5 | Claude Code | DNS exfiltration via prompts |
| CVE-2025-8217 | 9.1 | Amazon Q | Extension compromise chain |
| CVE-2025-6514 | 9.6 | All MCP clients | mcp-remote RCE |

Full coverage documentation: [deepsweep.ai/coverage](https://deepsweep.ai/coverage)

---

## Configuration

Create `.deepsweep.yaml` in your repository root:

```yaml
mode: observe

include:
  - .cursorrules
  - .cursor/
  - .github/copilot-instructions.md
  - CLAUDE.md
  - AGENTS.md
  - mcp.json

exclude:
  - node_modules/
  - .git/
  - vendor/

detectors:
  prompt_injection: true
  exfiltration: true
  destructive_ops: true
  supply_chain: true
  mcp_poisoning: true
  extension_risk: true

severity_threshold: low
```

---

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DEEPSWEEP_API_KEY` | API key for Pro features | — |
| `DEEPSWEEP_MODE` | Default validation mode | `observe` |
| `DEEPSWEEP_OFFLINE` | Disable all network calls | `false` |
| `DEEPSWEEP_TELEMETRY` | Enable/disable telemetry | `true` |
| `NO_COLOR` | Disable colored output | — |

---

## Privacy

All validation executes locally. Your code never leaves your machine.

Anonymous usage telemetry is enabled by default to help improve detection patterns. No source code, file contents, secrets, or personally identifiable information is ever collected. Only:
- Validation invocation count
- Detection pattern matches (IDs only, not content)
- CLI version and platform
- Validation duration

Disable telemetry:

```bash
deepsweep config set telemetry false
# Or environment variable
export DEEPSWEEP_TELEMETRY=false
```

Force offline mode (disables all network calls including telemetry):

```bash
export DEEPSWEEP_OFFLINE=1
deepsweep scan .
```

---

## Python API

```python
from deepsweep_ai import Scanner, Config, Mode

# Basic scan
scanner = Scanner()
result = scanner.scan(".")

print(f"Safe: {result.safe}")
print(f"Score: {result.score}/100")
print(f"Findings: {len(result.findings)}")

# With configuration
config = Config()
config.mode = Mode.ENFORCE

scanner = Scanner(config)
result = scanner.scan("/path/to/project")

# Access findings
for finding in result.findings:
    print(f"{finding.severity}: {finding.id} - {finding.title}")
    print(f"  File: {finding.file_path}:{finding.line_number}")
    if finding.cve_ids:
        print(f"  CVEs: {', '.join(finding.cve_ids)}")
```

---

## Development

```bash
git clone https://github.com/deepsweep-ai/deepsweep
cd deepsweep

pip install -e ".[dev]"

pytest
ruff check src/
mypy src/
```

---

## Links

| Resource | URL |
|----------|-----|
| Documentation | [deepsweep.ai/docs](https://deepsweep.ai/docs) |
| CVE Coverage | [deepsweep.ai/coverage](https://deepsweep.ai/coverage) |
| Pricing | [deepsweep.ai/pricing](https://deepsweep.ai/pricing) |
| Issues | [github.com/deepsweep-ai/deepsweep/issues](https://github.com/deepsweep-ai/deepsweep/issues) |
| Security | [github.com/deepsweep-ai/deepsweep/security](https://github.com/deepsweep-ai/deepsweep/security) |

---

## License

MIT License. See [LICENSE](LICENSE) for details.

---

<div align="center">

[deepsweep.ai](https://deepsweep.ai)

</div>
