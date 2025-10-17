"""
Loop Factory AI - Backend API
FastAPI application serving all 11 companies

Author: Manus AI
Date: October 17, 2025
"""

from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
from supabase import create_client, Client
from datetime import datetime

# Initialize FastAPI
app = FastAPI(
    title="Loop Factory AI API",
    description="AI Agent Marketplace API powering 11 industry-specific companies",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Supabase client
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")

def get_supabase() -> Client:
    """Get Supabase client"""
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise HTTPException(status_code=500, detail="Supabase not configured")
    return create_client(SUPABASE_URL, SUPABASE_KEY)


# ============================================================================
# MODELS
# ============================================================================

class Company(BaseModel):
    id: str
    name: str
    slug: str
    domain: str
    industry: str
    description: Optional[str]
    logo_url: Optional[str]
    is_active: bool


class Agent(BaseModel):
    id: str
    name: str
    slug: str
    description: Optional[str]
    category: Optional[str]
    price_usd: float
    rating_average: float
    rating_count: int
    is_featured: bool


class AgentDetail(Agent):
    long_description: Optional[str]
    tags: List[str]
    pricing_model: str
    view_count: int
    purchase_count: int


# ============================================================================
# ROUTES - COMPANIES
# ============================================================================

@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "name": "Loop Factory AI API",
        "version": "1.0.0",
        "status": "operational",
        "companies": 11,
        "documentation": "/docs"
    }


@app.get("/api/companies", response_model=List[Company])
async def list_companies(
    supabase: Client = Depends(get_supabase)
):
    """List all active companies"""
    try:
        result = supabase.table("companies").select("*").eq("is_active", True).execute()
        return result.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/companies/{slug}", response_model=Company)
async def get_company(
    slug: str,
    supabase: Client = Depends(get_supabase)
):
    """Get company by slug"""
    try:
        result = supabase.table("companies").select("*").eq("slug", slug).single().execute()
        if not result.data:
            raise HTTPException(status_code=404, detail="Company not found")
        return result.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# ROUTES - AGENTS
# ============================================================================

@app.get("/api/agents", response_model=List[Agent])
async def list_agents(
    company_slug: Optional[str] = None,
    category: Optional[str] = None,
    featured: Optional[bool] = None,
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0),
    supabase: Client = Depends(get_supabase)
):
    """List agents with optional filtering"""
    try:
        query = supabase.table("agents").select("*").eq("is_active", True)
        
        if company_slug:
            # Get company ID first
            company = supabase.table("companies").select("id").eq("slug", company_slug).single().execute()
            if company.data:
                query = query.eq("company_id", company.data["id"])
        
        if category:
            query = query.eq("category", category)
        
        if featured is not None:
            query = query.eq("is_featured", featured)
        
        result = query.order("created_at", desc=True).range(offset, offset + limit - 1).execute()
        return result.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/agents/{slug}", response_model=AgentDetail)
async def get_agent(
    slug: str,
    supabase: Client = Depends(get_supabase)
):
    """Get agent details by slug"""
    try:
        result = supabase.table("agents").select("*").eq("slug", slug).single().execute()
        if not result.data:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # Increment view count
        supabase.table("agents").update({
            "view_count": result.data["view_count"] + 1
        }).eq("id", result.data["id"]).execute()
        
        return result.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# ROUTES - SEARCH
# ============================================================================

@app.get("/api/search")
async def search_agents(
    q: str = Query(..., min_length=2),
    limit: int = Query(20, le=50),
    supabase: Client = Depends(get_supabase)
):
    """Search agents by name, description, or tags"""
    try:
        # Simple text search (can be improved with full-text search)
        result = supabase.table("agents").select("*").eq("is_active", True).ilike("name", f"%{q}%").limit(limit).execute()
        return result.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# ROUTES - BLOG
# ============================================================================

@app.get("/api/blog")
async def list_blog_posts(
    company_slug: Optional[str] = None,
    limit: int = Query(10, le=50),
    offset: int = Query(0, ge=0),
    supabase: Client = Depends(get_supabase)
):
    """List published blog posts"""
    try:
        query = supabase.table("blog_posts").select("*").eq("is_published", True)
        
        if company_slug:
            company = supabase.table("companies").select("id").eq("slug", company_slug).single().execute()
            if company.data:
                query = query.eq("company_id", company.data["id"])
        
        result = query.order("published_at", desc=True).range(offset, offset + limit - 1).execute()
        return result.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/blog/{slug}")
async def get_blog_post(
    slug: str,
    company_slug: str,
    supabase: Client = Depends(get_supabase)
):
    """Get blog post by slug"""
    try:
        # Get company ID
        company = supabase.table("companies").select("id").eq("slug", company_slug).single().execute()
        if not company.data:
            raise HTTPException(status_code=404, detail="Company not found")
        
        result = supabase.table("blog_posts").select("*").eq("slug", slug).eq("company_id", company.data["id"]).single().execute()
        if not result.data:
            raise HTTPException(status_code=404, detail="Blog post not found")
        
        # Increment view count
        supabase.table("blog_posts").update({
            "view_count": result.data["view_count"] + 1
        }).eq("id", result.data["id"]).execute()
        
        return result.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# ROUTES - STATS
# ============================================================================

@app.get("/api/stats")
async def get_stats(
    supabase: Client = Depends(get_supabase)
):
    """Get platform statistics"""
    try:
        # Count agents
        agents_result = supabase.table("agents").select("id", count="exact").eq("is_active", True).execute()
        
        # Count companies
        companies_result = supabase.table("companies").select("id", count="exact").eq("is_active", True).execute()
        
        # Count users (if accessible)
        users_count = 0
        try:
            users_result = supabase.table("users").select("id", count="exact").execute()
            users_count = users_result.count
        except:
            pass
        
        return {
            "agents": agents_result.count,
            "companies": companies_result.count,
            "users": users_count,
            "last_updated": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# HEALTH CHECK
# ============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

