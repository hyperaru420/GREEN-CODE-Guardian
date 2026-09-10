# 🌿 GreenCode Guardian v2.0 - Setup & Features Guide

## ✨ New Features Added

### 1. **CI/CD Webhook Integration** 🔗
Connect GreenCode to your GitHub, GitLab, or custom CI/CD pipeline.

**Features:**
- Automatic sustainability scans on every push
- Pull request comments with green scores
- Branch-based tracking
- Carbon threshold alerts

**Setup:**

#### GitHub
1. Generate webhook secret:
   ```bash
   openssl rand -hex 32
   ```
2. Go to your repository → Settings → Webhooks → Add webhook
3. Payload URL: `https://your-api.com/webhook/github`
4. Content type: `application/json`
5. Events: Push, Pull Request, Workflow run
6. Secret: Paste the generated secret
7. Update `.env`:
   ```
   GITHUB_WEBHOOK_SECRET=your-secret-here
   ```

#### GitHub Actions Workflow
Copy `.github/workflows/greencode-webhook.yml` to your projects!

```bash
# In your project repository
cp greencode-guardian/.github/workflows/greencode-webhook.yml .github/workflows/
git add .github/workflows/greencode-webhook.yml
git commit -m "Add GreenCode Guardian CI/CD checks"
```

---

### 2. **Leaderboards & Competitive Rankings** 🏆

Endpoints:
- **`GET /leaderboard/global`** - Global rankings by green score
- **`GET /leaderboard/trending`** - Projects with biggest improvements
- **`GET /leaderboard/regions`** - Regional sustainability stats
- **`GET /leaderboard/user/{user_id}`** - Personal career stats

**Example:**
```bash
# Get top 10 projects this month
curl "http://localhost:8000/leaderboard/global?period=month&limit=10"

# Get trending projects
curl "http://localhost:8000/leaderboard/trending?period=week"
```

---

### 3. **Real-Time Notifications** 🔔

**Notification Types:**
- Carbon threshold alerts
- Achievement unlocks
- Daily/weekly digests
- Team milestones

**Channels:**
- 📧 Email
- 💬 Slack
- 🔔 In-app

**Setup Slack Notifications:**
1. Create Slack webhook: https://api.slack.com/messaging/webhooks
2. Test connection:
   ```bash
   curl -X POST http://localhost:8000/notifications/test-slack \
     -H "Content-Type: application/json" \
     -d '{"slack_webhook_url":"https://hooks.slack.com/services/YOUR/WEBHOOK"}'
   ```

3. Update user preferences:
   ```bash
   curl -X POST http://localhost:8000/notifications/preferences/{user_id} \
     -H "Content-Type: application/json" \
     -d '{
       "slack_enabled": true,
       "email_enabled": true,
       "slack_webhook_url": "https://hooks.slack.com/services/YOUR/WEBHOOK"
     }'
   ```

---

### 4. **Team Collaboration** 👥

**Features:**
- Create teams with invite-based membership
- Share project insights across team
- Team-wide carbon footprint tracking
- Team leaderboards

**API:**
```bash
# Create team
curl -X POST http://localhost:8000/teams/create \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Team",
    "description": "Green developers",
    "owner_id": "user123",
    "public": false
  }'

# Invite member
curl -X POST http://localhost:8000/teams/invite \
  -H "Content-Type: application/json" \
  -d '{
    "team_id": "team123",
    "user_email": "dev@company.com",
    "inviter_id": "user123"
  }'

# Get team analytics
curl http://localhost:8000/teams/{team_id}/analytics

# Get team leaderboard
curl http://localhost:8000/leaderboard/team/{team_id}
```

---

## 🖥️ CLI Tool

**Installation:**
```bash
# Make CLI executable
chmod +x backend/gcg_cli.py

# Or run directly
python backend/gcg_cli.py --help
```

**Commands:**

```bash
# Scan project
python backend/gcg_cli.py scan ./my-project --region us-east

# View leaderboard
python backend/gcg_cli.py leaderboard --period month

# View trending
python backend/gcg_cli.py trending --period week

# View user stats
python backend/gcg_cli.py stats user123

# Set API key for auth
export GCG_API_KEY=your_key
export GCG_API_URL=https://api.greencode.app
python backend/gcg_cli.py scan ./project
```

---

## 🚀 Deployment Checklist

- [ ] Add new env variables to `.env`:
  ```
  GITHUB_WEBHOOK_SECRET=your-secret
  SLACK_BOT_TOKEN=xoxb-your-token (optional)
  ```

- [ ] Install new dependencies:
  ```bash
  pip install -r backend/requirements.txt
  ```

- [ ] Run migrations (if using MongoDB):
  ```bash
  # Indexes
  db.projects.createIndex({"timestamp": -1})
  db.webhook_events.createIndex({"repo": 1})
  db.notifications.createIndex({"user_id": 1})
  db.teams.createIndex({"members": 1})
  ```

- [ ] Update Docker: Re-build containers
  ```bash
  docker-compose up --build
  ```

- [ ] Update GitHub workflows in your projects

---

## 📊 Webhook Custom Payload Format

**Send sustainability data to your dashboard:**

```bash
curl -X POST http://localhost:8000/webhook/custom \
  -H "Content-Type: application/json" \
  -d '{
    "repo": "my-project",
    "branch": "main",
    "commit": "abc123def456",
    "metrics": {
      "cpu": 45.2,
      "memory_gb": 2.5,
      "execution_time": 120,
      "disk": 30.1
    },
    "carbon_threshold": 75
  }'
```

---

## 🎯 Hackathon Winning Features

### Already Implemented:
✅ CI/CD webhooks (GitHub, GitLab, Custom)  
✅ Global leaderboards with trends  
✅ Multi-channel notifications  
✅ Team collaboration  
✅ CLI tool for integration  
✅ Real-time alerts  
✅ Regional analytics  

### Potential Next Steps:
- [ ] Browser extension for website monitoring
- [ ] Mobile app (React Native / Flutter)
- [ ] Integration marketplace (add Jira, Azure DevOps)
- [ ] Predictive ML model for carbon trends
- [ ] ESG compliance reports
- [ ] Gamification (badges, streaks)

---

## 🐛 Troubleshooting

**Webhook not receiving events?**
- Check API URL is publicly accessible
- Verify webhook secret matches GitHub setting
- Check server logs: `docker logs gcg_backend`

**Notifications not sending?**
- Verify Slack webhook URL is correct
- Check SMTP credentials for email
- Ensure user preferences are enabled

**Leaderboard empty?**
- Submit at least one scan via `/webhook/custom` or `/metrics/collect`
- Check database is populated: `db.projects.find().count()`

---

## 📚 API Documentation

**Full docs available at:**
```
GET http://localhost:8000/docs
```

(Swagger UI auto-generated from FastAPI)

---

## 🎓 Example Integrations

### Jenkins
```groovy
stage('Sustainability Check') {
  steps {
    sh '''
      curl -X POST http://greencode-api.com/webhook/custom \
        -H "Content-Type: application/json" \
        -d '{
          "repo": "${GIT_REPOSITORY}",
          "branch": "${GIT_BRANCH}",
          "commit": "${GIT_COMMIT}",
          "metrics": {"cpu": 50, "memory_gb": 2.0}
        }'
    '''
  }
}
```

### GitLab CI
```yaml
sustainability_check:
  stage: test
  script:
    - |
      curl -X POST $GCG_WEBHOOK_URL \
        -H "Content-Type: application/json" \
        -d '{
          "repo": "$CI_PROJECT_PATH",
          "branch": "$CI_COMMIT_REF_NAME",
          "commit": "$CI_COMMIT_SHA"
        }'
```

---

## 🌍 Environment Variables

```bash
# MongoDB
MONGODB_URL=mongodb://<username>:<password>@localhost:27017
DATABASE_NAME=greencode_guardian

# Auth
SECRET_KEY=your-jwt-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# AI
GROQ_API_KEY=your-groq-api-key

# Blockchain
HEDERA_ACCOUNT_ID=0.0.xxxxx
HEDERA_PRIVATE_KEY=YOUR_HEDERA_PRIVATE_KEY
HEDERA_NETWORK=testnet

# Webhooks
GITHUB_WEBHOOK_SECRET=your-github-secret
GITLAB_WEBHOOK_TOKEN=your-gitlab-token

# Notifications
SLACK_BOT_TOKEN=xoxb-your-slack-token
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_ADDRESS=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

---

**Version:** 2.0.0  
**Last Updated:** April 19, 2026  
**Status:** 🟢 Production Ready
