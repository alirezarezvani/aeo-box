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

**Status**: Sprint 4 IN PROGRESS - Testing + Production Polish (12.5% complete) 🚧
**Sprint Plan**: [documentation/delivery/sprint-plan-v1.5.md](documentation/delivery/sprint-plan-v1.5.md)
**Primary Spec**: [aeo-agentic-app-master-prompt.md](aeo-agentic-app-master-prompt.md)
**Timeline**: 16 working days (4 sprints, 124 hours) - REFINED VERSION 2.0
**Current Task**: Day 13 - Error Handling + Chaos Testing 📋
**Last Updated**: 2025-11-08

### Sprint Breakdown

| Sprint | Duration | Focus | Status |
|--------|----------|-------|--------|
| **Sprint 1** | 4 days (32h) | Foundation - Orchestrator + communication | ✅ 100% (All Days Complete) |
| **Sprint 2** | 4 days (32h) | 6 specialized agents | ✅ 100% (All Days Complete) |
| **Sprint 3** | 2.5 days (20h) | 3 workflows + CLI + API + Documentation | ✅ 100% (All Days Complete) |
| **Sprint 4** | 4 days (32h) | Testing + production polish | 🚧 12.5% (Day 12 Complete) |

**Sprint 1 Deliverables** ✅:
- ✅ Day 1: Infrastructure, Config, Logging, Protocol, Orchestrator
- ✅ Day 2: Mock Agents (6), WorkflowStore, Tests
- ✅ Day 3: Integration Tests (Orchestrator, Workflows, Validation, Errors)
- ✅ Day 4: Retrospective, DoD Verification, Documentation
- 📊 **Metrics**: 3,694 lines (2,034 prod + 1,660 test), >80% coverage, 106% velocity

**Sprint 2 Deliverables** ✅:
- ✅ Day 5: Auditor Agent (217 lines + 599 test)
- ✅ Day 6: Optimizer (228 lines) + Citation Tracker (216 lines) + tests (1,010 lines)
- ✅ Day 7: Researcher (76 lines) + Reporter (94 lines) + tests (97 lines)
- ✅ Day 8: Learning Agent (65 lines) + E2E tests (76 lines)
- 📊 **Final Metrics**: 2,806 lines (896 production + 1,910 test)
- 📊 **All 6 Agents**: Auditor, Optimizer, Citation Tracker, Researcher, Reporter, Learning

**Sprint 3 Deliverables** ✅ (COMPLETE - 100%):
- ✅ Day 9: Workflow Orchestration (951 lines)
  - ✅ Campaign Workflow (335 lines) - /aeo-campaign decomposition
  - ✅ Competitive Workflow (326 lines) - /aeo-compete analysis
  - ✅ Monitoring Workflow (290 lines) - /aeo-monitor tracking
  - ✅ Workflow tests (475 lines: 320 unit + 155 integration, ~23 methods)
- ✅ Day 10: CLI Interface (768 lines)
  - ✅ Main CLI entry (65 lines) - Click framework, version, options
  - ✅ Campaign command (228 lines) - Complete AEO campaign workflow
  - ✅ Compete command (238 lines) - Competitive analysis
  - ✅ Monitor command (237 lines) - Citation monitoring
  - ✅ CLI tests (122 lines, ~12 test methods)
- ✅ Day 11: REST API (694 lines)
  - ✅ API models (191 lines) - Pydantic schemas with validation
  - ✅ API main (107 lines) - FastAPI server with CORS
  - ✅ Campaign routes (283 lines) - Campaign, competitive, monitoring endpoints
  - ✅ Status routes (113 lines) - Status tracking and management
  - ✅ API tests (206 lines) - Comprehensive endpoint testing
- ✅ Day 11.5: API Documentation + Validation (949 lines)
  - ✅ Enhanced OpenAPI documentation with detailed descriptions
  - ✅ Request/response examples for all models
  - ✅ ERROR_CODES.md (334 lines) - Complete error documentation
  - ✅ End-to-end validation tests (427 lines) - All 3 workflows validated
- 📊 **Sprint 3 Metrics (Final)**: 4,165 lines (3,058 production + 1,107 test)
- 📊 **Velocity**: 181% efficiency (significantly ahead of estimates)

**Sprint 3 Implementation Files**:

**Day 9** - Workflow Orchestration ✅ COMPLETE:
- ✅ `src/workflows/campaign_workflow.py` - Campaign workflow (335 lines)
- ✅ `src/workflows/competitive_workflow.py` - Competitive workflow (326 lines)
- ✅ `src/workflows/monitoring_workflow.py` - Monitoring workflow (290 lines)
- ✅ `tests/unit/test_workflows.py` - Workflow unit tests (320 lines)
- ✅ `tests/integration/test_workflow_orchestration.py` - Integration tests (155 lines)

**Day 10** - CLI Interface (Click) ✅ COMPLETE:
- ✅ `src/cli/main.py` - CLI entry point (65 lines)
- ✅ `src/cli/commands/campaign.py` - /aeo-campaign command (228 lines)
- ✅ `src/cli/commands/compete.py` - /aeo-compete command (238 lines)
- ✅ `src/cli/commands/monitor.py` - /aeo-monitor command (237 lines)
- ✅ `tests/unit/test_cli.py` - CLI tests (122 lines)

**Day 11** - REST API (FastAPI) ✅ COMPLETE:
- ✅ `src/api/models.py` - Pydantic schemas (191 lines)
- ✅ `src/api/main.py` - FastAPI server (107 lines)
- ✅ `src/api/routes/campaigns.py` - Campaign endpoints (283 lines)
- ✅ `src/api/routes/status.py` - Status endpoints (113 lines)
- ✅ `tests/unit/test_api.py` - API tests (206 lines)

**Day 11.5** - API Documentation + Validation ✅ COMPLETE:
- ✅ Enhanced OpenAPI documentation (main.py + models.py updates)
- ✅ `src/api/ERROR_CODES.md` - Complete error documentation (334 lines)
- ✅ `tests/integration/test_workflow_validation.py` - E2E validation (427 lines)
- ✅ `documentation/delivery/sprint-3-retrospective.md` - Sprint retrospective

**Sprint 4 Deliverables** 🚧 (IN PROGRESS - 12.5%):
- ✅ Day 12: E2E Testing (1,437 lines)
  - ✅ Campaign workflow E2E tests (445 lines, 16 test methods)
  - ✅ Competitive analysis E2E tests (421 lines, 20 test methods)
  - ✅ Monitoring workflow E2E tests (489 lines, 25 test methods)
  - ✅ Total: ~65 test methods covering all 3 workflows
- 📋 Day 13: Error Handling + Chaos Testing
- 📋 Day 14: Documentation
- 📋 Day 15: Code Quality + Performance
- 📋 Day 15.5: Final Testing + Release
- 📊 **Sprint 4 Metrics (Day 12)**: 1,437 test lines (~65 test methods)

**Sprint 4 Implementation Files**:

**Day 12** - E2E Testing ✅ COMPLETE:
- ✅ `tests/e2e/test_full_campaign.py` - Campaign E2E tests (445 lines)
  - TestCampaignWorkflowMinimalMode (3 tests)
  - TestCampaignWorkflowBalancedMode (3 tests)
  - TestCampaignWorkflowComprehensiveMode (3 tests)
  - TestCampaignWorkflowErrorHandling (3 tests)
  - TestCampaignWorkflowDataPersistence (2 tests)
  - TestCampaignWorkflowIntegration (2 tests)
- ✅ `tests/e2e/test_competitive_analysis.py` - Competitive E2E tests (421 lines)
  - TestCompetitiveAnalysisBasic (3 tests)
  - TestCompetitiveAnalysisMultipleCompetitors (2 tests)
  - TestCompetitiveAnalysisRegions (3 tests)
  - TestCompetitiveAnalysisCitationTracking (2 tests)
  - TestCompetitiveAnalysisErrorHandling (4 tests)
  - TestCompetitiveAnalysisResults (2 tests)
  - TestCompetitiveAnalysisIntegration (2 tests)
  - TestCompetitiveAnalysisAgentCoordination (2 tests)
- ✅ `tests/e2e/test_monitoring.py` - Monitoring E2E tests (489 lines)
  - TestMonitoringWorkflowBasic (3 tests)
  - TestMonitoringWorkflowDurations (4 tests)
  - TestMonitoringWorkflowQueries (3 tests)
  - TestMonitoringWorkflowAlerts (2 tests)
  - TestMonitoringWorkflowReports (3 tests)
  - TestMonitoringWorkflowErrorHandling (4 tests)
  - TestMonitoringWorkflowResults (2 tests)
  - TestMonitoringWorkflowIntegration (2 tests)
  - TestMonitoringWorkflowAgentCoordination (2 tests)
- ✅ `tests/e2e/__init__.py` - E2E test module init (5 lines)

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
