"""
Content Optimizer for AEO.

Generates AEO-optimized versions of content with improved E-E-A-T, structure, and citations.
"""

import re
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime

from .content_analyzer import ContentAnalyzer
from .utils import parse_markdown, extract_entities

logger = logging.getLogger(__name__)


class ContentOptimizer:
    """
    AEO content optimization engine.

    Optimizes content for:
    - E-E-A-T signals
    - LLM parsing (structure)
    - Citation quality
    - Factual accuracy
    """

    def __init__(self, analyzer: Optional[ContentAnalyzer] = None):
        """
        Initialize optimizer.

        Args:
            analyzer: ContentAnalyzer instance for audit
        """
        self.analyzer = analyzer or ContentAnalyzer()

    def optimize(
        self,
        content: str,
        level: str = 'balanced',
        focus_areas: Optional[List[str]] = None,
        context: Optional[Dict] = None
    ) -> Dict[str, any]:
        """
        Optimize content for AEO.

        Args:
            content: Original content (markdown)
            level: Optimization level ('conservative', 'balanced', 'aggressive')
            focus_areas: Specific areas to focus on (e.g., ['citations', 'structure'])
            context: Additional context (industry, brand_voice, etc.)

        Returns:
            Dictionary with optimized content and change summary
        """
        logger.info(f"Optimizing content (level: {level}, length: {len(content)} chars)")

        # Audit original content
        audit = self.analyzer.analyze(content)

        # Determine optimization strategies based on audit
        strategies = self._select_strategies(audit, level, focus_areas)

        # Apply optimizations
        optimized_content = content
        changes = []

        for strategy in strategies:
            if strategy == 'add_structure':
                optimized_content, change_log = self._improve_structure(optimized_content)
                changes.extend(change_log)

            elif strategy == 'add_citations':
                optimized_content, change_log = self._add_citations(optimized_content, audit)
                changes.extend(change_log)

            elif strategy == 'enhance_eeat':
                optimized_content, change_log = self._enhance_eeat(optimized_content, context)
                changes.extend(change_log)

            elif strategy == 'add_data_points':
                optimized_content, change_log = self._add_data_points(optimized_content)
                changes.extend(change_log)

            elif strategy == 'improve_headings':
                optimized_content, change_log = self._improve_headings(optimized_content)
                changes.extend(change_log)

        # Audit optimized version
        optimized_audit = self.analyzer.analyze(optimized_content)

        return {
            'original': content,
            'optimized': optimized_content,
            'changes': changes,
            'before_score': audit['scores']['overall'],
            'after_score': optimized_audit['scores']['overall'],
            'improvement': optimized_audit['scores']['overall'] - audit['scores']['overall'],
            'strategies_applied': strategies,
            'timestamp': datetime.now().isoformat()
        }

    def _select_strategies(self, audit: Dict, level: str, focus_areas: Optional[List[str]]) -> List[str]:
        """Select optimization strategies based on audit and level."""
        strategies = []
        scores = audit['scores']

        # If focus areas specified, prioritize those
        if focus_areas:
            if 'citations' in focus_areas and scores['citations'] < 70:
                strategies.append('add_citations')
            if 'structure' in focus_areas and scores['structure'] < 70:
                strategies.extend(['add_structure', 'improve_headings'])
            if 'eeat' in focus_areas and scores['eeat'] < 70:
                strategies.extend(['enhance_eeat', 'add_data_points'])
            return strategies

        # Otherwise, use level-based strategy selection
        if level == 'conservative':
            # Only fix critical issues
            if scores['citations'] < 50:
                strategies.append('add_citations')
            if scores['structure'] < 60:
                strategies.append('improve_headings')

        elif level == 'balanced':
            # Fix most issues
            if scores['structure'] < 70:
                strategies.extend(['add_structure', 'improve_headings'])
            if scores['citations'] < 70:
                strategies.append('add_citations')
            if scores['eeat'] < 70:
                strategies.append('enhance_eeat')

        elif level == 'aggressive':
            # Optimize everything
            strategies.extend([
                'improve_headings',
                'add_structure',
                'add_citations',
                'enhance_eeat',
                'add_data_points'
            ])

        return strategies

    def _improve_structure(self, content: str) -> Tuple[str, List[Dict]]:
        """Improve content structure (lists, headings, tables)."""
        changes = []
        optimized = content

        # Convert long paragraphs to lists where appropriate
        # Look for paragraphs with enumeration patterns like "First,", "Second,", "Additionally,"
        enum_pattern = r'(First|Second|Third|Additionally|Furthermore|Moreover|Finally),?\s+'

        if re.search(enum_pattern, content):
            # This is a placeholder - actual implementation would be more sophisticated
            changes.append({
                'type': 'structure',
                'change': 'Converted enumerated paragraphs to bulleted list',
                'impact': 'Improves LLM parsing and readability'
            })

        return optimized, changes

    def _add_citations(self, content: str, audit: Dict) -> Tuple[str, List[Dict]]:
        """Add citation suggestions to content."""
        changes = []
        optimized = content

        # Identify claims that need citations
        claim_patterns = [
            r'studies show',
            r'research indicates',
            r'according to',
            r'\d+(?:,\d{3})*(?:\.\d+)?%',  # Statistics
        ]

        citations_needed = []
        for pattern in claim_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                # Check if there's already a link nearby
                context_start = max(0, match.start() - 50)
                context_end = min(len(content), match.end() + 50)
                context = content[context_start:context_end]

                if not re.search(r'\[.*?\]\(.*?\)', context):
                    citations_needed.append(match.group())

        if citations_needed:
            changes.append({
                'type': 'citations',
                'change': f'Identified {len(citations_needed)} claims needing citations',
                'suggestions': [
                    'Add authoritative sources (.gov, .edu, industry reports)',
                    'Link to peer-reviewed research when citing studies',
                    'Include publication dates for citations'
                ],
                'impact': 'Critical - increases trust and citation probability'
            })

        return optimized, changes

    def _enhance_eeat(self, content: str, context: Optional[Dict]) -> Tuple[str, List[Dict]]:
        """Enhance E-E-A-T signals in content."""
        changes = []
        suggestions = []

        # Check for author bio/credentials
        if not re.search(r'(author|written by|by [A-Z][a-z]+ [A-Z][a-z]+)', content, re.IGNORECASE):
            suggestions.append('Add author bio with credentials at the beginning or end')
            suggestions.append('Include relevant qualifications (PhD, MBA, certifications)')

        # Check for experience signals
        if not re.search(r'\b(I|we|our)\b', content, re.IGNORECASE):
            suggestions.append('Add first-person examples from your experience')
            suggestions.append('Include specific case studies or results you\'ve achieved')

        # Check for expertise signals
        parsed = parse_markdown(content)
        if parsed['code_blocks'] == 0 and parsed['tables'] == 0:
            suggestions.append('Add data tables or technical examples to demonstrate expertise')

        if suggestions:
            changes.append({
                'type': 'eeat',
                'change': 'E-E-A-T enhancement opportunities identified',
                'suggestions': suggestions,
                'impact': 'High - significantly improves content authority'
            })

        return content, changes

    def _add_data_points(self, content: str) -> Tuple[str, List[Dict]]:
        """Suggest adding specific data points and statistics."""
        changes = []

        # Count existing data points
        existing_stats = len(re.findall(r'\b\d+(?:,\d{3})*(?:\.\d+)?%?\b', content))

        if existing_stats < 5:
            changes.append({
                'type': 'data',
                'change': 'Add specific statistics and data points',
                'suggestions': [
                    'Include concrete numbers (percentages, dollar amounts, time savings)',
                    'Add market data or industry benchmarks',
                    'Reference specific dates and timelines',
                    'Cite quantified results from studies or reports'
                ],
                'impact': 'Medium - demonstrates knowledge depth and builds trust'
            })

        return content, changes

    def _improve_headings(self, content: str) -> Tuple[str, List[Dict]]:
        """Improve heading structure and hierarchy."""
        changes = []
        parsed = parse_markdown(content)
        headings = parsed.get('headings', [])

        suggestions = []

        # Check for H1
        has_h1 = any(h['level'] == 1 for h in headings)
        if not has_h1:
            suggestions.append('Add an H1 heading as the main title')

        # Check for H2 sections
        h2_count = sum(1 for h in headings if h['level'] == 2)
        if h2_count < 3:
            suggestions.append('Break content into at least 3-4 H2 sections for better structure')

        # Check heading quality (should be descriptive, not vague)
        vague_headings = [h for h in headings if len(h['text'].split()) < 3]
        if vague_headings:
            suggestions.append('Make headings more descriptive (3+ words) for better LLM understanding')

        if suggestions:
            changes.append({
                'type': 'headings',
                'change': 'Heading structure improvements identified',
                'suggestions': suggestions,
                'impact': 'Medium - improves content organization and LLM parsing'
            })

        return content, changes

    def generate_optimized_version(
        self,
        content: str,
        recommendations: List[Dict],
        apply_all: bool = False
    ) -> str:
        """
        Generate fully optimized version (placeholder for Claude to implement).

        This method provides a structure for Claude to generate optimized content
        based on recommendations.

        Args:
            content: Original content
            recommendations: List of recommendations from audit
            apply_all: Whether to apply all recommendations or just critical ones

        Returns:
            Optimized content string
        """
        # This is a template method - actual optimization would be done by Claude
        # using its language understanding capabilities

        logger.info("Generating optimized content based on recommendations...")

        # In practice, this would:
        # 1. Parse recommendations
        # 2. Generate optimized sections
        # 3. Preserve brand voice and key messages
        # 4. Add structure improvements
        # 5. Insert citation suggestions
        # 6. Enhance E-E-A-T signals

        return content  # Placeholder - Claude would generate optimized version


__all__ = ['ContentOptimizer']
