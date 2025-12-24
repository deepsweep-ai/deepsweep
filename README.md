<div align="center">

# DeepSweep

Security validation for AI code assistant configuration surfaces.

Validate Cursor, Copilot, Claude Code, Windsurf, and other configurations
before they execute in your environment.

[![CI](https://github.com/deepsweep-ai/deepsweep/actions/workflows/ci.yml/badge.svg)](https://github.com/deepsweep-ai/deepsweep/actions)
[![PyPI](https://img.shields.io/pypi/v/deepsweep-ai.svg)](https://pypi.org/project/deepsweep-ai/)
[![Python](https://img.shields.io/pypi/pyversions/deepsweep-ai)](https://pypi.org/project/deepsweep-ai/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

[Quick Start](#quick-start) · [Documentation](https://docs.deepsweep.ai) · [Contributing](CONTRIBUTING.md)

</div>

---

## Overview

DeepSweep is designed for modern development environments where AI code assistants
are heavily relied upon for generating code and configuration (sometimes referred
to as “vibe coding”).

It validates AI assistant configuration files before execution, surfacing
deterministic, review-oriented security signals.

These files form a security boundary and are increasingly targeted by prompt injection, MCP poisoning, and supply-chain attacks.

DeepSweep validates and, when explicitly configured, quarantines these configurations **before execution**, providing deterministic, review-oriented security signals.

---

## Quick Start

```bash
pip install deepsweep-ai
deepsweep validate .