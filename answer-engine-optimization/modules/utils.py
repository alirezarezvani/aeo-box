"""
Utility functions for AEO skill.
Safe operations, web scraping, content parsing, and validation.
"""

import re
import json
import hashlib
from typing import Dict, List, Optional, Union, Tuple
from urllib.parse import urlparse, urljoin
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """
    Safely divide two numbers, returning default if denominator is zero.

    Args:
        numerator: The number to divide
        denominator: The number to divide by
        default: Value to return if division fails (default: 0.0)

    Returns:
        Result of division or default value

    Example:
        >>> safe_divide(100, 10)
        10.0
        >>> safe_divide(100, 0)
        0.0
        >>> safe_divide(100, 0, default=1.0)
        1.0
    """
    try:
        if denominator == 0:
            return default
        return numerator / denominator
    except (TypeError, ZeroDivisionError):
        return default


def validate_url(url: str) -> bool:
    """
    Validate if a string is a valid HTTP/HTTPS URL.

    Args:
        url: URL string to validate

    Returns:
        True if valid URL, False otherwise

    Example:
        >>> validate_url("https://example.com")
        True
        >>> validate_url("not-a-url")
        False
    """
    try:
        result = urlparse(url)
        return all([result.scheme in ['http', 'https'], result.netloc])
    except Exception:
        return False


def fetch_url_content(url: str, timeout: int = 10) -> Optional[Dict[str, Union[str, int]]]:
    """
    Fetch content from a URL using Claude's WebFetch capability.

    Args:
        url: URL to fetch
        timeout: Request timeout in seconds (default: 10)

    Returns:
        Dictionary with content, status_code, and metadata
        None if fetch fails

    Example:
        >>> content = fetch_url_content("https://example.com")
        >>> print(content['text'][:100])
    """
    if not validate_url(url):
        logger.error(f"Invalid URL: {url}")
        return None

    try:
        # This is a placeholder - actual implementation would use Claude's WebFetch
        # In practice, Claude Code will use its built-in WebFetch capability
        logger.info(f"Fetching content from: {url}")

        # Return structure (actual fetch happens via Claude's tools)
        return {
            'url': url,
            'status_code': 200,
            'text': '',  # Will be populated by Claude's WebFetch
            'title': '',
            'meta_description': '',
            'headings': [],
            'links': [],
            'word_count': 0,
            'fetch_timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error fetching URL {url}: {str(e)}")
        return None


def parse_markdown(content: str) -> Dict[str, Union[List, int, str]]:
    """
    Parse markdown content and extract structure.

    Args:
        content: Markdown text to parse

    Returns:
        Dictionary with headings, links, word count, structure analysis

    Example:
        >>> parsed = parse_markdown("# Title\\n\\nParagraph text.")
        >>> print(parsed['headings'])
        [{'level': 1, 'text': 'Title'}]
    """
    try:
        # Extract headings
        headings = []
        for match in re.finditer(r'^(#{1,6})\s+(.+)$', content, re.MULTILINE):
            level = len(match.group(1))
            text = match.group(2).strip()
            headings.append({'level': level, 'text': text})

        # Extract links
        links = []
        for match in re.finditer(r'\[([^\]]+)\]\(([^\)]+)\)', content):
            links.append({
                'text': match.group(1),
                'url': match.group(2)
            })

        # Count words (excluding markdown syntax)
        text_only = re.sub(r'[#*`\[\]()]', '', content)
        words = text_only.split()
        word_count = len(words)

        # Extract lists
        lists = {
            'unordered': len(re.findall(r'^\s*[-*+]\s+', content, re.MULTILINE)),
            'ordered': len(re.findall(r'^\s*\d+\.\s+', content, re.MULTILINE))
        }

        # Extract code blocks
        code_blocks = len(re.findall(r'```[\s\S]*?```', content))

        # Extract tables
        tables = len(re.findall(r'^\|.+\|$', content, re.MULTILINE)) // 2  # Rough estimate

        return {
            'headings': headings,
            'links': links,
            'word_count': word_count,
            'lists': lists,
            'code_blocks': code_blocks,
            'tables': tables,
            'structure_score': calculate_structure_score(headings, lists, tables)
        }

    except Exception as e:
        logger.error(f"Error parsing markdown: {str(e)}")
        return {
            'headings': [],
            'links': [],
            'word_count': 0,
            'lists': {'unordered': 0, 'ordered': 0},
            'code_blocks': 0,
            'tables': 0,
            'structure_score': 0
        }


def calculate_structure_score(headings: List[Dict], lists: Dict, tables: int) -> int:
    """
    Calculate content structure score (0-100) for AEO optimization.

    Well-structured content (clear headings, lists, tables) is easier for LLMs to parse.

    Args:
        headings: List of heading dictionaries
        lists: Dictionary with unordered/ordered list counts
        tables: Number of tables

    Returns:
        Structure score (0-100)
    """
    score = 0

    # Heading hierarchy (max 40 points)
    if headings:
        has_h1 = any(h['level'] == 1 for h in headings)
        has_h2 = any(h['level'] == 2 for h in headings)
        has_h3 = any(h['level'] == 3 for h in headings)

        if has_h1:
            score += 15
        if has_h2:
            score += 15
        if has_h3:
            score += 10

    # Lists (max 30 points)
    total_lists = lists.get('unordered', 0) + lists.get('ordered', 0)
    if total_lists > 0:
        score += min(30, total_lists * 5)

    # Tables (max 30 points)
    if tables > 0:
        score += min(30, tables * 10)

    return min(100, score)


def calculate_readability(text: str) -> Dict[str, Union[float, str]]:
    """
    Calculate readability metrics for content.

    Args:
        text: Text to analyze

    Returns:
        Dictionary with readability scores and grade level

    Example:
        >>> metrics = calculate_readability("Simple sentence here.")
        >>> print(metrics['grade_level'])
    """
    try:
        # Basic readability calculation (simplified Flesch-Kincaid)
        sentences = len(re.split(r'[.!?]+', text))
        words = len(text.split())
        syllables = sum(count_syllables(word) for word in text.split())

        if sentences == 0 or words == 0:
            return {
                'flesch_reading_ease': 0,
                'grade_level': 'Unknown',
                'avg_sentence_length': 0,
                'avg_word_length': 0
            }

        # Flesch Reading Ease (0-100, higher = easier)
        flesch_score = 206.835 - 1.015 * (words / sentences) - 84.6 * (syllables / words)
        flesch_score = max(0, min(100, flesch_score))

        # Grade level estimation
        if flesch_score >= 90:
            grade = "5th grade (very easy)"
        elif flesch_score >= 80:
            grade = "6th grade (easy)"
        elif flesch_score >= 70:
            grade = "7th grade (fairly easy)"
        elif flesch_score >= 60:
            grade = "8th-9th grade (standard)"
        elif flesch_score >= 50:
            grade = "10th-12th grade (fairly difficult)"
        elif flesch_score >= 30:
            grade = "College (difficult)"
        else:
            grade = "College graduate (very difficult)"

        return {
            'flesch_reading_ease': round(flesch_score, 1),
            'grade_level': grade,
            'avg_sentence_length': round(words / sentences, 1),
            'avg_word_length': round(len(text.replace(' ', '')) / words, 1)
        }

    except Exception as e:
        logger.error(f"Error calculating readability: {str(e)}")
        return {
            'flesch_reading_ease': 0,
            'grade_level': 'Error',
            'avg_sentence_length': 0,
            'avg_word_length': 0
        }


def count_syllables(word: str) -> int:
    """
    Estimate syllable count for a word (simple heuristic).

    Args:
        word: Word to count syllables for

    Returns:
        Estimated syllable count
    """
    word = word.lower()
    syllables = 0
    vowels = 'aeiouy'
    previous_was_vowel = False

    for char in word:
        is_vowel = char in vowels
        if is_vowel and not previous_was_vowel:
            syllables += 1
        previous_was_vowel = is_vowel

    # Adjust for silent 'e'
    if word.endswith('e'):
        syllables -= 1

    # Ensure at least 1 syllable
    if syllables == 0:
        syllables = 1

    return syllables


def extract_entities(text: str) -> Dict[str, List[str]]:
    """
    Extract named entities from text (simplified version).

    Args:
        text: Text to extract entities from

    Returns:
        Dictionary with entity types and values

    Example:
        >>> entities = extract_entities("Apple Inc. announced new iPhone.")
        >>> print(entities['organizations'])
    """
    entities = {
        'organizations': [],
        'people': [],
        'locations': [],
        'dates': [],
        'numbers': []
    }

    try:
        # Extract potential organizations (capitalized words followed by Inc, Corp, LLC, etc.)
        org_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:Inc|Corp|LLC|Ltd|Co)\b'
        entities['organizations'] = list(set(re.findall(org_pattern, text)))

        # Extract dates (simple patterns)
        date_pattern = r'\b(?:\d{1,2}/\d{1,2}/\d{2,4}|\d{4}-\d{2}-\d{2}|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4})\b'
        entities['dates'] = list(set(re.findall(date_pattern, text, re.IGNORECASE)))

        # Extract numbers with context (statistics)
        number_pattern = r'\b\d+(?:,\d{3})*(?:\.\d+)?%?\b'
        entities['numbers'] = list(set(re.findall(number_pattern, text)))

        # Extract potential people names (simplified - capitalized first + last)
        # This is very basic and would benefit from NLP library
        name_pattern = r'\b([A-Z][a-z]+\s+[A-Z][a-z]+)\b'
        potential_names = re.findall(name_pattern, text)
        # Filter out common false positives
        exclude = ['New York', 'Los Angeles', 'United States', 'South Africa']
        entities['people'] = [name for name in potential_names if name not in exclude]

    except Exception as e:
        logger.error(f"Error extracting entities: {str(e)}")

    return entities


def generate_content_hash(content: str) -> str:
    """
    Generate SHA-256 hash of content for tracking changes.

    Args:
        content: Content to hash

    Returns:
        Hexadecimal hash string
    """
    return hashlib.sha256(content.encode('utf-8')).hexdigest()


def format_timestamp(dt: Optional[datetime] = None) -> str:
    """
    Format datetime for consistent timestamps.

    Args:
        dt: Datetime to format (default: now)

    Returns:
        ISO format timestamp string
    """
    if dt is None:
        dt = datetime.now()
    return dt.isoformat()


def load_json_file(filepath: str, default: Optional[Dict] = None) -> Dict:
    """
    Safely load JSON file with fallback to default.

    Args:
        filepath: Path to JSON file
        default: Default value if file doesn't exist or is invalid

    Returns:
        Parsed JSON data or default
    """
    if default is None:
        default = {}

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.warning(f"File not found: {filepath}, using default")
        return default
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in {filepath}: {str(e)}")
        return default
    except Exception as e:
        logger.error(f"Error loading JSON file {filepath}: {str(e)}")
        return default


def save_json_file(filepath: str, data: Dict, pretty: bool = True) -> bool:
    """
    Safely save data to JSON file.

    Args:
        filepath: Path to save JSON file
        data: Data to save
        pretty: Whether to use indentation (default: True)

    Returns:
        True if successful, False otherwise
    """
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            if pretty:
                json.dump(data, f, indent=2, ensure_ascii=False)
            else:
                json.dump(data, f, ensure_ascii=False)
        return True
    except Exception as e:
        logger.error(f"Error saving JSON file {filepath}: {str(e)}")
        return False


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to maximum length with suffix.

    Args:
        text: Text to truncate
        max_length: Maximum length (default: 100)
        suffix: Suffix to add when truncated (default: "...")

    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


# Export all utility functions
__all__ = [
    'safe_divide',
    'validate_url',
    'fetch_url_content',
    'parse_markdown',
    'calculate_structure_score',
    'calculate_readability',
    'count_syllables',
    'extract_entities',
    'generate_content_hash',
    'format_timestamp',
    'load_json_file',
    'save_json_file',
    'truncate_text'
]
