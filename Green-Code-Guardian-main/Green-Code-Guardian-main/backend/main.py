from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import metrics, carbon, greenscore, suggestions, certificate, history, auth, webhook, leaderboard, notifications, teams, users
import uvicorn

app = FastAPI(
    title="GreenCode Guardian API",
    description="Sustainability-focused software monitoring platform with CI/CD webhooks",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Core routers
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(metrics.router, prefix="/metrics", tags=["metrics"])
app.include_router(carbon.router, prefix="/carbon", tags=["carbon"])
app.include_router(greenscore.router, prefix="/greenscore", tags=["greenscore"])
app.include_router(suggestions.router, prefix="/suggestions", tags=["suggestions"])
app.include_router(certificate.router, prefix="/certificate", tags=["certificate"])
app.include_router(history.router, prefix="/history", tags=["history"])

# New premium features
app.include_router(webhook.router, prefix="/webhook", tags=["ci/cd"])
app.include_router(leaderboard.router, prefix="/leaderboard", tags=["competitive"])
app.include_router(notifications.router, prefix="/notifications", tags=["alerts"])
app.include_router(teams.router, prefix="/teams", tags=["collaboration"])
app.include_router(users.router, prefix="/users", tags=["user"])

@app.get("/")
async def root():
    return {
        "message": "GreenCode Guardian API v2.0",
        "status": "active",
        "features": [
            "Real-time monitoring",
            "Carbon estimation",
            "AI suggestions",
            "Blockchain certificates",
            "CI/CD webhooks",
            "Leaderboards",
            "Notifications",
            "Team collaboration"
        ]
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "version": "2.0.0"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
