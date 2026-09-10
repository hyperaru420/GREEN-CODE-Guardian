# 🌿 GreenCode Guardian

> **Sustainability-focused software monitoring platform** — Track resource usage, estimate carbon emissions, get AI-powered optimizations, and generate blockchain-backed sustainability certificates. **Now with CI/CD webhooks, leaderboards, real-time notifications, and team collaboration!**

---

## ✨ Features

| Module | Description |
|--------|-------------|
| 📊 **Live Monitoring** | CPU, Memory, Disk, Network, Execution Time via `psutil` |
| 🌍 **Carbon Estimation** | Region-aware energy → CO2 conversion (15 regions) |
| 🟢 **Green Score** | 0–100 composite sustainability score with letter grades |
| 🤖 **AI Suggestions** | Groq LLaMA-3 powered optimization recommendations |
| ⛓️ **Blockchain Certs** | Hedera HCS verified sustainability certificates |
| 📈 **Dashboard** | Real-time charts with Recharts + trend history |
| 🔄 **CI/CD Webhooks** | 🆕 GitHub, GitLab, custom pipeline integration |
| 🏆 **Leaderboards** | 🆕 Global rankings, trending projects, user achievements |
| 🔔 **Notifications** | 🆕 Slack, Email, in-app alerts for thresholds & milestones |
| 👥 **Teams** | 🆕 Invite-based collaboration, shared projects, team analytics |
| 🖥️ **CLI Tool** | 🆕 `gcg scan`, `gcg leaderboard`, command-line integration |
| 🐳 **Docker** | Full docker-compose stack with optional Prometheus/Grafana |

---

## 🚀 Quick Start

### Local Development

```
greencode-guardian/
│
├── backend/                         # FastAPI Python backend
│   ├── main.py                      # App entry point
│   ├── config.py                    # Settings / env vars
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── .env.example                 # ← copy to .env and fill in
│   │
│   ├── api/                         # REST API routers
│   │   ├── auth.py                  # POST /auth/login, /auth/register
│   │   ├── auth_utils.py            # JWT helpers
│   │   ├── metrics.py               # GET /metrics/live, POST /metrics/collect
│   │   ├── carbon.py                # GET /carbon/estimate
│   │   ├── greenscore.py            # GET /greenscore/calculate
│   │   ├── suggestions.py           # GET /suggestions/generate
│   │   ├── certificate.py           # POST /certificate/generate
│   │   └── history.py               # GET /history/projects, /trends, /summary
│   │
│   ├── monitoring/                  # Core metric & carbon logic
│   │   ├── collector.py             # psutil-based system metrics
│   │   ├── carbon_estimator.py      # Power → Energy → CO2 formulas
│   │   └── green_score.py           # Weighted scoring algorithm
│   │
│   ├── ai/
│   │   └── suggestions.py           # Groq LLaMA-3 + static fallback rules
│   │
│   ├── blockchain/
│   │   └── hedera_client.py         # Hedera HCS + mock hash fallback
│   │
│   ├── database/
│   │   └── connection.py            # Motor async MongoDB client
│   │
│   └── models/
│       └── schemas.py               # Pydantic request/response models
│
├── frontend/                        # React + Tailwind frontend
│   ├── package.json
│   ├── tailwind.config.js
│   ├── Dockerfile
│   ├── public/
│   │   └── index.html
│   └── src/
│       ├── App.js                   # Router + Auth guard
│       ├── index.js
│       ├── index.css                # Global dark-green theme
│       │
│       ├── context/
│       │   └── AuthContext.js       # Login state via React Context
│       │
│       ├── services/
│       │   └── api.js               # Axios client + all API calls
│       │
│       ├── pages/
│       │   ├── LoginPage.js         # Auth (login + register)
│       │   ├── DashboardPage.js     # Main monitoring dashboard
│       │   ├── HistoryPage.js       # Project scan history table
│       │   ├── CertificatePage.js   # Blockchain certificates list
│       │   └── SettingsPage.js      # API keys + platform config
│       │
│       ├── components/
│       │   ├── Layout.js            # Sidebar navigation wrapper
│       │   ├── GreenScoreRing.js    # SVG animated score ring
│       │   ├── MetricCard.js        # Stat card with progress bar
│       │   └── SuggestionCard.js    # Expandable AI suggestion card
│       │
│       └── charts/
│           ├── EmissionChart.js     # Area chart (carbon + score trends)
│           └── ResourceBarChart.js  # Bar chart (CPU/Mem/Disk/Net)
│
├── monitoring/
│   └── prometheus.yml               # Prometheus scrape config
│
├── .github/
│   └── workflows/
│       └── greencode.yml            # CI/CD sustainability pipeline
│
├── docker-compose.yml               # Full stack orchestration
└── README.md
```

---

## 🚀 Quick Start

### Option A — Local Development

#### 1. Backend Setup

```bash
cd backend

# Copy and configure environment
cp .env.example .env
# Edit .env with your keys (see Configuration section)

# Create virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start FastAPI server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

> API docs available at: http://localhost:8000/docs

#### 2. Frontend Setup

```bash
cd frontend

npm install --legacy-peer-deps

# Start dev server
npm start
```

> Frontend available at: http://localhost:3000

#### 3. MongoDB

```bash
# Using Docker (easiest)
docker run -d --name mongodb -p 27017:27017 mongo:6

# Or install MongoDB Community locally:
# https://www.mongodb.com/try/download/community
```

---

### Option B — Docker Compose (Recommended)

```bash
# Clone the repo
git clone https://github.com/your-org/greencode-guardian.git
cd greencode-guardian

# Configure backend
cp backend/.env.example backend/.env
# Edit backend/.env

# Start all services
docker-compose up -d

# With Prometheus + Grafana monitoring
docker-compose --profile monitoring up -d
```

Services:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Grafana: http://localhost:3001 (admin / set via GF_SECURITY_ADMIN_PASSWORD)
- Prometheus: http://localhost:9090

---

## ⚙️ Configuration

Edit `backend/.env`:

```env
# MongoDB
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=greencode_guardian

# JWT Secret (change this!)
SECRET_KEY=your-very-long-random-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Groq AI — https://console.groq.com (free tier available)
GROQ_API_KEY=YOUR_GROQ_API_KEY

# Hedera Blockchain — https://portal.hedera.com (free testnet)
HEDERA_ACCOUNT_ID=0.0.XXXXXXX
HEDERA_PRIVATE_KEY=YOUR_HEDERA_PRIVATE_KEY
HEDERA_NETWORK=testnet
```

> **Without API keys:** The platform works fully with mock data.
> - No Groq key → Uses built-in static optimization rules
> - No Hedera key → Uses SHA-256 mock blockchain hashes

---

## 📡 API Reference

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Register new user |
| POST | `/auth/login` | Login (returns JWT token) |

### Metrics
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/metrics/live` | Live system metrics (no DB write) |
| POST | `/metrics/collect?project_name=X&region=Y` | Collect + store full scan |
| GET | `/metrics/regions` | List available carbon regions |

### Carbon
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/carbon/estimate` | Estimate carbon from params |

### Green Score
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/greenscore/calculate` | Calculate score from params |

### AI Suggestions
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/suggestions/generate` | Get Groq AI optimization tips |
| POST | `/suggestions/refactor` | Analyze code files and return green refactor suggestions |

### Certificates
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/certificate/generate` | Generate blockchain certificate |
| GET | `/certificate/list` | List all certificates |
| GET | `/certificate/{id}/html` | View certificate as HTML |

### History
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/history/projects` | Paginated project scan history |
| GET | `/history/projects/names` | Unique project names |
| GET | `/history/trends?project_name=X` | Time-series trends |
| GET | `/history/summary` | Platform-wide statistics |

---

## 🌍 Supported Regions & Carbon Intensities

| Region ID | Name | gCO2/kWh |
|-----------|------|-----------|
| `us-east` | US East | 386 |
| `us-west` | US West | 210 |
| `eu-north` | EU North | 53 |
| `eu-west` | EU West | 233 |
| `ap-south` | Asia South (India) | 708 |
| `sa-east` | South America | 109 |
| `ca-central` | Canada | 120 |
| `global-average` | Global Average | 442 |

---

## 🟢 Green Score Algorithm

```
Score = CPU(25%) + Memory(20%) + Carbon(35%) + Execution(10%) + Disk(10%)
```

| Score | Grade | Status |
|-------|-------|--------|
| 85–100 | A+ | 🟢 Excellent |
| 75–84 | A | 🟢 Good |
| 65–74 | B | 🟡 Moderate |
| 50–64 | C | 🟡 Needs Work |
| 35–49 | D | 🟠 Poor |
| 0–34 | F | 🔴 Critical |

---

## 🤖 AI Model

The platform uses **Groq's LLaMA 3 8B** (`llama3-8b-8192`) for generating optimization suggestions. Groq offers a generous free tier at https://console.groq.com.

**Fallback rules** (no API key needed):
- Nested loop optimization
- N+1 query detection
- Response caching suggestions
- Memory management tips
- API batching recommendations

---

## ⛓️ Blockchain Certification

Certificates are stored using **Hedera Consensus Service (HCS)**:

1. Scan metrics collected → Green Score computed
2. Certificate payload hashed + submitted to HCS topic
3. Transaction ID returned + stored in MongoDB
4. Certificate viewable as styled HTML page

**Without Hedera credentials:** SHA-256 mock hashes are generated locally (still tamper-evident, just not on-chain).

---

## 🔄 CI/CD Integration

Add to your repo's GitHub Actions:

```yaml
- name: GreenCode Scan
  run: |
    curl -X POST "http://your-gcg-server/metrics/collect\
      ?project_name=${{ github.repository }}\
      &region=us-east"
```

The included workflow (`.github/workflows/greencode.yml`) will:
- Run on every push/PR
- Collect system metrics during CI
- Comment Green Score on PRs
- Fail build if score < 25 (critical)
- Upload sustainability report as artifact

---

## 🧩 Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | React 18, Tailwind CSS, Recharts, Axios |
| Backend | Python 3.11, FastAPI, Uvicorn |
| Database | MongoDB 6, Motor (async) |
| Auth | JWT (python-jose), bcrypt |
| Monitoring | psutil, Prometheus, Grafana |
| AI | Groq API (LLaMA 3 8B) |
| Blockchain | Hedera HCS SDK |
| DevOps | Docker, Docker Compose, GitHub Actions |

---

## 📝 License

MIT License — see LICENSE for details.

---

<div align="center">
  Made with 🌿 for a greener internet
</div>
