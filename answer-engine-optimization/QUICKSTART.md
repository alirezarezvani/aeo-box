# AEO Skill - 5-Minute Quick Start

Get your first AEO audit in 5 minutes!

---

## Step 1: Install (1 minute)

```bash
# Copy to your Claude skills folder
cp -r answer-engine-optimization ~/.claude/skills/

# Restart Claude Code (if running)
```

---

## Step 2: Configure (1 minute)

Edit `~/.claude/skills/answer-engine-optimization/SKILL.md`:

```yaml
# Change these 3 variables:
TARGET_INDUSTRY: "Your Industry"     # e.g., SaaS, Healthcare, Finance
GEOGRAPHIC_REGION: "Your Region"     # e.g., US, UK, Canada
PROJECT_NAME: "your-project-name"    # e.g., myblog
```

Save the file.

---

## Step 3: Run Your First Audit (1 minute)

In Claude Code:

```bash
aeo-audit https://yourblog.com/your-best-article
```

**You'll get:**
- ✅ Overall AEO score (0-100)
- ✅ E-E-A-T breakdown
- ✅ Prioritized action items
- ✅ Specific recommendations

---

## Step 4: Optimize Content (1 minute)

```bash
aeo-optimize https://yourblog.com/your-best-article
```

**You'll get:**
- ✅ Optimized content (markdown)
- ✅ Before/after score comparison
- ✅ List of changes made
- ✅ Estimated citation improvement

---

## Step 5: Start Tracking (1 minute)

```bash
aeo-track https://yourblog.com/your-best-article
```

**You'll get:**
- ✅ Citation tracking across ChatGPT, Perplexity, Claude, Gemini
- ✅ Historical data (CSV)
- ✅ Trending analysis

---

## Next Steps

### Generate a Client Report

```bash
aeo-report your-project-name
```

### Research New Topics

```bash
aeo-research "your target topic"
```

### Advanced: Configure API Keys (Optional)

For enhanced features, add API keys:

```bash
aeo-configure
# Follow prompts to add Ahrefs, SEMrush, or OpenAI keys
```

**Note**: The skill works perfectly **without** API keys using Claude's capabilities!

---

## Common First-Time Issues

### "Skill not found"

- Verify path: `~/.claude/skills/answer-engine-optimization/SKILL.md` exists
- Restart Claude Code

### "Python error"

```bash
# Install dependencies (optional, not required for core features)
cd ~/.claude/skills/answer-engine-optimization
pip3 install -r requirements.txt
```

### "No data directory"

The `.aeo-data/` folder is created automatically on first use. If it doesn't appear, create it:

```bash
mkdir -p ~/.claude/skills/answer-engine-optimization/.aeo-data/projects
```

---

## Example Workflow

**Day 1**: Audit your top 10 articles

```bash
for url in article1 article2 article3; do
  aeo-audit https://yourblog.com/$url
done
```

**Day 2-3**: Optimize based on recommendations

```bash
aeo-optimize https://yourblog.com/article1
# Apply suggested changes
# Publish optimized version
```

**Week 2+**: Track citation performance

```bash
aeo-track https://yourblog.com/article1 --report
```

**Month 2+**: Review adaptive learning

```bash
cat .aeo-data/success_patterns.json
# See what's working, double down
```

---

**That's it! You're now optimizing for Answer Engines.** 🚀

For full documentation, see [README.md](README.md)
