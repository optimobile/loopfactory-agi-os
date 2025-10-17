"""
AGI OS - Main Pipeline Orchestrator
Coordinates all components of the automation flywheel.

Author: Manus AI
Date: October 17, 2025
"""

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path

# Import components
from components.discovery.web_scraper import ScraperOrchestrator
from components.curation.feature_extractor import FeatureExtractor
from components.curation.quality_scorer import HeuristicQualityScorer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AGIOSPipeline:
    """Main pipeline orchestrator for AGI OS"""
    
    def __init__(self, data_dir: str = "/home/ubuntu/loopfactory-agi-os/data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        # Initialize components
        self.scraper = ScraperOrchestrator()
        self.feature_extractor = FeatureExtractor()
        self.quality_scorer = HeuristicQualityScorer()
        
        # File paths
        self.discoveries_file = self.data_dir / "discoveries.json"
        self.features_file = self.data_dir / "extracted_features.json"
        self.scores_file = self.data_dir / "quality_scores.json"
        self.approved_file = self.data_dir / "approved_loops.json"
        self.pipeline_stats_file = self.data_dir / "pipeline_stats.json"
    
    async def run_discovery(self) -> int:
        """Step 1: Run web scraping to discover loops"""
        logger.info("="*60)
        logger.info("STEP 1: DISCOVERY - Running web scrapers...")
        logger.info("="*60)
        
        discoveries = await self.scraper.run_all_agents()
        
        # Save discoveries
        self.scraper.save_discoveries(str(self.discoveries_file))
        
        logger.info(f"✅ Discovery complete: {len(discoveries)} loops found")
        return len(discoveries)
    
    def run_feature_extraction(self) -> int:
        """Step 2: Extract features from discoveries"""
        logger.info("="*60)
        logger.info("STEP 2: FEATURE EXTRACTION - Analyzing loops...")
        logger.info("="*60)
        
        features = self.feature_extractor.process_discoveries(
            str(self.discoveries_file),
            str(self.features_file)
        )
        
        logger.info(f"✅ Feature extraction complete: {len(features)} loops processed")
        return len(features)
    
    def run_quality_scoring(self) -> dict:
        """Step 3: Score loops for quality"""
        logger.info("="*60)
        logger.info("STEP 3: QUALITY SCORING - Evaluating loops...")
        logger.info("="*60)
        
        scores = self.quality_scorer.score_all_loops(
            str(self.features_file),
            str(self.scores_file)
        )
        
        summary = self.quality_scorer.get_summary()
        
        logger.info(f"✅ Quality scoring complete:")
        logger.info(f"   Approved: {summary['approved']}")
        logger.info(f"   Rejected: {summary['rejected']}")
        logger.info(f"   Needs Review: {summary['needs_review']}")
        
        return summary
    
    def filter_approved_loops(self) -> int:
        """Step 4: Filter and save approved loops"""
        logger.info("="*60)
        logger.info("STEP 4: FILTERING - Extracting approved loops...")
        logger.info("="*60)
        
        # Load scores
        with open(self.scores_file, 'r') as f:
            scores = json.load(f)
        
        # Load features
        with open(self.features_file, 'r') as f:
            features = json.load(f)
        
        # Load original discoveries
        with open(self.discoveries_file, 'r') as f:
            discoveries = json.load(f)
        
        # Create lookup dictionaries
        features_by_id = {f['loop_id']: f for f in features}
        
        # Filter approved loops
        approved_loops = []
        for score in scores:
            if score['approval_decision'] == 'approved':
                loop_id = score['loop_id']
                
                # Find corresponding feature and discovery
                feature = features_by_id.get(loop_id)
                if feature:
                    # Find original discovery by URL
                    discovery = next(
                        (d for d in discoveries if hash(d['source_url']) % 1000000 == int(loop_id.split('_')[1])),
                        None
                    )
                    
                    approved_loop = {
                        'loop_id': loop_id,
                        'score': score,
                        'features': feature,
                        'discovery': discovery
                    }
                    approved_loops.append(approved_loop)
        
        # Save approved loops
        with open(self.approved_file, 'w') as f:
            json.dump(approved_loops, f, indent=2)
        
        logger.info(f"✅ Filtering complete: {len(approved_loops)} approved loops saved")
        return len(approved_loops)
    
    def save_pipeline_stats(self, stats: dict):
        """Save pipeline statistics"""
        with open(self.pipeline_stats_file, 'w') as f:
            json.dump(stats, f, indent=2)
    
    async def run_full_pipeline(self):
        """Run the complete end-to-end pipeline"""
        start_time = datetime.now()
        
        logger.info("\n" + "="*60)
        logger.info("AGI OS PIPELINE - FULL EXECUTION")
        logger.info("="*60 + "\n")
        
        # Step 1: Discovery
        num_discoveries = await self.run_discovery()
        
        # Step 2: Feature Extraction
        num_features = self.run_feature_extraction()
        
        # Step 3: Quality Scoring
        scoring_summary = self.run_quality_scoring()
        
        # Step 4: Filter Approved
        num_approved = self.filter_approved_loops()
        
        # Calculate statistics
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        stats = {
            'timestamp': end_time.isoformat(),
            'duration_seconds': duration,
            'discoveries': num_discoveries,
            'features_extracted': num_features,
            'scoring_summary': scoring_summary,
            'approved_loops': num_approved,
            'approval_rate': scoring_summary['approval_rate'],
            'pipeline_status': 'success'
        }
        
        self.save_pipeline_stats(stats)
        
        # Print final summary
        logger.info("\n" + "="*60)
        logger.info("PIPELINE EXECUTION COMPLETE")
        logger.info("="*60)
        logger.info(f"Duration: {duration:.1f} seconds")
        logger.info(f"Discoveries: {num_discoveries}")
        logger.info(f"Approved: {num_approved} ({scoring_summary['approval_rate']*100:.1f}%)")
        logger.info(f"Ready for deployment: {num_approved} loops")
        logger.info("="*60 + "\n")
        
        return stats


# Main execution
if __name__ == "__main__":
    pipeline = AGIOSPipeline()
    
    # Run the full pipeline
    stats = asyncio.run(pipeline.run_full_pipeline())
    
    print("\n🎉 AGI OS Pipeline execution complete!")
    print(f"📊 {stats['approved_loops']} loops ready for deployment")
    print(f"📁 Results saved to: {pipeline.data_dir}")

