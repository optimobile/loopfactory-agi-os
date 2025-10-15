"""
Web Scraping Agents - Component 1
Autonomously scan the internet for potential automation loops.

Author: Manus AI
Date: October 15, 2025
"""

import asyncio
import json
import logging
import re
from datetime import datetime
from typing import Dict, List, Optional
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LoopDiscovery:
    """Data class for discovered loops"""
    
    def __init__(
        self,
        source_url: str,
        source_type: str,
        content_type: str,
        raw_content: str,
        metadata: Dict
    ):
        self.source_url = source_url
        self.discovery_timestamp = datetime.utcnow().isoformat()
        self.source_type = source_type
        self.content_type = content_type
        self.raw_content = raw_content
        self.metadata = metadata
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "source_url": self.source_url,
            "discovery_timestamp": self.discovery_timestamp,
            "source_type": self.source_type,
            "content_type": self.content_type,
            "raw_content": self.raw_content,
            "metadata": self.metadata
        }
    
    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), indent=2)


class BaseScraperAgent:
    """Base class for all scraper agents"""
    
    def __init__(self, name: str, target_urls: List[str], keywords: List[str]):
        self.name = name
        self.target_urls = target_urls
        self.keywords = keywords
        self.discovered_loops = []
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; AGI-OS-Bot/1.0; +https://loopfactory.ai)'
        })
    
    def matches_keywords(self, text: str) -> bool:
        """Check if text contains any of the target keywords"""
        text_lower = text.lower()
        return any(keyword.lower() in text_lower for keyword in self.keywords)
    
    def extract_code_blocks(self, soup: BeautifulSoup) -> List[str]:
        """Extract code blocks from HTML"""
        code_blocks = []
        
        # Find <pre> and <code> tags
        for tag in soup.find_all(['pre', 'code']):
            code = tag.get_text(strip=True)
            if code and len(code) > 50:  # Minimum length filter
                code_blocks.append(code)
        
        return code_blocks
    
    def scrape(self) -> List[LoopDiscovery]:
        """Main scraping method - to be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement scrape()")


class GitHubScraperAgent(BaseScraperAgent):
    """Scraper agent for GitHub trending repositories and code snippets"""
    
    def __init__(self):
        super().__init__(
            name="GitHub Scraper",
            target_urls=[
                "https://github.com/trending/python",
                "https://github.com/trending/python?since=daily",
                "https://github.com/trending/python?since=weekly"
            ],
            keywords=[
                "automation", "script", "bot", "workflow", "task",
                "automate", "scheduler", "scraper", "api wrapper"
            ]
        )
    
    def scrape(self) -> List[LoopDiscovery]:
        """Scrape GitHub trending for automation-related repositories"""
        logger.info(f"[{self.name}] Starting scraping cycle...")
        
        for url in self.target_urls:
            try:
                response = self.session.get(url, timeout=10)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find repository articles
                repos = soup.find_all('article', class_='Box-row')
                
                for repo in repos:
                    try:
                        # Extract repository information
                        title_elem = repo.find('h2', class_='h3')
                        if not title_elem:
                            continue
                        
                        repo_link = title_elem.find('a')
                        if not repo_link:
                            continue
                        
                        repo_name = repo_link.get_text(strip=True)
                        repo_url = urljoin("https://github.com", repo_link['href'])
                        
                        # Extract description
                        desc_elem = repo.find('p', class_='col-9')
                        description = desc_elem.get_text(strip=True) if desc_elem else ""
                        
                        # Check if matches keywords
                        if self.matches_keywords(f"{repo_name} {description}"):
                            # Extract stars
                            stars_elem = repo.find('span', class_='d-inline-block float-sm-right')
                            stars = stars_elem.get_text(strip=True) if stars_elem else "0"
                            
                            # Create discovery object
                            discovery = LoopDiscovery(
                                source_url=repo_url,
                                source_type="github",
                                content_type="text_description",
                                raw_content=description,
                                metadata={
                                    "title": repo_name,
                                    "author": repo_url.split('/')[3],
                                    "stars": stars,
                                    "language": "python"
                                }
                            )
                            
                            self.discovered_loops.append(discovery)
                            logger.info(f"[{self.name}] Discovered: {repo_name}")
                    
                    except Exception as e:
                        logger.error(f"[{self.name}] Error processing repo: {e}")
                        continue
            
            except Exception as e:
                logger.error(f"[{self.name}] Error scraping {url}: {e}")
                continue
        
        logger.info(f"[{self.name}] Scraping complete. Discovered {len(self.discovered_loops)} loops.")
        return self.discovered_loops


class RedditScraperAgent(BaseScraperAgent):
    """Scraper agent for Reddit automation-related subreddits"""
    
    def __init__(self):
        super().__init__(
            name="Reddit Scraper",
            target_urls=[
                "https://old.reddit.com/r/Python/",
                "https://old.reddit.com/r/learnpython/",
                "https://old.reddit.com/r/automation/",
                "https://old.reddit.com/r/AutomateYourself/"
            ],
            keywords=[
                "script", "automation", "automate", "bot", "workflow",
                "how to", "tutorial", "code", "python"
            ]
        )
    
    def scrape(self) -> List[LoopDiscovery]:
        """Scrape Reddit for automation discussions and code snippets"""
        logger.info(f"[{self.name}] Starting scraping cycle...")
        
        for url in self.target_urls:
            try:
                response = self.session.get(url, timeout=10)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find posts
                posts = soup.find_all('div', class_='thing')
                
                for post in posts[:25]:  # Limit to top 25 posts
                    try:
                        # Extract post information
                        title_elem = post.find('a', class_='title')
                        if not title_elem:
                            continue
                        
                        title = title_elem.get_text(strip=True)
                        post_url = title_elem.get('href', '')
                        
                        # Make URL absolute
                        if post_url.startswith('/r/'):
                            post_url = f"https://old.reddit.com{post_url}"
                        
                        # Check if matches keywords
                        if self.matches_keywords(title):
                            # Extract upvotes
                            score_elem = post.find('div', class_='score')
                            upvotes = score_elem.get_text(strip=True) if score_elem else "0"
                            
                            # Extract author
                            author_elem = post.find('a', class_='author')
                            author = author_elem.get_text(strip=True) if author_elem else "unknown"
                            
                            # Extract subreddit
                            subreddit_elem = post.find('a', class_='subreddit')
                            subreddit = subreddit_elem.get_text(strip=True) if subreddit_elem else ""
                            
                            # Create discovery object
                            discovery = LoopDiscovery(
                                source_url=post_url,
                                source_type="reddit",
                                content_type="text_description",
                                raw_content=title,
                                metadata={
                                    "title": title,
                                    "author": author,
                                    "upvotes": upvotes,
                                    "subreddit": subreddit
                                }
                            )
                            
                            self.discovered_loops.append(discovery)
                            logger.info(f"[{self.name}] Discovered: {title[:50]}...")
                    
                    except Exception as e:
                        logger.error(f"[{self.name}] Error processing post: {e}")
                        continue
            
            except Exception as e:
                logger.error(f"[{self.name}] Error scraping {url}: {e}")
                continue
        
        logger.info(f"[{self.name}] Scraping complete. Discovered {len(self.discovered_loops)} loops.")
        return self.discovered_loops


class ScraperOrchestrator:
    """Orchestrates multiple scraper agents"""
    
    def __init__(self):
        self.agents = [
            GitHubScraperAgent(),
            RedditScraperAgent()
        ]
        self.all_discoveries = []
    
    async def run_agent(self, agent: BaseScraperAgent) -> List[LoopDiscovery]:
        """Run a single agent asynchronously"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, agent.scrape)
    
    async def run_all_agents(self) -> List[LoopDiscovery]:
        """Run all agents in parallel"""
        logger.info("Starting scraper orchestrator...")
        
        tasks = [self.run_agent(agent) for agent in self.agents]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Agent failed with error: {result}")
            else:
                self.all_discoveries.extend(result)
        
        logger.info(f"All agents complete. Total discoveries: {len(self.all_discoveries)}")
        return self.all_discoveries
    
    def save_discoveries(self, filepath: str = "discoveries.json"):
        """Save all discoveries to a JSON file"""
        with open(filepath, 'w') as f:
            json.dump(
                [d.to_dict() for d in self.all_discoveries],
                f,
                indent=2
            )
        logger.info(f"Discoveries saved to {filepath}")


# Main execution
if __name__ == "__main__":
    orchestrator = ScraperOrchestrator()
    
    # Run the scraping cycle
    discoveries = asyncio.run(orchestrator.run_all_agents())
    
    # Save results
    orchestrator.save_discoveries("/home/ubuntu/loopfactory-agi-os/data/discoveries.json")
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"SCRAPING CYCLE COMPLETE")
    print(f"{'='*60}")
    print(f"Total discoveries: {len(discoveries)}")
    print(f"\nBreakdown by source:")
    
    source_counts = {}
    for d in discoveries:
        source_counts[d.source_type] = source_counts.get(d.source_type, 0) + 1
    
    for source, count in source_counts.items():
        print(f"  {source}: {count}")
    
    print(f"\nResults saved to: data/discoveries.json")
    print(f"{'='*60}\n")

