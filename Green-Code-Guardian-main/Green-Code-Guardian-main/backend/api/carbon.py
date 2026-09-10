from fastapi import APIRouter, HTTPException, Query
from monitoring.carbon_estimator import get_carbon_breakdown, estimate_power_consumption
from datetime import datetime

router = APIRouter()

@router.get("/estimate")
async def estimate_carbon(
    cpu_usage: float = Query(...),
    memory_used_gb: float = Query(...),
    disk_usage: float = Query(...),
    network_usage_mbps: float = Query(default=0.0),
    region: str = Query(default="global-average"),
    duration_hours: float = Query(default=1.0)
):
    result = get_carbon_breakdown(
        cpu_usage=cpu_usage,
        memory_used_gb=memory_used_gb,
        disk_usage=disk_usage,
        network_usage_mbps=network_usage_mbps,
        region=region,
        duration_hours=duration_hours
    )
    return {"status": "success", "data": result}