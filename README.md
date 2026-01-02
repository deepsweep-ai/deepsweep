<div align="center">

# DeepSweep

**The #1 Security Gateway for Agentic AI Code Assistants**

*Ship with vibes. Ship secure.*

Privacy-preserving validation for AI assistant configurations—preventing prompt injection, MCP poisoning, and supply chain attacks before execution.

[![CI](https://github.com/deepsweep-ai/deepsweep/actions/workflows/ci.yml/badge.svg)](https://github.com/deepsweep-ai/deepsweep/actions)
[![PyPI](https://img.shields.io/pypi/v/deepsweep-ai.svg)](https://pypi.org/project/deepsweep-ai/)
[![Python](https://img.shields.io/pypi/pyversions/deepsweep-ai)](https://pypi.org/project/deepsweep-ai/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

[Quick Start](#quick-start) · [Documentation](https://docs.deepsweep.ai) · [Contributing](CONTRIBUTING.md)

</div>

---

## Why DeepSweep

**The Problem:** 48% of AI-generated code contains exploitable vulnerabilities. Configuration files for AI code assistants (Cursor, Copilot, Claude Code, Windsurf, MCP servers) form a critical security boundary—yet traditional SAST tools scan *after* code commits, missing validation during AI generation.

**The Reality:** With the agentic AI security market growing from $1.83B (2025) to $7.84B (2030) at 33.8% CAGR, attacks targeting AI assistant configurations are intensifying: prompt injection in tool definitions, MCP server poisoning, and supply chain compromises through malicious agent registries.

**The Solution:** DeepSweep validates AI assistant configurations **before execution**, blocking threats at inception. Purpose-built for agentic AI security—not SAST with AI features bolted on.

---

## Protocol Coverage

DeepSweep validates three critical agentic AI protocols:

- **MCP (Model Context Protocol)**: Validates 13,000+ public MCP servers, detects tool poisoning, prevents unauthorized data access
- **AG-UI (Agent-User Interface)**: Monitors 16 event types (TEXT_MESSAGE_CONTENT, TOOL_CALL_START/END) for injection attempts
- **A2A (Agent-to-Agent)**: Google/Linux Foundation protocol validation, prevents cascade failures across agent networks

---

## Quick Start

```bash
pip install deepsweep-ai
deepsweep validate .
```

**Output:**
```
DeepSweep v0.1.0
The #1 Security Gateway for Agentic AI Code Assistants
Ship with vibes. Ship secure.

Validating .
  [INFO] Loaded 47 detection patterns
  [INFO] Checking AI assistant configurations

[PASS] .cursorrules
[FAIL] .mcp/config.json:12
  MCP server URL lacks HTTPS - potential interception
  > Pattern: mcp-insecure-transport
  > How to address: Use HTTPS URLs for all MCP server endpoints

---
Score: 85/100 (B)
A few items to review

1 item to review
---
```

---

## Features

### Secure at Inception
- **Sub-100ms validation** in CLI/IDE before code commits
- **Blocking/quarantine modes** prevent unsafe configurations from executing
- **Zero context switches**: integrates with existing workflows (GitHub Actions, GitLab CI, Jenkins, CircleCI)

### Privacy-Preserving Architecture
- **No source code transmission**: only configuration files validated locally
- **Anonymous telemetry**: `install_id_prefix` only, no PII or file paths
- **DO_NOT_TRACK support**: fully offline mode available

### Technical Authority
- **85%+ backend test coverage**, 60/60 passing CLI tests
- **95%+ validation pass rate** with <10% false positives
- **Locked API contract**: canonical POST /v1/signal endpoint (202 Accepted)

### Integration Excellence
- **IDEs**: VS Code (75.9% market share), Cursor, Windsurf, with PyCharm/IntelliJ roadmap
- **CI/CD**: Native GitHub Actions, GitLab CI, Jenkins, CircleCI integration
- **Cloud Security**: AWS Security Hub (ASFF), Azure Defender, GCP Security Command Center

---

## Supported AI Assistants

DeepSweep validates configurations for:

- **Cursor** (`.cursorrules`, `.cursor/rules`)
- **GitHub Copilot** (`.github/copilot-instructions.md`, `.copilot/instructions.md`)
- **Claude Code** (`claude_desktop_config.json`, `.claude/config.json`)
- **Windsurf** (`.windsurfrules`, `.windsurf/rules`)
- **MCP Servers** (`mcp.json`, `.mcp/config.json`)

---

## Compliance & Governance

Addresses enterprise regulatory requirements:

- **EU AI Act (August 2025)**: §9 high-risk system controls, prevents $35M penalties (7% global turnover)
- **Colorado AI Act (June 2026)**: Algorithmic discrimination requirements
- **SOC2, ISO 27001**: Compliance reporting, audit logging, RBAC-ready

---

## CLI Commands

### Validate configurations
```bash
# Validate current directory
deepsweep validate .

# Fail on critical/high severity only
deepsweep validate . --fail-on high

# Generate SARIF for GitHub Security tab
deepsweep validate . --format sarif --output report.sarif
```

### Generate security badge
```bash
deepsweep badge --output badge.svg
```

### List detection patterns
```bash
deepsweep patterns
```

### Manage telemetry
```bash
deepsweep telemetry status
deepsweep telemetry disable
```

---

## GitHub Actions Integration

```yaml
name: DeepSweep Security Gateway
on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - uses: deepsweep-ai/deepsweep@main
        with:
          fail-on-critical: true
          upload-sarif: true
```

---

## Architecture

**Open-core model:**
- **Apache 2.0 CLI**: Local validation, privacy-preserving telemetry
- **Commercial platform** (roadmap): Cross-project governance, centralized agent registry, compliance dashboards

**Infrastructure:**
- AWS serverless: API Gateway, Lambda, DynamoDB
- CloudFormation IaC for reproducible deployments
- Anonymous telemetry with install_id fingerprinting (DO_NOT_TRACK supported)

---

## Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for:

- Development setup
- Design standards (NO EMOJIS, optimistic messaging)
- Pattern templates
- Testing requirements (85%+ coverage)

---

## Security

Report vulnerabilities to **security@deepsweep.ai**. See [SECURITY.md](SECURITY.md) for our disclosure policy.

---

## License

MIT License - see [LICENSE](LICENSE) for details.

---

## Resources

- **Documentation**: [docs.deepsweep.ai](https://docs.deepsweep.ai)
- **GitHub Issues**: [github.com/deepsweep-ai/deepsweep/issues](https://github.com/deepsweep-ai/deepsweep/issues)
- **Changelog**: [CHANGELOG.md](CHANGELOG.md)

---

<div align="center">

**Built for elite senior engineers, AI researchers, and security teams who demand authoritative, data-driven security without marketing theater.**

*Market intelligence: Agentic AI security market $1.83B (2025) → $7.84B (2030), 33.8% CAGR*

</div>
