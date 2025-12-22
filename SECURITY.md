# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | Yes                |
| < 1.0   | No                 |

## Reporting a Vulnerability

If you discover a security vulnerability in DeepSweep, please report it
responsibly:

1. **Do not** open a public issue
2. Email security@deepsweep.ai with:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Any suggested fixes

We will respond within 48 hours and work with you to address the issue.

## Security Design

DeepSweep is designed with security in mind:

- **100% local execution**: Your code never leaves your machine
- **No network requests**: Validation runs entirely offline
- **No telemetry**: We don't collect any data
- **Open source**: Full transparency into what the tool does

## Pattern Updates

Detection patterns are updated regularly to cover new CVEs.
Update to the latest version to get the newest patterns:

```bash
pip install --upgrade deepsweep-ai
```
