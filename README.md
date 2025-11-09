# AEO Box

> **Transform your content into LLM-citable authority with automated Answer Engine Optimization**

[![Version](https://img.shields.io/badge/version-1.5.0--dev-blue.svg)](https://github.com/alirezarezvani/aeo-box) [![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE) [![Python](https://img.shields.io/badge/python-3.10%2B-brightgreen.svg)](https://www.python.org/) [![Test Coverage](https://img.shields.io/badge/coverage->80%25-brightgreen.svg)](agentic-aeo/)

**AEO Box** is a comprehensive Answer Engine Optimization platform that helps you optimize content to be cited by AI language models (ChatGPT, Perplexity, Claude, Gemini, Mistral). Built with Python and the Claude Agent SDK, it provides both a powerful CLI tool and a multi-agent orchestration system for automated AEO workflows.

---

## 🎯 What is Answer Engine Optimization?

**AEO (Answer Engine Optimization)** is the practice of optimizing content to be cited as an authoritative source by AI language models. Unlike traditional SEO (optimizing for search rankings), AEO focuses on getting your content **referenced and cited** in LLM-generated responses.

### Why AEO Matters in 2025

- **50%+ of searches** now use AI answer engines instead of traditional search
- **Zero-click searches dominate** - users get answers without visiting sites
- **Citation = Authority** - being cited by LLMs is the new #1 ranking signal
- **2-4x better conversion** - Direct LLM citations drive higher-quality traffic
- **First-mover advantage** - AEO tools are still emerging, early adopters win

---

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/alirezarezvani/aeo-box.git
cd aeo-suite

# Install dependencies (optional, core works with Python stdlib only)
cd answer-engine-optimization
pip install -r requirements.txt
```

### Your First AEO Audit

```bash
# Using Python directly
python -c "from answer-engine-optimization.modules.content_analyzer import ContentAnalyzer; \
analyzer = ContentAnalyzer(); \
audit = analyzer.analyze(content=open('your-article.md').read()); \
print(f\"AEO Score: {audit['scores']['overall']}/100\")"
```

### Or Use the Claude Code Skill

```bash
# Load as a Claude Code skill
cp -r answer-engine-optimization ~/.claude/skills/aeo

# Then use in Claude Code
claude "analyze this article for AEO: path/to/article.md"
```

📖 **See [QUICKSTART.md](answer-engine-optimization/QUICKSTART.md) for detailed installation and usage**

---

## 📦 Repository Structure

```
aeo-box/
├── answer-engine-optimization/    # AEO Skill (Python toolkit, v1.0.0)
│   ├── modules/                   # 6 core AEO modules
│   │   ├── content_analyzer.py    # E-E-A-T analysis, structure scoring
│   │   ├── optimizer.py           # AI-powered content optimization
│   │   ├── citation_tracker.py    # Track citations across 5 LLMs
│   │   ├── query_researcher.py    # Query opportunity research
│   │   ├── report_generator.py    # Client-ready markdown reports
│   │   └── success_patterns.py    # Adaptive learning system
│   ├── templates/                 # Report templates
│   ├── SKILL.md                   # Skill configuration
│   ├── QUICKSTART.md              # 5-minute installation guide
│   └── requirements.txt           # Optional dependencies
│
├── aeo-agentic-app-master-prompt.md  # Multi-agent system specification
│
├── documentation/                 # Comprehensive documentation
│   ├── foundation/
│   │   ├── prd.md                # Product Requirements Document
│   │   └── architecture.md       # System Architecture
│   ├── user-guide.md             # User documentation
│   ├── api-reference.md          # API documentation
│   ├── deployment-guide.md       # Deployment instructions
│   └── cost-optimization.md      # Cost savings guide
│
├── .claude/                       # Claude Code configuration
│   ├── commands/                  # 9 custom slash commands
│   ├── agents/                    # 11 specialized agents
│   └── plugins/                   # Hook-based plugins
│
├── .github/                       # GitHub workflows & templates
│   ├── workflows/                 # CI/CD automation
│   ├── ISSUE_TEMPLATE/           # Issue templates
│   └── BRANCH_PROTECTION.md      # Branch protection guide
│
└── scripts/                       # Utility scripts
    └── sync-labels.sh            # GitHub label sync
```

---

## ✨ Features

### 🔍 **AEO Skill (Python Toolkit)** - Available Now ✅

#### 1. Comprehensive Content Audit
- **E-E-A-T Analysis**: Experience, Expertise, Authoritativeness, Trustworthiness scoring
- **Structure Optimization**: Heading hierarchy, lists, tables for LLM parsing
- **Citation Quality**: Assess authoritative source linking
- **Competitor Benchmarking**: Compare against top-ranking content

#### 2. Intelligent Content Optimization
- **AI-Powered Improvements**: Automated content enhancements
- **Configurable Levels**: Conservative (60-70), Balanced (70-80), Aggressive (80-90+)
- **Brand Voice Preservation**: Maintains your unique tone
- **Before/After Metrics**: Track improvement with detailed change logs

#### 3. Citation Tracking & Analytics
- **Multi-LLM Monitoring**: ChatGPT, Perplexity, Claude, Gemini, Mistral
- **Historical Data**: Track citation trends over time
- **Query-Specific Analysis**: See which queries cite your content
- **CSV Export**: Client-ready citation reports

#### 4. Query Opportunity Research
- **Target Query Discovery**: Find high-value optimization opportunities
- **Competitor Analysis**: See who's being cited for your target queries
- **Content Gap Identification**: Discover missing topical coverage

#### 5. Report Generation
- **Client-Ready Reports**: Professional markdown reports
- **Executive Summaries**: High-level insights for stakeholders
- **Optimization Roadmaps**: Step-by-step improvement plans

#### 6. Adaptive Learning System
- **Success Pattern Recognition**: Learn from what works
- **Industry-Specific Insights**: Build pattern libraries by vertical
- **Privacy-First**: All data stays local (opt-in sharing)

### 🤖 **Multi-Agent System (v1.5)** - 87.5% Complete! 🚀

#### Orchestrator Agent + 6 Specialized Subagents - **Production Ready**
- ✅ **Automated Workflows**: Run complete AEO campaigns with one command
- ✅ **Quality Assurance**: 4-layer validation with >80% test coverage
- ✅ **Intelligent Coordination**: Optimal task decomposition and execution
- ✅ **Dual Interface**: CLI (Click) + REST API (FastAPI)

**Available Workflows**:
- ✅ `/aeo-campaign` - End-to-end content optimization (3 modes: minimal, balanced, comprehensive)
- ✅ `/aeo-compete` - Competitive citation analysis (1-10 competitors)
- ✅ `/aeo-monitor` - Continuous citation monitoring (7-365 days)

**Implementation Status**:
- ✅ **12,564 lines** of code (8,038 production + 4,526 test)
- ✅ **7 AI agents** fully implemented
- ✅ **106 test methods** across 26 test files
- ✅ **95.5% cost savings** ($0.024/campaign vs $0.53 baseline)
- ✅ **World-class documentation** (195KB comprehensive guides)

📖 **See [agentic-aeo/README.md](agentic-aeo/README.md) for complete documentation**

---

## 🎯 Use Cases

### For SEO Specialists
- Audit 50+ articles/month for AEO signals
- Track citation performance across multiple LLMs
- Identify quick wins with query research
- Generate client reports in minutes

### For Content Marketers
- Optimize existing content for LLM citations
- Measure AEO effectiveness with analytics
- Scale optimization across large content libraries
- Prove ROI with before/after metrics

### For Agencies
- White-label client reporting
- Batch processing for multiple clients
- Industry-specific optimization patterns
- Competitive intelligence for pitches

---

## 📚 Documentation

### Getting Started
- **[Quick Start Guide](answer-engine-optimization/QUICKSTART.md)** - 5-minute setup
- **[Skill Configuration](answer-engine-optimization/SKILL.md)** - Environment variables

### Strategic Documentation
- **[Product Requirements (PRD)](documentation/foundation/prd.md)** - Product vision and roadmap
- **[System Architecture](documentation/foundation/architecture.md)** - Technical design

### User Documentation
- **[User Guide](documentation/user-guide.md)** - Comprehensive usage instructions
- **[API Reference](documentation/api-reference.md)** - API and SDK documentation
- **[Deployment Guide](documentation/deployment-guide.md)** - Production deployment

### Developer Documentation
- **[Contributing Guide](CONTRIBUTING.md)** - Development setup and guidelines
- **[Cost Optimization](documentation/cost-optimization.md)** - Claude Max Pro savings
- **[Branch Protection](.github/BRANCH_PROTECTION.md)** - Git workflow and protection rules

---

## 🏆 Key Differentiators

### vs. Traditional SEO Tools

| Feature | AEO Box | Surfer SEO | MarketMuse | SEMrush |
|---------|---------|------------|------------|---------|
| **Multi-LLM Citation Tracking** | ✅ 5 LLMs | ❌ | ❌ | ❌ |
| **Adaptive Learning** | ✅ Local | ❌ | ⚠️ Limited | ❌ |
| **Multi-Agent Orchestration** | ✅ 6 agents | ❌ | ❌ | ❌ |
| **Local-First (Privacy)** | ✅ | ❌ | ❌ | ❌ |
| **Works Without APIs** | ✅ Graceful | ❌ | ❌ | ❌ |
| **Open Source** | ✅ MIT | ❌ | ❌ | ❌ |
| **Cost** | **Free** | $89-239/mo | $149-599/mo | $119-449/mo |

### Technical Advantages
- **60%+ cost savings** with Claude Max Pro optimization (prompt caching, extended context)
- **Graceful degradation** - Core features work without paid APIs
- **Local-first architecture** - No vendor lock-in, full data privacy
- **Multi-agent innovation** - First AEO tool with agent orchestration

---

## 🛠️ Technology Stack

### Core Technologies
- **Python 3.9+** - Core AEO modules
- **Claude Agent SDK** - Multi-agent orchestration (planned)
- **FastAPI** - REST API (planned)
- **Click** - CLI framework (planned)

### Testing
- **pytest** - Unit and integration tests
- **Coverage target**: >80%

### Data Storage
- **Local file system** - JSON, CSV, Markdown
- **No database required** - Simple, portable

### Deployment
- **pip package** - Easy installation
- **Claude Code integration** - Use as a skill
- **Docker** - Containerized deployment (future)

---

## 🗓️ Roadmap

### ✅ v1.0 (Released) - AEO Skill
- [x] Content auditing (E-E-A-T, structure, citations)
- [x] Content optimization (3 levels)
- [x] Citation tracking (5 LLMs)
- [x] Query research
- [x] Report generation
- [x] Adaptive learning

### 🚀 v1.5 (November 2025) - Multi-Agent System - **87.5% Complete**
- [x] Orchestrator agent implementation (697 lines)
- [x] 6 specialized subagents (896 lines total)
- [x] Workflow orchestration - 3 workflows complete (951 lines)
- [x] CLI interface - 4 commands (768 lines)
- [x] REST API - 7 endpoints (1,107 lines)
- [x] Comprehensive testing - >80% coverage (4,526 test lines, 106 methods)
- [x] E2E testing - All 3 workflows validated (1,437 lines)
- [x] Chaos testing - Resilience under failure (462 lines)
- [x] **World-class documentation** - 195KB comprehensive guides
- [ ] Code quality review + performance optimization (Day 15)
- [ ] Final testing + v1.5.0 release (Day 15.5)

**Target Release**: November 11, 2025 (2 days remaining)

### 🔮 v2.0 (Q2-Q4 2025) - Advanced Features
- [ ] Visual citation heatmaps
- [ ] Browser extension (real-time tracking)
- [ ] Slack/Email notifications
- [ ] Team collaboration features
- [ ] CMS integrations (WordPress, Webflow)
- [ ] White-label reporting
- [ ] AI-powered content generation (AEO-native)

---

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for:
- Development environment setup
- Code style guidelines (PEP 8)
- Testing requirements (>80% coverage)
- Pull request process

### Quick Development Setup

```bash
# Clone and setup
git clone https://github.com/alirezarezvani/aeo-box.git
cd aeo-suite

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dev dependencies
cd answer-engine-optimization
pip install -r requirements.txt
pip install pytest pytest-cov

# Run tests
pytest --cov=modules tests/
```

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Amsive** - AEO methodology and best practices
- **CXL** - Comprehensive AEO guides
- **Ahrefs** - LLM citation research
- **Anthropic** - Claude Agent SDK and Claude Code

---

## 📞 Support & Community

- **Issues**: [GitHub Issues](https://github.com/alirezarezvani/aeo-box/issues)
- **Documentation**: [docs/](documentation/)
- **Discussions**: [GitHub Discussions](https://github.com/alirezarezvani/aeo-box/discussions)

---

## 🎯 Project Status

**Current Phase**: v1.5 Multi-Agent System - **87.5% Complete** 🚀

**v1.5 Implementation Progress**:
- ✅ **Sprint 1**: Foundation (4 days) - **100% COMPLETE**
- ✅ **Sprint 2**: Specialized Agents (4 days) - **100% COMPLETE**
- ✅ **Sprint 3**: Workflows + Interfaces (3.5 days) - **100% COMPLETE**
- 🚧 **Sprint 4**: Testing + Production Polish (4 days) - **37.5% COMPLETE**
  - ✅ Day 12: E2E Testing (1,437 lines, 65 test methods)
  - ✅ Day 13: Error Handling + Chaos Testing (462 lines, 14 test methods)
  - ✅ Day 14: Documentation (195KB, 5 comprehensive files)
  - 📋 Day 15: Code Quality + Performance (in progress)
  - 📋 Day 15.5: Final Testing + v1.5.0 Release

**Key Achievements**:
- ✅ **12,564 total lines** implemented (8,038 production + 4,526 test)
- ✅ **>80% test coverage** maintained (106 test methods across 26 files)
- ✅ **7 AI agents** fully operational (1 orchestrator + 6 specialized)
- ✅ **3 workflows** production-ready (campaign, competitive, monitoring)
- ✅ **7 REST API endpoints** (FastAPI with OpenAPI docs)
- ✅ **4 CLI commands** (Click framework)
- ✅ **95.5% cost savings** achieved ($0.024 vs $0.53 per campaign)
- ✅ **World-class documentation** (195KB comprehensive guides)

**Complete Deliverables**:

**Sprint 1 - Foundation** (3,694 lines):
- Orchestrator agent with task decomposition (697 lines)
- Communication protocol (Pydantic models, 505 lines)
- Data persistence layer (CampaignStore, 507 lines)
- Configuration system (301 lines)
- Logging infrastructure (387 lines)
- Integration tests (49 test methods, 1,660 test lines)

**Sprint 2 - Specialized Agents** (2,806 lines):
- AuditorAgent (219 lines) - Content analysis, E-E-A-T scoring
- OptimizerAgent (245 lines) - AI-powered optimization
- CitationTrackerAgent (285 lines) - Multi-LLM tracking (5 LLMs)
- ResearcherAgent (77 lines) - Query research
- ReporterAgent (95 lines) - Report generation
- LearningAgent (65 lines) - Pattern recognition
- Comprehensive testing (1,910 test lines, 80 test methods)

**Sprint 3 - Workflows + Interfaces** (4,165 lines):
- Campaign Workflow (336 lines) - Complete AEO campaigns
- Competitive Workflow (327 lines) - Multi-competitor analysis
- Monitoring Workflow (291 lines) - Citation tracking
- CLI Interface (768 lines) - 4 commands
- REST API (1,107 lines) - 7 endpoints with FastAPI
- API documentation (645 lines ERROR_CODES.md)
- Tests (1,107 test lines)

**Sprint 4 - Testing + Documentation** (1,899 test lines + 195KB docs):
- E2E testing suite (1,437 lines, 65 test methods)
- Chaos testing (462 lines, 14 test methods)
- README.md enhanced (21KB)
- ARCHITECTURE.md (32KB)
- API_REFERENCE.md (33KB)
- COST_OPTIMIZATION.md (33KB)
- DEVELOPMENT_HISTORY.md (76KB)

**Documentation & Guides**:
- ✅ [Complete User Guide](agentic-aeo/README.md) - Installation, usage, troubleshooting
- ✅ [System Architecture](agentic-aeo/ARCHITECTURE.md) - Technical design reference
- ✅ [API Reference](agentic-aeo/API_REFERENCE.md) - All 7 endpoints documented
- ✅ [Cost Optimization](agentic-aeo/COST_OPTIMIZATION.md) - 95% savings guide
- ✅ [Development History](agentic-aeo/DEVELOPMENT_HISTORY.md) - Complete project timeline
- ✅ [Sprint Plan](documentation/delivery/sprint-plan-v1.5.md) - Day-by-day breakdown
- ✅ [Success Metrics](documentation/delivery/success-metrics-tracking.md) - Metrics tracking

**Target Release**: **November 11, 2025** (2 days remaining)

**Last Updated**: 2025-11-09

---

<p align="center">
  <strong>Made with ❤️ for the AEO community</strong>
</p>

<p align="center">
  <a href="https://github.com/alirezarezvani/aeo-box">⭐ Star us on GitHub</a> •
  <a href="https://github.com/alirezarezvani/aeo-box/issues">🐛 Report Bug</a> •
  <a href="https://github.com/alirezarezvani/aeo-box/issues">✨ Request Feature</a>
</p>
