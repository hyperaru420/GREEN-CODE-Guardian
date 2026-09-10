from fastapi import APIRouter, Query, Depends
from database.connection import projects_collection, db
from typing import Optional
from datetime import datetime, timedelta
from api.auth_utils import get_current_user

router = APIRouter()

@router.get("/usage-stats")
async def get_usage_stats(current_user: dict = Depends(get_current_user)):
    """Get user usage statistics including scans, CO2 saved, teams, and projects."""
    try:
        user_id = str(current_user["_id"])
        total_projects = await projects_collection.count_documents({"user_id": user_id})
        
        pipeline = [
            {"$match": {"user_id": user_id}},
            {
                "$group": {
                    "_id": None,
                    "total_carbon_saved": {"$sum": "$carbon_emissions"},
                    "avg_green_score": {"$avg": "$green_score"},
                    "count": {"$sum": 1}
                }
            }
        ]
        
        metrics = await projects_collection.aggregate(pipeline).to_list(1)
        
        if metrics:
            total_co2 = metrics[0].get("total_carbon_saved", 0)
            avg_score = metrics[0].get("avg_green_score", 0)
            total_scans = metrics[0].get("count", 0)
        else:
            total_co2 = 0
            avg_score = 0
            total_scans = 0
        
        try:
            teams_collection = db["teams"]
            teams_count = await teams_collection.count_documents({"members": user_id})
        except:
            teams_count = 0
        
        return {
            "totalScans": int(total_scans),
            "totalCO2Saved": f"{total_co2:.2f}",
            "teamsJoined": int(teams_count),
            "projectsTracked": int(total_projects),
            "avgGreenScore": int(avg_score) if avg_score else 0,
            "lastUpdated": datetime.utcnow().isoformat()
        }
    except Exception as e:
        print(f"Error fetching usage stats: {e}")
        # Return demo data if there's an error
        return {
            "totalScans": 0,
            "totalCO2Saved": "0.00",
            "teamsJoined": 0,
            "projectsTracked": 0,
            "avgGreenScore": 0,
            "lastUpdated": datetime.utcnow().isoformat()
        }

@router.get("/profile")
async def get_user_profile(current_user: dict = Depends(get_current_user)):
    """Get user profile information."""
    try:
        return {
            "id": str(current_user.get("_id", "")),
            "name": current_user.get("name", "Demo User"),
            "email": current_user.get("email", "demo@example.com"),
            "created_at": current_user.get("created_at", datetime.utcnow()).isoformat() if isinstance(current_user.get("created_at"), datetime) else str(current_user.get("created_at", ""))
        }
    except Exception as e:
        print(f"Error fetching user profile: {e}")
        return {
            "id": "demo-user",
            "name": "Demo User",
            "email": "demo@example.com",
            "created_at": datetime.utcnow().isoformat()
        }