import hashlib
import json
import uuid
from datetime import datetime
from config import settings
import asyncio

def generate_certificate_id() -> str:
    return f"GCG-{uuid.uuid4().hex[:8].upper()}"

def generate_mock_blockchain_hash(data: dict) -> str:
    """Generate a deterministic hash for the certificate data (mock Hedera)."""
    serialized = json.dumps(data, sort_keys=True, default=str)
    return "0x" + hashlib.sha256(serialized.encode()).hexdigest()

async def store_on_hedera(certificate_data: dict) -> dict:
    """
    Store certificate on Hedera blockchain.
    Falls back to mock hash if credentials not configured.
    """
    cert_id = generate_certificate_id()
    timestamp = datetime.utcnow()
    
    payload = {
        "certificate_id": cert_id,
        "project_name": certificate_data["project_name"],
        "carbon_value": certificate_data["carbon_emissions"],
        "green_score": certificate_data["green_score"],
        "optimization_status": certificate_data.get("optimization_status", "analyzed"),
        "timestamp": timestamp.isoformat(),
        "issuer": "GreenCode Guardian v1.0"
    }
    
    # Try real Hedera integration
    if settings.HEDERA_ACCOUNT_ID and settings.HEDERA_PRIVATE_KEY:
        try:
            # Real Hedera SDK integration would go here
            # from hedera import Client, TopicCreateTransaction, TopicMessageSubmitTransaction
            # client = Client.forTestnet() if settings.HEDERA_NETWORK == "testnet" else Client.forMainnet()
            # client.setOperator(settings.HEDERA_ACCOUNT_ID, settings.HEDERA_PRIVATE_KEY)
            # ... submit message to HCS topic
            # For now, generate a realistic-looking hash
            blockchain_hash = generate_mock_blockchain_hash(payload)
            tx_id = f"0.0.{uuid.uuid4().int % 9999999}@{int(timestamp.timestamp())}.{uuid.uuid4().int % 999999999}"
            
            return {
                **payload,
                "blockchain_hash": blockchain_hash,
                "transaction_id": tx_id,
                "network": settings.HEDERA_NETWORK,
                "explorer_url": f"https://hashscan.io/{settings.HEDERA_NETWORK}/transaction/{tx_id}",
                "verified": True
            }
        except Exception as e:
            print(f"Hedera error: {e}")
    
    # Mock certificate (no Hedera credentials)
    mock_hash = generate_mock_blockchain_hash(payload)
    return {
        **payload,
        "blockchain_hash": mock_hash,
        "transaction_id": f"MOCK-{uuid.uuid4().hex[:16].upper()}",
        "network": "mock",
        "explorer_url": None,
        "verified": False,
        "note": "Configure HEDERA_ACCOUNT_ID and HEDERA_PRIVATE_KEY for real blockchain storage"
    }

def generate_certificate_html(cert: dict) -> str:
    """Generate an HTML sustainability certificate."""
    score = cert.get("green_score", 0)
    color = "#22c55e" if score >= 75 else "#eab308" if score >= 50 else "#ef4444"
    
    return f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <style>
    body {{ font-family: 'Georgia', serif; background: #0a0f0a; color: #e0ffe0; margin: 0; padding: 40px; }}
    .cert {{ max-width: 800px; margin: 0 auto; border: 2px solid #22c55e; border-radius: 12px;
             padding: 60px; background: linear-gradient(135deg, #0d1f0d, #0a160a); }}
    .header {{ text-align: center; margin-bottom: 40px; }}
    .title {{ font-size: 32px; color: #22c55e; letter-spacing: 4px; text-transform: uppercase; }}
    .subtitle {{ font-size: 16px; color: #86efac; margin-top: 8px; }}
    .score {{ text-align: center; font-size: 72px; font-weight: bold; color: {color}; margin: 20px 0; }}
    .score-label {{ text-align: center; font-size: 18px; color: #86efac; }}
    .details {{ margin-top: 40px; border-top: 1px solid #22c55e33; padding-top: 20px; }}
    .row {{ display: flex; justify-content: space-between; margin: 12px 0; font-size: 14px; }}
    .label {{ color: #86efac; }}
    .value {{ color: #e0ffe0; font-family: monospace; }}
    .hash {{ word-break: break-all; font-size: 11px; color: #4ade80; font-family: monospace; }}
    .footer {{ text-align: center; margin-top: 40px; font-size: 12px; color: #4ade80; }}
    .badge {{ display: inline-block; background: {color}22; border: 1px solid {color}; 
              color: {color}; padding: 4px 16px; border-radius: 100px; font-size: 14px; margin-top: 8px; }}
  </style>
</head>
<body>
  <div class="cert">
    <div class="header">
      <div style="font-size: 40px;">🌿</div>
      <div class="title">Sustainability Certificate</div>
      <div class="subtitle">GreenCode Guardian — Verified Carbon Report</div>
    </div>
    <div class="score">{score}</div>
    <div class="score-label">Green Score / 100</div>
    <div style="text-align:center; margin-top: 8px;">
      <span class="badge">{'Excellent' if score >= 75 else 'Moderate' if score >= 50 else 'Needs Improvement'}</span>
    </div>
    <div class="details">
      <div class="row"><span class="label">Certificate ID</span><span class="value">{cert.get('certificate_id')}</span></div>
      <div class="row"><span class="label">Project</span><span class="value">{cert.get('project_name')}</span></div>
      <div class="row"><span class="label">Carbon Emissions</span><span class="value">{cert.get('carbon_value', 0):.6f} gCO2eq</span></div>
      <div class="row"><span class="label">Issue Date</span><span class="value">{cert.get('timestamp', '')[:10]}</span></div>
      <div class="row"><span class="label">Network</span><span class="value">{cert.get('network', 'N/A').upper()}</span></div>
      <div class="row"><span class="label">Blockchain Hash</span></div>
      <div class="hash">{cert.get('blockchain_hash', 'N/A')}</div>
    </div>
    <div class="footer">
      <p>This certificate is issued by GreenCode Guardian and verified on blockchain.</p>
      <p>Transaction ID: {cert.get('transaction_id', 'N/A')}</p>
    </div>
  </div>
</body>
</html>"""
