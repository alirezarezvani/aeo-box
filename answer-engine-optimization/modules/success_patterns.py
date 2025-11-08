"""
Adaptive Learning System for AEO.

Tracks successful optimizations and builds pattern library to improve recommendations over time.
"""

import json
import logging
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path

from .utils import load_json_file, save_json_file

logger = logging.getLogger(__name__)


class SuccessPatternLearner:
    """
    Adaptive learning system that tracks successful AEO optimizations.

    Learns from:
    - Which optimizations lead to citations
    - What content structures perform best
    - Industry-specific patterns
    - Query-specific strategies
    """

    def __init__(self, data_path: str = '.aeo-data/success_patterns.json'):
        """
        Initialize success pattern learner.

        Args:
            data_path: Path to success patterns data file
        """
        self.data_path = data_path
        self.patterns = self._load_patterns()

    def _load_patterns(self) -> Dict:
        """Load existing success patterns from file."""
        patterns = load_json_file(self.data_path, default={
            'version': '1.0',
            'last_updated': datetime.now().isoformat(),
            'total_optimizations': 0,
            'total_successes': 0,
            'patterns': {},
            'industry_patterns': {},
            'query_patterns': {}
        })

        logger.info(f"Loaded {len(patterns.get('patterns', {}))} success patterns")
        return patterns

    def _save_patterns(self) -> bool:
        """Save success patterns to file."""
        self.patterns['last_updated'] = datetime.now().isoformat()

        # Ensure data directory exists
        Path(self.data_path).parent.mkdir(parents=True, exist_ok=True)

        return save_json_file(self.data_path, self.patterns)

    def record_optimization(
        self,
        optimization_type: str,
        context: Dict,
        changes: List[Dict],
        success_metrics: Optional[Dict] = None
    ) -> str:
        """
        Record an optimization attempt.

        Args:
            optimization_type: Type of optimization (e.g., 'citations', 'structure', 'eeat')
            context: Context information (industry, query, content type)
            changes: List of changes made
            success_metrics: Optional success metrics (citation count, etc.)

        Returns:
            Optimization ID for tracking
        """
        opt_id = f"opt_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{optimization_type}"

        self.patterns['total_optimizations'] += 1

        # Store optimization record
        if 'optimizations' not in self.patterns:
            self.patterns['optimizations'] = {}

        self.patterns['optimizations'][opt_id] = {
            'id': opt_id,
            'type': optimization_type,
            'timestamp': datetime.now().isoformat(),
            'context': context,
            'changes': changes,
            'success_metrics': success_metrics or {},
            'status': 'pending'  # Will be updated when results are measured
        }

        self._save_patterns()
        logger.info(f"Recorded optimization: {opt_id}")

        return opt_id

    def record_success(
        self,
        optimization_id: str,
        success_metrics: Dict
    ):
        """
        Record successful outcome of an optimization.

        Args:
            optimization_id: ID from record_optimization
            success_metrics: Metrics showing success (citations gained, ranking improvement, etc.)
        """
        if 'optimizations' not in self.patterns or optimization_id not in self.patterns['optimizations']:
            logger.error(f"Optimization {optimization_id} not found")
            return

        opt = self.patterns['optimizations'][optimization_id]
        opt['status'] = 'success'
        opt['success_metrics'] = success_metrics
        opt['success_timestamp'] = datetime.now().isoformat()

        self.patterns['total_successes'] += 1

        # Extract and store patterns
        self._extract_pattern(opt)

        self._save_patterns()
        logger.info(f"Recorded success for optimization: {optimization_id}")

    def _extract_pattern(self, optimization: Dict):
        """Extract successful pattern from optimization."""
        opt_type = optimization['type']
        context = optimization['context']
        changes = optimization['changes']

        # Create pattern key
        pattern_key = f"{opt_type}_{context.get('industry', 'general')}"

        if pattern_key not in self.patterns['patterns']:
            self.patterns['patterns'][pattern_key] = {
                'pattern_type': opt_type,
                'industry': context.get('industry', 'general'),
                'successful_changes': [],
                'success_count': 0,
                'total_attempts': 0,
                'success_rate': 0.0,
                'avg_improvement': 0.0
            }

        pattern = self.patterns['patterns'][pattern_key]
        pattern['success_count'] += 1
        pattern['total_attempts'] += 1
        pattern['success_rate'] = pattern['success_count'] / pattern['total_attempts']

        # Store successful change types
        for change in changes:
            change_type = change.get('type', 'unknown')
            if change_type not in [c.get('type') for c in pattern['successful_changes']]:
                pattern['successful_changes'].append({
                    'type': change_type,
                    'description': change.get('change', ''),
                    'occurrences': 1
                })
            else:
                # Increment occurrence count
                for sc in pattern['successful_changes']:
                    if sc.get('type') == change_type:
                        sc['occurrences'] += 1

    def get_recommendations(
        self,
        optimization_type: str,
        context: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Get recommendations based on learned patterns.

        Args:
            optimization_type: Type of optimization needed
            context: Context (industry, content type, etc.)

        Returns:
            List of recommended changes based on successful patterns
        """
        context = context or {}
        industry = context.get('industry', 'general')

        # Look for matching patterns
        pattern_key = f"{optimization_type}_{industry}"

        if pattern_key in self.patterns['patterns']:
            pattern = self.patterns['patterns'][pattern_key]

            if pattern['success_rate'] >= 0.5:  # At least 50% success rate
                return [{
                    'recommendation_source': 'learned_pattern',
                    'pattern_type': optimization_type,
                    'industry': industry,
                    'success_rate': pattern['success_rate'],
                    'successful_changes': pattern['successful_changes'],
                    'confidence': 'high' if pattern['success_rate'] >= 0.75 else 'medium'
                }]

        # Fallback to general patterns
        general_key = f"{optimization_type}_general"
        if general_key in self.patterns['patterns']:
            pattern = self.patterns['patterns'][general_key]
            return [{
                'recommendation_source': 'general_pattern',
                'pattern_type': optimization_type,
                'industry': 'general',
                'success_rate': pattern['success_rate'],
                'successful_changes': pattern['successful_changes'],
                'confidence': 'low'
            }]

        # No patterns found
        return [{
            'recommendation_source': 'no_pattern',
            'message': 'No learned patterns yet for this optimization type and industry',
            'suggestion': 'Using best practices from AEO guidelines'
        }]

    def get_industry_insights(self, industry: str) -> Dict:
        """
        Get industry-specific insights.

        Args:
            industry: Industry name

        Returns:
            Dictionary with industry-specific patterns and recommendations
        """
        industry_patterns = {
            k: v for k, v in self.patterns['patterns'].items()
            if v.get('industry') == industry
        }

        if not industry_patterns:
            return {
                'industry': industry,
                'patterns_found': 0,
                'message': f'No industry-specific patterns for {industry} yet',
                'recommendation': 'Start optimizing and tracking to build industry patterns'
            }

        # Calculate industry statistics
        total_success = sum(p['success_count'] for p in industry_patterns.values())
        total_attempts = sum(p['total_attempts'] for p in industry_patterns.values())
        avg_success_rate = total_success / total_attempts if total_attempts > 0 else 0

        # Identify most successful pattern types
        pattern_types = {}
        for pattern in industry_patterns.values():
            ptype = pattern['pattern_type']
            if ptype not in pattern_types:
                pattern_types[ptype] = {'successes': 0, 'attempts': 0}
            pattern_types[ptype]['successes'] += pattern['success_count']
            pattern_types[ptype]['attempts'] += pattern['total_attempts']

        best_patterns = sorted(
            pattern_types.items(),
            key=lambda x: x[1]['successes'] / x[1]['attempts'] if x[1]['attempts'] > 0 else 0,
            reverse=True
        )

        return {
            'industry': industry,
            'patterns_found': len(industry_patterns),
            'total_optimizations': total_attempts,
            'total_successes': total_success,
            'avg_success_rate': round(avg_success_rate, 2),
            'best_optimization_types': [
                {
                    'type': ptype,
                    'success_rate': round(data['successes'] / data['attempts'], 2),
                    'total_attempts': data['attempts']
                }
                for ptype, data in best_patterns[:3]
            ]
        }

    def export_patterns(self, filepath: Optional[str] = None) -> str:
        """
        Export success patterns to file.

        Args:
            filepath: Optional custom export path

        Returns:
            Path to exported file
        """
        export_path = filepath or f'.aeo-data/patterns_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'

        Path(export_path).parent.mkdir(parents=True, exist_ok=True)

        export_data = {
            'export_timestamp': datetime.now().isoformat(),
            'version': self.patterns.get('version'),
            'statistics': {
                'total_optimizations': self.patterns.get('total_optimizations', 0),
                'total_successes': self.patterns.get('total_successes', 0),
                'success_rate': self.patterns.get('total_successes', 0) / max(self.patterns.get('total_optimizations', 1), 1)
            },
            'patterns': self.patterns.get('patterns', {}),
            'industry_insights': {
                industry: self.get_industry_insights(industry)
                for industry in set(p.get('industry', 'general') for p in self.patterns.get('patterns', {}).values())
            }
        }

        save_json_file(export_path, export_data)
        logger.info(f"Exported patterns to: {export_path}")

        return export_path

    def get_statistics(self) -> Dict:
        """Get overall learning statistics."""
        return {
            'total_optimizations': self.patterns.get('total_optimizations', 0),
            'total_successes': self.patterns.get('total_successes', 0),
            'success_rate': self.patterns.get('total_successes', 0) / max(self.patterns.get('total_optimizations', 1), 1),
            'patterns_learned': len(self.patterns.get('patterns', {})),
            'industries_tracked': len(set(
                p.get('industry', 'general')
                for p in self.patterns.get('patterns', {}).values()
            )),
            'last_updated': self.patterns.get('last_updated')
        }


__all__ = ['SuccessPatternLearner']
