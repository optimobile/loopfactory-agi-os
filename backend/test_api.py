from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import json

app = FastAPI(title="Loop Factory AI - Test API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load mock data
try:
    with open('../data/discoveries.json') as f:
        discoveries = json.load(f)
    with open('../data/quality_scores.json') as f:
        scores = json.load(f)
except:
    discoveries = []
    scores = []

@app.get("/")
def root():
    return {"message": "Loop Factory AI API", "status": "operational"}

@app.get("/api/health")
def health():
    return {"status": "healthy", "agents": 1, "companies": 11}

@app.get("/api/stats")
def stats():
    return {
        "agents": 1,
        "companies": 11,
        "users": 150000,
        "loops_discovered": len(discoveries),
        "loops_approved": len([s for s in scores if s.get('decision') == 'approved'])
    }

@app.get("/api/agents")
def get_agents():
    return [{
        "id": "agent_001",
        "name": "KoiKeeper Water Quality Monitor",
        "description": "AI-powered water quality monitoring for koi ponds",
        "category": "koi_management",
        "price_usd": 29.00,
        "company": "KoiKeeper AI",
        "is_featured": True,
        "rating_average": 4.8,
        "rating_count": 127
    }]

@app.get("/api/companies")
def get_companies():
    companies = [
        {"id": 1, "name": "Loop Factory AI", "domain": "loopfactory.ai", "industry": "AI Automation"},
        {"id": 2, "name": "KoiKeeper AI", "domain": "koikeeper.ai", "industry": "Koi Management"},
        {"id": 3, "name": "FishKeeper AI", "domain": "fishkeeper.ai", "industry": "Aquarium Management"},
        {"id": 4, "name": "LandLaw AI", "domain": "landlaw.ai", "industry": "Property Legal"},
        {"id": 5, "name": "Social Media Mananger AI", "domain": "socialmediamananger.ai", "industry": "Social Media"},
        {"id": 6, "name": "MuckAway AI", "domain": "muckaway.ai", "industry": "Waste Management"},
        {"id": 7, "name": "GrabHire AI", "domain": "grabhire.ai", "industry": "Equipment Rental"},
        {"id": 8, "name": "PlantHire AI", "domain": "planthire.ai", "industry": "Plant Rental"},
        {"id": 9, "name": "DIYHelp AI", "domain": "diyhelp.ai", "industry": "DIY"},
        {"id": 10, "name": "PokerHUD AI", "domain": "pokerhud.ai", "industry": "Poker Analytics"},
        {"id": 11, "name": "CommercialVehicle AI", "domain": "commercialvehicle.ai", "industry": "Fleet Management"}
    ]
    return companies

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
