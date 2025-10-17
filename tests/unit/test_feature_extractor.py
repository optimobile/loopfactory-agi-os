"""
Unit tests for Feature Extractor component
"""

import pytest
from components.curation.feature_extractor import (
    CodeAnalyzer,
    TextAnalyzer,
    QualityScorer,
    FeatureExtractor
)


class TestCodeAnalyzer:
    """Test CodeAnalyzer functionality"""
    
    def test_detect_python(self):
        """Test Python language detection"""
        code = "import os\ndef main():\n    pass"
        assert CodeAnalyzer.detect_language(code) == 'python'
    
    def test_detect_javascript(self):
        """Test JavaScript language detection"""
        code = "function test() { return true; }"
        assert CodeAnalyzer.detect_language(code) == 'javascript'
    
    def test_count_lines(self):
        """Test line counting"""
        code = "line1\nline2\n\nline3\n  \nline4"
        assert CodeAnalyzer.count_lines(code) == 4  # Empty lines not counted
    
    def test_calculate_complexity_simple(self):
        """Test complexity calculation for simple code"""
        code = "x = 1\ny = 2"
        complexity = CodeAnalyzer.calculate_complexity(code, 'python')
        assert 0 <= complexity <= 1


class TestTextAnalyzer:
    """Test TextAnalyzer functionality"""
    
    def test_extract_keywords(self):
        """Test keyword extraction"""
        text = "This is a test automation script for web scraping"
        keywords = TextAnalyzer.extract_keywords(text)
        
        assert isinstance(keywords, list)
        assert len(keywords) > 0
        assert "automation" in keywords or "script" in keywords
    
    def test_categorize_automation(self):
        """Test categorization for automation content"""
        text = "Automate your workflow with this script"
        primary, secondary = TextAnalyzer.categorize(text)
        
        assert primary == 'automation'
    
    def test_categorize_web_scraping(self):
        """Test categorization for web scraping content"""
        text = "BeautifulSoup scraper for extracting data"
        primary, secondary = TextAnalyzer.categorize(text)
        
        assert primary == 'web_scraping'
    
    def test_detect_complexity_beginner(self):
        """Test complexity level detection for beginner content"""
        text = "Simple tutorial for beginners to learn Python"
        level = TextAnalyzer.detect_complexity_level(text)
        
        assert level == 'beginner'
    
    def test_detect_complexity_advanced(self):
        """Test complexity level detection for advanced content"""
        text = "Advanced production-ready scalable system"
        level = TextAnalyzer.detect_complexity_level(text)
        
        assert level == 'advanced'
    
    def test_has_tutorial_indicators(self):
        """Test tutorial detection"""
        assert TextAnalyzer.has_tutorial_indicators("Step by step tutorial")
        assert TextAnalyzer.has_tutorial_indicators("How to build a bot")
        assert not TextAnalyzer.has_tutorial_indicators("Random text")
    
    def test_has_documentation_indicators(self):
        """Test documentation detection"""
        assert TextAnalyzer.has_documentation_indicators("See the documentation")
        assert TextAnalyzer.has_documentation_indicators("API reference manual")
        assert not TextAnalyzer.has_documentation_indicators("Random text")


class TestQualityScorer:
    """Test QualityScorer functionality"""
    
    def test_calculate_popularity_github(self):
        """Test popularity calculation for GitHub"""
        metadata = {"stars": "1,500 stars this week"}
        score = QualityScorer.calculate_popularity_score(metadata, 'github')
        
        assert 0 <= score <= 1
        assert score > 0.5  # 1500 stars should be high
    
    def test_calculate_popularity_reddit(self):
        """Test popularity calculation for Reddit"""
        metadata = {"upvotes": "50"}
        score = QualityScorer.calculate_popularity_score(metadata, 'reddit')
        
        assert 0 <= score <= 1
        assert score == 0.5  # 50 upvotes = 0.5
    
    def test_calculate_author_reputation(self):
        """Test author reputation calculation"""
        metadata = {"author": "test_user"}
        score = QualityScorer.calculate_author_reputation(metadata, 'github')
        
        assert 0 <= score <= 1
    
    def test_estimate_value(self):
        """Test value estimation"""
        features = {
            'popularity_score': 0.8,
            'code_complexity': 0.6,
            'author_reputation': 0.7,
            'has_code': True
        }
        value = QualityScorer.estimate_value(features)
        
        assert 0 <= value <= 1
        assert value > 0.5  # High scores should give high value

