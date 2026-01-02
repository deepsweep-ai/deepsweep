# Security Policy

## Supported Versions

| Version | Status |
|---------|--------|
| Version | Status |
|---------|--------|
| 0.1.x   | Active support |
| < 0.1   | End of life |

---

## Reporting Vulnerabilities

### Contact

**Email:** security@deepsweep.ai

**PGP Key:** Available at https://deepsweep.ai/.well-known/pgp-key.txt

### What to Report

Report any security vulnerabilities in:
- DeepSweep core detection engine
- Pattern matching logic
- CLI command handling
- Telemetry implementation
- Dependency vulnerabilities

### Response Timeline

| Stage | Timeline |
|-------|----------|
| Initial response | Within 24 hours |
| Triage and assessment | Within 72 hours |
| Fix development | Within 7 days (critical), 30 days (high) |
| Public disclosure | 90 days or upon fix release |

---

## Security Practices

### Development

- All dependencies pinned with hash verification
- Automated security scanning via GitHub Actions
- Code review required for all changes
- No secrets in code or git history

### Releases

- Signed releases with GPG
- SBOM (Software Bill of Materials) published
- CVE tracking for all security fixes
- Security advisories via GitHub Security

### Privacy

- No PII collection (see Privacy Policy in README)
- Telemetry data anonymized at source
- SHA-256 hashing for install IDs (irreversible)
- No file paths or code transmitted

---

## Disclosure Policy

DeepSweep follows **coordinated disclosure**:

1. **Private report** to security@deepsweep.ai
2. **Acknowledgment** within 24 hours
3. **Triage and fix** developed privately
4. **Coordinated disclosure** 90 days after report or upon fix
5. **Public CVE** issued if applicable
6. **Credit** to reporter in release notes and Hall of Fame

We do NOT support bug bounties at this time but maintain a Hall of Fame for responsible disclosure.

---

## Hall of Fame

Security researchers who have responsibly disclosed vulnerabilities:

*None yet - be the first!*

---

## Security Features

DeepSweep is purpose-built for agentic AI security with proven reliability:

### Detection Coverage
- **Prompt injection** in AI assistant configurations (MCP tool definitions, system prompts)
- **MCP server poisoning**: Validates 13,000+ public servers, detects excessive permissions
- **Supply chain attacks** via configuration files and agent registries
- **Protocol validation**: MCP (Model Context Protocol), AG-UI (Agent-User Interface), A2A (Agent-to-Agent)

### Technical Authority Signals
- **Test coverage**: 85%+ backend, 60/60 passing CLI tests
- **Validation accuracy**: 95%+ pass rate with <10% false positives
- **Performance**: Sub-100ms validation, zero context switches
- **API contract**: Canonical POST /v1/signal endpoint (202 Accepted)
- **Privacy-preserving**: Anonymous telemetry with install_id_prefix only, no source code transmission

### Market Context
- **Agentic AI security market**: $1.83B (2025) → $7.84B (2030), 33.8% CAGR
- **Vulnerability reality**: 48% of AI-generated code contains exploitable vulnerabilities
- **Compliance pressure**: EU AI Act (August 2025), Colorado AI Act (June 2026)

For complete detection details, see [README.md](README.md).

---

## Telemetry

DeepSweep uses a two-tier telemetry model:

**Essential telemetry (always enabled)**  
Anonymous operational signals used to improve detection quality and reliability.

**Optional telemetry**  
Product analytics that can be disabled at any time.

**Offline mode**  
Set `DEEPSWEEP_OFFLINE=1` to disable all telemetry.

---

## Contact

**Security issues:** security@deepsweep.ai
**General issues:** https://github.com/deepsweep-ai/deepsweep/issues
**Questions:** hello@deepsweep.ai
