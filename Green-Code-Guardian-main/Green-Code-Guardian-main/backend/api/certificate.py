from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import HTMLResponse
from blockchain.hedera_client import store_on_hedera, generate_certificate_html
from database.connection import certificates_collection, projects_collection
from models.schemas import CertificateCreate
from bson import ObjectId
from datetime import datetime
from api.auth_utils import get_current_user

router = APIRouter()

@router.post("/generate")
async def generate_certificate(data: CertificateCreate, current_user: dict = Depends(get_current_user)):
    """Generate and store a blockchain-backed certificate."""
    user_id = str(current_user["_id"])

    # Fetch latest project metrics for the authenticated user
    project = await projects_collection.find_one(
        {"project_name": data.project_name, "user_id": user_id},
        sort=[("timestamp", -1)]
    )
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found. Run a metrics collection first.")
    
    cert_input = {
        "project_name": data.project_name,
        "carbon_emissions": project.get("carbon_emissions", 0),
        "green_score": project.get("green_score", 0),
        "optimization_status": "analyzed"
    }
    
    blockchain_result = await store_on_hedera(cert_input)
    
    cert_doc = {
        **blockchain_result,
        "user_id": user_id,
        "project_name": data.project_name,
        "project_id": data.project_id,
        "carbon_value": project.get("carbon_emissions", 0),
        "green_score": project.get("green_score", 0),
        "created_at": datetime.utcnow()
    }
    
    result = await certificates_collection.insert_one(cert_doc)
    cert_doc["_id"] = str(result.inserted_id)
    cert_doc["id"] = str(result.inserted_id)
    
    return {"status": "success", "certificate": cert_doc}

@router.get("/{certificate_id}/html", response_class=HTMLResponse)
async def get_certificate_html(certificate_id: str, current_user: dict = Depends(get_current_user)):
    """Get certificate as HTML page."""
    user_id = str(current_user["_id"])
    cert = await certificates_collection.find_one({"certificate_id": certificate_id, "user_id": user_id})
    if not cert:
        raise HTTPException(status_code=404, detail="Certificate not found")
    cert["_id"] = str(cert["_id"])
    return generate_certificate_html(cert)

@router.get("/list")
async def list_certificates(current_user: dict = Depends(get_current_user), limit: int = 10):
    """List certificates for the authenticated user."""
    user_id = str(current_user["_id"])
    certs = []
    async for cert in certificates_collection.find({"user_id": user_id}).sort("created_at", -1).limit(limit):
        cert["_id"] = str(cert["_id"])
        certs.append(cert)
    return {"status": "success", "certificates": certs}
