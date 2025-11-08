# AEO Box User Guide

**Version**: 1.0
**Last Updated**: 2025-11-08

Welcome to the comprehensive AEO Box user guide! This document will help you master Answer Engine Optimization and get your content cited by AI language models.

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Core Workflows](#core-workflows)
3. [Advanced Features](#advanced-features)
4. [Best Practices](#best-practices)
5. [Troubleshooting](#troubleshooting)
6. [FAQ](#faq)

---

## Getting Started

### Installation

#### Option 1: Use as Claude Code Skill (Recommended)

```bash
# Copy to Claude Code skills directory
cp -r answer-engine-optimization ~/.claude/skills/aeo

# Restart Claude Code or reload skills
claude --reload-skills

# Use in Claude Code
claude "analyze this article for AEO: path/to/article.md"
```

#### Option 2: Standalone Python Usage

```bash
# Clone repository
git clone https://github.com/alirezarezvani/aeo-box.git
cd aeo-suite/answer-engine-optimization

# Install optional dependencies (for enhanced features)
pip install -r requirements.txt

# Run directly with Python
python -c "from modules.content_analyzer import ContentAnalyzer; \
analyzer = ContentAnalyzer(); \
audit = analyzer.analyze(content=open('your-article.md').read()); \
print(f'AEO Score: {audit[\"scores\"][\"overall\"]}/100')"
```

#### Option 3: Install as Python Package (Future)

```bash
# Will be available via PyPI
pip install aeo-box
```

---

### Configuration

#### Environment Variables

Create a `.env` file in your project directory:

```bash
# Optional: Anthropic API key for enhanced analysis
ANTHROPIC_API_KEY=your_api_key_here

# Optional: External API keys (Ahrefs, SEMrush)
AHREFS_API_KEY=your_key_here
SEMRUSH_API_KEY=your_key_here

# Data retention (days)
DATA_RETENTION_DAYS=90

# Project name (for organizing data)
PROJECT_NAME=my-website
```

#### Configuration File

See `answer-engine-optimization/SKILL.md` for detailed configuration options.

---

### Your First Audit

**Quick Start** (5 minutes):

```python
from answer_engine_optimization.modules.content_analyzer import ContentAnalyzer

# Create analyzer
analyzer = ContentAnalyzer()

# Analyze your content
content = open("your-article.md").read()
audit = analyzer.analyze(content=content, url="https://yoursite.com/article")

# View results
print(f"Overall AEO Score: {audit['scores']['overall']}/100")
print(f"E-E-A-T Score: {audit['scores']['eeat']}/100")
print(f"Structure Score: {audit['scores']['structure']}/100")
print(f"Citations Score: {audit['scores']['citations']}/100")

# Top recommendations
for rec in audit['recommendations'][:3]:
    print(f"- {rec['description']} (Priority: {rec['priority']})")
```

**Expected Output**:
```
Overall AEO Score: 75/100
E-E-A-T Score: 68/100
Structure Score: 82/100
Citations Score: 70/100

Top Recommendations:
- Add H2 subheadings for better content chunking (Priority: high)
- Link to authoritative sources (.edu, .gov, research papers) (Priority: high)
- Add author credentials section (Priority: medium)
```

---

## Core Workflows

### 1. Content Auditing

**When to audit**:
- Before publishing new content
- Quarterly for existing high-value pages
- After algorithm/LLM updates
- When citations drop

#### Basic Audit

```python
from answer_engine_optimization.modules.content_analyzer import ContentAnalyzer

analyzer = ContentAnalyzer()
audit = analyzer.analyze(
    content=content,
    url="https://yoursite.com/article"
)

# Save audit report
import json
with open("audit-report.json", "w") as f:
    json.dump(audit, f, indent=2)
```

#### Competitive Audit

```python
audit = analyzer.analyze(
    content=content,
    url="https://yoursite.com/article",
    competitor_urls=[
        "https://competitor1.com/article",
        "https://competitor2.com/article"
    ]
)

# View competitive comparison
print(f"Your Score: {audit['scores']['overall']}")
print(f"Avg Competitor Score: {audit['competitor_comparison']['avg_score']}")
print(f"Your Rank: {audit['competitor_comparison']['your_rank']}")
```

#### Understanding Audit Scores

| Score Range | Meaning | Action |
|-------------|---------|--------|
| **90-100** | Excellent | Monitor and maintain |
| **75-89** | Good | Minor optimizations |
| **60-74** | Fair | Moderate improvements needed |
| **40-59** | Poor | Major overhaul required |
| **0-39** | Very Poor | Complete rewrite recommended |

**Score Components**:

1. **E-E-A-T** (0-100):
   - Experience: First-hand knowledge, case studies
   - Expertise: Author credentials, technical accuracy
   - Authoritativeness: Backlinks, citations, brand recognition
   - Trustworthiness: Transparent sources, fact-checking

2. **Structure** (0-100):
   - Heading hierarchy (H1, H2, H3)
   - Lists and tables
   - Paragraph chunking (1 idea per paragraph)
   - Readability (Flesch-Kincaid)

3. **Citations** (0-100):
   - Authoritative source linking (.edu, .gov, research papers)
   - Citation diversity (multiple sources)
   - Recency (up-to-date references)

4. **Readability** (0-100):
   - Flesch-Kincaid score
   - Sentence length
   - Word complexity

#### Interpreting Recommendations

**High Priority** (Fix immediately):
```
- Add H2 subheadings for better content chunking
  Expected impact: +5 points

- Link to 3+ authoritative sources
  Expected impact: +8 points
```

**Medium Priority** (Fix next):
```
- Add author bio with credentials
  Expected impact: +3 points

- Include data points and statistics
  Expected impact: +4 points
```

**Low Priority** (Nice to have):
```
- Add table of contents
  Expected impact: +2 points
```

---

### 2. Content Optimization

**When to optimize**:
- After audit identifies issues (score <75)
- Before major product launches
- Quarterly content refresh
- When competitors rank higher

#### Conservative Optimization

**Use when**: Preserving brand voice is critical

```python
from answer_engine_optimization.modules.optimizer import ContentOptimizer

optimizer = ContentOptimizer()
result = optimizer.optimize(
    content=content,
    level="conservative",  # Minimal changes
    preserve_sections=["Introduction", "Conclusion"]  # Don't touch these
)

print(f"Before: {result['metrics']['before_score']}")
print(f"After: {result['metrics']['after_score']}")
print(f"Improvement: +{result['metrics']['improvement']} points")

# Review changes
for change in result['change_log']:
    print(f"\nLine {change['line']}: {change['type']}")
    print(f"Before: {change['before'][:50]}...")
    print(f"After: {change['after'][:50]}...")
    print(f"Rationale: {change['rationale']}")
```

#### Balanced Optimization (Recommended)

**Use when**: Standard optimization for most content

```python
result = optimizer.optimize(
    content=content,
    level="balanced",  # Moderate improvements (default)
    focus_areas=["structure", "eeat", "citations"]  # Optional focus
)

# Save optimized content
with open("article-optimized.md", "w") as f:
    f.write(result['optimized_content'])
```

#### Aggressive Optimization

**Use when**: Maximum AEO score is priority over voice

```python
result = optimizer.optimize(
    content=content,
    level="aggressive"  # Maximum optimization
)

# Note: May significantly alter writing style
# Review changes carefully before publishing
```

#### Reviewing Optimized Content

**Best Practice**:
1. Review change log line-by-line
2. Accept changes that preserve meaning
3. Reject changes that alter key messaging
4. Manually tweak for brand voice

```python
# Example: Selective change acceptance
accepted_changes = []
for change in result['change_log']:
    if change['type'] in ['add_structure', 'add_citations']:
        accepted_changes.append(change)  # Auto-accept
    elif change['type'] == 'enhance_eeat':
        # Manual review required
        print(f"Review: {change['before']} → {change['after']}")
        if input("Accept? (y/n): ") == 'y':
            accepted_changes.append(change)
```

---

### 3. Citation Tracking

**When to track**:
- After publishing optimized content
- Daily/weekly for monitoring
- Competitive intelligence

#### Setting Up Tracking

```python
from answer_engine_optimization.modules.citation_tracker import CitationTracker

tracker = CitationTracker()

# Define target queries
queries = [
    "What is Answer Engine Optimization?",
    "How to optimize content for ChatGPT?",
    "AEO best practices 2025"
]

# Track citations
result = tracker.track(
    url="https://yoursite.com/article",
    queries=queries,
    llms=["chatgpt", "perplexity", "claude", "gemini", "mistral"]
)

print(f"Citation Rate: {result['summary']['citation_rate']:.1%}")
print(f"Total Citations: {result['summary']['total_citations']}/{result['summary']['total_queries']}")
```

#### Reading Citation Reports

**Example Output**:
```json
{
  "url": "https://yoursite.com/article",
  "timestamp": "2025-01-07T10:30:00Z",
  "citations": [
    {
      "llm": "chatgpt",
      "query": "What is AEO?",
      "cited": true,
      "position": 2,  // 2nd source mentioned
      "context": "According to [source], AEO is the practice of optimizing content to be cited by AI language models..."
    },
    {
      "llm": "perplexity",
      "query": "What is AEO?",
      "cited": false,
      "position": null,
      "context": ""
    }
  ],
  "summary": {
    "total_queries": 3,
    "total_citations": 7,  // Out of 15 total checks (3 queries × 5 LLMs)
    "citation_rate": 0.467  // 46.7%
  }
}
```

#### Trend Analysis

```python
# Load historical data
import pandas as pd

df = pd.read_csv(".aeo-data/projects/my-website/citation_tracking.csv")

# Group by date
daily_citations = df.groupby(df['timestamp'].str[:10])['cited'].mean()

print("Citation Rate Trend:")
for date, rate in daily_citations.items():
    print(f"{date}: {rate:.1%}")
```

**Expected Output**:
```
Citation Rate Trend:
2025-01-01: 20.0%
2025-01-02: 33.3%
2025-01-03: 46.7%
2025-01-04: 53.3%  # 📈 Trending up!
```

#### Alert Configuration (Manual Setup)

```python
# Example: Alert if citation rate drops >10%
BASELINE_RATE = 0.50  # 50%
current_rate = result['summary']['citation_rate']

if current_rate < (BASELINE_RATE - 0.10):
    print(f"⚠️ ALERT: Citation rate dropped to {current_rate:.1%}")
    print("Consider re-optimizing content.")
```

---

### 4. Query Research

**When to research**:
- Before creating new content
- Quarterly content strategy review
- Competitive intelligence

#### Basic Query Research

```python
from answer_engine_optimization.modules.query_researcher import QueryResearcher

researcher = QueryResearcher()

# Research a topic
result = researcher.research(
    topic="Answer Engine Optimization",
    industry="SaaS"
)

# View target queries
for query in result['target_queries'][:5]:
    print(f"\nQuery: {query['query']}")
    print(f"Citation Potential: {query['citation_potential']:.1%}")
    print(f"Competition: {query['competition']}")
    print(f"Content Gap: {'✓' if query['content_gap'] else '✗'}")
```

**Example Output**:
```
Query: What is AEO?
Citation Potential: 85%
Competition: medium
Content Gap: ✓

Query: AEO vs SEO differences
Citation Potential: 72%
Competition: low
Content Gap: ✓

Query: How to track LLM citations
Citation Potential: 68%
Competition: high
Content Gap: ✗
```

#### Competitive Analysis

```python
result = researcher.research(
    topic="Answer Engine Optimization",
    competitor_urls=[
        "https://competitor1.com/aeo-guide",
        "https://competitor2.com/aeo-guide"
    ],
    industry="SaaS"
)

# Identify content gaps
for query in result['target_queries']:
    if query['content_gap']:
        print(f"Opportunity: {query['query']}")
        print(f"  Competitors being cited: {query['current_citations']}")
        print(f"  Your position: Not ranked\n")
```

#### Prioritizing Queries

**Strategy**: Focus on high-potential, low-competition queries first

```python
# Sort by citation potential / competition ratio
sorted_queries = sorted(
    result['target_queries'],
    key=lambda q: q['citation_potential'] / (1 if q['competition'] == 'low' else 2 if q['competition'] == 'medium' else 3),
    reverse=True
)

print("Top 5 Quick Wins:")
for i, query in enumerate(sorted_queries[:5], 1):
    print(f"{i}. {query['query']} (Potential: {query['citation_potential']:.0%}, Competition: {query['competition']})")
```

---

### 5. Report Generation

**When to generate reports**:
- Client deliverables (agencies)
- Stakeholder updates (internal teams)
- Monthly/quarterly reviews

#### Executive Summary Report

```python
from answer_engine_optimization.modules.report_generator import ReportGenerator

generator = ReportGenerator()

# Generate executive summary
report = generator.generate(
    audit_results=audit,
    optimization_results=optimization_result,
    citation_data=citation_result,
    template="executive"  # High-level overview
)

# Save report
with open("executive-summary.md", "w") as f:
    f.write(report)
```

**Example Output** (`executive-summary.md`):
```markdown
# AEO Executive Summary

**URL**: https://yoursite.com/article
**Date**: 2025-01-07
**Status**: ✅ Optimized

## Key Metrics

- **AEO Score**: 78/100 (+13 improvement)
- **Citation Rate**: 46.7% (7/15 LLM checks)
- **Competitive Rank**: 2nd out of 5

## Recommendations

1. **High Priority**: Add 2 more authoritative citations (+8 points)
2. **Medium Priority**: Enhance author credentials (+3 points)
3. **Low Priority**: Add table of contents (+2 points)

## Next Steps

1. Implement high-priority recommendations
2. Monitor citations for 30 days
3. Re-audit in 90 days
```

#### Full Audit Report

```python
report = generator.generate(
    audit_results=audit,
    template="full"  # Detailed analysis
)
```

#### Optimization Report

```python
report = generator.generate(
    audit_results=audit,
    optimization_results=optimization_result,
    template="optimization"  # Before/after comparison
)
```

**Example Output** (`optimization-report.md`):
```markdown
# Content Optimization Report

## Before Optimization

- **Score**: 65/100
- **Issues**: 12 identified
- **Priority Fixes**: 5

## After Optimization

- **Score**: 78/100 (+13 improvement)
- **Changes**: 18 modifications
- **Time**: 2.5 minutes

## Change Summary

### High-Impact Changes (+10 points)
1. Added H2 subheadings (lines 15, 42, 68)
2. Linked to 3 authoritative sources (lines 24, 51, 89)
3. Enhanced author bio with credentials (line 5)

### Medium-Impact Changes (+3 points)
4. Added data points and statistics (lines 33, 55)
5. Improved paragraph chunking (lines 20-25)

[Full change log...]
```

---

## Advanced Features

### Adaptive Learning System

The adaptive learning system improves recommendations over time by learning from successful optimizations.

#### How It Works

1. **Track Optimization Outcomes**:
   ```python
   from answer_engine_optimization.modules.success_patterns import SuccessPatternLearner

   learner = SuccessPatternLearner()

   # After optimization + citation tracking
   learner.learn(
       optimization_result=optimization_result,
       citation_performance=citation_result,
       industry="SaaS"
   )
   ```

2. **Get Learned Recommendations**:
   ```python
   recommendations = learner.get_recommendations(
       content_type="listicle",  # Article type
       industry="SaaS"
   )

   for rec in recommendations:
       print(f"{rec['strategy']}: {rec['success_rate']:.1%} success rate")
   ```

**Example Output**:
```
add_structure: 85% success rate
add_citations: 78% success rate
enhance_eeat: 72% success rate
```

#### Privacy & Sharing

**Default**: All learning data stays local (`.aeo-data/success_patterns.json`)

**Opt-in Sharing** (Community Patterns):
```python
# Enable anonymized pattern sharing
learner.enable_community_sharing()

# Disable
learner.disable_community_sharing()
```

---

### API Integration

#### Ahrefs Integration

**When to use**: Competitor research, backlink analysis

```python
# Set API key
import os
os.environ['AHREFS_API_KEY'] = 'your_key'

# Analyzer will automatically use Ahrefs for competitor data
audit = analyzer.analyze(
    content=content,
    competitor_urls=competitor_urls
)
```

#### SEMrush Integration

**When to use**: Keyword research, competitive analysis

```python
os.environ['SEMRUSH_API_KEY'] = 'your_key'

# Query researcher will use SEMrush data
result = researcher.research(
    topic="AEO",
    competitor_urls=competitor_urls
)
```

#### Cost Considerations

**Pricing** (as of 2025):
- Ahrefs: $99-999/month (1-10 req/sec)
- SEMrush: $119-449/month (1-5 req/sec)

**Recommendation**: Start without APIs, add when scaling

---

### Multi-Language AEO

**Status**: Experimental (v1.0), Full support in v1.5

```python
# Configure for non-English markets
analyzer = ContentAnalyzer(language="es")  # Spanish

audit = analyzer.analyze(
    content=spanish_content,
    url="https://yoursite.es/article"
)
```

**Supported Languages** (v1.5):
- English (en)
- Spanish (es)
- French (fr)
- German (de)
- Portuguese (pt)

---

### Batch Processing

**When to use**: Optimize 10+ articles at once

```python
import asyncio
from answer_engine_optimization.modules.content_analyzer import ContentAnalyzer

async def batch_audit(urls):
    analyzer = ContentAnalyzer()
    tasks = [analyzer.analyze_async(url=url) for url in urls]
    return await asyncio.gather(*tasks)

# Run batch
urls = [
    "https://yoursite.com/article1",
    "https://yoursite.com/article2",
    # ... 100 more URLs
]

results = asyncio.run(batch_audit(urls))

print(f"Audited {len(results)} articles")
print(f"Avg Score: {sum(r['scores']['overall'] for r in results) / len(results):.1f}")
```

**Expected Time**: ~20 minutes for 100 articles (vs 3+ hours sequentially)

---

## Best Practices

### Content Strategy

#### 1. Start with High-Value Pages

**Priority Order**:
1. **Top 10 traffic pages** - Highest ROI
2. **Product/service pages** - Commercial intent
3. **Long-form guides** - Authority building
4. **Recent content** - Quick wins

**Rationale**: Focus on pages that drive business value first.

---

#### 2. Optimization Levels by Content Type

| Content Type | Recommended Level | Rationale |
|--------------|-------------------|-----------|
| **Blog Posts** | Balanced | Preserve voice while improving |
| **Landing Pages** | Conservative | Brand voice critical |
| **Technical Docs** | Aggressive | Accuracy > voice |
| **News Articles** | Conservative | Journalistic style important |
| **Tutorials** | Balanced | Structure matters most |

---

#### 3. Measurement Timeline

**Week 1**: Optimize and publish

**Week 2-4**: Monitor citations daily
- Expect: 0-20% citation rate (ramp-up)

**Month 2-3**: Analyze trends
- Expect: 20-40% citation rate (growth)
- Action: Re-optimize underperformers

**Quarterly**: Full audit and refresh
- Expect: 40-60% citation rate (mature)
- Action: Maintain and expand

---

### Optimization Tips

#### Conservative Optimization

**Do**:
- Add structure (headings, lists)
- Link to authoritative sources
- Add data points
- Improve readability

**Don't**:
- Rewrite core messaging
- Change brand terminology
- Alter value propositions
- Remove personality

---

#### Aggressive Optimization

**Do**:
- Maximize LLM parsing
- Prioritize citations over voice
- Add extensive data
- Restructure completely if needed

**Don't**:
- Remove key differentiators
- Lose factual accuracy
- Over-optimize (spam)

---

### Citation Tracking Strategy

#### Daily Tracking

**Who**: High-value content, competitive topics

```python
# Set up daily checks
tracker.track(
    url="https://yoursite.com/high-value-article",
    queries=top_queries,
    frequency="daily"
)
```

#### Weekly Tracking

**Who**: Standard content library

```python
tracker.track(
    url="https://yoursite.com/article",
    queries=queries,
    frequency="weekly"
)
```

#### Monthly Tracking

**Who**: Evergreen content, low priority

```python
tracker.track(
    url="https://yoursite.com/evergreen-guide",
    queries=queries,
    frequency="monthly"
)
```

---

## Troubleshooting

### Common Errors

#### Error: "ANTHROPIC_API_KEY not found"

**Cause**: Missing API key for enhanced analysis

**Solution**:
```bash
# Option 1: Set environment variable
export ANTHROPIC_API_KEY="your_key_here"

# Option 2: Use .env file
echo "ANTHROPIC_API_KEY=your_key_here" > .env

# Option 3: Use without API (graceful degradation)
# Tool will use built-in capabilities
```

---

#### Error: "Rate limit exceeded (429)"

**Cause**: Too many API requests

**Solution**:
```python
# Add delay between requests
import time

for url in urls:
    audit = analyzer.analyze(url=url)
    time.sleep(2)  # 2-second delay
```

---

#### Error: "Invalid URL format"

**Cause**: Malformed URL

**Solution**:
```python
# Ensure URL includes protocol
url = "https://yoursite.com/article"  # ✓ Correct
# not: "yoursite.com/article"  # ✗ Missing https://
```

---

### Performance Issues

#### Slow Audits (>3 minutes)

**Cause**: Large content, many competitors

**Solutions**:
1. **Reduce competitor count**:
   ```python
   # Instead of 10 competitors
   competitor_urls = competitors[:3]  # Limit to 3
   ```

2. **Split large content**:
   ```python
   # Audit in sections
   audit_intro = analyzer.analyze(content=content[:5000])
   audit_body = analyzer.analyze(content=content[5000:10000])
   ```

---

#### High API Costs

**Cause**: Too many external API calls

**Solutions**:
1. **Disable external APIs**:
   ```python
   os.environ['USE_EXTERNAL_APIS'] = 'false'
   ```

2. **Use prompt caching**:
   ```python
   # Already enabled by default in v1.0
   ```

3. **Batch requests**:
   ```python
   # Process multiple articles in one request
   batch_audit(urls)
   ```

---

### Data Management

#### Storage Space Issues

**Cause**: Too much historical data

**Solution**:
```python
# Clean old data (>90 days)
from answer_engine_optimization.modules import utils

utils.cleanup_old_data(days=90)
```

**Manual Cleanup**:
```bash
# Remove all project data
rm -rf .aeo-data/projects/old-project

# Remove citation history
rm .aeo-data/projects/*/citation_tracking.csv
```

---

#### Data Backup

**Best Practice**: Backup `.aeo-data/` regularly

```bash
# Backup script
#!/bin/bash
DATE=$(date +%Y%m%d)
tar -czf "aeo-data-backup-${DATE}.tar.gz" .aeo-data/

# Upload to cloud storage (optional)
aws s3 cp "aeo-data-backup-${DATE}.tar.gz" s3://your-bucket/backups/
```

---

## FAQ

### Q: When will I see results?

**A**: Citation improvements typically appear within 2-4 weeks:

- **Week 1**: 0-10% citation rate (LLMs update their knowledge)
- **Week 2-4**: 20-30% citation rate (ramp-up)
- **Month 2-3**: 40-50% citation rate (mature)
- **Ongoing**: 50-70% citation rate (well-optimized)

**Note**: Results vary by topic competitiveness and content quality.

---

### Q: How accurate are the scores?

**A**: AEO scores are **directional indicators**, not guarantees:

- **E-E-A-T**: 80-90% accuracy (based on known Google factors)
- **Structure**: 90-95% accuracy (objective metrics)
- **Citations**: 70-80% accuracy (LLM behavior varies)
- **Overall**: 75-85% accuracy (conservative estimate)

**Use scores to**:
- Compare content before/after optimization
- Benchmark against competitors
- Track improvement trends

**Don't use scores as**:
- Absolute guarantees of citation
- Direct LLM ranking predictions

---

### Q: Can I use without API keys?

**A**: Yes! Core features work without any APIs:

**Works Without APIs**:
- ✅ Basic content auditing
- ✅ Structure analysis
- ✅ Readability scoring
- ✅ Report generation

**Requires APIs**:
- ⚠️ AI-powered optimization (ANTHROPIC_API_KEY)
- ⚠️ Enhanced E-E-A-T analysis (ANTHROPIC_API_KEY)
- ⚠️ Competitor benchmarking (AHREFS_API_KEY or SEMRUSH_API_KEY)
- ⚠️ Citation tracking (LLM API access)

**Recommendation**: Start without APIs, add when needed.

---

### Q: How much data storage is needed?

**A**: Very minimal:

| Component | Storage per 100 Articles |
|-----------|--------------------------|
| **Audit Reports** (JSON) | ~5 MB |
| **Citation Data** (CSV) | ~2 MB |
| **Success Patterns** (JSON) | ~1 MB (total, not per 100) |
| **Total** | ~8 MB per 100 articles |

**Annual Estimate**:
- 1,000 articles/year: ~80 MB
- 10,000 articles/year: ~800 MB

**Recommendation**: <1 GB for most users.

---

### Q: Is my data private?

**A**: Yes, 100% local-first by default:

- ✅ All data stored on your machine (`.aeo-data/`)
- ✅ No external transmission (unless APIs enabled)
- ✅ No telemetry/tracking
- ✅ Opt-in for community pattern sharing

**External API Calls** (opt-in):
- Anthropic API (for AI optimization)
- Ahrefs/SEMrush (for competitor data)
- LLM APIs (for citation tracking)

**Control**: You control all API usage via environment variables.

---

### Q: Can I cancel optimization mid-process?

**A**: Yes, use Ctrl+C:

```bash
# During optimization
^C  # Ctrl+C

# Partial results saved to .aeo-data/projects/{PROJECT}/optimization_log.json
```

**Safety**: Partial optimizations are saved, no data loss.

---

### Q: How do I reset to defaults?

**A**: Delete project data or reset config:

```bash
# Reset specific project
rm -rf .aeo-data/projects/my-website

# Reset all data
rm -rf .aeo-data/

# Reset configuration
rm .env
```

---

## Next Steps

1. **Run your first audit**: `aeo audit your-article.md`
2. **Optimize content**: `aeo optimize your-article.md --level balanced`
3. **Track citations**: `aeo track https://yoursite.com/article`
4. **Join community**: [GitHub Discussions](https://github.com/alirezarezvani/aeo-box/discussions)

---

**Need more help?**

- 📖 [API Reference](api-reference.md)
- 🏗️ [Architecture Documentation](foundation/architecture.md)
- 🐛 [GitHub Issues](https://github.com/alirezarezvani/aeo-box/issues)
- 💬 [Discussions](https://github.com/alirezarezvani/aeo-box/discussions)

---

<p align="center">
  <strong>Happy optimizing! 🚀</strong>
</p>
