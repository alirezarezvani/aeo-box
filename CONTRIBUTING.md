# Contributing to AEO Box

Thank you for your interest in contributing to AEO Box! This document provides guidelines and instructions for contributing to the project.

---

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [Code Style Guidelines](#code-style-guidelines)
- [Testing Requirements](#testing-requirements)
- [Pull Request Process](#pull-request-process)
- [Branch Strategy](#branch-strategy)
- [Commit Message Guidelines](#commit-message-guidelines)
- [Documentation Guidelines](#documentation-guidelines)
- [Issue Reporting](#issue-reporting)
- [Community](#community)

---

## Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inclusive environment for all contributors, regardless of experience level, background, or identity.

### Expected Behavior

- **Be Respectful**: Treat all contributors with respect and professionalism
- **Be Collaborative**: Work together to achieve project goals
- **Be Constructive**: Provide helpful feedback and accept constructive criticism
- **Be Inclusive**: Welcome newcomers and help them get started
- **Be Transparent**: Communicate clearly about your work and intentions

### Unacceptable Behavior

- Harassment, discrimination, or offensive comments
- Personal attacks or trolling
- Spam or irrelevant contributions
- Violating others' privacy or intellectual property

### Enforcement

Violations of the code of conduct may result in:
1. Warning from maintainers
2. Temporary ban from the project
3. Permanent ban for severe or repeated violations

Report violations to: [rezvani.rezaalireza@gmail.com](mailto:rezvani.rezaalireza@gmail.com)

---

## Getting Started

### Prerequisites

Before contributing, ensure you have:

- **Python 3.9+** installed
- **Git** for version control
- **GitHub account** for pull requests
- **Basic understanding** of AEO concepts (see [README.md](README.md))

### Finding Ways to Contribute

1. **Browse Open Issues**: Check [GitHub Issues](https://github.com/alirezarezvani/aeo-box/issues) for tasks labeled:
   - `good-first-issue` - Beginner-friendly tasks
   - `help-wanted` - Tasks needing assistance
   - `enhancement` - Feature requests
   - `bug` - Bug reports

2. **Propose New Features**: Create a feature request issue with:
   - Clear problem statement
   - Proposed solution
   - Expected benefits
   - Implementation complexity estimate

3. **Improve Documentation**: Help with:
   - Fixing typos or unclear sections
   - Adding examples and tutorials
   - Translating documentation
   - Improving API documentation

4. **Report Bugs**: Found a bug? Create a bug report with:
   - Steps to reproduce
   - Expected vs. actual behavior
   - Environment details (OS, Python version)
   - Error messages or logs

---

## Development Setup

### 1. Fork and Clone

```bash
# Fork the repository on GitHub, then clone your fork
git clone https://github.com/YOUR_USERNAME/aeo-box.git
cd aeo-suite

# Add upstream remote
git remote add upstream https://github.com/alirezarezvani/aeo-box.git
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
# Navigate to AEO Skill directory
cd answer-engine-optimization

# Install required dependencies
pip install -r requirements.txt

# Install development dependencies
pip install pytest pytest-cov black flake8 mypy isort
```

### 4. Verify Installation

```bash
# Run tests to verify setup
pytest tests/

# Check code style
flake8 modules/
black --check modules/
mypy modules/
```

### 5. Configure Environment

```bash
# Copy example environment file (if available)
cp .env.example .env

# Edit .env and add your API keys (optional)
# ANTHROPIC_API_KEY=your_key_here
# OPENAI_API_KEY=your_key_here
```

---

## Project Structure

```
aeo-box/
├── answer-engine-optimization/    # AEO Skill (Python toolkit)
│   ├── modules/                   # Core AEO modules
│   │   ├── content_analyzer.py    # Content analysis
│   │   ├── optimizer.py           # Content optimization
│   │   ├── citation_tracker.py    # Citation tracking
│   │   ├── query_researcher.py    # Query research
│   │   ├── report_generator.py    # Report generation
│   │   └── success_patterns.py    # Adaptive learning
│   ├── templates/                 # Report templates
│   ├── tests/                     # Test suite
│   │   ├── test_content_analyzer.py
│   │   ├── test_optimizer.py
│   │   └── ...
│   ├── SKILL.md                   # Skill configuration
│   ├── QUICKSTART.md              # Quick start guide
│   └── requirements.txt           # Dependencies
│
├── documentation/                 # Comprehensive docs
│   ├── foundation/
│   │   ├── prd.md                # Product requirements
│   │   └── architecture.md       # System architecture
│   ├── user-guide.md             # User documentation
│   ├── api-reference.md          # API reference
│   ├── deployment-guide.md       # Deployment guide
│   └── cost-optimization.md      # Cost optimization
│
├── .github/                       # GitHub configuration
│   ├── workflows/                 # CI/CD workflows
│   ├── ISSUE_TEMPLATE/           # Issue templates
│   └── BRANCH_PROTECTION.md      # Branch protection
│
├── scripts/                       # Utility scripts
│   └── sync-labels.sh            # Label sync script
│
├── README.md                      # Project overview
├── CONTRIBUTING.md               # This file
├── LICENSE                        # MIT License
└── .gitignore                    # Git ignore rules
```

---

## Code Style Guidelines

### Python Code Style (PEP 8)

We follow [PEP 8](https://pep8.org/) with some modifications:

#### General Rules

- **Line Length**: Maximum 100 characters (not 79)
- **Indentation**: 4 spaces (no tabs)
- **Encoding**: UTF-8
- **Imports**: Grouped and sorted (stdlib → third-party → local)

#### Naming Conventions

```python
# Classes: PascalCase
class ContentAnalyzer:
    pass

# Functions/methods: snake_case
def analyze_content(content: str) -> Dict[str, Any]:
    pass

# Constants: UPPER_SNAKE_CASE
MAX_RETRY_ATTEMPTS = 3
DEFAULT_TIMEOUT = 30

# Private methods: _leading_underscore
def _internal_helper(data: str) -> str:
    pass

# Module-level variables: snake_case
default_config = {}
```

#### Type Hints

**Always use type hints** for function signatures:

```python
from typing import Dict, List, Optional, Any

def analyze(
    self,
    content: str,
    url: Optional[str] = None,
    competitor_urls: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Analyze content for AEO signals.

    Args:
        content: Article content (markdown or plain text)
        url: URL of the article for reference
        competitor_urls: Competitor URLs for benchmarking

    Returns:
        Dictionary containing audit results

    Raises:
        ValueError: If content is empty or invalid
    """
    pass
```

#### Docstrings

Use **Google-style docstrings**:

```python
def optimize_content(
    content: str,
    target_score: int = 80,
    preserve_voice: bool = True
) -> Dict[str, Any]:
    """
    Optimize content to achieve target AEO score.

    This function analyzes the provided content and applies AI-powered
    optimizations to improve its likelihood of being cited by LLMs.

    Args:
        content: Original article content
        target_score: Desired AEO score (60-90)
        preserve_voice: Whether to maintain brand voice

    Returns:
        Dictionary containing:
            - optimized_content (str): Improved content
            - changes (List[Dict]): Applied changes
            - score_improvement (int): Score delta
            - timestamp (str): ISO 8601 timestamp

    Raises:
        ValueError: If target_score is outside valid range

    Example:
        >>> optimizer = Optimizer()
        >>> result = optimizer.optimize_content(
        ...     content="Original article text",
        ...     target_score=85
        ... )
        >>> print(result['score_improvement'])
        +12
    """
    pass
```

#### Code Formatting

We use **Black** for automatic formatting:

```bash
# Format all Python files
black modules/ tests/

# Check formatting without modifying
black --check modules/

# Format specific file
black modules/content_analyzer.py
```

#### Import Ordering

Use **isort** to organize imports:

```python
# Standard library imports
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional

# Third-party imports
import anthropic
import requests
from pydantic import BaseModel

# Local application imports
from .config import Config
from .utils import sanitize_content
```

Run isort:

```bash
# Sort imports
isort modules/ tests/

# Check without modifying
isort --check modules/
```

#### Linting

Use **flake8** for linting:

```bash
# Lint all files
flake8 modules/ tests/

# Custom configuration (.flake8)
# [flake8]
# max-line-length = 100
# exclude = venv,.git,__pycache__
# ignore = E203,W503
```

#### Type Checking

Use **mypy** for static type checking:

```bash
# Type check all modules
mypy modules/

# Configuration (mypy.ini)
# [mypy]
# python_version = 3.9
# warn_return_any = True
# warn_unused_configs = True
# disallow_untyped_defs = True
```

---

## Testing Requirements

### Coverage Target

**Minimum 80% code coverage** is required for all pull requests.

### Test Structure

```
tests/
├── conftest.py                    # Pytest fixtures
├── test_content_analyzer.py       # ContentAnalyzer tests
├── test_optimizer.py              # Optimizer tests
├── test_citation_tracker.py       # CitationTracker tests
├── test_query_researcher.py       # QueryResearcher tests
├── test_report_generator.py       # ReportGenerator tests
└── test_success_patterns.py       # SuccessPatterns tests
```

### Writing Tests

#### Unit Tests

```python
import pytest
from answer_engine_optimization.modules.content_analyzer import ContentAnalyzer

class TestContentAnalyzer:
    """Test suite for ContentAnalyzer."""

    @pytest.fixture
    def analyzer(self):
        """Create ContentAnalyzer instance for tests."""
        return ContentAnalyzer()

    @pytest.fixture
    def sample_content(self):
        """Sample content for testing."""
        return """
        # Sample Article

        This is a sample article with E-E-A-T signals.

        ## Key Points
        - Point 1
        - Point 2
        """

    def test_analyze_returns_dict(self, analyzer, sample_content):
        """Test that analyze() returns a dictionary."""
        result = analyzer.analyze(sample_content)
        assert isinstance(result, dict)
        assert "scores" in result
        assert "recommendations" in result

    def test_analyze_calculates_eeat_score(self, analyzer, sample_content):
        """Test that E-E-A-T score is calculated."""
        result = analyzer.analyze(sample_content)
        assert "eeat" in result["scores"]
        assert 0 <= result["scores"]["eeat"] <= 100

    def test_analyze_raises_on_empty_content(self, analyzer):
        """Test that analyze() raises ValueError for empty content."""
        with pytest.raises(ValueError, match="Content cannot be empty"):
            analyzer.analyze("")

    @pytest.mark.parametrize("content,expected_score_range", [
        ("Short content", (0, 50)),
        ("Medium length content with multiple paragraphs", (50, 75)),
        ("Long, detailed content with citations and structure", (75, 100)),
    ])
    def test_analyze_score_ranges(self, analyzer, content, expected_score_range):
        """Test score ranges for different content qualities."""
        result = analyzer.analyze(content)
        score = result["scores"]["overall"]
        assert expected_score_range[0] <= score <= expected_score_range[1]
```

#### Integration Tests

```python
def test_full_workflow():
    """Test complete AEO workflow (analyze → optimize → track)."""
    # Analyze content
    analyzer = ContentAnalyzer()
    audit = analyzer.analyze(content=sample_content)

    # Optimize content
    optimizer = Optimizer()
    optimized = optimizer.optimize(
        content=sample_content,
        target_score=80
    )

    # Verify improvement
    improved_audit = analyzer.analyze(content=optimized["optimized_content"])
    assert improved_audit["scores"]["overall"] > audit["scores"]["overall"]

    # Track citations (mock API)
    tracker = CitationTracker()
    citations = tracker.track_citations(
        url="https://example.com/article",
        queries=["test query"]
    )
    assert isinstance(citations, dict)
```

#### Fixtures

```python
# conftest.py
import pytest

@pytest.fixture
def sample_article():
    """Sample article for testing."""
    return {
        "content": "# Article Title\n\nContent here...",
        "url": "https://example.com/article",
        "metadata": {
            "author": "Test Author",
            "published": "2025-01-07"
        }
    }

@pytest.fixture
def mock_api_client(mocker):
    """Mock API client for testing."""
    mock_client = mocker.Mock()
    mock_client.analyze.return_value = {"score": 75}
    return mock_client
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=modules tests/

# Generate HTML coverage report
pytest --cov=modules --cov-report=html tests/
# Open htmlcov/index.html in browser

# Run specific test file
pytest tests/test_content_analyzer.py

# Run specific test
pytest tests/test_content_analyzer.py::TestContentAnalyzer::test_analyze_returns_dict

# Run tests matching pattern
pytest -k "analyze"

# Run with verbose output
pytest -v

# Run and stop on first failure
pytest -x
```

### Coverage Requirements

**Before submitting a pull request**:

1. Run coverage report:
   ```bash
   pytest --cov=modules --cov-report=term-missing tests/
   ```

2. Ensure **>80% coverage**:
   ```
   Name                                      Stmts   Miss  Cover   Missing
   -----------------------------------------------------------------------
   modules/__init__.py                          0      0   100%
   modules/content_analyzer.py                150     10    93%   45-47, 89
   modules/optimizer.py                        120      8    93%   67-69
   modules/citation_tracker.py                 100     15    85%   23-25, 78-82
   modules/query_researcher.py                  90     12    87%   34-37, 91-94
   modules/report_generator.py                  80      5    94%   56-58
   modules/success_patterns.py                  70      8    89%   45-48, 67-68
   -----------------------------------------------------------------------
   TOTAL                                       610     58    90%
   ```

3. Fix untested code or add test cases

4. Update tests if you modify existing functionality

---

## Pull Request Process

### 1. Create Feature Branch

```bash
# Sync with upstream
git checkout dev
git pull upstream dev

# Create feature branch
git checkout -b feature/your-feature-name
# or
git checkout -b fix/bug-description
```

### 2. Make Changes

- Write clean, well-documented code
- Follow code style guidelines
- Add tests for new functionality
- Update documentation if needed

### 3. Test Your Changes

```bash
# Run full test suite
pytest --cov=modules tests/

# Check code style
black --check modules/
flake8 modules/
mypy modules/
isort --check modules/
```

### 4. Commit Your Changes

```bash
# Stage changes
git add .

# Commit with descriptive message
git commit -m "feat: add citation tracking for Gemini"
```

See [Commit Message Guidelines](#commit-message-guidelines) for format.

### 5. Push to Your Fork

```bash
git push origin feature/your-feature-name
```

### 6. Create Pull Request

1. Go to [GitHub repository](https://github.com/alirezarezvani/aeo-box)
2. Click "Pull Request" → "New Pull Request"
3. Select:
   - **Base**: `alirezarezvani/aeo-box` `dev`
   - **Compare**: `your-username/aeo-box` `feature/your-feature-name`
4. Fill out PR template:

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix (non-breaking change fixing an issue)
- [ ] New feature (non-breaking change adding functionality)
- [ ] Breaking change (fix or feature causing existing functionality to change)
- [ ] Documentation update

## Related Issue
Closes #123

## Changes Made
- Change 1
- Change 2
- Change 3

## Testing
- [ ] Tests pass locally (`pytest`)
- [ ] Coverage >80% (`pytest --cov`)
- [ ] Code style checks pass (`black`, `flake8`, `mypy`)
- [ ] Manual testing completed

## Documentation
- [ ] Updated docstrings
- [ ] Updated user guide (if needed)
- [ ] Updated API reference (if needed)

## Screenshots (if applicable)
Before: [screenshot]
After: [screenshot]

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex logic
- [ ] Documentation updated
- [ ] No new warnings introduced
- [ ] Tests added/updated
- [ ] All tests passing
```

### 7. Code Review Process

1. **Automated Checks**: CI/CD runs automatically
   - Tests must pass
   - Coverage must be >80%
   - Code style must pass

2. **Maintainer Review**: Maintainers will review your PR
   - They may request changes
   - Address feedback promptly
   - Push updates to same branch

3. **Approval**: Once approved:
   - PR will be merged to `dev`
   - Feature branches deleted
   - Your contribution will be in next release

### 8. After Merge

```bash
# Switch to dev branch
git checkout dev

# Pull latest changes
git pull upstream dev

# Delete feature branch
git branch -d feature/your-feature-name
git push origin --delete feature/your-feature-name
```

---

## Branch Strategy

### Branch Types

```
main           # Production-ready code (protected)
├── dev        # Development branch (protected)
    ├── feature/citation-gemini
    ├── feature/adaptive-learning
    ├── fix/analyzer-bug
    └── docs/api-reference
```

#### Main Branch

- **Always stable and production-ready**
- Only accepts merges from `dev`
- Tagged with version numbers (v1.0.0, v1.1.0)
- Protected: Requires PR approval

#### Dev Branch

- **Active development**
- Accepts merges from feature branches
- Should always be functional
- Protected: Requires PR approval + passing tests

#### Feature Branches

- **New features or enhancements**
- Naming: `feature/short-description`
- Examples:
  - `feature/citation-tracking`
  - `feature/adaptive-learning`
  - `feature/cli-interface`

#### Fix Branches

- **Bug fixes**
- Naming: `fix/short-description`
- Examples:
  - `fix/analyzer-crash`
  - `fix/memory-leak`
  - `fix/report-generation`

#### Docs Branches

- **Documentation updates**
- Naming: `docs/section-name`
- Examples:
  - `docs/api-reference`
  - `docs/user-guide`
  - `docs/quickstart`

### Merge Strategy

```
feature/xyz → dev (via PR)
dev → main (via PR, on release)
```

**Never commit directly to `main` or `dev`**

---

## Commit Message Guidelines

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Type

- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation only
- **style**: Code style (formatting, no logic change)
- **refactor**: Code refactoring (no feature/fix)
- **perf**: Performance improvement
- **test**: Adding/updating tests
- **chore**: Maintenance (dependencies, build)

### Scope

Optional. Indicates affected component:
- `analyzer`: ContentAnalyzer
- `optimizer`: Optimizer
- `tracker`: CitationTracker
- `researcher`: QueryResearcher
- `reporter`: ReportGenerator
- `patterns`: SuccessPatterns
- `cli`: CLI interface
- `api`: REST API

### Subject

- **Use imperative mood**: "add" not "added" or "adds"
- **Don't capitalize first letter**: "add feature" not "Add feature"
- **No period at end**: "add feature" not "add feature."
- **Maximum 50 characters**

### Body

- Optional detailed explanation
- **Wrap at 72 characters**
- Explain **what** and **why**, not **how**

### Footer

- Optional references to issues
- Breaking changes

### Examples

#### Simple Feature

```
feat(tracker): add citation tracking for Gemini

Add support for tracking citations in Google Gemini responses.
This completes our 5-LLM tracking capability.

Closes #45
```

#### Bug Fix

```
fix(analyzer): prevent crash on empty content

The analyzer was crashing when analyzing empty strings.
Added validation to raise ValueError with helpful message.

Fixes #78
```

#### Breaking Change

```
feat(api): redesign optimization API

BREAKING CHANGE: Optimizer.optimize() now returns a dictionary
instead of a string. Update your code:

Before: optimized = optimizer.optimize(content)
After: result = optimizer.optimize(content)
       optimized = result["optimized_content"]

Closes #102
```

#### Documentation

```
docs(guide): add citation tracking tutorial

Add step-by-step tutorial for multi-LLM citation tracking
with code examples and troubleshooting tips.
```

#### Refactoring

```
refactor(analyzer): extract E-E-A-T scoring logic

Move E-E-A-T scoring to separate method for better
testability and maintainability.
```

---

## Documentation Guidelines

### User-Facing Documentation

Located in `documentation/`:

- **user-guide.md**: How-to guides and tutorials
- **api-reference.md**: API documentation
- **deployment-guide.md**: Deployment instructions
- **cost-optimization.md**: Cost optimization strategies

**When to update**:
- New features added
- API changes
- New workflows or examples
- Configuration options changed

### Developer Documentation

- **README.md**: Project overview
- **CONTRIBUTING.md**: This file
- **documentation/foundation/architecture.md**: System architecture
- **Code comments**: Inline explanations

### Docstring Standards

Every public function/class must have docstrings:

```python
def track_citations(
    self,
    url: str,
    queries: List[str],
    llms: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Track citations across multiple LLMs for given queries.

    This method queries multiple LLMs with the specified search queries
    and detects whether the provided URL is cited in their responses.

    Args:
        url: Target URL to track citations for
        queries: List of search queries to test
        llms: List of LLM names to query (default: all 5 supported)
              Options: ["chatgpt", "perplexity", "claude", "gemini", "mistral"]

    Returns:
        Dictionary containing:
            - timestamp (str): ISO 8601 timestamp
            - url (str): Tracked URL
            - queries (List[str]): Queries tested
            - results (List[Dict]): Per-LLM citation results
            - summary (Dict): Aggregate statistics

    Raises:
        ValueError: If URL is invalid or queries list is empty
        APIError: If API calls fail after retries

    Example:
        >>> tracker = CitationTracker()
        >>> results = tracker.track_citations(
        ...     url="https://yoursite.com/article",
        ...     queries=["best AEO tools", "optimize for ChatGPT"],
        ...     llms=["chatgpt", "perplexity"]
        ... )
        >>> print(results["summary"]["citation_rate"])
        0.75  # 75% citation rate

    Note:
        This method may take several minutes for multiple queries and LLMs.
        Consider using async version for better performance.

    See Also:
        - track_citations_async(): Async version
        - get_citation_history(): Historical data
    """
    pass
```

### Documentation Review Checklist

Before submitting PR with docs changes:

- [ ] **Accuracy**: Information is correct and up-to-date
- [ ] **Clarity**: Language is clear and concise
- [ ] **Examples**: Code examples work correctly
- [ ] **Links**: All links work (internal and external)
- [ ] **Formatting**: Markdown renders correctly
- [ ] **Spelling**: No typos or grammar errors
- [ ] **Completeness**: All sections filled out

---

## Issue Reporting

### Bug Reports

Use the [Bug Report template](.github/ISSUE_TEMPLATE/bug_report.yml):

**Required Information**:
- **Description**: Clear description of the bug
- **Steps to Reproduce**:
  1. Step 1
  2. Step 2
  3. ...
- **Expected Behavior**: What should happen
- **Actual Behavior**: What actually happens
- **Environment**:
  - OS: macOS 14.0
  - Python: 3.11.5
  - AEO Box: v1.0.0
- **Error Messages**: Full error traceback
- **Screenshots**: If applicable

**Example**:

```markdown
**Description**: ContentAnalyzer crashes on PDF files

**Steps to Reproduce**:
1. Load PDF file content
2. Call analyzer.analyze(content)
3. Observe crash

**Expected**: Should analyze PDF content or raise helpful error

**Actual**: Crashes with UnicodeDecodeError

**Environment**:
- OS: macOS 14.0
- Python: 3.11.5
- AEO Box: v1.0.0

**Error**:
```
UnicodeDecodeError: 'utf-8' codec can't decode byte 0xff in position 0
```

**Workaround**: Convert PDF to text first
```

### Feature Requests

Use the [Feature Request template](.github/ISSUE_TEMPLATE/feature_request.yml):

**Required Information**:
- **Problem Statement**: What problem does this solve?
- **Proposed Solution**: How should it work?
- **Alternatives Considered**: Other approaches
- **Benefits**: Who benefits and how?
- **Implementation Complexity**: Low/Medium/High estimate

**Example**:

```markdown
**Problem**: No way to export citation data to Google Sheets

**Proposed Solution**: Add Google Sheets export functionality
- OAuth integration with Google Sheets API
- One-click export button in reports
- Automatic formatting and charts

**Alternatives**:
- CSV export (already exists, but manual)
- Google Data Studio integration (more complex)

**Benefits**:
- Easier client reporting for agencies
- Real-time dashboard updates
- Reduces manual work by ~30 min/report

**Complexity**: Medium
- Google API integration: ~8 hours
- UI implementation: ~4 hours
- Testing: ~4 hours
```

### Issue Labels

When creating issues, use appropriate labels:

**Type**:
- `bug` - Something isn't working
- `enhancement` - New feature or improvement
- `documentation` - Docs improvements
- `question` - Questions or clarifications

**Priority**:
- `priority-critical` - System broken, immediate fix
- `priority-high` - Major issue, fix soon
- `priority-medium` - Standard priority
- `priority-low` - Nice to have

**Effort**:
- `effort-small` - <4 hours
- `effort-medium` - 4-16 hours
- `effort-large` - >16 hours

**Status**:
- `good-first-issue` - Beginner-friendly
- `help-wanted` - Community help needed
- `blocked` - Waiting on dependency
- `wontfix` - Won't be implemented

**Component**:
- `aeo-skill` - AEO Skill modules
- `multi-agent` - Multi-agent system
- `cli` - CLI interface
- `api` - REST API
- `testing` - Test infrastructure

---

## Community

### Getting Help

- **Documentation**: Start with [User Guide](documentation/user-guide.md)
- **GitHub Issues**: Search [existing issues](https://github.com/alirezarezvani/aeo-box/issues)
- **GitHub Discussions**: Ask questions in [Discussions](https://github.com/alirezarezvani/aeo-box/discussions)
- **Email**: Contact maintainers at [rezvani.rezaalireza@gmail.com](mailto:rezvani.rezaalireza@gmail.com)

### Helping Others

- Answer questions in GitHub Discussions
- Review pull requests
- Improve documentation
- Share your AEO success stories

### Stay Updated

- **Star the repository** to get notifications
- **Watch releases** for new versions
- **Follow discussions** for announcements
- **Join community calls** (TBD)

---

## Development Workflow Examples

### Example 1: Adding a New Feature

```bash
# 1. Sync with upstream
git checkout dev
git pull upstream dev

# 2. Create feature branch
git checkout -b feature/pdf-support

# 3. Implement feature
# - Add PDF parsing to content_analyzer.py
# - Add tests to test_content_analyzer.py
# - Update documentation

# 4. Test changes
pytest --cov=modules tests/
black modules/ tests/
flake8 modules/
mypy modules/

# 5. Commit changes
git add .
git commit -m "feat(analyzer): add PDF file support

Add ability to analyze PDF files directly. Converts PDF to text
using PyPDF2 and then analyzes as normal content.

Closes #123"

# 6. Push and create PR
git push origin feature/pdf-support
# Create PR on GitHub

# 7. Address review feedback
# - Make requested changes
# - Commit and push updates

# 8. After merge
git checkout dev
git pull upstream dev
git branch -d feature/pdf-support
```

### Example 2: Fixing a Bug

```bash
# 1. Create fix branch from dev
git checkout dev
git pull upstream dev
git checkout -b fix/memory-leak

# 2. Fix the bug
# - Modify affected module
# - Add regression test
# - Verify fix works

# 3. Test thoroughly
pytest tests/test_citation_tracker.py -v
pytest --cov=modules tests/

# 4. Commit with clear message
git commit -m "fix(tracker): resolve memory leak in citation monitoring

The tracker was keeping all API responses in memory indefinitely.
Now properly clears cache after 1000 requests or 1 hour.

Fixes #234"

# 5. Submit PR
git push origin fix/memory-leak
# Create PR targeting dev branch
```

### Example 3: Updating Documentation

```bash
# 1. Create docs branch
git checkout -b docs/add-tutorials

# 2. Make documentation changes
# - Add tutorials to user-guide.md
# - Add examples to api-reference.md

# 3. Preview changes
# - Open markdown files in viewer
# - Check formatting and links

# 4. Commit
git commit -m "docs(guide): add step-by-step tutorials

Add 3 new tutorials:
- Getting started with AEO Box
- Citation tracking workflow
- Advanced optimization techniques"

# 5. Submit PR
git push origin docs/add-tutorials
```

---

## Recognition

### Contributors

All contributors are recognized in:
- **README.md** - Contributors section
- **Release notes** - Per-release credits
- **GitHub insights** - Automatic tracking

### Contribution Types

We value all contributions:
- Code (features, fixes)
- Documentation (guides, examples)
- Testing (bug reports, QA)
- Design (UI/UX, graphics)
- Community (support, advocacy)

---

## Questions?

If you have questions about contributing:

1. **Check documentation** first
2. **Search existing issues** for similar questions
3. **Ask in Discussions** for general questions
4. **Create an issue** for specific problems
5. **Email maintainers** for private matters

---

## Thank You!

Thank you for contributing to AEO Box! Your efforts help make content optimization accessible to everyone.

**Every contribution matters** - whether it's fixing a typo, reporting a bug, or adding a major feature.

Happy coding!

---

**Last Updated**: 2025-01-08

**Maintainers**:
- Alireza Rezvani ([@alirezarezvani](https://github.com/alirezarezvani)) - Project Lead

**License**: MIT - See [LICENSE](LICENSE) for details
