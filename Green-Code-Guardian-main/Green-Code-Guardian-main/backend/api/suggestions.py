from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel
from ai.suggestions import get_ai_suggestions, get_ai_refactor_suggestions
from datetime import datetime
import os
import radon.complexity as cc
import radon.metrics as met
from typing import Dict, Any, List, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from monitoring.carbon_estimator import (
    estimate_power_consumption,
    estimate_energy_consumption,
    estimate_carbon_emissions,
    CARBON_INTENSITY_BY_REGION
)

router = APIRouter()

# ── Directories to always skip when walking a project ─────────────────────────
SKIP_DIRS = {
    'node_modules', '.git', '__pycache__', '.venv', 'venv', 'env',
    '.mypy_cache', '.pytest_cache', 'dist', 'build', '.next', 'coverage',
    '.tox', 'htmlcov', '.eggs',
}

# ── Code file extensions we care about ────────────────────────────────────────
CODE_EXTENSIONS = {
    '.py', '.js', '.ts', '.jsx', '.tsx',
    '.java', '.cs', '.go', '.rb', '.php',
    '.html', '.css', '.scss',
}


@router.get("/generate")
async def generate_suggestions(
    cpu_usage: float = Query(None),
    memory_usage: float = Query(None),
    carbon_emissions: float = Query(None),
    green_score: float = Query(None),
    project_name: str = Query(default="application"),
    scan_type: str = Query(default="runtime"),
    avg_complexity: float = Query(None),
    avg_lines_per_file: float = Query(None),
    total_files: int = Query(None),
    issues_count: int = Query(None),
    disk_usage: float = Query(None),
    network_usage: float = Query(None)
):
    result = await get_ai_suggestions(
        cpu_usage=cpu_usage,
        memory_usage=memory_usage,
        carbon_emissions=carbon_emissions,
        green_score=green_score,
        project_name=project_name,
        scan_type=scan_type,
        avg_complexity=avg_complexity,
        avg_lines_per_file=avg_lines_per_file,
        total_files=total_files,
        issues_count=issues_count,
        disk_usage=disk_usage,
        network_usage=network_usage
    )
    return {"status": "success", "data": result}


def analyze_single_file(filepath: str) -> Tuple[int, int, List[str]]:
    """Analyze a single file and return (total_lines, total_complexity, issues)."""
    total_lines = 0
    total_complexity = 0
    issues = []

    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            lines = len(content.splitlines())
            total_lines = lines

            if filepath.endswith('.py'):
                try:
                    blocks = cc.cc_visit(content)
                    file_complexity = sum(block.complexity for block in blocks)
                    total_complexity = file_complexity
                except Exception:
                    file_complexity = 0

                if lines > 500:
                    issues.append(
                        f"{os.path.basename(filepath)}: Too many lines ({lines}) - consider splitting"
                    )
                if file_complexity > 20:
                    issues.append(
                        f"{os.path.basename(filepath)}: High complexity ({file_complexity}) - refactor needed"
                    )
            else:
                if lines > 1000:
                    issues.append(
                        f"{os.path.basename(filepath)}: Large file ({lines} lines) - consider splitting"
                    )

    except Exception as e:
        issues.append(f"Error reading {os.path.basename(filepath)}: {str(e)}")

    return total_lines, total_complexity, issues


def _collect_files(path: str) -> List[str]:
    """
    Walk *path* and return all scannable files, properly skipping
    junk directories (node_modules, .git, __pycache__, etc.).
    """
    if os.path.isfile(path):
        return [path]

    files_to_scan: List[str] = []
    for root, dirs, files in os.walk(path):
        # Prune skip-dirs IN PLACE so os.walk won't descend into them
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.startswith('.')]
        for file in files:
            if not file.startswith('.'):
                files_to_scan.append(os.path.join(root, file))

    return files_to_scan


def _build_dynamic_recommendations(
    avg_complexity: float,
    avg_lines: float,
    issues: List[str],
    python_files: int,
) -> List[str]:
    """Return data-driven recommendations instead of hardcoded strings."""
    recs: List[str] = []

    if avg_complexity > 15:
        recs.append(f"Reduce cyclomatic complexity (avg {avg_complexity:.1f}) — aim for < 10 per function")
    elif avg_complexity > 8:
        recs.append(f"Complexity is moderate ({avg_complexity:.1f}) — review functions above 10")

    if avg_lines > 300:
        recs.append(f"Files average {avg_lines:.0f} lines — split large modules into smaller ones")
    elif avg_lines > 150:
        recs.append(f"Files average {avg_lines:.0f} lines — consider extracting helper modules")

    if len(issues) > 10:
        recs.append(f"{len(issues)} issues detected — prioritise the high-complexity files first")
    elif len(issues) > 0:
        recs.append(f"{len(issues)} issue(s) found — see the Issues Breakdown for details")

    if python_files > 0:
        recs.append("Use generators instead of building large lists in memory")
        recs.append("Profile with cProfile before optimising — measure first")
    else:
        recs.append("Enable tree-shaking and code-splitting for JS/TS bundles")
        recs.append("Lazy-load heavy components to reduce initial parse time")

    if not recs:
        recs.append("Code looks good — keep functions focused and complexity low")

    return recs


def analyze_code_files(directory: str) -> Dict[str, Any]:
    """Analyze files in a directory or a single file using parallel processing."""
    directory = directory.strip('"').strip("'")

    if not os.path.exists(directory):
        raise HTTPException(status_code=404, detail="Path not found")

    if not os.path.isfile(directory) and not os.path.isdir(directory):
        raise HTTPException(status_code=400, detail="Path must be a file or directory")

    # Use fixed collector that properly skips junk dirs
    files_to_scan = _collect_files(directory)

    if not files_to_scan:
        raise HTTPException(status_code=400, detail="No files found")

    total_lines = 0
    total_complexity = 0
    file_count = len(files_to_scan)
    issues: List[str] = []

    max_workers = min(8, file_count)
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(analyze_single_file, fp): fp
            for fp in files_to_scan
        }
        for future in as_completed(futures):
            try:
                lines, complexity, file_issues = future.result()
                total_lines += lines
                total_complexity += complexity
                issues.extend(file_issues)
            except Exception as e:
                issues.append(f"Error processing file: {str(e)}")

    avg_complexity = total_complexity / file_count if file_count > 0 else 0
    avg_lines = total_lines / file_count if file_count > 0 else 0

    python_files = sum(1 for f in files_to_scan if f.endswith('.py'))
    complexity_score = (
        max(0, 100 - (avg_complexity * 2)) if python_files > 0 else 80
    )
    lines_score = max(0, 100 - (avg_lines / 10))
    issues_penalty = len(issues) * 5
    green_score = max(0, min(100, (complexity_score + lines_score) / 2 - issues_penalty))

    estimated_cpu_usage = min(avg_complexity * 2, 100)
    estimated_memory_usage = min(avg_lines / 5, 100)
    estimated_power = estimate_power_consumption(
        estimated_cpu_usage, estimated_memory_usage * 8, 10
    )
    estimated_energy = estimate_energy_consumption(estimated_power, 1)
    estimated_carbon = estimate_carbon_emissions(estimated_energy, "global-average")

    return {
        "total_files": file_count,
        "total_lines": total_lines,
        "avg_complexity": round(avg_complexity, 2),
        "avg_lines_per_file": round(avg_lines, 2),
        "issues": issues,
        "green_score": round(green_score, 2),
        "estimated_carbon_gco2": round(estimated_carbon, 2),
        "estimated_power_watts": round(estimated_power, 2),
        "estimated_energy_kwh": round(estimated_energy, 6),
        "carbon_region": "global-average",
        "carbon_intensity_gco2_kwh": CARBON_INTENSITY_BY_REGION["global-average"],
        # Dynamic recommendations based on actual metrics
        "recommendations": _build_dynamic_recommendations(
            avg_complexity, avg_lines, issues, python_files
        ),
    }


class RefactorRequest(BaseModel):
    path: str
    project_name: str = "application"
    scan_type: str = "code"
    max_files: Optional[int] = 8   # increased from 3 → more context for AI


@router.post("/refactor")
async def refactor_project(request: RefactorRequest):
    """Analyze file(s) and return sustainability-aware refactor suggestions."""
    if not os.path.exists(request.path):
        raise HTTPException(status_code=404, detail="Path not found")

    # Collect only real code files, skipping junk dirs
    file_paths: List[str] = []
    if os.path.isfile(request.path):
        file_paths = [request.path]
    else:
        for root, dirs, files in os.walk(request.path):
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.startswith('.')]
            for file in files:
                if file.startswith('.'):
                    continue
                candidate = os.path.join(root, file)
                ext = os.path.splitext(file)[1].lower()
                if ext in CODE_EXTENSIONS:
                    file_paths.append(candidate)

    if not file_paths:
        raise HTTPException(status_code=400, detail="No code files found in the provided path")

    # Pick the largest files — most likely to have impactful refactoring opportunities
    max_files = request.max_files or 8
    file_paths = sorted(file_paths, key=lambda p: os.path.getsize(p), reverse=True)[:max_files]

    file_contents: Dict[str, str] = {}
    for path in file_paths:
        try:
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                # Truncate very large files to keep prompt size reasonable
                if len(content) > 15000:
                    content = content[:15000] + "\n\n# ...truncated..."
                file_contents[path] = content
        except Exception as exc:
            raise HTTPException(status_code=500, detail=f"Error reading file {path}: {exc}")

    print(f"Refactor endpoint: read {len(file_contents)} files successfully")

    metrics = analyze_code_files(request.path)
    suggestions = await get_ai_refactor_suggestions(
        file_path=request.path,
        files=file_contents,
        project_name=request.project_name,
        scan_type=request.scan_type,
        avg_complexity=metrics.get('avg_complexity'),
        avg_lines_per_file=metrics.get('avg_lines_per_file'),
        total_files=metrics.get('total_files'),
        issues_count=len(metrics.get('issues', [])),
        carbon_emissions=metrics.get('estimated_carbon_gco2'),
        green_score=metrics.get('green_score')
    )
    print(f"Refactor endpoint: generated {len(suggestions.get('suggestions', []))} suggestions")

    return {
        "status": "success",
        "data": {
            "metrics": metrics,
            "refactor_suggestions": suggestions.get('suggestions', []),
            "scanned_files": list(file_contents.keys())
        }
    }


@router.get("/scan")
async def scan_project(directory: str = Query(..., description="Path to project directory")):
    """Scan project files and calculate green score."""
    result = analyze_code_files(directory)
    return {"status": "success", "data": result}