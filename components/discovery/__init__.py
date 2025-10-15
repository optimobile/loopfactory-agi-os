"""
Discovery Component - Zone 1 of AGI OS

Responsible for discovering automation opportunities from various sources:
- Web scraping (GitHub, Reddit, forums)
- Desktop observation (Phase 4)
- User submissions
"""

from .web_scraper import (
    LoopDiscovery,
    BaseScraperAgent,
    GitHubScraperAgent,
    RedditScraperAgent,
    ScraperOrchestrator
)

__all__ = [
    'LoopDiscovery',
    'BaseScraperAgent',
    'GitHubScraperAgent',
    'RedditScraperAgent',
    'ScraperOrchestrator'
]

