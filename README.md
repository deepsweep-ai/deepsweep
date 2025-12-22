# DeepSweep

**Security Gateway for AI Coding Assistants**

> "Vibe coding" is Collins' Word of the Year 2025. 25% of YC W25 startups
> have 95% AI-generated codebases. DeepSweep ensures your AI assistant
> setup is secure before you ship.

Validate configurations for Cursor, Copilot, Claude Code, Windsurf, and
MCP servers. Catch prompt injection, supply chain attacks, and misconfigurations
before they become problems.

[![PyPI version](https://img.shields.io/pypi/v/deepsweep-ai)](https://pypi.org/project/deepsweep-ai/)
[![Python](https://img.shields.io/pypi/pyversions/deepsweep-ai)](https://pypi.org/project/deepsweep-ai/)
[![License](https://img.shields.io/github/license/deepsweep-ai/deepsweep)](https://github.com/deepsweep-ai/deepsweep/blob/main/LICENSE)

## Quick Start

```bash
pip install deepsweep-ai
deepsweep validate .
```

Expected output:

```
DeepSweep v1.2.0
Security Gateway for AI Coding Assistants
Ship with vibes. Ship secure.

Validating .
  [INFO] Loaded 20 detection patterns
  [INFO] Checking AI assistant configurations

  [PASS] .github/copilot-instructions.md
  [FAIL] .cursorrules:15
    Prompt injection detected: ignore all previous...
    > Pattern: CURSOR-RULES-001
    > CVE: CVE-2025-43570
    > How to address: Remove instruction override patterns

---
Score: 75/100 (C - Review recommended)
A few items to review

1 item to review
---
```

## Why DeepSweep?

Traditional security tools scan code *after* generation. But attacks like
prompt injection happen at *configuration time*—before your AI assistant
writes a single line.

DeepSweep validates your AI assistant setup before execution:

- **20+ detection patterns** covering known CVEs
- **OWASP Agentic AI** alignment
- **Sub-50ms validation** (doesn't slow you down)
- **100% local** (your code never leaves your machine)

## Supported Assistants

| Assistant | Config Files | Status |
|-----------|--------------|--------|
| Cursor | `.cursorrules` | Full coverage |
| GitHub Copilot | `copilot-instructions.md` | Full coverage |
| Claude Code | `claude_desktop_config.json` | Full coverage |
| Windsurf | `.windsurfrules` | Full coverage |
| MCP Servers | `mcp.json` | Full coverage |

## CI/CD Integration

### GitHub Actions

```yaml
name: Security

on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install DeepSweep
        run: pip install deepsweep-ai

      - name: Validate configurations
        run: deepsweep validate . --fail-on high
```

### Pre-commit Hook

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: deepsweep
        name: DeepSweep
        entry: deepsweep validate .
        language: system
        pass_filenames: false
```

## Commands

### validate

Validate AI assistant configurations:

```bash
deepsweep validate .                    # Current directory
deepsweep validate ./project            # Specific path
deepsweep validate . --format json      # JSON output
deepsweep validate . --format sarif     # SARIF for GitHub Security
deepsweep validate . --fail-on critical # Only fail on critical
```

### badge

Generate a security badge for your README:

```bash
deepsweep badge                         # Creates badge.svg
deepsweep badge --format markdown       # Markdown embed code
deepsweep badge --format json           # Shields.io endpoint
```

### patterns

List all detection patterns:

```bash
deepsweep patterns
```

### telemetry

Manage telemetry settings:

```bash
deepsweep telemetry status       # View current settings
deepsweep telemetry disable      # Opt out of telemetry
deepsweep telemetry enable       # Opt back in
```

## Telemetry & Privacy

DeepSweep uses a **two-tier telemetry system** following Snyk's model.

### TIER 1: Essential (Always Active)

**Threat Intelligence** - Powers the community security flywheel:

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
- Funnel optimization

**Disable optional analytics:**

```bash
deepsweep telemetry disable
```

**Re-enable anytime:**

```bash
deepsweep telemetry enable
```

Config stored in `~/.deepsweep/config.json`.

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

For more details, see [docs/POSTHOG_SETUP.md](docs/POSTHOG_SETUP.md).

## Scoring

DeepSweep calculates a security score from 0-100:

| Grade | Score | Meaning |
|-------|-------|---------|
| A | 90-100 | Ship ready |
| B | 80-89 | Looking good |
| C | 70-79 | Review recommended |
| D | 60-69 | Attention needed |
| F | 0-59 | Let's fix this together |

Scoring formula:
- Start at 100
- Critical finding: -25
- High finding: -15
- Medium finding: -5
- Low finding: -1

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Security

Found a vulnerability? See [SECURITY.md](SECURITY.md) for reporting.

## License

MIT - see [LICENSE](LICENSE)

---

Ship with vibes. Ship secure.
