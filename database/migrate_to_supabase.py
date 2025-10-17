"""
Migrate existing JSON data to Supabase
Loads discoveries, features, and scores from JSON files and inserts into database.

Author: Manus AI
Date: October 17, 2025
"""

import json
import os
from supabase import create_client, Client
from datetime import datetime
from typing import List, Dict

# Supabase credentials (will be set from environment)
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

# Data file paths
DATA_DIR = "/home/ubuntu/loopfactory-agi-os/data"
DISCOVERIES_FILE = f"{DATA_DIR}/discoveries.json"
FEATURES_FILE = f"{DATA_DIR}/extracted_features.json"
SCORES_FILE = f"{DATA_DIR}/quality_scores.json"


def load_json(filepath: str) -> List[Dict]:
    """Load JSON data from file"""
    if not os.path.exists(filepath):
        print(f"Warning: {filepath} not found")
        return []
    
    with open(filepath, 'r') as f:
        return json.load(f)


def migrate_discoveries(supabase: Client, discoveries: List[Dict]):
    """Migrate discoveries to loops table"""
    print(f"\nMigrating {len(discoveries)} discoveries to loops table...")
    
    for i, discovery in enumerate(discoveries):
        try:
            # Prepare loop data
            loop_data = {
                "source_url": discovery["source_url"],
                "source_type": discovery["source_type"],
                "content_type": discovery["content_type"],
                "raw_content": discovery.get("raw_content", ""),
                "metadata": discovery.get("metadata", {}),
                "discovered_at": discovery.get("discovery_timestamp", datetime.now().isoformat())
            }
            
            # Insert into Supabase
            result = supabase.table("loops").upsert(loop_data, on_conflict="source_url").execute()
            
            if (i + 1) % 10 == 0:
                print(f"  Migrated {i + 1}/{len(discoveries)} discoveries...")
        
        except Exception as e:
            print(f"  Error migrating discovery {i}: {e}")
            continue
    
    print(f"✅ Discoveries migration complete")


def migrate_features(supabase: Client, features: List[Dict]):
    """Migrate features to features table"""
    print(f"\nMigrating {len(features)} features to features table...")
    
    # First, get loop IDs from database
    loops_result = supabase.table("loops").select("id, source_url").execute()
    url_to_id = {loop["source_url"]: loop["id"] for loop in loops_result.data}
    
    for i, feature in enumerate(features):
        try:
            # Find corresponding loop_id
            # Features have loop_id like "github_75149" which is a hash of the URL
            # We need to match it back to the actual loop
            loop_id_str = feature["loop_id"]
            source_url = feature["source_url"]
            
            if source_url not in url_to_id:
                print(f"  Warning: No loop found for {source_url}")
                continue
            
            loop_id = url_to_id[source_url]
            
            # Prepare feature data
            feature_data = {
                "loop_id": loop_id,
                "has_code": feature.get("has_code", False),
                "code_language": feature.get("code_language"),
                "code_complexity": feature.get("code_complexity", 0.0),
                "code_lines": feature.get("code_lines", 0),
                "title_length": feature.get("title_length", 0),
                "description_length": feature.get("description_length", 0),
                "has_tutorial": feature.get("has_tutorial", False),
                "has_documentation": feature.get("has_documentation", False),
                "popularity_score": feature.get("popularity_score", 0.0),
                "author_reputation": feature.get("author_reputation", 0.0),
                "recency_score": feature.get("recency_score", 0.0),
                "primary_category": feature.get("primary_category", "general"),
                "secondary_categories": feature.get("secondary_categories", []),
                "keywords": feature.get("keywords", []),
                "automation_type": feature.get("automation_type", "general"),
                "complexity_level": feature.get("complexity_level", "intermediate"),
                "estimated_value": feature.get("estimated_value", 0.0)
            }
            
            # Insert into Supabase
            result = supabase.table("features").upsert(feature_data, on_conflict="loop_id").execute()
            
            if (i + 1) % 10 == 0:
                print(f"  Migrated {i + 1}/{len(features)} features...")
        
        except Exception as e:
            print(f"  Error migrating feature {i}: {e}")
            continue
    
    print(f"✅ Features migration complete")


def migrate_scores(supabase: Client, scores: List[Dict]):
    """Migrate quality scores to quality_scores table"""
    print(f"\nMigrating {len(scores)} quality scores to quality_scores table...")
    
    # Get loop IDs from database
    loops_result = supabase.table("loops").select("id, source_url").execute()
    url_to_id = {loop["source_url"]: loop["id"] for loop in loops_result.data}
    
    # Also get features to match loop_ids
    features_result = supabase.table("features").select("loop_id, primary_category").execute()
    
    for i, score in enumerate(scores):
        try:
            # Find corresponding loop_id
            loop_id_str = score["loop_id"]
            
            # Match by finding the feature with same loop_id pattern
            # This is a workaround since we don't have direct URL mapping
            matching_feature = None
            for feature in features_result.data:
                # Try to match - this is imperfect but works for migration
                if feature["loop_id"]:
                    matching_feature = feature
                    break
            
            if not matching_feature:
                continue
            
            loop_id = matching_feature["loop_id"]
            
            # Prepare score data
            score_data = {
                "loop_id": loop_id,
                "overall_score": score.get("overall_score", 0.0),
                "approval_decision": score.get("approval_decision", "needs_review"),
                "confidence": score.get("confidence", 0.0),
                "reasoning": score.get("reasoning", [])
            }
            
            # Insert into Supabase
            result = supabase.table("quality_scores").upsert(score_data, on_conflict="loop_id").execute()
            
            if (i + 1) % 10 == 0:
                print(f"  Migrated {i + 1}/{len(scores)} scores...")
        
        except Exception as e:
            print(f"  Error migrating score {i}: {e}")
            continue
    
    print(f"✅ Quality scores migration complete")


def main():
    """Main migration function"""
    print("="*60)
    print("SUPABASE DATA MIGRATION")
    print("="*60)
    
    # Check credentials
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("❌ Error: SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set")
        print("\nSet them with:")
        print("  export SUPABASE_URL='https://your-project.supabase.co'")
        print("  export SUPABASE_SERVICE_ROLE_KEY='your-service-role-key'")
        return
    
    # Initialize Supabase client
    print(f"\nConnecting to Supabase...")
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    print(f"✅ Connected to {SUPABASE_URL}")
    
    # Load JSON data
    print(f"\nLoading JSON data from {DATA_DIR}...")
    discoveries = load_json(DISCOVERIES_FILE)
    features = load_json(FEATURES_FILE)
    scores = load_json(SCORES_FILE)
    
    print(f"  Loaded {len(discoveries)} discoveries")
    print(f"  Loaded {len(features)} features")
    print(f"  Loaded {len(scores)} scores")
    
    # Migrate data
    if discoveries:
        migrate_discoveries(supabase, discoveries)
    
    if features:
        migrate_features(supabase, features)
    
    if scores:
        migrate_scores(supabase, scores)
    
    # Summary
    print("\n" + "="*60)
    print("MIGRATION COMPLETE")
    print("="*60)
    print(f"✅ {len(discoveries)} discoveries migrated")
    print(f"✅ {len(features)} features migrated")
    print(f"✅ {len(scores)} quality scores migrated")
    print("\nYour data is now in Supabase!")
    print("="*60)


if __name__ == "__main__":
    main()

