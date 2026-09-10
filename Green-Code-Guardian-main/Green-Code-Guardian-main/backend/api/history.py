from fastapi import APIRouter, Query, Depends
from database.connection import projects_collection
from typing import Optional
from api.auth_utils import get_current_user

router = APIRouter()

@router.get("/projects")
async def get_project_history(
    project_name: Optional[str] = Query(default=None),
    limit: int = Query(default=20),
    skip: int = Query(default=0),
    current_user: dict = Depends(get_current_user)
):
    """Get historical project metrics."""
    query = {"user_id": str(current_user["_id"])}
    if project_name:
        query["project_name"] = project_name
    
    projects = []
    total = await projects_collection.count_documents(query)
    
    async for p in projects_collection.find(query).sort("timestamp", -1).skip(skip).limit(limit):
        p["_id"] = str(p["_id"])
        p["id"] = p["_id"]
        projects.append(p)
    
    return {
        "status": "success",
        "total": total,
        "projects": projects,
        "limit": limit,
        "skip": skip
    }

@router.get("/projects/names")
async def get_project_names(current_user: dict = Depends(get_current_user)):
    """Get list of unique project names for the current user."""
    names = await projects_collection.distinct("project_name", {"user_id": str(current_user["_id"])})
    return {"status": "success", "projects": names}

@router.get("/trends")
async def get_emission_trends(
    project_name: Optional[str] = Query(default=None),
    limit: int = Query(default=30),
    current_user: dict = Depends(get_current_user)
):
    """Get carbon emission and energy trends over time."""
    try:
        query = {"user_id": str(current_user["_id"])}
        if project_name:
            query["project_name"] = project_name
        
        # Get all documents
        all_docs = []
        cursor = projects_collection.find(query)
        if hasattr(cursor, '__aiter__'):
            async for doc in cursor:
                all_docs.append(doc)
        else:
            all_docs = list(cursor)
        
        trends = []
        for p in all_docs:
            try:
                trends.append({
                    "timestamp": p["timestamp"].isoformat() if hasattr(p["timestamp"], "isoformat") else str(p["timestamp"]),
                    "carbon_emissions": p.get("carbon_emissions", 0),
                    "green_score": p.get("green_score", 0),
                    "cpu_usage": p.get("cpu_usage", 0),
                    "memory_usage": p.get("memory_usage", 0),
                    "project_name": p.get("project_name", ""),
                })
            except Exception as e:
                continue
        
        # Sort by timestamp
        trends.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        trends = trends[:limit]
        trends.reverse()  # chronological order
        
        return {"status": "success", "trends": trends}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@router.get("/summary")
async def get_summary(current_user: dict = Depends(get_current_user)):
    """Get current user summary statistics."""
    total_projects = await projects_collection.count_documents({"user_id": str(current_user["_id"])})
    
    pipeline = [
        {"$match": {"user_id": str(current_user["_id"]) }},
        {"$group": {
            "_id": None,
            "avg_green_score": {"$avg": "$green_score"},
            "total_carbon": {"$sum": "$carbon_emissions"},
            "avg_cpu": {"$avg": "$cpu_usage"},
            "avg_memory": {"$avg": "$memory_usage"},
        }}
    ]
    
    stats = {}
    async for doc in projects_collection.aggregate(pipeline):
        stats = doc
        stats.pop("_id", None)
        break
    
    return {
        "status": "success",
        "total_scans": total_projects,
        "avg_green_score": round(stats.get("avg_green_score", 0), 1),
        "total_carbon_gco2": round(stats.get("total_carbon", 0), 4),
        "avg_cpu_usage": round(stats.get("avg_cpu", 0), 1),
        "avg_memory_usage": round(stats.get("avg_memory", 0), 1),
    }