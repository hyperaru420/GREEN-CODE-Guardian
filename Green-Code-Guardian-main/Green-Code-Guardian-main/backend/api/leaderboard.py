"""
Leaderboard router for competitive rankings and team analytics.
Features: Global leaderboard, team leaderboards, weekly/monthly challenges.
"""

from fastapi import APIRouter, Query, HTTPException, Depends
from database.connection import projects_collection, users_collection, teams_collection
from datetime import datetime, timedelta
from typing import Optional
from api.auth_utils import get_current_user

router = APIRouter()


@router.get("/global")
async def get_global_leaderboard(
    period: str = Query("all", regex="^(week|month|all)$"),
    limit: int = Query(50, ge=1, le=100),
    region: Optional[str] = None
):
    """
    Get global leaderboard ranked by average green score.
    
    Periods:
    - week: Last 7 days
    - month: Last 30 days
    - all: All-time
    """
    
    # Calculate date threshold
    query = {}
    if period == "week":
        threshold_date = datetime.utcnow() - timedelta(days=7)
        query["timestamp"] = {"$gte": threshold_date}
    elif period == "month":
        threshold_date = datetime.utcnow() - timedelta(days=30)
        query["timestamp"] = {"$gte": threshold_date}
    
    if region:
        query["region"] = region
    
    # Aggregate by project to get average scores
    pipeline = [
        {"$match": query},
        {
            "$group": {
                "_id": "$project_name",
                "avg_score": {"$avg": "$green_score"},
                "avg_carbon": {"$avg": "$carbon_emissions"},
                "total_scans": {"$sum": 1},
                "last_scan": {"$max": "$timestamp"},
                "region": {"$first": "$region"}
            }
        },
        {"$sort": {"avg_score": -1}},
        {"$limit": limit}
    ]
    
    results = await projects_collection.aggregate(pipeline).to_list(None)
    
    # Format response with ranking
    leaderboard = [
        {
            "rank": idx + 1,
            "project": result["_id"],
            "green_score": round(result["avg_score"], 2),
            "carbon_emissions": round(result["avg_carbon"], 2),
            "total_scans": result["total_scans"],
            "last_scan": result["last_scan"],
            "region": result.get("region", "unknown")
        }
        for idx, result in enumerate(results)
    ]
    
    return {
        "period": period,
        "total_entries": len(leaderboard),
        "leaderboard": leaderboard
    }


@router.get("/me")
async def get_my_leaderboard(
    current_user: dict = Depends(get_current_user),
    period: str = Query("all", regex="^(week|month|all)$"),
    limit: int = Query(50, ge=1, le=100)
):
    """Get leaderboard for the authenticated user's projects."""
    user_id = str(current_user["_id"])

    query = {"user_id": user_id}
    if period == "week":
        threshold_date = datetime.utcnow() - timedelta(days=7)
        query["timestamp"] = {"$gte": threshold_date}
    elif period == "month":
        threshold_date = datetime.utcnow() - timedelta(days=30)
        query["timestamp"] = {"$gte": threshold_date}

    pipeline = [
        {"$match": query},
        {
            "$group": {
                "_id": "$project_name",
                "avg_score": {"$avg": "$green_score"},
                "avg_carbon": {"$avg": "$carbon_emissions"},
                "total_scans": {"$sum": 1},
                "last_scan": {"$max": "$timestamp"}
            }
        },
        {"$sort": {"avg_score": -1}},
        {"$limit": limit}
    ]

    results = await projects_collection.aggregate(pipeline).to_list(None)

    leaderboard = [
        {
            "rank": idx + 1,
            "project": result["_id"],
            "green_score": round(result["avg_score"], 2),
            "carbon_emissions": round(result["avg_carbon"], 2),
            "total_scans": result["total_scans"],
            "last_scan": result["last_scan"]
        }
        for idx, result in enumerate(results)
    ]

    return {
        "period": period,
        "total_entries": len(leaderboard),
        "leaderboard": leaderboard
    }


@router.get("/team/{team_id}")
async def get_team_leaderboard(team_id: str, limit: int = Query(50, ge=1, le=100)):
    """Get leaderboard for a specific team's projects."""
    
    # Verify team exists
    team = await teams_collection.find_one({"_id": team_id})
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    # Get all projects for team members
    member_ids = team.get("members", [])
    
    pipeline = [
        {"$match": {"user_id": {"$in": member_ids}}},
        {
            "$group": {
                "_id": "$project_name",
                "avg_score": {"$avg": "$green_score"},
                "total_scans": {"$sum": 1}
            }
        },
        {"$sort": {"avg_score": -1}},
        {"$limit": limit}
    ]
    
    results = await projects_collection.aggregate(pipeline).to_list(None)
    
    return {
        "team_id": team_id,
        "team_name": team.get("name"),
        "leaderboard": [
            {
                "rank": idx + 1,
                "project": r["_id"],
                "green_score": round(r["avg_score"], 2),
                "total_scans": r["total_scans"]
            }
            for idx, r in enumerate(results)
        ]
    }


@router.get("/trending")
async def get_trending_projects(period: str = Query("week"), limit: int = 10):
    """
    Get trending projects with biggest improvements.
    Compares first half vs second half of period.
    """
    
    if period == "week":
        days = 7
    elif period == "month":
        days = 30
    else:
        days = 7
    
    now = datetime.utcnow()
    mid_point = now - timedelta(days=days/2)
    start_point = now - timedelta(days=days)
    
    # First period: start -> mid
    first_period = await projects_collection.aggregate([
        {"$match": {"timestamp": {"$gte": start_point, "$lt": mid_point}}},
        {"$group": {"_id": "$project_name", "avg_score_1": {"$avg": "$green_score"}}}
    ]).to_list(None)
    
    first_dict = {p["_id"]: p["avg_score_1"] for p in first_period}
    
    # Second period: mid -> now
    second_period = await projects_collection.aggregate([
        {"$match": {"timestamp": {"$gte": mid_point, "$lt": now}}},
        {"$group": {"_id": "$project_name", "avg_score_2": {"$avg": "$green_score"}}}
    ]).to_list(None)
    
    # Calculate improvements
    trending = []
    for p in second_period:
        project_name = p["_id"]
        score_2 = p["avg_score_2"]
        score_1 = first_dict.get(project_name, score_2)
        improvement = score_2 - score_1
        
        trending.append({
            "project": project_name,
            "previous_score": round(score_1, 2),
            "current_score": round(score_2, 2),
            "improvement": round(improvement, 2),
            "improvement_percent": round((improvement / score_1 * 100) if score_1 > 0 else 0, 1)
        })
    
    # Sort by improvement
    trending.sort(key=lambda x: x["improvement"], reverse=True)
    
    return {
        "period": period,
        "trending": trending[:limit]
    }


@router.get("/user/{user_id}")
async def get_user_stats(user_id: str):
    """Get a user's career stats and achievements."""
    
    user = await users_collection.find_one({"_id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # User's projects
    projects = await projects_collection.find({"user_id": user_id}).to_list(None)
    
    if not projects:
        return {
            "user_id": user_id,
            "name": user.get("name"),
            "total_scans": 0,
            "avg_green_score": 0,
            "total_carbon_saved": 0,
            "achievements": []
        }
    
    total_scans = len(projects)
    avg_score = sum(p.get("green_score", 0) for p in projects) / total_scans
    total_carbon = sum(p.get("carbon_emissions", 0) for p in projects)
    
    # Calculate achievements
    achievements = []
    if total_scans >= 10:
        achievements.append("🌟 Prolific Analyzer")
    if avg_score >= 80:
        achievements.append("🟢 Green Champion")
    if total_carbon < 100:
        achievements.append("♻️ Low Emission Hero")
    
    return {
        "user_id": user_id,
        "name": user.get("name"),
        "total_scans": total_scans,
        "avg_green_score": round(avg_score, 2),
        "total_carbon_saved": round(100 - total_carbon, 2),  # Placeholder logic
        "achievements": achievements
    }


@router.get("/regions")
async def get_regional_stats():
    """See which regions are most sustainable."""
    
    pipeline = [
        {
            "$group": {
                "_id": "$region",
                "avg_score": {"$avg": "$green_score"},
                "total_scans": {"$sum": 1}
            }
        },
        {"$sort": {"avg_score": -1}}
    ]
    
    regions = await projects_collection.aggregate(pipeline).to_list(None)
    
    return {
        "regions": [
            {
                "region": r["_id"],
                "avg_score": round(r["avg_score"], 2),
                "total_scans": r["total_scans"]
            }
            for r in regions
        ]
    }