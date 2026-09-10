from fastapi import APIRouter, HTTPException, Query, Depends
from monitoring.collector import collect_system_metrics
from monitoring.carbon_estimator import get_carbon_breakdown, get_available_regions
from monitoring.green_score import calculate_green_score
from database.connection import projects_collection, metrics_collection
from api.auth_utils import get_current_user
from datetime import datetime
from bson import ObjectId
import asyncio

router = APIRouter()

@router.get("/live")
async def get_live_metrics():
    """Get real-time system metrics."""
    metrics = collect_system_metrics()
    return {"status": "success", "data": metrics}

@router.get("/regions")
async def get_regions():
    """Get available regions and their carbon intensities."""
    return {"regions": get_available_regions()}

@router.post("/collect")
async def collect_and_store(
    project_name: str = Query(...),
    region: str = Query(default="us-east"),
    current_user: dict = Depends(get_current_user)
):
    """Collect metrics, estimate carbon, compute green score, and store."""
    # Collect live metrics
    raw = collect_system_metrics()
    
    # Estimate carbon
    carbon_data = get_carbon_breakdown(
        cpu_usage=raw["cpu_usage"],
        memory_used_gb=raw["memory_used_gb"],
        disk_usage=raw["disk_usage"],
        network_usage_mbps=raw["network_usage"],
        region=region,
        duration_hours=1/3600  # per second reading
    )
    
    # Calculate green score
    score_data = calculate_green_score(
        cpu_usage=raw["cpu_usage"],
        memory_usage=raw["memory_usage"],
        carbon_emissions_gco2=carbon_data["carbon_emissions_gco2"],
        execution_time=raw["execution_time"],
        disk_usage=raw["disk_usage"]
    )
    
    # Store in DB
    doc = {
        "project_name": project_name,
        "region": region,
        "cpu_usage": raw["cpu_usage"],
        "memory_usage": raw["memory_usage"],
        "memory_used_gb": raw["memory_used_gb"],
        "execution_time": raw["execution_time"],
        "disk_usage": raw["disk_usage"],
        "network_usage": raw["network_usage"],
        "energy_consumed_kwh": carbon_data["energy_consumed_kwh"],
        "carbon_emissions": carbon_data["carbon_emissions_gco2"],
        "green_score": score_data["score"],
        "grade": score_data["grade"],
        "timestamp": datetime.utcnow(),
        "user_id": str(current_user["_id"]),
        "user_email": current_user.get("email")
    }
    result = await projects_collection.insert_one(doc)
    doc["id"] = str(result.inserted_id)
    doc["_id"] = str(result.inserted_id)
    
    return {
        "status": "success",
        "project_id": str(result.inserted_id),
        "metrics": raw,
        "carbon": carbon_data,
        "green_score": score_data
    }