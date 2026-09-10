import psutil
import time
from datetime import datetime
from typing import Dict, Any

def collect_system_metrics() -> Dict[str, Any]:
    """Collect real-time system metrics using psutil."""
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    net_io = psutil.net_io_counters()
    
    return {
        "cpu_usage": round(cpu_percent, 2),
        "memory_usage": round(memory.percent, 2),
        "memory_used_gb": round(memory.used / (1024**3), 2),
        "memory_total_gb": round(memory.total / (1024**3), 2),
        "disk_usage": round(disk.percent, 2),
        "disk_used_gb": round(disk.used / (1024**3), 2),
        "disk_total_gb": round(disk.total / (1024**3), 2),
        "network_bytes_sent": net_io.bytes_sent,
        "network_bytes_recv": net_io.bytes_recv,
        "network_usage": round((net_io.bytes_sent + net_io.bytes_recv) / (1024**2), 2),
        "timestamp": datetime.utcnow().isoformat(),
        "execution_time": round(time.process_time(), 4)
    }

def get_cpu_frequency() -> float:
    """Get CPU frequency in GHz."""
    freq = psutil.cpu_freq()
    if freq:
        return round(freq.current / 1000, 2)
    return 2.5

def get_process_count() -> int:
    return len(psutil.pids())

def get_uptime() -> float:
    """System uptime in hours."""
    boot_time = psutil.boot_time()
    uptime_seconds = time.time() - boot_time
    return round(uptime_seconds / 3600, 2)
