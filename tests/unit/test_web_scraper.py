"""
Unit tests for Web Scraper component
"""

import pytest
from components.discovery.web_scraper import (
    LoopDiscovery,
    BaseScraperAgent,
    GitHubScraperAgent,
    RedditScraperAgent
)


class TestLoopDiscovery:
    """Test LoopDiscovery data class"""
    
    def test_loop_discovery_creation(self):
        """Test creating a LoopDiscovery object"""
        discovery = LoopDiscovery(
            source_url="https://github.com/test/repo",
            source_type="github",
            content_type="text_description",
            raw_content="Test automation script",
            metadata={"title": "Test Repo", "stars": "100"}
        )
        
        assert discovery.source_url == "https://github.com/test/repo"
        assert discovery.source_type == "github"
        assert discovery.content_type == "text_description"
        assert discovery.raw_content == "Test automation script"
        assert discovery.metadata["title"] == "Test Repo"
    
    def test_loop_discovery_to_dict(self):
        """Test converting LoopDiscovery to dictionary"""
        discovery = LoopDiscovery(
            source_url="https://test.com",
            source_type="test",
            content_type="text",
            raw_content="content",
            metadata={}
        )
        
        d = discovery.to_dict()
        assert isinstance(d, dict)
        assert "source_url" in d
        assert "discovery_timestamp" in d
    
    def test_loop_discovery_to_json(self):
        """Test converting LoopDiscovery to JSON"""
        discovery = LoopDiscovery(
            source_url="https://test.com",
            source_type="test",
            content_type="text",
            raw_content="content",
            metadata={}
        )
        
        json_str = discovery.to_json()
        assert isinstance(json_str, str)
        assert "source_url" in json_str


class TestBaseScraperAgent:
    """Test BaseScraperAgent functionality"""
    
    def test_matches_keywords(self):
        """Test keyword matching"""
        agent = BaseScraperAgent(
            name="Test Agent",
            target_urls=[],
            keywords=["automation", "script", "bot"]
        )
        
        assert agent.matches_keywords("This is an automation tool")
        assert agent.matches_keywords("Python script for testing")
        assert agent.matches_keywords("Build a bot")
        assert not agent.matches_keywords("Random text without keywords")
    
    def test_matches_keywords_case_insensitive(self):
        """Test that keyword matching is case-insensitive"""
        agent = BaseScraperAgent(
            name="Test Agent",
            target_urls=[],
            keywords=["Automation"]
        )
        
        assert agent.matches_keywords("automation tool")
        assert agent.matches_keywords("AUTOMATION TOOL")
        assert agent.matches_keywords("AuToMaTiOn ToOl")


class TestGitHubScraperAgent:
    """Test GitHubScraperAgent"""
    
    def test_initialization(self):
        """Test GitHubScraperAgent initialization"""
        agent = GitHubScraperAgent()
        
        assert agent.name == "GitHub Scraper"
        assert len(agent.target_urls) > 0
        assert len(agent.keywords) > 0
        assert "automation" in agent.keywords


class TestRedditScraperAgent:
    """Test RedditScraperAgent"""
    
    def test_initialization(self):
        """Test RedditScraperAgent initialization"""
        agent = RedditScraperAgent()
        
        assert agent.name == "Reddit Scraper"
        assert len(agent.target_urls) > 0
        assert len(agent.keywords) > 0
        assert "automation" in agent.keywords

