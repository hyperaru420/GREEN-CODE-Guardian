"""
Webhook router for CI/CD pipeline integrations.
Supports GitHub, GitLab, and custom webhooks.
"""

from fastapi import APIRouter, HTTPException, Header, Body
from models.schemas import WebhookEvent, WebhookResponse, GitHubPushPayload
from database.connection import projects_collection, webhook_events_collection
from monitoring.collector import collect_system_metrics
from monitoring.carbon_estimator import get_carbon_breakdown
from monitoring.green_score import calculate_green_score
from config import settings
from datetime import datetime
import hmac
import hashlib
import json
from typing import Optional

router = APIRouter()

GITHUB_WEBHOOK_SECRET = settings.GITHUB_WEBHOOK_SECRET
GITLAB_WEBHOOK_TOKEN = settings.GITLAB_WEBHOOK_TOKEN


def verify_github_signature(payload_body: bytes, signature: str) -> bool:
    """Verify GitHub webhook signature for security."""
    if not GITHUB_WEBHOOK_SECRET:
        return False
    expected_sig = "sha256=" + hmac.new(
        GITHUB_WEBHOOK_SECRET.encode(),
        payload_body,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected_sig, signature)


@router.post("/github")
async def github_webhook(
    x_hub_signature_256: Optional[str] = Header(None),
    x_github_event: Optional[str] = Header(None),
    body: dict = Body(...)
):
    """
    GitHub webhook receiver.
    Listens to push, pull_request, workflow_run events.
    
    Setup in GitHub:
    1. Go to Settings > Webhooks
    2. Add webhook: https://your-api.com/webhook/github
    3. Events: Push, Pull Request, Workflow run
    4. Secret: Generate and store in .env as GITHUB_WEBHOOK_SECRET
    """
    
    if not x_hub_signature_256:
        raise HTTPException(status_code=400, detail="Missing signature header")
    
    if not verify_github_signature(json.dumps(body).encode(), x_hub_signature_256):
        raise HTTPException(status_code=401, detail="Invalid webhook signature")
    
    event_type = x_github_event or "unknown"
    
    # Parse event
    repo = body.get("repository", {})
    repo_name = repo.get("full_name", "unknown-repo")
    
    event_data = {
        "source": "github",
        "event_type": event_type,
        "repo": repo_name,
        "timestamp": datetime.utcnow(),
        "raw_payload": body
    }
    
    # Handle different event types
    if event_type == "push":
        event_data["branch"] = body.get("ref", "").split("/")[-1]
        event_data["commits"] = len(body.get("commits", []))
        event_data["action"] = "push"
        
        # Collect metrics at webhook time
        metrics = collect_system_metrics()
        carbon = get_carbon_breakdown(
            cpu_usage=metrics["cpu_usage"],
            memory_used_gb=metrics["memory_used_gb"],
            disk_usage=metrics["disk_usage"],
            network_usage_mbps=metrics["network_usage"],
            region="us-east"
        )
        score = calculate_green_score(
            cpu_usage=metrics["cpu_usage"],
            memory_usage=metrics["memory_usage"],
            carbon_emissions_gco2=carbon["carbon_emissions_gco2"],
            execution_time=metrics["execution_time"],
            disk_usage=metrics["disk_usage"]
        )
        
        event_data["metrics"] = {
            "cpu": metrics["cpu_usage"],
            "memory_gb": metrics["memory_used_gb"],
            "carbon_g": carbon["carbon_emissions_gco2"],
            "green_score": score["score"]
        }
    
    elif event_type == "pull_request":
        event_data["action"] = body.get("action")
        event_data["pr_number"] = body.get("number")
        event_data["pr_title"] = body.get("pull_request", {}).get("title")
    
    elif event_type == "workflow_run":
        event_data["action"] = body.get("action")
        event_data["workflow"] = body.get("workflow_run", {}).get("name")
        event_data["conclusion"] = body.get("workflow_run", {}).get("conclusion")
    
    # Store event
    result = await webhook_events_collection.insert_one(event_data)
    
    return WebhookResponse(
        status="received",
        webhook_id=str(result.inserted_id),
        event_type=event_type,
        repo=repo_name
    )


@router.post("/gitlab")
async def gitlab_webhook(
    x_gitlab_token: Optional[str] = Header(None),
    x_gitlab_event: Optional[str] = Header(None),
    body: dict = Body(...)
):
    """GitLab webhook receiver (similar to GitHub)."""
    
    if not x_gitlab_token:
        raise HTTPException(status_code=400, detail="Missing GitLab token")
    
    event_type = x_gitlab_event or "unknown"
    
    event_data = {
        "source": "gitlab",
        "event_type": event_type,
        "repo": body.get("project", {}).get("path_with_namespace"),
        "timestamp": datetime.utcnow(),
        "raw_payload": body
    }
    
    result = await webhook_events_collection.insert_one(event_data)
    
    return WebhookResponse(
        status="received",
        webhook_id=str(result.inserted_id),
        event_type=event_type,
        repo=event_data["repo"]
    )


@router.post("/custom")
async def custom_webhook(body: dict = Body(...)):
    """
    Custom webhook for manual CI/CD integrations.
    
    Expected payload:
    {
        "repo": "my-project",
        "branch": "main",
        "commit": "abc123",
        "metrics": {
            "cpu": 45.2,
            "memory_gb": 2.5,
            "execution_time": 120
        },
        "carbon_threshold": 50  # Alert if exceeds this
    }
    """
    
    metrics = body.get("metrics", {})
    repo = body.get("repo", "unknown")
    branch = body.get("branch", "main")
    
    # Store webhook event
    event_data = {
        "source": "custom",
        "event_type": "custom_submission",
        "repo": repo,
        "branch": branch,
        "commit": body.get("commit"),
        "metrics": metrics,
        "timestamp": datetime.utcnow(),
        "raw_payload": body
    }
    
    result = await webhook_events_collection.insert_one(event_data)
    
    # Check against threshold
    carbon_threshold = body.get("carbon_threshold", 100)
    carbon = metrics.get("carbon", 0)
    
    alert = None
    if carbon > carbon_threshold:
        alert = f"⚠️ Carbon threshold exceeded: {carbon}g > {carbon_threshold}g"
    
    return {
        "status": "received",
        "webhook_id": str(result.inserted_id),
        "repo": repo,
        "branch": branch,
        "alert": alert
    }


@router.get("/events/{webhook_id}")
async def get_webhook_event(webhook_id: str):
    """Retrieve a specific webhook event."""
    from bson import ObjectId
    
    try:
        event = await webhook_events_collection.find_one({"_id": ObjectId(webhook_id)})
        if not event:
            raise HTTPException(status_code=404, detail="Webhook event not found")
        
        event["id"] = str(event.pop("_id"))
        return event
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/events")
async def list_webhook_events(repo: Optional[str] = None, limit: int = 50):
    """List recent webhook events, optionally filtered by repo."""
    
    query = {}
    if repo:
        query["repo"] = repo
    
    events = []
    async for event in webhook_events_collection.find(query).sort("timestamp", -1).limit(limit):
        event["id"] = str(event.pop("_id"))
        events.append(event)
    
    return {"total": len(events), "events": events}