# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This repository contains the **AEO Suite** - a collection of tools and applications for Answer Engine Optimization (AEO), the practice of optimizing content to be cited by AI language models (ChatGPT, Perplexity, Claude, Gemini, etc.).

### Repository Structure

```
aeo-suite/
├── answer-engine-optimization/    # AEO Skill (Python modules, v1.0.0)
│   ├── modules/                   # Core AEO Python modules
│   ├── templates/                 # Report templates
│   ├── SKILL.md                   # Skill configuration
│   └── requirements.txt           # Zero core dependencies (optional only)
├── aeo-agentic-app-master-prompt.md  # Multi-agent system specification
├── .claude/                       # Claude Code configuration
│   ├── commands/                  # Custom slash commands (9 commands)
│   ├── agents/                    # Specialized agents (11 agents)
│   ├── plugins/                   # Hook-based plugins
│   └── settings.json              # Plugin configuration
└── scripts/                       # Utility scripts
```

## Architecture

### Two Primary Components

1. **AEO Skill** (`answer-engine-optimization/`)
   - Python-based content optimization toolkit
   - Six core modules: content_analyzer, optimizer, citation_tracker, query_researcher, report_generator, success_patterns
   - Self-contained (uses only Python stdlib, optional dependencies for enhanced features)
   - Data stored locally in `.aeo-data/` directory

2. **Multi-Agent AEO System** (v1.5 - in development, see [Sprint Plan](documentation/delivery/sprint-plan-v1.5.md))
   - Orchestrator agent coordinating 6 specialized subagents
   - FastAPI REST API + CLI interface
   - Hybrid deployment model (CLI + Web API)
   - JSON + Markdown communication protocol between agents
   - **Status**: Sprint 1, Day 1 COMPLETE - Implementation Ready (2025-01-08)
   - **Timeline**: 16 working days (4 sprints, 124 hours)
   - **Primary Spec**: [aeo-agentic-app-master-prompt.md](aeo-agentic-app-master-prompt.md)

### AEO Skill Modules

Located in `answer-engine-optimization/modules/`:

- **content_analyzer.py** - E-E-A-T analysis, structure scoring, citation quality
- **optimizer.py** - Content optimization with configurable levels (conservative/balanced/aggressive)
- **citation_tracker.py** - Monitor citations across ChatGPT, Perplexity, Claude, Gemini, Mistral
- **query_researcher.py** - Query opportunity research and competitor analysis
- **report_generator.py** - Client-ready strategic reports
- **success_patterns.py** - Adaptive learning system (builds pattern library from successes)
- **api_manager.py** - Optional external API integration (Ahrefs, SEMrush)
- **utils.py** - Shared utilities

### Custom Commands & Agents

**Commands** (`.claude/commands/`):
- `/new-sdk-app` - Create Claude Agent SDK applications
- `/commit`, `/commit-push-pr`, `/clean_gone` - Git workflow automation
- `/code-review` - Automated PR review with confidence scoring
- `/feature-dev` - 7-phase feature development workflow
- `/review-pr` - PR review toolkit

**Agents** (`.claude/agents/`):
- **SDK Verifiers**: `agent-sdk-verifier-py`, `agent-sdk-verifier-ts`
- **Code Analysis**: `code-explorer`, `code-architect`, `code-reviewer`, `guideline-reviewer`
- **Quality Tools**: `code-simplifier`, `comment-analyzer`, `pr-test-analyzer`, `silent-failure-hunter`, `type-design-analyzer`

## Working with the AEO Skill

### Configuration

Edit `answer-engine-optimization/SKILL.md` to configure:

```yaml
TARGET_INDUSTRY: "SaaS"              # SaaS, Healthcare, Finance, E-commerce, etc.
GEOGRAPHIC_REGION: "US"              # US, UK, Canada, Germany, Global, etc.
BRAND_VOICE: "conversational"        # formal, conversational, technical, academic
OPTIMIZATION_LEVEL: "balanced"       # conservative, balanced, aggressive
TARGET_LLMS:                         # Which LLMs to optimize for
  - "ChatGPT"
  - "Perplexity"
  - "Claude"
  - "Gemini"
```

### Key Commands (via Claude Code)

```bash
# Content audit
aeo-audit https://example.com/article

# Optimize content
aeo-optimize content/article.md

# Track citations
aeo-track https://example.com/article

# Generate report
aeo-report client-website
```

### Data Storage

All AEO data stored locally in `.aeo-data/`:
```
.aeo-data/
├── projects/{PROJECT_NAME}/
│   ├── config.json              # Project settings
│   ├── audit_history.csv        # Audit results
│   ├── optimization_log.json    # Changes made
│   └── citation_tracking.csv    # Citation data
└── success_patterns.json        # Adaptive learning data
```

## v1.5 Multi-Agent System Development

**Status**: Sprint 2, Day 6 COMPLETE - 3 Agents (50%)
**Sprint Plan**: [documentation/delivery/sprint-plan-v1.5.md](documentation/delivery/sprint-plan-v1.5.md)
**Primary Spec**: [aeo-agentic-app-master-prompt.md](aeo-agentic-app-master-prompt.md)
**Timeline**: 16 working days (4 sprints, 124 hours) - REFINED VERSION 2.0
**Current Sprint**: Sprint 2 - Specialized Agents (Days 5-6 complete, Day 7 next) 🚧
**Refinement**: Validated by rr-product-owner, rr-project-manager, rr-requirements (2025-01-08)

### Sprint Breakdown

| Sprint | Duration | Focus | Status |
|--------|----------|-------|--------|
| **Sprint 1** | 4 days (32h) | Foundation - Orchestrator + communication | ✅ 100% (All Days Complete) |
| **Sprint 2** | 4 days (32h) | 6 specialized agents | 🚧 50% (Days 5-6 Complete) |
| **Sprint 3** | 3.5 days (28h) | 3 workflows + CLI + API | 📋 Planned |
| **Sprint 4** | 4 days (32h) | Testing + production polish | 📋 Planned |

**Sprint 1 Deliverables** ✅:
- ✅ Day 1: Infrastructure, Config, Logging, Protocol, Orchestrator
- ✅ Day 2: Mock Agents (6), WorkflowStore, Tests
- ✅ Day 3: Integration Tests (Orchestrator, Workflows, Validation, Errors)
- ✅ Day 4: Retrospective, DoD Verification, Documentation
- 📊 **Metrics**: 3,694 lines (2,034 prod + 1,660 test), >80% coverage, 106% velocity

**Sprint 2 Progress** (Days 5-6 Complete - 50%):
- ✅ Day 5: Auditor Agent
  - `src/agents/auditor_agent.py` (217 lines) + tests (599 lines)
  - E-E-A-T analysis, structure scoring, citations, readability
- ✅ Day 6: Optimizer + Citation Tracker Agents
  - `src/agents/optimizer_agent.py` (228 lines) + tests (358 + 160 lines)
  - `src/agents/citation_tracker_agent.py` (216 lines) + tests (331 + 161 lines)
  - Optimizer: E-E-A-T enhancement, structure optimization, citation improvement
  - Citation Tracker: Multi-LLM tracking (5 LLMs), query-specific analysis
- 📊 **Days 5-6 Metrics**: 2,298 lines added (661 production + 1,637 test)
- 📊 **Agents Complete**: 3 of 6 (Auditor, Optimizer, Citation Tracker)

**Sprint 2 Implementation Files** (Days 7-8, remaining):

**Day 7** - Researcher + Reporter:
- `src/agents/researcher_agent.py` - Query researcher integrating with `answer-engine-optimization/modules/query_researcher.py`
- `src/agents/reporter_agent.py` - Report generator integrating with `answer-engine-optimization/modules/report_generator.py`
- `tests/unit/test_researcher_agent.py` - Researcher unit tests
- `tests/unit/test_reporter_agent.py` - Reporter unit tests
- `tests/integration/test_researcher_integration.py` - Integration tests

**Day 8** - Learning Agent + E2E Testing:
- `src/agents/learning_agent.py` - Learning optimizer integrating with `answer-engine-optimization/modules/success_patterns.py`
- `tests/unit/test_learning_agent.py` - Learning agent unit tests
- `tests/e2e/test_campaign_workflow.py` - End-to-end workflow tests
- `tests/e2e/test_user_scenarios.py` - User validation scenarios
- `documentation/delivery/sprint-2-retrospective.md` - Sprint 2 retrospective

**Note**: 0.5 day contingency buffer available (total capacity: 16 days)

### Planning Documents Reference

**PRIMARY EXECUTION PLAN** (use daily for implementation):

- **[sprint-plan-v1.5.md](documentation/delivery/sprint-plan-v1.5.md)** - Main execution blueprint
  - 16 working days broken down by day and hour
  - Day-by-day task breakdown with estimates
  - 38 specific Definition of Done checkboxes
  - Technology stack and implementation guidelines
  - **When to use**: Every day during implementation - this is your single source of truth

**SUPPORTING DOCUMENTS** (reference as needed):

- **[user-validation-plan.md](documentation/testing/user-validation-plan.md)** - User testing procedures
  - 3 validation checkpoints (Sprints 2, 3, 4)
  - Test scenarios and success criteria
  - Participant recruitment ($1,850 budget)
  - **When to use**: End of Sprint 2 (Day 8), Sprint 3 (Day 11.5), Sprint 4 (Day 16)

- **[success-metrics-tracking.md](documentation/delivery/success-metrics-tracking.md)** - Metrics tracking
  - Sprint-level metrics (processing time, workflow time, coverage)
  - PRD success metrics (WAU, retention, engagement)
  - User value metrics (time savings: 2-3 hours → <5 min)
  - Cost optimization tracking (95%+ savings target)
  - **When to use**: Track metrics throughout development, report at sprint ends

- **[sprint-refinement-action-plan.md](documentation/delivery/sprint-refinement-action-plan.md)** - Refinement summary
  - How we refined the plan (meta-document)
  - 6 critical actions and completion status
  - Consolidated findings from 3 agents
  - **When to use**: Reference only if questions about plan changes arise

- **[product-validation-v1.5.md](documentation/delivery/product-validation-v1.5.md)** - Product Owner assessment
  - 32 user stories in standard format
  - Requirements gap analysis
  - 59-page comprehensive validation
  - **When to use**: Reference for user story context and requirements traceability

- **[project-management-assessment-v1.5.md](documentation/delivery/project-management-assessment-v1.5.md)** - PM analysis
  - Sprint structure validation
  - Risk assessment (6 risks identified)
  - Timeline commitment analysis
  - **When to use**: Reference for project management decisions and risk mitigation

**TECHNICAL SPECIFICATION**:

- **[aeo-agentic-app-master-prompt.md](aeo-agentic-app-master-prompt.md)** - Complete system spec
  - Agent specifications (lines 94-441)
  - Workflow definitions (lines 444-555)
  - Communication protocol (lines 557-651)
  - **When to use**: Reference constantly during implementation for technical details

### Next Steps

1. Review comprehensive sprint plan: [sprint-plan-v1.5.md](documentation/delivery/sprint-plan-v1.5.md)
2. Review user validation plan: [user-validation-plan.md](documentation/testing/user-validation-plan.md)
3. Review success metrics tracking: [success-metrics-tracking.md](documentation/delivery/success-metrics-tracking.md)
4. Continue Sprint 1, Day 2: Base Agent Class + Data Persistence
5. Follow detailed task breakdown in sprint plan
6. Update this section after each sprint completion
7. Keep documentation/ as living structure (update after major changes)

### Implementation Principles

- **Follow sprint plan sequentially** - Tasks have dependencies
- **Maintain >80% test coverage** - Write tests alongside code
- **Update docs as living structure** - Keep README.md, CLAUDE.md, and documentation/ current
- **Commit frequently** - After each major task completion
- **Reference spec constantly** - aeo-agentic-app-master-prompt.md is source of truth

### Agent Architecture

- **Orchestrator Agent** - Task decomposition, workflow coordination, quality validation
- **6 Specialized Subagents**:
  1. Content Auditor - Comprehensive content audits
  2. Content Optimizer - AEO-optimized content generation
  3. Citation Tracker - LLM citation monitoring
  4. Query Researcher - Query opportunities & competitor analysis
  5. Report Generator - Client-ready reports
  6. Learning Optimizer - Adaptive learning & pattern analysis

### Slash Commands (Future)

- `/aeo-campaign <url>` - Complete end-to-end AEO campaign
- `/aeo-compete <topic> <competitors>` - Deep competitive analysis
- `/aeo-monitor <url>` - Continuous citation monitoring

### Technology Stack

- **Backend**: Python 3.10+, FastAPI, asyncio
- **CLI**: Click
- **Agent Framework**: Claude Agent SDK
- **Testing**: pytest (>80% coverage target)
- **Data**: Local file storage (`.aeo-agent-data/`)

## Development Guidelines

### Python Code Standards

- **Zero core dependencies** - AEO skill uses only Python stdlib
- Optional dependencies for enhanced features (see `requirements.txt`)
- Type hints on all functions (when implementing multi-agent system)
- Docstrings on all public APIs
- PEP 8 compliance

### Multi-Agent Communication Protocol

Messages use JSON + Markdown hybrid format:

```json
{
  "message_id": "msg_001",
  "from": "orchestrator",
  "to": "auditor",
  "message_type": "task_assignment",
  "task": {...},
  "results": {...},
  "markdown_report": "# Report\n\n..."
}
```

### Quality Validation (3-Layer System)

When multi-agent system is implemented:

1. **Status Check**: `success`, `failed`, `partial`
2. **Completeness Check**: All required fields present
3. **Quality Criteria**: Agent-specific validation (e.g., Auditor score >= 0)
4. **Consistency Check**: Results align with inputs

## Cost Optimization (Future Multi-Agent System)

When using Claude Agent SDK:

- **Prompt Caching** - Cache system prompts (90% savings on repeated requests)
- **Extended Context** - Use 200K token context to batch data
- **Request Batching** - Bundle agent tasks into single API calls
- **Target**: 60%+ cost savings through Max Pro plan optimization

## Testing Strategy (Future)

- **Unit Tests**: >80% coverage, test each agent/module independently
- **Integration Tests**: Test agent coordination and communication
- **E2E Tests**: Test complete workflows (`/aeo-campaign`, `/aeo-compete`)

## Privacy & Data Retention

- **Local-first**: All data stays on your machine
- **No external tracking**: Content never leaves unless using optional external APIs
- **Configurable retention**: `DATA_RETENTION_DAYS` in SKILL.md
- **Opt-in sharing**: `SHARE_ANONYMIZED_PATTERNS` (default: false)

## Plugin System

Active plugins (`.claude/plugins/`):
- **security-guidance** - PreToolUse hook for security warnings

Disabled (available):
- **explanatory-output-style** - SessionStart hook for educational insights
- **learning-output-style** - SessionStart hook for interactive learning mode

## Key Files to Understand

1. **answer-engine-optimization/SKILL.md** - Main skill configuration and documentation
2. **aeo-agentic-app-master-prompt.md** - Complete multi-agent system specification
3. **answer-engine-optimization/modules/** - Core AEO Python modules
4. **.claude/settings.json** - Plugin and tool configuration

## Next Steps for Development

When implementing the multi-agent system:

1. **Phase 1** (Weeks 1-2): Core agent system (orchestrator + base agent class)
2. **Phase 2** (Weeks 3-4): Specialized agents using AEO skill modules
3. **Phase 3** (Week 5): Workflow orchestration (campaign, compete, monitor)
4. **Phase 4** (Week 6): CLI + FastAPI interfaces
5. **Phase 5** (Week 7): Testing & documentation

Refer to `aeo-agentic-app-master-prompt.md` for complete implementation requirements.

**Remember**: Answer always honest, No fluff. Stay focused and solution driven. Break bigger tasks into smaller and create always a todolist before starting the work.  
