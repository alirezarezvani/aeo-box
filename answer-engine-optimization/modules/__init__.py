"""
Answer Engine Optimization (AEO) Skill
Core modules for content audit, optimization, and citation tracking.
"""

__version__ = "1.0.0"
__author__ = "AEO Skill Team"

from .content_analyzer import ContentAnalyzer
from .query_researcher import QueryResearcher
from .citation_tracker import CitationTracker
from .optimizer import ContentOptimizer
from .api_manager import APIManager
from .success_patterns import SuccessPatternLearner
from .report_generator import ReportGenerator
from .utils import (
    safe_divide,
    fetch_url_content,
    parse_markdown,
    calculate_readability,
    extract_entities,
    validate_url
)

__all__ = [
    'ContentAnalyzer',
    'QueryResearcher',
    'CitationTracker',
    'ContentOptimizer',
    'APIManager',
    'SuccessPatternLearner',
    'ReportGenerator',
    'safe_divide',
    'fetch_url_content',
    'parse_markdown',
    'calculate_readability',
    'extract_entities',
    'validate_url'
]
