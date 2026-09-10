from typing import Tuple

def calculate_green_score(
    cpu_usage: float,
    memory_usage: float,
    carbon_emissions_gco2: float,
    execution_time: float,
    disk_usage: float
) -> dict:
    """
    Calculate Green Score (0-100).
    Higher = greener.
    """
    # Component scores (each 0-100)
    cpu_score = max(0, 100 - cpu_usage)
    memory_score = max(0, 100 - memory_usage)
    disk_score = max(0, 100 - disk_usage)
    
    # Carbon score - scale based on typical emission ranges
    # < 1g = excellent, > 100g = poor
    if carbon_emissions_gco2 < 1:
        carbon_score = 100
    elif carbon_emissions_gco2 < 10:
        carbon_score = 90 - (carbon_emissions_gco2 - 1) * 5
    elif carbon_emissions_gco2 < 50:
        carbon_score = 45 - (carbon_emissions_gco2 - 10) * 0.75
    elif carbon_emissions_gco2 < 100:
        carbon_score = 15 - (carbon_emissions_gco2 - 50) * 0.2
    else:
        carbon_score = 0
    carbon_score = max(0, min(100, carbon_score))
    
    # Execution time score
    if execution_time < 1:
        exec_score = 100
    elif execution_time < 10:
        exec_score = 100 - (execution_time - 1) * 5
    elif execution_time < 60:
        exec_score = 55 - (execution_time - 10) * 0.8
    else:
        exec_score = 0
    exec_score = max(0, min(100, exec_score))
    
    # Weighted final score
    final_score = (
        cpu_score * 0.25 +
        memory_score * 0.20 +
        carbon_score * 0.35 +
        exec_score * 0.10 +
        disk_score * 0.10
    )
    final_score = round(max(0, min(100, final_score)), 1)
    
    grade, color = get_grade_and_color(final_score)
    
    return {
        "score": final_score,
        "grade": grade,
        "color": color,
        "breakdown": {
            "cpu_score": round(cpu_score, 1),
            "memory_score": round(memory_score, 1),
            "carbon_score": round(carbon_score, 1),
            "execution_score": round(exec_score, 1),
            "disk_score": round(disk_score, 1),
        },
        "weights": {
            "cpu": "25%",
            "memory": "20%",
            "carbon": "35%",
            "execution": "10%",
            "disk": "10%",
        }
    }

def get_grade_and_color(score: float) -> Tuple[str, str]:
    if score >= 85:
        return "A+", "green"
    elif score >= 75:
        return "A", "green"
    elif score >= 65:
        return "B", "yellow"
    elif score >= 50:
        return "C", "yellow"
    elif score >= 35:
        return "D", "orange"
    else:
        return "F", "red"

def get_score_label(score: float) -> str:
    if score >= 75:
        return "Excellent"
    elif score >= 50:
        return "Moderate"
    elif score >= 25:
        return "Poor"
    else:
        return "Critical"
