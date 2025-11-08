"""
Content Analyzer for AEO audits.

Analyzes content for E-E-A-T signals, structure, and LLM optimization readiness.
"""

import re
import logging
from typing import Dict, List, Optional, Union, Tuple
from datetime import datetime

from .utils import (
    parse_markdown,
    calculate_readability,
    extract_entities,
    safe_divide,
    fetch_url_content
)
from .api_manager import APIManager

logger = logging.getLogger(__name__)


class ContentAnalyzer:
    """
    Comprehensive content analysis for AEO optimization.

    Analyzes:
    - E-E-A-T (Experience, Expertise, Authoritativeness, Trustworthiness)
    - Content structure and readability
    - Citation quality
    - LLM parsing optimization
    """

    def __init__(self, api_manager: Optional[APIManager] = None):
        """
        Initialize content analyzer.

        Args:
            api_manager: Optional API manager for enhanced analysis
        """
        self.api_manager = api_manager or APIManager()

    def analyze(self, content: str, url: Optional[str] = None, context: Optional[Dict] = None) -> Dict:
        """
        Perform comprehensive content analysis.

        Args:
            content: Content text (markdown or plain text)
            url: Optional source URL for additional context
            context: Optional context (industry, region, etc.)

        Returns:
            Complete audit report with scores and recommendations
        """
        logger.info(f"Starting content analysis (length: {len(content)} chars)")

        # Parse content structure
        parsed = parse_markdown(content)

        # Analyze different aspects
        eeat_score = self._analyze_eeat(content, parsed)
        structure_score = self._analyze_structure(content, parsed)
        citation_score = self._analyze_citations(content, parsed)
        readability = calculate_readability(content)
        entities = extract_entities(content)

        # Calculate overall AEO score
        overall_score = self._calculate_overall_score(
            eeat_score,
            structure_score,
            citation_score,
            readability
        )

        # Generate recommendations
        recommendations = self._generate_recommendations(
            eeat_score,
            structure_score,
            citation_score,
            readability,
            parsed
        )

        return {
            'timestamp': datetime.now().isoformat(),
            'url': url,
            'content_length': len(content),
            'word_count': parsed['word_count'],
            'scores': {
                'overall': overall_score,
                'eeat': eeat_score,
                'structure': structure_score,
                'citations': citation_score,
                'readability': readability['flesch_reading_ease']
            },
            'analysis': {
                'eeat_signals': self._get_eeat_signals(content, parsed),
                'structure_analysis': parsed,
                'readability_metrics': readability,
                'entities': entities,
                'citations': self._extract_citations(content, parsed)
            },
            'recommendations': recommendations,
            'priority_actions': self._prioritize_actions(recommendations)
        }

    def _analyze_eeat(self, content: str, parsed: Dict) -> Dict[str, Union[int, Dict]]:
        """
        Analyze E-E-A-T (Experience, Expertise, Authoritativeness, Trustworthiness) signals.

        Returns score dict with:
        - experience_score (0-25)
        - expertise_score (0-25)
        - authoritativeness_score (0-25)
        - trustworthiness_score (0-25)
        - total_score (0-100)
        """
        scores = {
            'experience': self._score_experience(content),
            'expertise': self._score_expertise(content, parsed),
            'authoritativeness': self._score_authoritativeness(content, parsed),
            'trustworthiness': self._score_trustworthiness(content, parsed)
        }

        total = sum(scores.values())

        return {
            'experience_score': scores['experience'],
            'expertise_score': scores['expertise'],
            'authoritativeness_score': scores['authoritativeness'],
            'trustworthiness_score': scores['trustworthiness'],
            'total_score': total,
            'grade': self._get_grade(total)
        }

    def _score_experience(self, content: str) -> int:
        """Score first-hand experience signals (0-25)."""
        score = 0

        # First-person perspective
        first_person_patterns = [r'\bI\b', r'\bwe\b', r'\bour\b', r'\bmy\b']
        first_person_count = sum(len(re.findall(pattern, content, re.IGNORECASE)) for pattern in first_person_patterns)
        if first_person_count > 0:
            score += min(10, first_person_count // 5)

        # Case studies / real examples
        case_study_patterns = [
            r'case study', r'real[- ]world example', r'in practice',
            r'our client', r'we worked with', r'we implemented'
        ]
        for pattern in case_study_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                score += 3

        # Specific numbers / data points (shows real experience)
        specific_numbers = re.findall(r'\b\d+(?:,\d{3})*(?:\.\d+)?%?\b', content)
        if len(specific_numbers) > 5:
            score += 5

        # Images/screenshots (not detectable in text, but mentioned)
        if re.search(r'!\[.*?\]\(.*?\)', content):  # Markdown images
            score += 7

        return min(25, score)

    def _score_expertise(self, content: str, parsed: Dict) -> int:
        """Score expertise signals (0-25)."""
        score = 0

        # Technical depth (technical terms, jargon)
        technical_indicators = len(re.findall(r'\b[A-Z]{2,}\b', content))  # Acronyms
        code_blocks = parsed.get('code_blocks', 0)
        tables = parsed.get('tables', 0)

        if technical_indicators > 5:
            score += 5
        if code_blocks > 0:
            score += 8
        if tables > 0:
            score += 7

        # Author credentials mentioned
        credentials_pattern = r'(?:PhD|MD|MBA|certified|expert|specialist|consultant|engineer|developer)'
        if re.search(credentials_pattern, content, re.IGNORECASE):
            score += 5

        return min(25, score)

    def _score_authoritativeness(self, content: str, parsed: Dict) -> int:
        """Score authoritativeness signals (0-25)."""
        score = 0

        # External citations/links to authoritative sources
        links = parsed.get('links', [])
        authoritative_domains = [
            'gov', 'edu', 'harvard', 'stanford', 'mit',
            'who.int', 'cdc.gov', 'nih.gov', 'ieee',
            'wikipedia', 'sciencedirect', 'nature.com'
        ]

        authoritative_links = 0
        for link in links:
            url = link.get('url', '').lower()
            if any(domain in url for domain in authoritative_domains):
                authoritative_links += 1

        score += min(15, authoritative_links * 3)

        # Data/statistics cited
        stats_patterns = [
            r'according to', r'study shows', r'research indicates',
            r'data from', r'survey of', r'report by'
        ]
        for pattern in stats_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                score += 2

        return min(25, score)

    def _score_trustworthiness(self, content: str, parsed: Dict) -> int:
        """Score trustworthiness signals (0-25)."""
        score = 0

        # Citations and sources
        links = parsed.get('links', [])
        if len(links) >= 5:
            score += 10
        elif len(links) >= 3:
            score += 5

        # Fact-checking patterns
        fact_patterns = [
            r'verified', r'confirmed', r'peer[- ]reviewed',
            r'fact[- ]checked', r'source:', r'reference:'
        ]
        for pattern in fact_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                score += 3

        # Transparent language (avoiding hype)
        hype_words = [
            r'guaranteed', r'miracle', r'secret', r'hack',
            r'100% effective', r'never fails', r'instant results'
        ]
        hype_count = sum(len(re.findall(pattern, content, re.IGNORECASE)) for pattern in hype_words)
        if hype_count == 0:
            score += 10  # Bonus for avoiding hype
        else:
            score -= min(10, hype_count * 2)  # Penalty for hype

        # Date/update information
        if re.search(r'updated|last modified|published', content, re.IGNORECASE):
            score += 5

        return max(0, min(25, score))

    def _analyze_structure(self, content: str, parsed: Dict) -> Dict[str, Union[int, str]]:
        """Analyze content structure for LLM optimization."""
        headings = parsed.get('headings', [])
        lists = parsed.get('lists', {'unordered': 0, 'ordered': 0})

        structure_score = parsed.get('structure_score', 0)

        # Check for good heading hierarchy
        has_h1 = any(h['level'] == 1 for h in headings)
        has_h2 = any(h['level'] == 2 for h in headings)
        has_proper_hierarchy = has_h1 and has_h2

        # Check for scannable content
        total_lists = lists.get('unordered', 0) + lists.get('ordered', 0)
        is_scannable = total_lists >= 2 or parsed.get('tables', 0) >= 1

        return {
            'score': structure_score,
            'has_proper_hierarchy': has_proper_hierarchy,
            'is_scannable': is_scannable,
            'heading_count': len(headings),
            'list_count': total_lists,
            'table_count': parsed.get('tables', 0),
            'grade': self._get_grade(structure_score)
        }

    def _analyze_citations(self, content: str, parsed: Dict) -> Dict[str, Union[int, List]]:
        """Analyze citation quality and quantity."""
        links = parsed.get('links', [])

        # Categorize links
        internal_links = []
        external_links = []
        authoritative_links = []

        authoritative_domains = ['gov', 'edu', 'harvard', 'stanford', 'mit']

        for link in links:
            url = link.get('url', '').lower()
            if url.startswith('#'):
                continue  # Skip anchor links
            elif url.startswith('/') or url.startswith('.'):
                internal_links.append(link)
            else:
                external_links.append(link)
                if any(domain in url for domain in authoritative_domains):
                    authoritative_links.append(link)

        # Calculate citation score (0-100)
        score = 0
        if len(external_links) >= 5:
            score += 30
        elif len(external_links) >= 3:
            score += 20
        elif len(external_links) >= 1:
            score += 10

        if len(authoritative_links) >= 3:
            score += 40
        elif len(authoritative_links) >= 1:
            score += 20

        # Bonus for citation diversity
        unique_domains = len(set(link.get('url', '').split('/')[2] for link in external_links if len(link.get('url', '').split('/')) > 2))
        if unique_domains >= 5:
            score += 30
        elif unique_domains >= 3:
            score += 20

        return {
            'score': min(100, score),
            'total_links': len(links),
            'external_links': len(external_links),
            'authoritative_links': len(authoritative_links),
            'unique_domains': unique_domains,
            'grade': self._get_grade(min(100, score))
        }

    def _calculate_overall_score(self, eeat: Dict, structure: Dict, citations: Dict, readability: Dict) -> int:
        """Calculate overall AEO score (0-100)."""
        # Weighted average
        weights = {
            'eeat': 0.40,      # E-E-A-T is most important for AEO
            'structure': 0.25,  # Structure helps LLM parsing
            'citations': 0.25,  # Citations boost authority
            'readability': 0.10 # Readability matters less for LLMs
        }

        weighted_score = (
            eeat['total_score'] * weights['eeat'] +
            structure['score'] * weights['structure'] +
            citations['score'] * weights['citations'] +
            readability['flesch_reading_ease'] * weights['readability']
        )

        return round(weighted_score)

    def _generate_recommendations(self, eeat: Dict, structure: Dict, citations: Dict, readability: Dict, parsed: Dict) -> List[Dict]:
        """Generate prioritized recommendations for improvement."""
        recommendations = []

        # E-E-A-T improvements
        if eeat['experience_score'] < 15:
            recommendations.append({
                'category': 'E-E-A-T',
                'priority': 'High',
                'issue': 'Low experience signals',
                'recommendation': 'Add first-hand examples, case studies, and specific results from your experience',
                'impact': 'High - significantly improves E-E-A-T'
            })

        if eeat['expertise_score'] < 15:
            recommendations.append({
                'category': 'E-E-A-T',
                'priority': 'High',
                'issue': 'Low expertise signals',
                'recommendation': 'Include technical details, data tables, or code examples demonstrating deep knowledge',
                'impact': 'High - establishes subject matter expertise'
            })

        if eeat['authoritativeness_score'] < 15:
            recommendations.append({
                'category': 'E-E-A-T',
                'priority': 'Critical',
                'issue': 'Low authoritativeness',
                'recommendation': 'Add citations to authoritative sources (.gov, .edu, industry reports)',
                'impact': 'Critical - essential for LLM citations'
            })

        # Structure improvements
        if structure['score'] < 60:
            recommendations.append({
                'category': 'Structure',
                'priority': 'Medium',
                'issue': 'Poor content structure',
                'recommendation': 'Add clear headings (H1, H2, H3), bullet lists, and tables for better LLM parsing',
                'impact': 'Medium - improves LLM understanding'
            })

        # Citation improvements
        if citations['external_links'] < 3:
            recommendations.append({
                'category': 'Citations',
                'priority': 'High',
                'issue': 'Insufficient external citations',
                'recommendation': 'Add at least 3-5 citations to authoritative external sources',
                'impact': 'High - increases trust and citation probability'
            })

        if citations['authoritative_links'] == 0:
            recommendations.append({
                'category': 'Citations',
                'priority': 'Critical',
                'issue': 'No authoritative sources',
                'recommendation': 'Include links to .gov, .edu, or recognized industry authorities',
                'impact': 'Critical - validates claims and builds trust'
            })

        # Readability
        if readability['flesch_reading_ease'] < 30:
            recommendations.append({
                'category': 'Readability',
                'priority': 'Low',
                'issue': 'Very complex language',
                'recommendation': 'Simplify some sentences for broader accessibility (optional for technical content)',
                'impact': 'Low - mainly affects human readability, not LLM parsing'
            })

        return recommendations

    def _prioritize_actions(self, recommendations: List[Dict]) -> List[Dict]:
        """Sort recommendations by priority."""
        priority_order = {'Critical': 0, 'High': 1, 'Medium': 2, 'Low': 3}
        return sorted(recommendations, key=lambda x: priority_order.get(x['priority'], 99))

    def _get_eeat_signals(self, content: str, parsed: Dict) -> Dict:
        """Extract detected E-E-A-T signals."""
        return {
            'first_person_usage': bool(re.search(r'\b(I|we|our|my)\b', content, re.IGNORECASE)),
            'author_credentials': bool(re.search(r'(PhD|MD|MBA|certified|expert)', content, re.IGNORECASE)),
            'citations_present': len(parsed.get('links', [])) > 0,
            'data_points': len(re.findall(r'\b\d+(?:,\d{3})*(?:\.\d+)?%?\b', content)),
            'code_examples': parsed.get('code_blocks', 0) > 0,
            'tables_present': parsed.get('tables', 0) > 0
        }

    def _extract_citations(self, content: str, parsed: Dict) -> List[Dict]:
        """Extract and categorize all citations."""
        links = parsed.get('links', [])
        citations = []

        for link in links:
            url = link.get('url', '')
            if url.startswith('#'):
                continue

            citation_type = 'internal' if url.startswith(('/','  .')) else 'external'
            is_authoritative = any(domain in url.lower() for domain in ['gov', 'edu', 'harvard', 'stanford'])

            citations.append({
                'text': link.get('text', ''),
                'url': url,
                'type': citation_type,
                'authoritative': is_authoritative
            })

        return citations

    def _get_grade(self, score: int) -> str:
        """Convert numeric score to letter grade."""
        if score >= 90:
            return 'A'
        elif score >= 80:
            return 'B'
        elif score >= 70:
            return 'C'
        elif score >= 60:
            return 'D'
        else:
            return 'F'


__all__ = ['ContentAnalyzer']
