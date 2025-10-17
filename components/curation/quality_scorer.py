"""
Heuristic Quality Scorer - Component 2b
Scores loops based on extracted features using rule-based heuristics.
This will be replaced by RL agent in Phase 2.

Author: Manus AI
Date: October 17, 2025
"""

import json
import logging
from typing import Dict, List
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class QualityScore:
    """Quality score for a loop"""
    loop_id: str
    overall_score: float  # 0-1 scale
    approval_decision: str  # approved, rejected, needs_review
    confidence: float  # 0-1 scale
    reasoning: List[str]  # Explanation of score
    
    def to_dict(self) -> Dict:
        return {
            "loop_id": self.loop_id,
            "overall_score": self.overall_score,
            "approval_decision": self.approval_decision,
            "confidence": self.confidence,
            "reasoning": self.reasoning
        }


class HeuristicQualityScorer:
    """Rule-based quality scoring system (v1)"""
    
    # Scoring weights
    WEIGHTS = {
        'popularity': 0.25,
        'code_quality': 0.20,
        'content_quality': 0.20,
        'categorization': 0.15,
        'recency': 0.10,
        'author': 0.10
    }
    
    # Approval thresholds
    APPROVAL_THRESHOLD = 0.60  # Score >= 0.60 = approved
    REJECTION_THRESHOLD = 0.35  # Score < 0.35 = rejected
    # Between 0.35 and 0.60 = needs_review
    
    def __init__(self):
        self.approved_count = 0
        self.rejected_count = 0
        self.review_count = 0
    
    def score_loop(self, features: Dict) -> QualityScore:
        """Score a single loop based on extracted features"""
        
        loop_id = features['loop_id']
        reasoning = []
        
        # 1. Popularity Score (25%)
        popularity_score = features['popularity_score']
        popularity_weight = self.WEIGHTS['popularity'] * popularity_score
        
        if popularity_score >= 0.7:
            reasoning.append(f"High popularity (score: {popularity_score:.2f})")
        elif popularity_score <= 0.2:
            reasoning.append(f"Low popularity (score: {popularity_score:.2f})")
        
        # 2. Code Quality Score (20%)
        code_quality_score = 0.0
        if features['has_code']:
            code_quality_score = min(
                features['code_complexity'] * 0.6 +
                min(features['code_lines'] / 100.0, 1.0) * 0.4,
                1.0
            )
            reasoning.append(f"Contains code (complexity: {features['code_complexity']:.2f})")
        else:
            code_quality_score = 0.3  # Text-only loops get lower score
            reasoning.append("No code detected")
        
        code_weight = self.WEIGHTS['code_quality'] * code_quality_score
        
        # 3. Content Quality Score (20%)
        content_quality_score = 0.0
        
        # Length indicators
        if features['description_length'] >= 200:
            content_quality_score += 0.4
            reasoning.append("Detailed description")
        elif features['description_length'] < 50:
            content_quality_score += 0.1
            reasoning.append("Very short description")
        else:
            content_quality_score += 0.25
        
        # Tutorial/documentation bonus
        if features['has_tutorial']:
            content_quality_score += 0.3
            reasoning.append("Has tutorial content")
        
        if features['has_documentation']:
            content_quality_score += 0.3
            reasoning.append("Has documentation")
        
        content_quality_score = min(content_quality_score, 1.0)
        content_weight = self.WEIGHTS['content_quality'] * content_quality_score
        
        # 4. Categorization Score (15%)
        categorization_score = 0.0
        
        # Prefer specific automation categories
        high_value_categories = ['automation', 'web_scraping', 'api_wrapper', 'bot', 'data_processing']
        if features['primary_category'] in high_value_categories:
            categorization_score = 0.8
            reasoning.append(f"High-value category: {features['primary_category']}")
        elif features['primary_category'] == 'general':
            categorization_score = 0.3
            reasoning.append("General category (unclear automation value)")
        else:
            categorization_score = 0.5
        
        categorization_weight = self.WEIGHTS['categorization'] * categorization_score
        
        # 5. Recency Score (10%)
        recency_score = features['recency_score']
        recency_weight = self.WEIGHTS['recency'] * recency_score
        
        # 6. Author Reputation Score (10%)
        author_score = features['author_reputation']
        author_weight = self.WEIGHTS['author'] * author_score
        
        # Calculate overall score
        overall_score = (
            popularity_weight +
            code_weight +
            content_weight +
            categorization_weight +
            recency_weight +
            author_weight
        )
        
        # Make approval decision
        if overall_score >= self.APPROVAL_THRESHOLD:
            decision = "approved"
            self.approved_count += 1
            confidence = min((overall_score - self.APPROVAL_THRESHOLD) / (1.0 - self.APPROVAL_THRESHOLD), 1.0)
        elif overall_score < self.REJECTION_THRESHOLD:
            decision = "rejected"
            self.rejected_count += 1
            confidence = min((self.REJECTION_THRESHOLD - overall_score) / self.REJECTION_THRESHOLD, 1.0)
        else:
            decision = "needs_review"
            self.review_count += 1
            confidence = 0.5
        
        reasoning.append(f"Overall score: {overall_score:.2f} → {decision}")
        
        return QualityScore(
            loop_id=loop_id,
            overall_score=overall_score,
            approval_decision=decision,
            confidence=confidence,
            reasoning=reasoning
        )
    
    def score_all_loops(self, features_file: str, output_file: str) -> List[QualityScore]:
        """Score all loops from extracted features"""
        
        logger.info(f"Loading features from {features_file}...")
        with open(features_file, 'r') as f:
            all_features = json.load(f)
        
        logger.info(f"Scoring {len(all_features)} loops...")
        
        scores = []
        for i, features in enumerate(all_features):
            try:
                score = self.score_loop(features)
                scores.append(score)
                
                if (i + 1) % 10 == 0:
                    logger.info(f"Scored {i + 1}/{len(all_features)} loops...")
            
            except Exception as e:
                logger.error(f"Error scoring loop {i}: {e}")
                continue
        
        logger.info(f"Saving scores to {output_file}...")
        with open(output_file, 'w') as f:
            json.dump([s.to_dict() for s in scores], f, indent=2)
        
        logger.info(f"Quality scoring complete.")
        
        return scores
    
    def get_summary(self) -> Dict:
        """Get summary statistics"""
        total = self.approved_count + self.rejected_count + self.review_count
        return {
            "total": total,
            "approved": self.approved_count,
            "rejected": self.rejected_count,
            "needs_review": self.review_count,
            "approval_rate": self.approved_count / total if total > 0 else 0,
            "rejection_rate": self.rejected_count / total if total > 0 else 0
        }


# Main execution
if __name__ == "__main__":
    scorer = HeuristicQualityScorer()
    
    # Score all loops
    scores = scorer.score_all_loops(
        features_file="/home/ubuntu/loopfactory-agi-os/data/extracted_features.json",
        output_file="/home/ubuntu/loopfactory-agi-os/data/quality_scores.json"
    )
    
    # Print summary
    summary = scorer.get_summary()
    
    print(f"\n{'='*60}")
    print(f"QUALITY SCORING COMPLETE")
    print(f"{'='*60}")
    print(f"Total loops scored: {summary['total']}")
    print(f"\nDecision breakdown:")
    print(f"  ✅ Approved: {summary['approved']} ({summary['approval_rate']*100:.1f}%)")
    print(f"  ❌ Rejected: {summary['rejected']} ({summary['rejection_rate']*100:.1f}%)")
    print(f"  ⚠️  Needs Review: {summary['needs_review']} ({(summary['needs_review']/summary['total'])*100:.1f}%)")
    
    # Show some approved loops
    approved_loops = [s for s in scores if s.approval_decision == "approved"]
    if approved_loops:
        print(f"\n✅ Sample approved loops:")
        for loop in approved_loops[:5]:
            print(f"\n  Loop ID: {loop.loop_id}")
            print(f"  Score: {loop.overall_score:.2f}")
            print(f"  Confidence: {loop.confidence:.2f}")
            print(f"  Reasoning: {'; '.join(loop.reasoning[:3])}")
    
    print(f"\nResults saved to: data/quality_scores.json")
    print(f"{'='*60}\n")

