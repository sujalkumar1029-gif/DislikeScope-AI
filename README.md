# DislikeScope-AI

**Authentic Social Sentiment & Dislike Diagnostics — Zero Fabricated Data**

DislikeScope-AI is a full-stack intelligence and diagnostics dashboard designed to analyze audience reactions on social platforms (**YouTube** and **X.com / Twitter**).

Unlike conventional analytics tools that fabricate sentiment scores when content is private, blocked, or unavailable, DislikeScope-AI operates under a strict **Truth Policy**:
- Reported metrics, retrieved text records, and analyzed sentiment counts are strictly reconciled and independently verifiable.
- When comments are disabled, unavailable, or restricted by login walls, the application displays honest diagnostic failure reasons rather than hallucinating metrics.
- All third-party estimates (such as Return YouTube Dislike counts) are prominently labeled as statistical estimates with transparent methodology notes.

---

## Supported Platforms

| Platform | Extraction Method | Sentiment Scope | Dislike Estimates | Status |
| :--- | :--- | :--- | :--- | :--- |
| **YouTube** | Public page & Innertube API | Public comments & replies | Return YouTube Dislike API (Labeled 3rd-Party) | **Phase 1 Verified** |
| **X.com** | Public syndication & web endpoints | Accessible thread replies | N/A (Platform has no dislike mechanism) | **Phase 2 Verified** |

*Note: Per strict scope, Instagram, Reddit, TikTok, and other platforms are intentionally excluded.*

---

## Architecture Overview

```
DislikeScope-AI/
├── .env.example              # Environment variables template
├── .env                      # Local runtime environment
├── .gitignore                # Git exclusions (.venv, node_modules, data/*.db, etc.)
├── README.md                 # System documentation & Fedora instructions
├── pytest.ini                # Pytest configuration
├── backend/
│   ├── requirements.txt      # Python dependencies
│   ├── config.py             # Configuration loader
│   ├── database.py           # SQLite persistence layer
│   ├── main.py               # FastAPI application & REST endpoints
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py        # Pydantic v2 schemas
│   ├── services/
│   │   ├── __init__.py
│   │   ├── sentiment.py      # Shared VADER sentiment engine
│   │   ├── youtube.py        # YouTube extraction & dislike estimates
│   │   ├── x_platform.py     # X.com syndication & login-wall diagnostics
│   │   └── exporter.py       # JSON and CSV export generators
│   └── tests/
│       ├── __init__.py
│       ├── conftest.py       # Isolated SQLite test fixtures
│       ├── test_youtube.py   # YouTube URL validation & extraction tests
│       ├── test_x_platform.py# X.com validation & diagnostic tests
│       ├── test_sentiment.py # VADER sentiment & reconciliation tests
│       ├── test_database.py  # SQLite CRUD & restart persistence tests
│       ├── test_api.py       # FastAPI HTTP endpoint tests
│       └── test_export.py    # CSV and JSON report export tests
├── frontend/
│   ├── package.json          # Node dependencies & scripts
│   ├── tsconfig.json         # TypeScript configuration (verbatimModuleSyntax)
│   ├── vite.config.ts        # Vite dev server with /api proxy to FastAPI
│   ├── index.html            # Semantic HTML with SEO & typography
│   └── src/
│       ├── main.tsx          # React application entry
│       ├── App.tsx           # Dashboard view coordinator
│       ├── index.css         # Modern dark theme design system
│       ├── api.ts            # Typed HTTP client
│       ├── types.ts          # TypeScript interfaces matching backend models
│       └── components/
│           ├── Header.tsx             # Brand header & Truth Policy indicator
│           ├── Icons.tsx              # Clean SVG icons
│           ├── UrlInput.tsx           # Platform selector & URL submission
│           ├── SentimentSummary.tsx   # Positive/Neutral/Negative cards & bar
│           ├── EngagementMetrics.tsx  # Views, likes, and dislike estimates
│           ├── DiagnosticsCard.tsx    # Record reconciliation & status table
│           ├── CommentsList.tsx       # Scored comment browser with filter
│           ├── HistoryPanel.tsx       # SQLite history sidebar
│           ├── ExportButtons.tsx      # CSV and JSON downloads
│           └── LimitationsNotice.tsx  # Access boundaries disclosure
└── data/
    └── dislikescope.db       # Local SQLite database (persisted)
```

---

## Fedora Linux Setup & Development Workflow

Tested and verified on **Fedora Linux 44 (Workstation Edition)** with **Python 3.14.8** and **Node.js v22.23.1**.

### 1. Prerequisites

Ensure system build tools, Git, Python, and Node.js are present:
```bash
sudo dnf install -y python3 python3-devel gcc git nodejs npm
```

### 2. Clone / Enter Workspace

```bash
cd /home/sk1029/Documents/projects/DislikeScope-AI
```

### 3. Backend Setup

Create and activate a Python virtual environment, then install dependencies:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r backend/requirements.txt
```

Set up environment variables:
```bash
cp .env.example .env
```

### 4. Frontend Setup

Install Node dependencies:
```bash
cd frontend
npm install
cd ..
```

---

## Running the Application

### Single Command (Recommended)

From the project root on Fedora Linux, run:

```bash
./run.sh
```
*(or alternatively: `npm start`)*

This single command automatically:
1. Verifies `.env` settings and prepares local data directories.
2. Uses the existing Python virtual environment (`.venv`) and checks backend dependencies.
3. Ensures frontend `node_modules` are present.
4. Checks for port conflicts on 8000 and 5173 to prevent duplicate servers.
5. Starts the **FastAPI backend** and verifies its health endpoint.
6. Starts the **Vite frontend server** and verifies it is accessible.
7. Streams colorized, tagged logs (`[BACKEND]` and `[FRONTEND]`).
8. Traps `Ctrl+C` (SIGINT/SIGTERM) to stop both processes cleanly without leaving orphaned servers.

| Service | Local URL |
| :--- | :--- |
| **Frontend Dashboard** | `http://localhost:5173` |
| **Backend API & Swagger Docs** | `http://127.0.0.1:8000/docs` |
| **Health Endpoint** | `http://127.0.0.1:8000/api/health` |

---

### Alternative: Manual Multi-Terminal Mode

If you prefer running services in separate terminal windows:

**Terminal 1 — Backend (FastAPI):**
```bash
source .venv/bin/activate
python3 -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

**Terminal 2 — Frontend (Vite):**
```bash
cd frontend
npm run dev
```

### Option B: Production Frontend Build

```bash
cd frontend
npm run build
```
Builds optimized production assets to `frontend/dist/`.

---

## Running the Test Suite

The test suite covers URL normalization, extraction failure modes, count reconciliation, database persistence, and CSV/JSON exports.

### Run Backend Tests (26 Automated Tests)
```bash
source .venv/bin/activate
pytest -v
```

### Run Frontend Typecheck & Build
```bash
cd frontend
npm run build
```

---

## Truth Policy & Diagnostics

DislikeScope-AI tracks data across four distinct stages:
1. **Platform Reported Comments**: Official counts published by the platform (e.g., YouTube video comment counter or X `conversation_count`).
2. **Retrieved Records**: Actual raw items pulled over the network through public endpoints.
3. **Usable Text Count**: Records containing genuine, non-empty text (filtering out blank or whitespace entries).
4. **Successfully Analyzed**: Comments passed through the sentiment pipeline and reconciled:
   $$\text{Positive Count} + \text{Neutral Count} + \text{Negative Count} = \text{Total Analyzed}$$

### Sentiment Methodology
Uses the **VADER (Valence Aware Dictionary and sEntiment Reasoner)** model, tuned specifically for social media micro-syntax, emojis, and slang:
- **Positive**: Compound score $\ge +0.05$
- **Neutral**: $-0.05 < \text{Compound score} < +0.05$
- **Negative**: Compound score $\le -0.05$

### Platform Limitations & Anonymous Access Boundaries
- **YouTube Dislikes**: YouTube permanently removed public dislike counts in 2021. Any dislike metrics displayed originate from the **Return YouTube Dislike (RYD)** project and are explicitly labeled as statistical estimates.
- **X.com Authentication**: X restricts anonymous access to thread replies behind login walls. When replies cannot be fetched anonymously, DislikeScope-AI reports an honest `restricted` diagnostic status with 0 analyzed comments, rather than inventing sentiment.
