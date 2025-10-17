"""
Feature Extraction Engine - Component 2
Analyzes discovered loops and extracts meaningful features for quality scoring.

Author: Manus AI
Date: October 17, 2025
"""

import ast
import json
import logging
import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from collections import Counter

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ExtractedFeatures:
    """Data class for extracted features from a loop"""
    
    # Identifiers
    loop_id: str
    source_url: str
    source_type: str
    
    # Content features
    has_code: bool
    code_language: Optional[str]
    code_complexity: float  # 0-1 scale
    code_lines: int
    
    # Text features
    title_length: int
    description_length: int
    has_tutorial: bool
    has_documentation: bool
    
    # Quality signals
    popularity_score: float  # 0-1 scale (stars, upvotes, etc.)
    author_reputation: float  # 0-1 scale
    recency_score: float  # 0-1 scale
    
    # Categorization
    primary_category: str
    secondary_categories: List[str]
    keywords: List[str]
    
    # Automation potential
    automation_type: str  # web_scraping, data_processing, api_wrapper, workflow, etc.
    complexity_level: str  # beginner, intermediate, advanced
    estimated_value: float  # 0-1 scale
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "loop_id": self.loop_id,
            "source_url": self.source_url,
            "source_type": self.source_type,
            "has_code": self.has_code,
            "code_language": self.code_language,
            "code_complexity": self.code_complexity,
            "code_lines": self.code_lines,
            "title_length": self.title_length,
            "description_length": self.description_length,
            "has_tutorial": self.has_tutorial,
            "has_documentation": self.has_documentation,
            "popularity_score": self.popularity_score,
            "author_reputation": self.author_reputation,
            "recency_score": self.recency_score,
            "primary_category": self.primary_category,
            "secondary_categories": self.secondary_categories,
            "keywords": self.keywords,
            "automation_type": self.automation_type,
            "complexity_level": self.complexity_level,
            "estimated_value": self.estimated_value
        }


class CodeAnalyzer:
    """Analyzes code snippets using AST parsing"""
    
    @staticmethod
    def detect_language(code: str) -> Optional[str]:
        """Detect programming language from code"""
        # Simple heuristics for language detection
        if 'import ' in code or 'def ' in code or 'class ' in code:
            return 'python'
        elif 'function' in code and ('{' in code or '=>' in code):
            return 'javascript'
        elif 'public class' in code or 'private ' in code:
            return 'java'
        elif '#include' in code or 'int main' in code:
            return 'c++'
        else:
            return 'unknown'
    
    @staticmethod
    def calculate_complexity(code: str, language: str) -> float:
        """Calculate code complexity (0-1 scale)"""
        if language != 'python':
            # Simple line-based complexity for non-Python
            lines = [l for l in code.split('\n') if l.strip()]
            return min(len(lines) / 100.0, 1.0)
        
        try:
            tree = ast.parse(code)
            
            # Count various complexity indicators
            num_functions = sum(1 for node in ast.walk(tree) if isinstance(node, ast.FunctionDef))
            num_classes = sum(1 for node in ast.walk(tree) if isinstance(node, ast.ClassDef))
            num_loops = sum(1 for node in ast.walk(tree) if isinstance(node, (ast.For, ast.While)))
            num_conditionals = sum(1 for node in ast.walk(tree) if isinstance(node, ast.If))
            num_try_except = sum(1 for node in ast.walk(tree) if isinstance(node, ast.Try))
            
            # Weighted complexity score
            complexity = (
                num_functions * 2 +
                num_classes * 3 +
                num_loops * 1.5 +
                num_conditionals * 1 +
                num_try_except * 2
            )
            
            # Normalize to 0-1 scale
            return min(complexity / 50.0, 1.0)
        
        except SyntaxError:
            # If parsing fails, use simple line count
            lines = [l for l in code.split('\n') if l.strip()]
            return min(len(lines) / 100.0, 1.0)
    
    @staticmethod
    def count_lines(code: str) -> int:
        """Count non-empty lines of code"""
        return len([l for l in code.split('\n') if l.strip()])


class TextAnalyzer:
    """Analyzes text content for categorization and quality signals"""
    
    # Keyword categories
    CATEGORIES = {
        'web_scraping': ['scrape', 'scraping', 'crawler', 'spider', 'beautifulsoup', 'selenium'],
        'data_processing': ['pandas', 'numpy', 'data', 'csv', 'excel', 'dataframe'],
        'api_wrapper': ['api', 'rest', 'endpoint', 'wrapper', 'client', 'sdk'],
        'automation': ['automate', 'automation', 'workflow', 'task', 'schedule'],
        'bot': ['bot', 'chatbot', 'telegram', 'discord', 'slack'],
        'ml_ai': ['machine learning', 'ai', 'neural', 'model', 'training', 'tensorflow', 'pytorch'],
        'web_dev': ['flask', 'django', 'fastapi', 'web', 'server', 'frontend'],
        'devops': ['docker', 'kubernetes', 'ci/cd', 'deployment', 'infrastructure'],
        'security': ['security', 'encryption', 'authentication', 'oauth', 'jwt'],
        'testing': ['test', 'testing', 'pytest', 'unittest', 'qa']
    }
    
    COMPLEXITY_KEYWORDS = {
        'beginner': ['simple', 'basic', 'beginner', 'tutorial', 'learn', 'intro'],
        'intermediate': ['intermediate', 'moderate', 'practical', 'real-world'],
        'advanced': ['advanced', 'complex', 'production', 'scalable', 'enterprise']
    }
    
    @staticmethod
    def extract_keywords(text: str, max_keywords: int = 10) -> List[str]:
        """Extract important keywords from text"""
        # Convert to lowercase and split
        words = re.findall(r'\b[a-z]{3,}\b', text.lower())
        
        # Remove common stop words
        stop_words = {'the', 'and', 'for', 'with', 'this', 'that', 'from', 'have', 'are', 'was'}
        words = [w for w in words if w not in stop_words]
        
        # Count frequency
        word_counts = Counter(words)
        
        # Return top keywords
        return [word for word, count in word_counts.most_common(max_keywords)]
    
    @staticmethod
    def categorize(text: str) -> Tuple[str, List[str]]:
        """Categorize text into primary and secondary categories"""
        text_lower = text.lower()
        
        category_scores = {}
        for category, keywords in TextAnalyzer.CATEGORIES.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                category_scores[category] = score
        
        if not category_scores:
            return 'general', []
        
        # Sort by score
        sorted_categories = sorted(category_scores.items(), key=lambda x: x[1], reverse=True)
        
        primary = sorted_categories[0][0]
        secondary = [cat for cat, score in sorted_categories[1:4]]
        
        return primary, secondary
    
    @staticmethod
    def detect_complexity_level(text: str) -> str:
        """Detect complexity level from text"""
        text_lower = text.lower()
        
        for level, keywords in TextAnalyzer.COMPLEXITY_KEYWORDS.items():
            if any(keyword in text_lower for keyword in keywords):
                return level
        
        return 'intermediate'  # Default
    
    @staticmethod
    def has_tutorial_indicators(text: str) -> bool:
        """Check if text indicates a tutorial"""
        tutorial_keywords = ['tutorial', 'how to', 'guide', 'step by step', 'learn', 'walkthrough']
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in tutorial_keywords)
    
    @staticmethod
    def has_documentation_indicators(text: str) -> bool:
        """Check if text indicates documentation"""
        doc_keywords = ['documentation', 'docs', 'readme', 'api reference', 'manual']
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in doc_keywords)


class QualityScorer:
    """Calculates quality scores based on various signals"""
    
    @staticmethod
    def calculate_popularity_score(metadata: Dict, source_type: str) -> float:
        """Calculate popularity score from metadata (0-1 scale)"""
        if source_type == 'github':
            stars_text = metadata.get('stars', '0')
            # Extract number from text like "1,150 stars this week"
            stars = int(re.sub(r'[^\d]', '', stars_text.split()[0]) or '0')
            # Normalize: 1000+ stars = 1.0
            return min(stars / 1000.0, 1.0)
        
        elif source_type == 'reddit':
            upvotes_text = metadata.get('upvotes', '0')
            upvotes = int(upvotes_text) if upvotes_text.isdigit() else 0
            # Normalize: 100+ upvotes = 1.0
            return min(upvotes / 100.0, 1.0)
        
        return 0.5  # Default
    
    @staticmethod
    def calculate_author_reputation(metadata: Dict, source_type: str) -> float:
        """Calculate author reputation score (0-1 scale)"""
        # Placeholder - would integrate with GitHub/Reddit APIs for real reputation
        author = metadata.get('author', '')
        
        # Simple heuristics
        if author in ['AutoModerator', 'unknown', '']:
            return 0.3
        
        # For now, give moderate score to all authors
        return 0.6
    
    @staticmethod
    def calculate_recency_score(timestamp: str) -> float:
        """Calculate recency score (0-1 scale)"""
        # For now, all discoveries are recent (just scraped)
        return 1.0
    
    @staticmethod
    def estimate_value(features: Dict) -> float:
        """Estimate overall value of the loop (0-1 scale)"""
        # Weighted combination of factors
        value = (
            features.get('popularity_score', 0.5) * 0.3 +
            features.get('code_complexity', 0.5) * 0.2 +
            features.get('author_reputation', 0.5) * 0.2 +
            (1.0 if features.get('has_code') else 0.3) * 0.3
        )
        
        return min(value, 1.0)


class FeatureExtractor:
    """Main feature extraction engine"""
    
    def __init__(self):
        self.code_analyzer = CodeAnalyzer()
        self.text_analyzer = TextAnalyzer()
        self.quality_scorer = QualityScorer()
    
    def extract_features(self, discovery: Dict) -> ExtractedFeatures:
        """Extract all features from a discovery"""
        
        # Basic identifiers
        loop_id = f"{discovery['source_type']}_{hash(discovery['source_url']) % 1000000}"
        source_url = discovery['source_url']
        source_type = discovery['source_type']
        
        # Get content
        title = discovery['metadata'].get('title', '')
        description = discovery.get('raw_content', '')
        full_text = f"{title} {description}"
        
        # Code analysis
        has_code = len(description) > 100 and any(indicator in description for indicator in ['def ', 'import ', 'class ', 'function'])
        code_language = self.code_analyzer.detect_language(description) if has_code else None
        code_complexity = self.code_analyzer.calculate_complexity(description, code_language or 'unknown') if has_code else 0.0
        code_lines = self.code_analyzer.count_lines(description) if has_code else 0
        
        # Text analysis
        title_length = len(title)
        description_length = len(description)
        has_tutorial = self.text_analyzer.has_tutorial_indicators(full_text)
        has_documentation = self.text_analyzer.has_documentation_indicators(full_text)
        keywords = self.text_analyzer.extract_keywords(full_text)
        primary_category, secondary_categories = self.text_analyzer.categorize(full_text)
        complexity_level = self.text_analyzer.detect_complexity_level(full_text)
        
        # Quality scoring
        popularity_score = self.quality_scorer.calculate_popularity_score(discovery['metadata'], source_type)
        author_reputation = self.quality_scorer.calculate_author_reputation(discovery['metadata'], source_type)
        recency_score = self.quality_scorer.calculate_recency_score(discovery['discovery_timestamp'])
        
        # Determine automation type
        automation_type = primary_category if primary_category in self.text_analyzer.CATEGORIES else 'general'
        
        # Create feature dict for value estimation
        feature_dict = {
            'popularity_score': popularity_score,
            'code_complexity': code_complexity,
            'author_reputation': author_reputation,
            'has_code': has_code
        }
        estimated_value = self.quality_scorer.estimate_value(feature_dict)
        
        # Create ExtractedFeatures object
        features = ExtractedFeatures(
            loop_id=loop_id,
            source_url=source_url,
            source_type=source_type,
            has_code=has_code,
            code_language=code_language,
            code_complexity=code_complexity,
            code_lines=code_lines,
            title_length=title_length,
            description_length=description_length,
            has_tutorial=has_tutorial,
            has_documentation=has_documentation,
            popularity_score=popularity_score,
            author_reputation=author_reputation,
            recency_score=recency_score,
            primary_category=primary_category,
            secondary_categories=secondary_categories,
            keywords=keywords,
            automation_type=automation_type,
            complexity_level=complexity_level,
            estimated_value=estimated_value
        )
        
        return features
    
    def process_discoveries(self, discoveries_file: str, output_file: str):
        """Process all discoveries and extract features"""
        logger.info(f"Loading discoveries from {discoveries_file}...")
        
        with open(discoveries_file, 'r') as f:
            discoveries = json.load(f)
        
        logger.info(f"Processing {len(discoveries)} discoveries...")
        
        extracted_features = []
        for i, discovery in enumerate(discoveries):
            try:
                features = self.extract_features(discovery)
                extracted_features.append(features.to_dict())
                
                if (i + 1) % 10 == 0:
                    logger.info(f"Processed {i + 1}/{len(discoveries)} discoveries...")
            
            except Exception as e:
                logger.error(f"Error processing discovery {i}: {e}")
                continue
        
        logger.info(f"Saving extracted features to {output_file}...")
        with open(output_file, 'w') as f:
            json.dump(extracted_features, f, indent=2)
        
        logger.info(f"Feature extraction complete. Processed {len(extracted_features)}/{len(discoveries)} discoveries.")
        
        return extracted_features


# Main execution
if __name__ == "__main__":
    extractor = FeatureExtractor()
    
    # Process discoveries
    features = extractor.process_discoveries(
        discoveries_file="/home/ubuntu/loopfactory-agi-os/data/discoveries.json",
        output_file="/home/ubuntu/loopfactory-agi-os/data/extracted_features.json"
    )
    
    # Print summary statistics
    print(f"\n{'='*60}")
    print(f"FEATURE EXTRACTION COMPLETE")
    print(f"{'='*60}")
    print(f"Total loops processed: {len(features)}")
    
    # Category breakdown
    categories = {}
    for f in features:
        cat = f['primary_category']
        categories[cat] = categories.get(cat, 0) + 1
    
    print(f"\nCategory breakdown:")
    for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
        print(f"  {cat}: {count}")
    
    # Value distribution
    high_value = sum(1 for f in features if f['estimated_value'] >= 0.7)
    medium_value = sum(1 for f in features if 0.4 <= f['estimated_value'] < 0.7)
    low_value = sum(1 for f in features if f['estimated_value'] < 0.4)
    
    print(f"\nValue distribution:")
    print(f"  High value (≥0.7): {high_value}")
    print(f"  Medium value (0.4-0.7): {medium_value}")
    print(f"  Low value (<0.4): {low_value}")
    
    print(f"\nResults saved to: data/extracted_features.json")
    print(f"{'='*60}\n")

