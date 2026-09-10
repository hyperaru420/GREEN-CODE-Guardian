"""
Notifications router - Send Slack, email, and in-app alerts.
Alerts for carbon thresholds, improvements, and milestones.
"""

from fastapi import APIRouter, Body, HTTPException, Query, Depends
from models.schemas import NotificationPreference, Notification
from database.connection import users_collection, notifications_collection, projects_collection
from datetime import datetime
from typing import Optional
import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import asyncio
from api.auth_utils import get_current_user

router = APIRouter()

# Initialize Slack client (optional - from .env)
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN", "")
slack_client = WebClient(token=SLACK_BOT_TOKEN) if SLACK_BOT_TOKEN else None


@router.put("/preferences")
async def update_notification_preferences(preferences: NotificationPreference, current_user: dict = Depends(get_current_user)):
    """Update user's notification settings."""
    
    user_id = current_user["_id"]
    result = await users_collection.update_one(
        {"_id": user_id},
        {"$set": {"notification_preferences": preferences.dict()}},
        upsert=False
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"status": "updated", "user_id": user_id, "preferences": preferences}


@router.get("/preferences")
async def get_notification_preferences(current_user: dict = Depends(get_current_user)):
    """Get user's notification settings."""
    
    user_id = current_user["_id"]
    user = await users_collection.find_one({"_id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    prefs = user.get("notification_preferences", {})
    return {"preferences": prefs}


@router.post("/test-slack")
async def test_slack_notification(slack_webhook_url: str = Body(...)):
    """Test Slack integration by sending a message."""
    
    import httpx
    
    payload = {
        "text": "✅ GreenCode Guardian Slack Integration Test",
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*🌿 GreenCode Guardian*\nSuccessfully connected to Slack!"
                }
            }
        ]
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(slack_webhook_url, json=payload)
            return {"status": "success", "message": "Test notification sent"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/carbon-alert")
async def send_carbon_threshold_alert(
    project_name: str = Body(...),
    carbon_value: float = Body(...),
    threshold: float = Body(...),
    slack_webhook_url: Optional[str] = Body(None),
    current_user: dict = Depends(get_current_user)
):
    """
    Send alert notification when carbon emissions exceed threshold.
    Supports Slack, Email, and in-app notifications.
    """
    
    user_id = str(current_user["_id"])
    user = current_user
    prefs = user.get("notification_preferences", {})
    
    # Create notification record for the authenticated user
    notification_data = {
        "user_id": user_id,
        "type": "carbon_alert",
        "project": project_name,
        "carbon_value": carbon_value,
        "threshold": threshold,
        "message": f"⚠️ {project_name} exceeded carbon threshold: {carbon_value}g > {threshold}g",
        "created_at": datetime.utcnow(),
        "read": False
    }
    
    result = await notifications_collection.insert_one(notification_data)
    
    alerts_sent = []
    
    # Send Slack notification
    if prefs.get("slack_notifications") and slack_webhook_url:
        try:
            import httpx
            payload = {
                "blocks": [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"*⚠️ Carbon Alert*\nProject: `{project_name}`\nEmissions: `{carbon_value}g` (threshold: `{threshold}g`)"
                        }
                    },
                    {
                        "type": "actions",
                        "elements": [
                            {
                                "type": "button",
                                "text": {"type": "plain_text", "text": "View Details"},
                                "url": "https://greencode-guardian.app/dashboard"
                            }
                        ]
                    }
                ]
            }
            async with httpx.AsyncClient() as client:
                await client.post(slack_webhook_url, json=payload)
            alerts_sent.append("slack")
        except Exception as e:
            print(f"Slack notification failed: {e}")
    
    # Send Email notification
    if prefs.get("email_notifications"):
        try:
            await send_email_alert(
                user.get("email"),
                project_name,
                carbon_value,
                threshold
            )
            alerts_sent.append("email")
        except (NotImplementedError, Exception) as e:
            print(f"Email notification failed: {e}")
    
    return {
        "notification_id": str(result.inserted_id),
        "alerts_sent": alerts_sent,
        "user_id": user_id
    }


async def send_email_alert(email: str, project: str, carbon: float, threshold: float):
    """Send email alert - not yet implemented (requires SMTP/SendGrid config)."""
    raise NotImplementedError("Email alerts are not configured. Set up aiosmtplib or SendGrid.")


@router.post("/achievement-unlock")
async def send_achievement_notification(
    achievement: str = Body(...),
    description: str = Body(...),
    current_user: dict = Depends(get_current_user)
):
    """Notify user when they unlock an achievement."""
    
    user_id = str(current_user["_id"])
    notification = {
        "user_id": user_id,
        "type": "achievement",
        "achievement": achievement,
        "description": description,
        "created_at": datetime.utcnow(),
        "read": False
    }
    
    result = await notifications_collection.insert_one(notification)
    
    return {
        "notification_id": str(result.inserted_id),
        "status": "sent"
    }


@router.get("/list")
async def get_user_notifications(
    current_user: dict = Depends(get_current_user),
    unread_only: bool = Query(False),
    limit: int = Query(20, ge=1, le=100)
):
    """Get user's notification history."""
    
    user_id = current_user["_id"]
    query = {"user_id": user_id}
    if unread_only:
        query["read"] = False
    
    notifications = await notifications_collection.find(query)\
        .sort("created_at", -1)\
        .limit(limit)\
        .to_list(None)
    
    return {
        "total": len(notifications),
        "notifications": [
            {
                "id": str(n["_id"]),
                "type": n["type"],
                "title": n.get("title") or n.get("type", "Notification"),
                "message": n.get("message", ""),
                "created_at": n["created_at"],
                "read": n["read"]
            }
            for n in notifications
        ]
    }


@router.post("/mark-as-read/{notification_id}")
async def mark_notification_read(notification_id: str, current_user: dict = Depends(get_current_user)):
    """Mark a notification as read."""
    
    from bson import ObjectId
    
    user_id = current_user["_id"]
    result = await notifications_collection.update_one(
        {"_id": ObjectId(notification_id), "user_id": user_id},
        {"$set": {"read": True}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    return {"status": "marked_as_read"}


@router.post("/mark-all-read")
async def mark_all_notifications_read(current_user: dict = Depends(get_current_user)):
    """Mark all user's notifications as read."""
    
    user_id = current_user["_id"]
    result = await notifications_collection.update_many(
        {"user_id": user_id, "read": False},
        {"$set": {"read": True}}
    )
    
    return {"status": "marked_all_as_read", "count": result.modified_count}


@router.post("/digest")
async def send_daily_digest(current_user: dict = Depends(get_current_user)):
    """Send a daily digest of project insights and improvements."""
    
    user_id = current_user["_id"]
    user = await users_collection.find_one({"_id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Aggregate user's projects from last 24 hours
    from datetime import timedelta
    yesterday = datetime.utcnow() - timedelta(days=1)
    
    projects = await projects_collection.find({
        "user_id": user_id,
        "timestamp": {"$gte": yesterday}
    }).to_list(None)
    
    if not projects:
        return {"status": "no_data"}
    
    avg_score = sum(p["green_score"] for p in projects) / len(projects)
    total_carbon = sum(p["carbon_emissions"] for p in projects)
    
    digest_message = f"""
    📊 Daily Digest for {user.get("name")}
    
    Total Scans: {len(projects)}
    Average Green Score: {avg_score:.1f}
    Total Carbon: {total_carbon:.2f}g
    
    Keep optimizing your code! 🌿
    """
    
    notification = {
        "user_id": user_id,
        "type": "digest",
        "message": digest_message,
        "created_at": datetime.utcnow(),
        "read": False
    }
    
    result = await notifications_collection.insert_one(notification)
    
    return {
        "digest_id": str(result.inserted_id),
        "summary": {
            "scans": len(projects),
            "avg_score": round(avg_score, 2),
            "total_carbon": round(total_carbon, 2)
        }
    }