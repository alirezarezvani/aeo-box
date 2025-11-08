# Answer Engine Optimization (AEO) Skill

> **Professional Answer Engine Optimization for Marketers & SEO Specialists**
>
> Get your content cited by ChatGPT, Perplexity, Claude, Gemini, and other leading LLMs.

---

## What This Skill Does

This comprehensive AEO skill helps marketers and SEO specialists optimize content for AI answer engines. Unlike traditional SEO (optimizing for search rankings), AEO focuses on getting your content **cited as the authoritative source** in LLM-generated responses.

### Core Capabilities

1. **Content Audit & Gap Analysis**
   - Analyze existing content for AEO readiness
   - Identify E-E-A-T (Experience, Expertise, Authoritativeness, Trustworthiness) gaps
   - Detect missing structured data, citations, and authority signals

2. **Query Research & Targeting**
   - Research what queries LLMs cite sources for
   - Analyze competitor citation rates
   - Identify high-value query targets for your niche

3. **Content Optimization**
   - Generate AEO-optimized content variations
   - Add proper citations, facts, and authority signals
   - Optimize structure for LLM parsing (headings, lists, tables)

4. **Citation Tracking & Monitoring**
   - Monitor when/where your content gets cited
   - Track citation performance across multiple LLMs
   - Measure AEO ROI and identify trends

5. **Adaptive Learning**
   - Learn from successful optimizations
   - Build industry-specific success pattern library
   - Improve recommendations over time

---

## Controllable Variables

Configure these variables for each project/client:

```yaml
# === TARGET CONFIGURATION ===
TARGET_INDUSTRY: "SaaS"
  # Options: SaaS, Healthcare, Finance, E-commerce, Legal, Technology, Marketing, Education, Real Estate, Travel
  # Affects: Authority signal requirements, fact-checking rigor, citation style

GEOGRAPHIC_REGION: "US"
  # Examples: US, UK, Canada, Australia, Germany, France, Global
  # Affects: Language optimization, regional authority sources, local LLM preferences

BRAND_VOICE: "conversational"
  # Options: formal, conversational, technical, academic, friendly
  # Affects: Content optimization tone and style recommendations

# === COMPETITOR TRACKING ===
COMPETITOR_URLS:
  - "https://competitor1.com"
  - "https://competitor2.com"
  - "https://competitor3.com"
# Monitor competitor citation rates and strategies

# === LLM TARGETING ===
TARGET_LLMS:
  - "ChatGPT"      # OpenAI search integration
  - "Perplexity"   # Citation-first model
  - "Claude"       # Strong in technical/research
  - "Gemini"       # Google search integration
  - "Mistral"      # European focus
# Prioritize which LLMs to optimize for and track

# === API CONFIGURATION (Optional - graceful degradation if not provided) ===
API_KEYS:
  AHREFS_API_KEY: ""           # For backlink/authority analysis
  SEMRUSH_API_KEY: ""          # For keyword/competitor data
  OPENAI_API_KEY: ""           # For content analysis
  ANTHROPIC_API_KEY: ""        # For Claude-specific optimization
# Leave empty to use self-contained analysis (reduced features but functional)

# === DATA PERSISTENCE ===
PROJECT_NAME: "client-website"
  # Creates .aeo-data/projects/{PROJECT_NAME}/ for tracking data

DATA_RETENTION_DAYS: 90
  # How long to keep historical citation data (0 = forever)

# === OPTIMIZATION PREFERENCES ===
OPTIMIZATION_LEVEL: "balanced"
  # Options: conservative, balanced, aggressive
  # Conservative: Minimal changes, preserve brand voice
  # Balanced: Moderate optimization, good for most cases
  # Aggressive: Maximum AEO focus, may alter tone significantly

INCLUDE_CITATIONS: true
  # Whether optimized content should include source citations

INCLUDE_STRUCTURED_DATA: true
  # Add schema.org markup suggestions for AEO

# === LEARNING CONFIGURATION ===
ENABLE_ADAPTIVE_LEARNING: true
  # Track successful patterns and improve recommendations

SHARE_ANONYMIZED_PATTERNS: false
  # Share successful patterns to improve skill for all users (opt-in)
```

---

## Commands

### 1. `aeo-audit <url|file>`

Perform comprehensive AEO audit on content.

**Usage:**
```bash
# Audit live URL
aeo-audit https://yourblog.com/article

# Audit local file
aeo-audit content/blog-post.md

# Audit with custom output
aeo-audit https://example.com --output reports/audit.md
```

**What It Analyzes:**
- ✅ E-E-A-T signals (author credentials, citations, expertise)
- ✅ Content structure (headings, lists, tables, readability)
- ✅ Factual accuracy and citation quality
- ✅ Keyword targeting for LLM queries
- ✅ Competitor comparison
- ✅ Technical SEO (schema, meta, performance)

**Output:**
- Markdown audit report with scores (0-100)
- Prioritized action items (Critical, High, Medium, Low)
- Competitor benchmark comparison
- Estimated optimization effort (hours)

---

### 2. `aeo-research <topic>`

Research query opportunities and competitor strategies.

**Usage:**
```bash
# Research topic
aeo-research "project management software"

# Research with geographic focus
aeo-research "health insurance" --region US

# Research competitor citations
aeo-research "email marketing" --competitors
```

**What It Researches:**
- 🔍 Query variations that trigger LLM citations
- 🔍 Current top-cited sources for topic
- 🔍 Competitor citation frequency and strategies
- 🔍 Content gaps and opportunities
- 🔍 Trending queries in your niche

**Output:**
- Target query list (prioritized by citation potential)
- Competitor citation analysis
- Content gap opportunities
- Recommended content topics/angles

---

### 3. `aeo-optimize <url|file>`

Generate AEO-optimized version of content.

**Usage:**
```bash
# Optimize content
aeo-optimize content/article.md

# Optimize with specific focus
aeo-optimize https://blog.com/post --focus citations

# Batch optimize directory
aeo-optimize content/*.md --batch
```

**Optimization Strategies:**
- 📝 Add authoritative citations and sources
- 📝 Restructure for LLM parsing (clear sections, lists, tables)
- 📝 Enhance E-E-A-T signals (author bios, credentials, experience)
- 📝 Add factual data points and statistics
- 📝 Optimize for target query variations
- 📝 Include schema.org structured data suggestions

**Output:**
- Optimized content version (markdown)
- Side-by-side comparison (before/after)
- Change summary with rationale
- Estimated citation improvement score

---

### 4. `aeo-track <url>`

Monitor citation performance across target LLMs.

**Usage:**
```bash
# Start tracking URL
aeo-track https://yourblog.com/article

# Track with custom queries
aeo-track https://example.com --queries "query1,query2,query3"

# Generate tracking report
aeo-track https://example.com --report
```

**What It Tracks:**
- 📊 Citation frequency per LLM (daily checks)
- 📊 Citation context (when/how content is referenced)
- 📊 Query variations that trigger citations
- 📊 Citation rank (1st, 2nd, 3rd source, etc.)
- 📊 Competitor citation comparison
- 📊 Trend analysis (improving/declining)

**Output:**
- CSV tracking data (.aeo-data/citation_history.csv)
- Trend dashboard (markdown with charts)
- Alert notifications (new citations, ranking changes)

---

### 5. `aeo-report <project>`

Generate strategic AEO report for client/stakeholder.

**Usage:**
```bash
# Generate comprehensive report
aeo-report client-website

# Generate executive summary only
aeo-report client-website --executive

# Export to PDF
aeo-report client-website --format pdf
```

**Report Sections:**
1. **Executive Summary**
   - Current AEO performance (citation count, rankings)
   - Key wins and improvements
   - ROI analysis (traffic from LLM citations)

2. **Audit Findings**
   - Content inventory AEO scores
   - Gap analysis
   - Competitor comparison

3. **Optimization Roadmap**
   - Prioritized action items
   - Effort estimates
   - Expected impact

4. **Citation Performance**
   - Historical trends
   - LLM-specific performance
   - Query analysis

5. **Success Patterns**
   - What's working (adaptive learning insights)
   - Recommended next steps

**Output:**
- Strategic report (markdown or PDF)
- Data appendices (CSV exports)
- Presentation-ready visualizations

---

### 6. `aeo-configure`

Set up or update project configuration.

**Usage:**
```bash
# Interactive configuration
aeo-configure

# Update specific variable
aeo-configure --set TARGET_INDUSTRY="Healthcare"

# View current configuration
aeo-configure --show
```

**Configures:**
- Project variables (industry, region, voice)
- API keys (optional)
- Competitor URLs
- Target LLMs
- Optimization preferences

---

## Installation

### Prerequisites

- Claude Code (desktop or CLI)
- Python 3.9+ (for advanced analysis modules)
- Optional: API keys for Ahrefs, SEMrush, etc.

### Quick Install

1. **Copy skill to Claude skills directory:**

```bash
# Project-level (current project only)
cp -r answer-engine-optimization .claude/skills/

# User-level (all projects)
cp -r answer-engine-optimization ~/.claude/skills/
```

2. **Install Python dependencies:**

```bash
cd .claude/skills/answer-engine-optimization
pip3 install -r requirements.txt
```

3. **Configure your first project:**

Edit `SKILL.md` controllable variables or run:
```bash
aeo-configure
```

4. **Test the skill:**

```bash
# Run your first audit
aeo-audit https://yourblog.com/sample-post
```

---

## Adaptive Learning System

This skill learns from your successes and improves over time:

### How It Works

1. **Track Optimizations**: When you run `aeo-optimize`, changes are logged
2. **Monitor Results**: `aeo-track` monitors citation performance
3. **Identify Patterns**: Successful optimizations build pattern library
4. **Improve Recommendations**: Future optimizations use learned patterns

### Success Pattern Library

Located in `.aeo-data/success_patterns.json`:

```json
{
  "industry": "SaaS",
  "successful_patterns": [
    {
      "pattern_type": "citation_addition",
      "description": "Adding authoritative industry reports",
      "success_rate": 0.87,
      "avg_citation_increase": 3.2,
      "sample_size": 42
    },
    {
      "pattern_type": "structure_optimization",
      "description": "Converting paragraphs to bulleted lists",
      "success_rate": 0.74,
      "avg_citation_increase": 1.8,
      "sample_size": 28
    }
  ]
}
```

### Privacy

- **Local storage only**: All learning data stays on your machine
- **Opt-in sharing**: `SHARE_ANONYMIZED_PATTERNS` (default: false)
- **No external tracking**: Skill never sends your content/data externally

---

## API Integration Guide

### Graceful Degradation

The skill works **without any API keys** using Claude's built-in capabilities:

| Feature | With APIs | Without APIs |
|---------|-----------|--------------|
| Content Audit | Full backlink/authority analysis | E-E-A-T analysis, structure check |
| Query Research | Real competitor citation data | LLM-simulated research |
| Optimization | Enhanced with SEO data | Core AEO optimizations |
| Citation Tracking | Automated daily checks | Manual query-based checks |

### Recommended APIs (Optional)

**For Professional Use:**
- **Ahrefs API** ($99/month): Backlink analysis, domain authority
- **SEMrush API** ($119.95/month): Keyword research, competitor data
- **OpenAI API** (pay-as-you-go): Content analysis, GPT-4 research

**For Basic Use:**
- **No APIs needed**: Use Claude's capabilities for core AEO work

### API Key Setup

Add to `SKILL.md` variables:
```yaml
API_KEYS:
  AHREFS_API_KEY: "your-key-here"
  SEMRUSH_API_KEY: "your-key-here"
```

Or via environment variables:
```bash
export AHREFS_API_KEY="your-key-here"
export SEMRUSH_API_KEY="your-key-here"
```

---

## Data Storage & Privacy

### Local Storage Structure

```
.aeo-data/
├── projects/
│   └── client-website/
│       ├── config.json              # Project configuration
│       ├── audit_history.csv        # Audit results over time
│       ├── optimization_log.json    # Changes made
│       └── citation_tracking.csv    # Citation performance
├── success_patterns.json            # Adaptive learning data
└── global_config.json               # Default settings
```

### Data Retention

- **Citation history**: Configurable (`DATA_RETENTION_DAYS`)
- **Success patterns**: Kept indefinitely (small size ~1MB)
- **Audit reports**: Keep last 10 per project
- **Total storage**: ~10-50MB per project

### Backup & Export

```bash
# Backup all AEO data
cp -r .aeo-data backups/aeo-backup-2025-01-07

# Export to client
aeo-report client-website --export-data client-data.zip
```

---

## Advanced Use Cases

### 1. Multi-Language AEO

```yaml
GEOGRAPHIC_REGION: "Germany"
BRAND_VOICE: "formal"
TARGET_LLMS:
  - "ChatGPT"
  - "Mistral"  # European LLM
```

Run audit in German:
```bash
aeo-audit https://example.de/artikel --lang de
```

### 2. E-commerce Product Pages

```yaml
TARGET_INDUSTRY: "E-commerce"
INCLUDE_STRUCTURED_DATA: true
OPTIMIZATION_LEVEL: "aggressive"
```

Optimize product descriptions:
```bash
aeo-optimize products/*.md --schema Product
```

### 3. Healthcare Content (High E-E-A-T)

```yaml
TARGET_INDUSTRY: "Healthcare"
OPTIMIZATION_LEVEL: "conservative"
INCLUDE_CITATIONS: true
```

Ensure medical accuracy:
```bash
aeo-audit medical-content/ --strict-citations
```

### 4. Competitor Intelligence

```yaml
COMPETITOR_URLS:
  - "https://competitor1.com"
  - "https://competitor2.com"
```

Run competitive analysis:
```bash
aeo-research "your topic" --competitors --benchmark
```

---

## Troubleshooting

### Skill Not Loading

1. Check installation path: `.claude/skills/answer-engine-optimization/`
2. Verify `SKILL.md` exists in skill folder
3. Restart Claude Code

### Python Dependencies Missing

```bash
cd .claude/skills/answer-engine-optimization
pip3 install -r requirements.txt --user
```

### API Rate Limits

Skill auto-throttles API requests:
- Ahrefs: Max 1 request/second
- SEMrush: Max 10 requests/minute

To disable API temporarily:
```yaml
API_KEYS:
  AHREFS_API_KEY: ""  # Leave empty
```

### Citation Tracking Not Working

Verify target LLMs are accessible:
```bash
# Test manually
aeo-track https://example.com --test-llms
```

If behind firewall, tracking may be limited.

---

## Roadmap & Future Features

**v1.0 (Current)**
- ✅ Content audit & optimization
- ✅ Query research
- ✅ Citation tracking
- ✅ Adaptive learning
- ✅ Multi-LLM support

**v1.1 (Planned)**
- 🔄 Visual citation heatmaps
- 🔄 Browser extension for real-time tracking
- 🔄 Slack/email notifications
- 🔄 Team collaboration features

**v2.0 (Future)**
- 🔮 AI-powered content generation (AEO-native)
- 🔮 Predictive citation modeling
- 🔮 Integration with CMS platforms (WordPress, etc.)
- 🔮 White-label reporting for agencies

---

## Support & Community

- **Issues**: Report bugs via GitHub issues
- **Questions**: Use Discussions tab
- **Updates**: Follow changelog for new features

---

## License

MIT License - Free for commercial and personal use.

---

**Built for the future of search. Optimized for AI.**

*Answer Engine Optimization Skill v1.0 - January 2025*
