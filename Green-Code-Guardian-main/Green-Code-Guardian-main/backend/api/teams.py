"""
Teams router - Enable multi-user collaboration and shared projects.
Teams can invite members, share insights, and track team carbon footprint.
"""

from fastapi import APIRouter, HTTPException, Body, Query, Depends
from database.connection import teams_collection, users_collection, projects_collection
from models.schemas import TeamCreate, TeamMember
from datetime import datetime
from typing import Optional
from bson import ObjectId
from api.auth_utils import get_current_user

router = APIRouter()


@router.post("/create")
async def create_team(team_data: TeamCreate):
    """Create a new team."""
    
    team = {
        "name": team_data.name,
        "description": team_data.description,
        "owner_id": team_data.owner_id,
        "members": [team_data.owner_id],
        "created_at": datetime.utcnow(),
        "settings": {
            "public": team_data.public,
            "invite_only": not team_data.public
        }
    }
    
    result = await teams_collection.insert_one(team)
    
    # Add team to owner's profile
    await users_collection.update_one(
        {"_id": team_data.owner_id},
        {"$push": {"teams": str(result.inserted_id)}}
    )
    
    return {
        "status": "created",
        "team_id": str(result.inserted_id),
        "team_name": team["name"]
    }


@router.post("/invite")
async def invite_member(
    team_id: str = Body(...),
    user_email: str = Body(...),
    inviter_id: str = Body(...)
):
    """
    Send invitation to join a team.
    User must exist in system first.
    """
    
    team = await teams_collection.find_one({"_id": ObjectId(team_id)})
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    # Verify inviter is owner or admin
    if team["owner_id"] != inviter_id:
        raise HTTPException(status_code=403, detail="Only team owner can invite")
    
    # Find user by email
    user = await users_collection.find_one({"email": user_email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_id = user["_id"]
    
    # Check if already member
    if user_id in team["members"]:
        raise HTTPException(status_code=400, detail="User is already a member")
    
    # Add member
    await teams_collection.update_one(
        {"_id": ObjectId(team_id)},
        {"$push": {"members": user_id}}
    )
    
    # Add team to user's profile
    await users_collection.update_one(
        {"_id": user_id},
        {"$push": {"teams": team_id}}
    )
    
    return {
        "status": "invited",
        "team_id": team_id,
        "user_email": user_email
    }


@router.get("/list")
async def list_teams(current_user: dict = Depends(get_current_user)):
    """List all teams a user is part of."""
    user_id = current_user["_id"]
    user = await users_collection.find_one({"_id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    team_ids = user.get("teams", [])
    teams = []
    for team_id in team_ids:
        team = await teams_collection.find_one({"_id": ObjectId(team_id)})
        if team:
            teams.append({
                "id": str(team['_id']),
                "name": team['name'],
                "member_count": len(team.get('members', [])),
                "owner": team['owner_id'] == user_id
            })
    return {"teams": teams, "total": len(teams)}


@router.get("/{team_id}")
async def get_team_details(team_id: str):
    """Get team information and member list."""
    
    team = await teams_collection.find_one({"_id": ObjectId(team_id)})
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    # Get member details
    members = []
    for member_id in team.get("members", []):
        user = await users_collection.find_one({"_id": member_id})
        if user:
            members.append({
                "id": member_id,
                "name": user.get("name"),
                "email": user.get("email"),
                "role": "owner" if member_id == team["owner_id"] else "member"
            })
    
    return {
        "team_id": str(team["_id"]),
        "name": team["name"],
        "description": team.get("description"),
        "owner_id": team["owner_id"],
        "members": members,
        "member_count": len(members),
        "created_at": team["created_at"]
    }


@router.get("/{team_id}/analytics")
async def get_team_analytics(team_id: str):
    """Get aggregated analytics for all team projects."""
    
    team = await teams_collection.find_one({"_id": ObjectId(team_id)})
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    member_ids = team.get("members", [])
    
    # Aggregate all projects by team members
    projects = await projects_collection.find({
        "user_id": {"$in": member_ids}
    }).to_list(None)
    
    if not projects:
        return {
            "team_id": team_id,
            "total_members": len(member_ids),
            "total_projects": 0,
            "avg_green_score": 0,
            "total_carbon": 0
        }
    
    total_scans = len(projects)
    avg_score = sum(p["green_score"] for p in projects) / total_scans
    total_carbon = sum(p["carbon_emissions"] for p in projects)
    
    return {
        "team_id": team_id,
        "team_name": team["name"],
        "total_members": len(member_ids),
        "total_projects": len(set(p["project_name"] for p in projects)),
        "total_scans": total_scans,
        "avg_green_score": round(avg_score, 2),
        "total_carbon": round(total_carbon, 2),
        "best_project": max(projects, key=lambda x: x["green_score"])["project_name"] if projects else None
    }


@router.post("/{team_id}/transfer-ownership")
async def transfer_ownership(
    team_id: str,
    new_owner_id: str = Body(...),
    current_owner_id: str = Body(...)
):
    """Transfer team ownership to another member."""
    
    team = await teams_collection.find_one({"_id": ObjectId(team_id)})
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    if team["owner_id"] != current_owner_id:
        raise HTTPException(status_code=403, detail="Only owner can transfer ownership")
    
    if new_owner_id not in team["members"]:
        raise HTTPException(status_code=400, detail="New owner must be a team member")
    
    await teams_collection.update_one(
        {"_id": ObjectId(team_id)},
        {"$set": {"owner_id": new_owner_id}}
    )
    
    return {"status": "ownership_transferred", "new_owner_id": new_owner_id}


@router.delete("/{team_id}/members/{member_id}")
async def remove_team_member(
    team_id: str,
    member_id: str,
    requester_id: str = Body(...)
):
    """Remove a member from team (owner only)."""
    
    team = await teams_collection.find_one({"_id": ObjectId(team_id)})
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    if team["owner_id"] != requester_id:
        raise HTTPException(status_code=403, detail="Only owner can remove members")
    
    if member_id == team["owner_id"]:
        raise HTTPException(status_code=400, detail="Cannot remove team owner")
    
    await teams_collection.update_one(
        {"_id": ObjectId(team_id)},
        {"$pull": {"members": member_id}}
    )
    
    await users_collection.update_one(
        {"_id": member_id},
        {"$pull": {"teams": team_id}}
    )
    
    return {"status": "member_removed", "member_id": member_id}