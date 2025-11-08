# Agentic AEO - Multi-Agent System (v1.5)

> Multi-agent Answer Engine Optimization system built with Claude Agent SDK

This directory contains the **v1.5 Multi-Agent System** for AEO Box - an orchestrated system of 7 specialized agents that automate complete AEO workflows.

## System Architecture

- **1 Orchestrator Agent** - Coordinates task decomposition and agent coordination
- **6 Specialized Agents**:
  - Auditor - Content analysis and E-E-A-T scoring
  - Optimizer - AI-powered content improvements
  - Tracker - Multi-LLM citation monitoring
  - Researcher - Query opportunity discovery
  - Reporter - Client-ready report generation
  - Learning - Adaptive pattern recognition

## Features

- **Automated Workflows**: `/aeo-campaign`, `/aeo-compete`, `/aeo-monitor`
- **Dual Interface**: CLI (Click) + REST API (FastAPI)
- **Cost Optimized**: 95%+ savings with prompt caching and request batching
- **Quality Assured**: 4-layer validation system with >80% test coverage
- **Local-First**: All data stored locally in `.aeo-agent-data/`

## Quick Start

### Installation

```bash
# From the agentic-aeo directory
pip install -r requirements.txt

# Or install with development tools
pip install -r requirements-dev.txt
```

### Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your API keys
# Required: ANTHROPIC_API_KEY
```

### Run CLI

```bash
# Run a complete AEO campaign
aeo-agent campaign --url "https://example.com/article" --queries "query1,query2"

# Run competitive analysis
aeo-agent compete --urls "url1,url2,url3" --query "target query"

# Monitor citations
aeo-agent monitor --baseline "baseline.json" --queries "query1,query2"
```

### Run API Server

```bash
# Start FastAPI server
uvicorn agentic_aeo.api.main:app --reload --port 8000

# Access API docs
# http://localhost:8000/docs
```

## Documentation

- **Sprint Plan**: [../documentation/delivery/sprint-plan-v1.5.md](../documentation/delivery/sprint-plan-v1.5.md)
- **Master Spec**: [../aeo-agentic-app-master-prompt.md](../aeo-agentic-app-master-prompt.md)
- **Architecture**: [../documentation/foundation/architecture.md](../documentation/foundation/architecture.md)
- **API Reference**: [../documentation/api-reference.md](../documentation/api-reference.md)

## Development

### Run Tests

```bash
# Run all tests with coverage
pytest --cov=src tests/

# Run specific test suite
pytest tests/unit/
pytest tests/integration/
pytest tests/e2e/
```

### Code Quality

```bash
# Format code
black src/ tests/

# Lint code
ruff check src/ tests/

# Type check
mypy src/
```

## Directory Structure

```
agentic-aeo/
├── src/
│   ├── agents/           # 7 agent implementations
│   ├── workflows/        # 3 automated workflows
│   ├── communication/    # Message protocol
│   ├── persistence/      # Data storage
│   ├── aeo_skill/        # Copied AEO Skill modules
│   ├── api/              # FastAPI REST API
│   ├── cli/              # Click CLI interface
│   └── utils/            # Config, logging, helpers
├── tests/
│   ├── unit/             # Unit tests
│   ├── integration/      # Integration tests
│   └── e2e/              # End-to-end workflow tests
├── docs/examples/        # Usage examples
└── scripts/              # Utility scripts
```

## Current Status

**Version**: 1.5.0-dev
**Phase**: Sprint 1 - Foundation (In Progress)
**Test Coverage**: Target >80%
**Last Updated**: 2025-01-08

## License

MIT License - See [../LICENSE](../LICENSE) for details.

---

**Part of [AEO Box](https://github.com/alirezarezvani/aeo-box)** - Transform your content into LLM-citable authority
