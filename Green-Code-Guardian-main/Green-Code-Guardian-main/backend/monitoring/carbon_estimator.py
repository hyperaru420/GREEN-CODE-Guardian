from typing import Dict

# Carbon intensity by region (gCO2eq/kWh)
CARBON_INTENSITY_BY_REGION: Dict[str, float] = {
    "us-east": 386.0,
    "us-west": 210.0,
    "us-central": 450.0,
    "eu-west": 233.0,
    "eu-north": 53.0,
    "eu-central": 338.0,
    "ap-south": 708.0,       # India
    "ap-southeast": 521.0,   # Southeast Asia
    "ap-east": 415.0,        # Japan/Korea
    "ap-australia": 500.0,
    "sa-east": 109.0,        # Brazil
    "af-south": 741.0,       # South Africa
    "me-east": 630.0,        # Middle East
    "ca-central": 120.0,     # Canada
    "uk": 225.0,
    "china": 581.0,
    "global-average": 442.0,
}

# Power consumption estimates (Watts)
CPU_POWER_PER_PERCENT = 0.5      # 0.5W per 1% CPU usage (typical server CPU ~50W at 100%)
MEMORY_POWER_PER_GB = 3.0        # ~3W per GB of memory used
DISK_POWER_BASE = 5.0            # Base disk power (W)
NETWORK_POWER_PER_MBPS = 0.01   # ~0.01W per Mbps

def estimate_power_consumption(
    cpu_usage: float,
    memory_usage_gb: float,
    disk_usage: float,
    network_usage_mbps: float = 0.0
) -> float:
    """Estimate power consumption in Watts."""
    cpu_power = cpu_usage * CPU_POWER_PER_PERCENT
    memory_power = memory_usage_gb * MEMORY_POWER_PER_GB
    disk_power = DISK_POWER_BASE * (disk_usage / 100)
    network_power = network_usage_mbps * NETWORK_POWER_PER_MBPS
    total_power = cpu_power + memory_power + disk_power + network_power
    return round(total_power, 4)

def estimate_energy_consumption(power_watts: float, duration_hours: float) -> float:
    """Estimate energy in kWh."""
    return round((power_watts * duration_hours) / 1000, 6)

def estimate_carbon_emissions(energy_kwh: float, region: str = "global-average") -> float:
    """Estimate carbon emissions in gCO2eq."""
    intensity = CARBON_INTENSITY_BY_REGION.get(region, CARBON_INTENSITY_BY_REGION["global-average"])
    return round(energy_kwh * intensity, 6)

def get_carbon_breakdown(
    cpu_usage: float,
    memory_used_gb: float,
    disk_usage: float,
    network_usage_mbps: float,
    region: str,
    duration_hours: float = 1.0
) -> dict:
    intensity = CARBON_INTENSITY_BY_REGION.get(region, CARBON_INTENSITY_BY_REGION["global-average"])
    
    components = {
        "cpu": cpu_usage * CPU_POWER_PER_PERCENT,
        "memory": memory_used_gb * MEMORY_POWER_PER_GB,
        "disk": DISK_POWER_BASE * (disk_usage / 100),
        "network": network_usage_mbps * NETWORK_POWER_PER_MBPS,
    }
    total_power = sum(components.values())
    total_energy = estimate_energy_consumption(total_power, duration_hours)
    total_carbon = estimate_carbon_emissions(total_energy, region)
    
    return {
        "region": region,
        "carbon_intensity_gco2_kwh": intensity,
        "power_breakdown_watts": {k: round(v, 4) for k, v in components.items()},
        "total_power_watts": round(total_power, 4),
        "energy_consumed_kwh": total_energy,
        "carbon_emissions_gco2": total_carbon,
        "carbon_emissions_kg": round(total_carbon / 1000, 8),
    }

def get_available_regions() -> list:
    return [{"id": k, "name": k.replace("-", " ").title(), "intensity": v}
            for k, v in CARBON_INTENSITY_BY_REGION.items()]
