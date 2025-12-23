# Changelog

All notable changes to DeepSweep will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.0] - 2025-12-22

### Added

- **Two-Tier Telemetry System** - The Flywheel/Moat
  - **ESSENTIAL Tier (Always Active)**: Threat intelligence signals power community security
    - Pattern effectiveness tracking
    - Attack trend analysis
    - Zero-day detection capability
    - Anonymized machine ID (SHA-256 hash)
    - Network effect moat - every validation strengthens the pattern database
  - **OPTIONAL Tier (User Controlled)**: PostHog product analytics
    - Activation and retention metrics
    - Feature usage patterns
    - Can be disabled with `deepsweep telemetry disable`
- Threat intelligence endpoint (`https://api.deepsweep.ai/v1/signal`)
- `DEEPSWEEP_OFFLINE` environment variable for fully offline mode
- CI detection (GitHub Actions, GitLab CI, CircleCI, Jenkins, etc.)
- Anonymized install ID generation (irreversible SHA-256 hash)
- Enhanced telemetry status command showing two-tier system
- IDEsaster CVE-2025-53109 coverage (MCP File System Escape, CVSS 9.0)

### Changed

- Telemetry now dual-track: essential + optional
- First-run notice updated to explain two-tier system
- TelemetryConfig now includes `offline_mode` property
- MCP-POISON-003 pattern upgraded to CRITICAL severity
- MCP-POISON-003 pattern now covers CVE-2025-53109
- Pattern CVE documentation enhanced with IDEsaster disclosure reference

### Technical

- `ThreatSignal` dataclass for flywheel data
- `send_threat_signal()` function (essential tier)
- `create_threat_signal()` helper
- Async sending with 2s timeout (non-blocking)
- Threat signals sent even when PostHog disabled

## [1.1.0] - 2025-12-22

### Added

- Anonymous telemetry with PostHog for product analytics
  - Command usage tracking (validate, badge, patterns)
  - Performance metrics (duration, exit codes)
  - Platform and version distribution
  - Error tracking with sanitized messages
  - First-run detection for activation metrics
- New telemetry CLI commands:
  - `deepsweep telemetry status`: View telemetry configuration
  - `deepsweep telemetry enable`: Enable telemetry collection
  - `deepsweep telemetry disable`: Disable telemetry collection
- Comprehensive PostHog dashboard setup guide (docs/POSTHOG_SETUP.md)
  - Activation funnel configuration
  - Retention tracking
  - Key metrics and KPIs
  - Competitor benchmarks (Snyk, Vercel CLI)
- First-run notice with opt-out instructions
- Privacy-first telemetry design:
  - No PII collection
  - No file paths or code content
  - No finding details
  - Anonymous UUID-based tracking
- Comprehensive telemetry test suite

### Changed

- Version bump to 1.1.0 for telemetry release
- Added PostHog dependency (posthog>=3.0.0)

### Security

- All telemetry data is anonymized
- Telemetry is opt-out (industry standard)
- Clear privacy policy in documentation
- Telemetry errors never crash the application

## [1.0.1] - 2025-12-22

### Changed
- Refined terminology consistency throughout codebase
  - Renamed `format_scan_start` to `format_validation_start`
  - Updated comments to use "validate" instead of "scan"
  - Updated file pattern constant comment to "File patterns to validate"
- Version bump to 1.0.1 for brand compliance release

### Fixed
- Minor terminology inconsistencies in internal methods
- Comment accuracy in validator subdirectory checking

## [1.0.0] - 2025-12-21

### Added

- Initial public release
- Core validation engine with sub-50ms performance
- 20+ detection patterns for known vulnerabilities:
  - CURSOR-RULES-001 through CURSOR-RULES-004: Cursor rules file security
  - COPILOT-INJ-001 through COPILOT-INJ-003: Copilot instructions injection
  - CLAUDE-WS-001 through CLAUDE-WS-003: Claude Code WebSocket security
  - MCP-POISON-001 through MCP-POISON-004: MCP server poisoning
  - WINDSURF-EXFIL-001 through WINDSURF-EXFIL-002: Windsurf exfiltration
- CVE coverage:
  - CVE-2025-43570: Cursor rules file backdoor
  - CVE-2025-43102: Copilot instructions injection
  - CVE-2025-52882: Claude Code WebSocket auth bypass
  - CVE-2025-54135: MCP server command injection
  - CVE-2025-55284: Windsurf data exfiltration
- CLI commands:
  - `deepsweep validate`: Validate configurations
  - `deepsweep badge`: Generate security badge
  - `deepsweep patterns`: List detection patterns
- Output formats: text, JSON, SARIF
- NO_COLOR environment variable support
- Optimistic messaging throughout (Wiz approach)
- 100% local execution (code never leaves machine)
- MIT license

### Security

- All validation runs locally
- No network requests during validation
- No telemetry or analytics
