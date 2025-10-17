"""
Curation Component - Zone 2 of AGI OS (The Automation Flywheel)

Responsible for analyzing and scoring discovered loops:
- Feature extraction (code analysis, text analysis)
- Quality scoring (heuristic v1, RL-based v2 in Phase 2)
- Redundancy detection (Phase 1 Day 3)
"""

from .feature_extractor import (
    ExtractedFeatures,
    CodeAnalyzer,
    TextAnalyzer,
    QualityScorer as FeatureQualityScorer,
    FeatureExtractor
)

from .quality_scorer import (
    QualityScore,
    HeuristicQualityScorer
)

__all__ = [
    'ExtractedFeatures',
    'CodeAnalyzer',
    'TextAnalyzer',
    'FeatureQualityScorer',
    'FeatureExtractor',
    'QualityScore',
    'HeuristicQualityScorer'
]

