from fastapi import APIRouter, Query
from monitoring.green_score import calculate_green_score

router = APIRouter()

@router.get("/calculate")
async def get_green_score(
    cpu_usage: float = Query(...),
    memory_usage: float = Query(...),
    carbon_emissions_gco2: float = Query(...),
    execution_time: float = Query(...),
    disk_usage: float = Query(...)
):
    result = calculate_green_score(
        cpu_usage=cpu_usage,
        memory_usage=memory_usage,
        carbon_emissions_gco2=carbon_emissions_gco2,
        execution_time=execution_time,
        disk_usage=disk_usage
    )
    return {"status": "success", "data": result}