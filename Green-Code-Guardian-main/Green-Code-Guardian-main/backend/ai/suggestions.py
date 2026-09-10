import httpx
import json
import os
from config import settings
from typing import List, Dict, Any
from datetime import datetime

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

STATIC_RULES = [
    {
        "category": "Algorithm Efficiency",
        "title": "Optimize Nested Loops",
        "description": "Nested loops with O(n²) complexity detected. Consider using hash maps or sorting to reduce to O(n log n) or O(n).",
        "severity": "high",
        "estimated_savings": 35.0,
        "code_example": "# Instead of O(n²)\nfor i in list1:\n    for j in list2:\n        if i == j: ...\n\n# Use O(n) with set\nset2 = set(list2)\nmatches = [i for i in list1 if i in set2]"
    },
    {
        "category": "Database Optimization",
        "title": "Avoid N+1 Query Problem",
        "description": "Multiple sequential database queries detected. Use batch queries or eager loading to reduce database round-trips.",
        "severity": "high",
        "estimated_savings": 45.0,
        "code_example": "# Instead of N+1 queries\nusers = db.find_all_users()\nfor user in users:\n    orders = db.find_orders(user.id)  # N queries!\n\n# Use JOIN or batch fetch\nresults = db.query('SELECT u.*, o.* FROM users u JOIN orders o ON u.id=o.user_id')"
    },
    {
        "category": "Caching",
        "title": "Implement Response Caching",
        "description": "Repeated identical API calls or computations detected. Add caching layer (Redis/Memcached) to reduce redundant work.",
        "severity": "medium",
        "estimated_savings": 30.0,
        "code_example": "import functools\n\n@functools.lru_cache(maxsize=128)\ndef expensive_computation(param):\n    return result  # Cached automatically"
    },
    {
        "category": "Memory Management",
        "title": "Use Generators for Large Datasets",
        "description": "Loading entire dataset into memory. Use generators/streaming to process data in chunks.",
        "severity": "medium",
        "estimated_savings": 25.0,
        "code_example": "# Memory-heavy\ndata = list(read_all_records())\n\n# Memory-efficient generator\ndef process_records():\n    for record in read_records_streaming():\n        yield process(record)"
    },
    {
        "category": "API Efficiency",
        "title": "Batch API Requests",
        "description": "Multiple single API calls detected. Use batch endpoints or parallel requests with asyncio to improve throughput.",
        "severity": "medium",
        "estimated_savings": 20.0,
        "code_example": "import asyncio\nimport aiohttp\n\nasync def fetch_all(urls):\n    async with aiohttp.ClientSession() as session:\n        tasks = [fetch(session, url) for url in urls]\n        return await asyncio.gather(*tasks)"
    },
]

RUNTIME_RULES = [
    {
        "category": "CPU Optimization",
        "title": "Reduce CPU Usage",
        "description": "High CPU usage detected. Optimize algorithms, use more efficient data structures, or consider parallel processing.",
        "severity": "high",
        "estimated_savings": 30.0,
        "code_example": "# Use efficient algorithms\n# Avoid unnecessary computations\n# Consider caching results"
    },
    {
        "category": "Memory Optimization",
        "title": "Optimize Memory Usage",
        "description": "High memory consumption detected. Implement memory-efficient data structures, use streaming for large data, or add memory limits.",
        "severity": "high",
        "estimated_savings": 25.0,
        "code_example": "# Use generators instead of lists\n# Implement pagination\n# Monitor memory usage"
    },
    {
        "category": "Disk I/O Optimization",
        "title": "Reduce Disk I/O",
        "description": "High disk usage detected. Use in-memory caching, batch writes, or optimize file operations.",
        "severity": "medium",
        "estimated_savings": 20.0,
        "code_example": "# Implement caching layers\n# Batch database operations\n# Use SSD storage"
    },
    {
        "category": "Network Optimization",
        "title": "Optimize Network Traffic",
        "description": "High network usage detected. Compress data, use efficient protocols, or implement connection pooling.",
        "severity": "medium",
        "estimated_savings": 15.0,
        "code_example": "# Compress responses\n# Use HTTP/2\n# Implement connection pooling"
    },
    {
        "category": "Resource Monitoring",
        "title": "Implement Resource Monitoring",
        "description": "Add monitoring to track resource usage and identify bottlenecks in real-time.",
        "severity": "low",
        "estimated_savings": 10.0,
        "code_example": "# Use monitoring tools like Prometheus\n# Set up alerts for high usage\n# Log performance metrics"
    },
]

async def get_ai_suggestions(
    cpu_usage: float = None,
    memory_usage: float = None,
    carbon_emissions: float = None,
    green_score: float = None,
    project_name: str = "your application",
    scan_type: str = "runtime",
    avg_complexity: float = None,
    avg_lines_per_file: float = None,
    total_files: int = None,
    issues_count: int = None,
    disk_usage: float = None,
    network_usage: float = None
) -> Dict[str, Any]:
    """Generate AI-powered optimization suggestions using Groq."""
    
    suggestions = []
    
    # Try Groq API first
    if settings.GROQ_API_KEY:
        try:
            if scan_type == "code":
                prompt = f"""You are a code quality and sustainability expert for the GreenCode Guardian platform.

Analyze this code's quality metrics:
- Average Complexity: {avg_complexity}
- Average Lines per File: {avg_lines_per_file}
- Total Files: {total_files}
- Issues Found: {issues_count}
- Green Score: {green_score}/100
- Project: {project_name}

Generate 4 specific, actionable code optimization recommendations to improve code quality, reduce complexity, and lower carbon footprint.

Focus on:
- Refactoring high-complexity functions
- Reducing code duplication
- Improving algorithmic efficiency
- Better code organization

Respond ONLY with a JSON array (no markdown, no explanation) with this exact structure:
[
  {{
    "category": "string",
    "title": "string",
    "description": "string (2-3 sentences)",
    "severity": "low|medium|high",
    "estimated_savings": number (percentage 1-50),
    "code_example": "string (optional short code snippet)"
  }}
]"""
            else:
                prompt = f"""You are a sustainability and performance optimization expert for the GreenCode Guardian platform.

Analyze this application's runtime performance metrics:
- CPU Usage: {cpu_usage}%
- Memory Usage: {memory_usage}%
- Disk Usage: {disk_usage}%
- Network Usage: {network_usage} MB
- Carbon Emissions: {carbon_emissions:.4f} gCO2eq
- Green Score: {green_score}/100
- Project: {project_name}

Generate 4 specific, actionable optimization recommendations to reduce resource usage and carbon footprint.

Focus on:
- CPU optimization techniques
- Memory management improvements
- Disk I/O reduction
- Network efficiency
- Performance monitoring

Respond ONLY with a JSON array (no markdown, no explanation) with this exact structure:
[
  {{
    "category": "string",
    "title": "string",
    "description": "string (2-3 sentences)",
    "severity": "low|medium|high",
    "estimated_savings": number (percentage 1-50),
    "code_example": "string (optional short code snippet)"
  }}
]"""

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    GROQ_API_URL,
                    headers={
                        "Authorization": f"Bearer {settings.GROQ_API_KEY}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "llama3-8b-8192",
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.7,
                        "max_tokens": 1500,
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    content = data["choices"][0]["message"]["content"].strip()
                    # Strip markdown code fences if present
                    if content.startswith("```"):
                        content = content.split("```")[1]
                        if content.startswith("json"):
                            content = content[4:]
                    ai_suggestions = json.loads(content)
                    suggestions = ai_suggestions[:5]
        except Exception as e:
            print(f"Groq API error: {e}. Falling back to static rules.")
    
    # Fall back to static rules + contextual filtering
    if not suggestions:
        if scan_type == "code":
            # Code-specific static rules
            code_rules = [
                {
                    "category": "Code Complexity",
                    "title": "Refactor High Complexity Functions",
                    "description": "Functions with high cyclomatic complexity detected. Break down complex functions into smaller, more manageable pieces.",
                    "severity": "high",
                    "estimated_savings": 30.0,
                    "code_example": "def complex_function():\n    # Break into smaller functions\n    pass"
                },
                {
                    "category": "Code Organization",
                    "title": "Reduce File Size",
                    "description": "Large files detected. Split large files into multiple modules for better maintainability and readability.",
                    "severity": "medium",
                    "estimated_savings": 20.0,
                    "code_example": "# Split into separate files\n# utils.py, models.py, etc."
                },
                {
                    "category": "Algorithm Optimization",
                    "title": "Optimize Nested Loops",
                    "description": "Nested loops increasing complexity. Consider using more efficient data structures or algorithms.",
                    "severity": "high",
                    "estimated_savings": 35.0,
                    "code_example": "# Use sets or dicts for O(1) lookups"
                },
                {
                    "category": "Code Quality",
                    "title": "Remove Code Duplication",
                    "description": "Duplicate code patterns found. Extract common functionality into reusable functions or classes.",
                    "severity": "medium",
                    "estimated_savings": 25.0,
                    "code_example": "def common_function():\n    # Extract duplicated logic\n    pass"
                },
            ]
            if avg_complexity and avg_complexity > 10:
                suggestions.append(code_rules[0])
            if avg_lines_per_file and avg_lines_per_file > 200:
                suggestions.append(code_rules[1])
            if issues_count and issues_count > 0:
                suggestions.append(code_rules[2])
            suggestions.append(code_rules[3])
        else:
            if cpu_usage and cpu_usage > 70:
                suggestions.append(RUNTIME_RULES[0])  # CPU
            if memory_usage and memory_usage > 60:
                suggestions.append(RUNTIME_RULES[1])  # Memory
            if disk_usage and disk_usage > 70:
                suggestions.append(RUNTIME_RULES[2])  # Disk
            if network_usage and network_usage > 100:
                suggestions.append(RUNTIME_RULES[3])  # Network
            suggestions.append(RUNTIME_RULES[4])  # Monitoring
        suggestions = suggestions[:5]
    
    total_savings = sum(s.get("estimated_savings", 0) for s in suggestions) / len(suggestions) if suggestions else 0
    
    return {
        "suggestions": suggestions,
        "total_potential_savings": round(total_savings, 1),
        "generated_at": datetime.utcnow().isoformat(),
        "ai_powered": bool(settings.GROQ_API_KEY and suggestions)
    }

REFACTOR_RULES = [
    {
        "file": "general",
        "category": "Code Efficiency",
        "title": "Refactor large functions and loops",
        "description": "Large or deeply nested functions can increase CPU usage and memory pressure. Split functionality into smaller units and use efficient data structures.",
        "severity": "high",
        "estimated_savings": 30.0,
        "original_snippet": "def process_data(data):\n    # 50+ lines of processing\n    for item in data:\n        if item.status == 'active':\n            # nested logic\n            pass",
        "refactored_snippet": "def filter_active_items(data):\n    return [item for item in data if item.status == 'active']\n\ndef process_active_items(active_items):\n    for item in active_items:\n        # processing logic\n        pass\n\ndef process_data(data):\n    active_items = filter_active_items(data)\n    process_active_items(active_items)"
    },
    {
        "file": "general",
        "category": "Memory Optimization",
        "title": "Use streaming or generators for large data",
        "description": "Loading large datasets into memory can increase energy consumption. Process data incrementally using generators, iterators, or streaming APIs.",
        "severity": "medium",
        "estimated_savings": 25.0,
        "original_snippet": "def read_file():\n    data = []\n    with open('large_file.txt') as f:\n        for line in f:\n            data.append(line.strip())\n    return data",
        "refactored_snippet": "def read_file():\n    with open('large_file.txt') as f:\n        for line in f:\n            yield line.strip()"
    },
    {
        "file": "general",
        "category": "Algorithm Optimization",
        "title": "Replace nested loops with hash-based lookups",
        "description": "Nested iteration is often the biggest cost in code. Use sets, dictionaries, or bulk operations to reduce runtime from O(n²) to O(n).",
        "severity": "high",
        "estimated_savings": 35.0,
        "original_snippet": "matches = []\nfor user in users:\n    for order in orders:\n        if user.id == order.user_id:\n            matches.append((user, order))",
        "refactored_snippet": "user_dict = {user.id: user for user in users}\nmatches = [(user_dict[order.user_id], order) for order in orders if order.user_id in user_dict]"
    },
    {
        "file": "general",
        "category": "Caching",
        "title": "Cache repeated computations",
        "description": "Repeated work across the same inputs wastes CPU and energy. Cache results for expensive calls to reduce redundant processing.",
        "severity": "medium",
        "estimated_savings": 20.0,
        "original_snippet": "def expensive_calc(x):\n    # complex calculation\n    return result\n\n# Called multiple times with same x\nresult1 = expensive_calc(5)\nresult2 = expensive_calc(5)",
        "refactored_snippet": "import functools\n\n@functools.lru_cache(maxsize=128)\ndef expensive_calc(x):\n    # complex calculation\n    return result\n\n# Cached automatically\nresult1 = expensive_calc(5)\nresult2 = expensive_calc(5)"
    },
]

async def get_ai_refactor_suggestions(
    file_path: str,
    files: Dict[str, str],
    project_name: str = "your application",
    scan_type: str = "code",
    avg_complexity: float = None,
    avg_lines_per_file: float = None,
    total_files: int = None,
    issues_count: int = None,
    carbon_emissions: float = None,
    green_score: float = None,
) -> Dict[str, Any]:
    """Generate AI-powered refactor suggestions for code files."""
    suggestions = []

    if settings.GROQ_API_KEY:
        try:
            prompt_items = []
            for path, content in files.items():
                prompt_items.append(f"FILE: {os.path.basename(path)}\n{content}\n")

            prompt = f"""You are a sustainability-aware code refactoring assistant for GreenCode Guardian.

Analyze the following code files and metrics. For each file, suggest one refactor that preserves behavior while reducing CPU, memory, or energy usage and improving sustainability.

Project: {project_name}
Path: {file_path}
Average Complexity: {avg_complexity}
Average Lines per File: {avg_lines_per_file}
Total Files: {total_files}
Issues Found: {issues_count}
Green Score: {green_score}/100
Estimated Carbon: {carbon_emissions} gCO2eq

{''.join(prompt_items)}

Return ONLY a JSON array with this exact structure. Do not include markdown fences or explanatory text.
[
  {{
    "file": "string",
    "category": "string",
    "title": "string",
    "description": "string",
    "severity": "low|medium|high",
    "estimated_savings": number,
    "original_snippet": "string (optional)",
    "refactored_snippet": "string (optional)"
  }}
]"""

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    GROQ_API_URL,
                    headers={
                        "Authorization": f"Bearer {settings.GROQ_API_KEY}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "llama3-8b-8192",
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.7,
                        "max_tokens": 1500,
                    }
                )

                if response.status_code == 200:
                    data = response.json()
                    content = data["choices"][0]["message"]["content"].strip()
                    if content.startswith("```"):
                        content = content.split("```")[1]
                        if content.startswith("json"):
                            content = content[4:]
                    suggestions = json.loads(content)
        except Exception as e:
            print(f"Groq refactor error: {e}. Falling back to static refactor rules.")

    if not suggestions:
        active = []
        if avg_complexity and avg_complexity > 10:
            active.append(REFACTOR_RULES[0])
        if avg_lines_per_file and avg_lines_per_file > 200:
            active.append(REFACTOR_RULES[1])
        if issues_count and issues_count > 0:
            active.append(REFACTOR_RULES[2])
        if not active:
            active.append(REFACTOR_RULES[3])

        suggestions = []
        for rule in active[:3]:
            suggestion = rule.copy()
            suggestion["file"] = list(files.keys())[0] if files else "general"
            suggestions.append(suggestion)

    # Always include at least one suggestion
    if not suggestions:
        suggestions = [REFACTOR_RULES[0].copy()]
        suggestions[0]["file"] = list(files.keys())[0] if files else "general"

    total_savings = sum(s.get("estimated_savings", 0) for s in suggestions) / len(suggestions) if suggestions else 0
    return {
        "suggestions": suggestions,
        "total_potential_savings": round(total_savings, 1),
        "generated_at": datetime.utcnow().isoformat(),
        "ai_powered": bool(settings.GROQ_API_KEY and suggestions)
    }
