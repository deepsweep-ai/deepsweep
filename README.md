<div align="center">

# DeepSweep

**Security gateway for AI code assistants**

Validate Cursor, Copilot, Claude Code, and Windsurf configurations
before they execute in your environment.

[![CI](https://github.com/deepsweep-ai/deepsweep/actions/workflows/ci.yml/badge.svg)](https://github.com/deepsweep-ai/deepsweep/actions)
[![PyPI](https://img.shields.io/pypi/v/deepsweep-ai.svg)](https://pypi.org/project/deepsweep-ai/)
[![Python](https://img.shields.io/pypi/pyversions/deepsweep-ai)](https://pypi.org/project/deepsweep-ai/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

[Quick Start](#quick-start) | [Documentation](https://docs.deepsweep.ai) | [Contributing](CONTRIBUTING.md)

</div>

---

## Why DeepSweep

AI coding assistants execute instructions from configuration files. Those files
can contain prompt injection, MCP poisoning, and supply chain attacks. DeepSweep
validates configurations before execution.

**December 2025**: 30+ CVEs disclosed across every major AI IDE (IDEsaster).
DeepSweep detects all of them.

---

## Quick Start

```bash
pip install deepsweep-ai
deepsweep validate .
```

---

## Output

```
DeepSweep v1.2.0
Security Gateway for AI Coding Assistants
Ship with vibes. Ship secure.

Validating .
  [INFO] Loaded 39 detection patterns
  [INFO] Checking AI assistant configurations

  [PASS] .github/copilot-instructions.md
  [FAIL] .cursorrules:15
    Prompt injection detected: instruction override attempt
    > Pattern: CURSOR-RULES-001
    > CVE: CVE-2025-43570 (CVSS 9.1)
    > How to address: Remove instruction override patterns

---
Score: 72/100 (C - Review recommended)
A few items to review

2 items to review
---
```

---

## Installation

```bash
# pip (recommended)
pip install deepsweep-ai

# pipx (isolated)
pipx install deepsweep-ai

# From source
git clone https://github.com/deepsweep-ai/deepsweep.git
cd deepsweep && pip install -e .
```

---

## Usage

```bash
# Validate current directory
deepsweep validate .

# Validate specific path
deepsweep validate ~/projects/my-repo

# Output formats
deepsweep validate . --format text    # Human readable (default)
deepsweep validate . --format json    # Machine readable
deepsweep validate . --format sarif   # GitHub Security integration

# List patterns
deepsweep patterns

# Generate badge
deepsweep badge --output badge.svg

# Telemetry management
deepsweep telemetry status
deepsweep telemetry disable
```

---

## GitHub Action

```yaml
name: DeepSweep Security
on: [push, pull_request]

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - name: Install DeepSweep
        run: pip install deepsweep-ai
      - name: Validate
        run: deepsweep validate . --fail-on high
```

---

## Detection Coverage

### Prompt Injection
- Hidden instruction patterns
- System prompt override attempts
- Base64-encoded payloads
- Unicode obfuscation

### MCP Security
- Excessive permissions (--allow-all)
- Untrusted server sources
- Missing sandboxing
- Dangerous tool configurations

### IDEsaster CVEs (December 2025)

| CVE | CVSS | Tool | Detection |
|-----|------|------|-----------|
| CVE-2025-43570 | 9.1 | Cursor | CURSOR-RULES-001 |
| CVE-2025-52882 | 9.3 | Claude Code | MCP-POISON-001 |
| CVE-2025-43102 | 8.5 | Copilot | COPILOT-001 |
| CVE-2025-55284 | 9.2 | Windsurf | WINDSURF-EXFIL-001 |
| CVE-2025-53109 | 9.0 | MCP | MCP-POISON-003 |

---

## Privacy & Telemetry

DeepSweep uses transparent two-tier telemetry:

### TIER 1: Essential (Always Active)

**Threat Intelligence** - Powers community security:
- Pattern effectiveness tracking
- Attack trend analysis
- Zero-day detection
- Network effect moat

Every validation contributes anonymous signals that strengthen the pattern database
for all users. This is the core moat - the more DeepSweep is used, the better it
gets for everyone.

**What's collected:**
- Pattern match counts (no code, no paths)
- CVE detection rates
- Severity distributions
- Tool/platform context

**Always sent unless:** `DEEPSWEEP_OFFLINE=1` (for air-gapped environments)

### TIER 2: Optional (You Control)

**Product Analytics** - PostHog for improvements:
- Activation and retention metrics
- Feature usage patterns
- Performance data

**Disable optional analytics:**

```bash
deepsweep telemetry disable
```

**Re-enable anytime:**

```bash
deepsweep telemetry enable
```

### What We NEVER Collect

- Your code or file contents
- File paths or repository names
- Finding details or patterns matched
- Personally identifiable information (PII)
- API keys, tokens, or secrets

### Why Two Tiers?

**Essential tier** creates network effects: More users → Better patterns → Safer for everyone

**Optional tier** helps us prioritize: Which features matter? Where to optimize?

We follow the same privacy-first approach as Snyk, Vercel CLI, and GitHub CLI.

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup and guidelines.

---

## Security

Report vulnerabilities: security@deepsweep.ai

See [SECURITY.md](SECURITY.md) for disclosure policy.

---

## License

MIT License. See [LICENSE](LICENSE).

---

<div align="center">

**Ship with vibes. Ship secure.**

[Website](https://deepsweep.ai) | [Docs](https://docs.deepsweep.ai) | [GitHub](https://github.com/deepsweep-ai/deepsweep)

</div>
