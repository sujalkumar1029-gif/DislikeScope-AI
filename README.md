<div align="center">

# 🔭 DislikeScope-AI

### Authentic Social Sentiment & Audience Dislike Diagnostics — Zero Fabricated Data

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-19.2+-61DAFB.svg?logo=react&logoColor=black)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-3178C6.svg?logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![Vite](https://img.shields.io/badge/Vite-6.0+-646CFF.svg?logo=vite&logoColor=white)](https://vitejs.dev/)
[![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Pytest](https://img.shields.io/badge/Tests-30%20Passed%20(100%25)-success.svg?logo=pytest&logoColor=white)](https://pytest.org/)
[![License: Dual](https://img.shields.io/badge/License-MIT%20%7C%20GNU%20GPL%20v3-orange.svg)](LICENSE)
[![Truth Policy](https://img.shields.io/badge/Truth%20Policy-Strict%20Reconciliation-purple.svg)](#-truth-policy--diagnostic-transparency)

<p align="center">
  <b>A full-stack diagnostic intelligence platform for deep YouTube & X.com audience feedback analysis.</b><br/>
  Combines rule-based NLP, Shannon entropy controversy modeling, praise/dislike keyphrase mining, like-weighted consensus resonance, head-to-head benchmarking, and strict mathematical record reconciliation.
</p>

[Key Features](#-key-features) •
[Architecture](#-system-architecture) •
[Truth Policy](#-truth-policy--diagnostic-transparency) •
[Quick Start](#-quick-start) •
[API Reference](#-rest-api-reference) •
[Testing](#-testing-suite) •
[Licensing](#-dual-licensing)

</div>

---

## 🎯 Executive Summary

In 2021, platforms like YouTube removed public dislike counts, creating an asymmetry where creators, researchers, and brands could no longer reliably assess genuine public reception. Furthermore, modern analytics tools often fabricate sentiment scores or hallucinate estimates when comments are disabled, deleted, or restricted by login walls.

**DislikeScope-AI** solves this through an unapologetic **Truth Policy**:
- **Zero Hallucinated Metrics**: If comments are disabled, deleted, or restricted by platform walls, DislikeScope-AI provides explicit diagnostic error statuses rather than fabricating synthetic sentiment scores.
- **Mathematical Reconciliation**: Every retrieved record is traced from HTTP response to VADER scoring. $\text{Positive} + \text{Neutral} + \text{Negative} = \text{Total Analyzed}$ is an invariant strictly validated across every run.
- **Transparent Third-Party Disclosures**: Dislike estimates (sourced via Return YouTube Dislike) are labeled as statistical estimates with transparent methodology notes.

---

## 🌟 Key Features

### 1. 🧠 Executive Diagnostic Verdicts
Synthesizes comment volume, sentiment skew, and community polarization into actionable diagnostic conclusions:
- **Overwhelmingly Positive Acclaim** ($\ge 75\%$ positive)
- **Favorable Reception** ($\ge 55\%$ positive)
- **Severe Audience Backlash** ($\ge 45\%$ negative)
- **Moderate Negative Pushback** ($\ge 30\%$ negative)
- **Polarized Community Debate** (Controversy Index $\ge 50$ with $\ge 25\%$ positive and negative)
- **Balanced Discourse** & **Neutral Observational Reception**

### 2. ⚡ Audience Controversy Index ($0 - 100$)
Quantifies community polarization using normalized Shannon entropy across sentiment distributions:
$$H(S) = - \sum_{i \in \{\text{pos}, \text{neu}, \text{neg}\}} p_i \ln(p_i), \quad \text{Controversy Index} = \frac{H(S)}{\ln(3)} \times 100$$
Distinguishes between a uniformly content audience ($CI \approx 0$) and a fiercely divided community debate ($CI \ge 60$).

### 3. 🔍 Praise & Dislike Drivers (NLP Keyphrase Mining)
Automatically mines meaningful n-gram candidate phrases (bigrams, trigrams, and salient single terms) filtered against custom stopwords. Extracts:
- Top praise themes driving positive applause with occurrence counts and direct quotes.
- Top complaint themes driving negative reactions with occurrence counts and direct quotes.
- **Interactive Pill Filters**: Click any driver pill to instantly filter the Comment Explorer down to related user reactions.

### 4. 📢 Community Resonance (Like-Weighted Sentiment)
Prevents a loud minority of un-upvoted comments from skewing perceived audience sentiment:
$$w_i = \max(\text{likes}_i, 0) + 1, \quad \bar{s}_{\text{weighted}} = \frac{\sum w_i \cdot s_i}{\sum w_i}$$
Surfaces when community upvotes amplify or contradict raw comment frequency.

### 5. 📊 5-Tier Polarity Distribution
Visualizes audience dispersion across five discrete sentiment tiers:
- **Strong Positive** ($s \ge 0.50$)
- **Mild Positive** ($0.05 \le s < 0.50$)
- **Neutral** ($-0.05 < s < 0.05$)
- **Mild Negative** ($-0.50 < s \le -0.05$)
- **Strong Negative** ($s \le -0.50$)

### 6. ⚔️ Head-to-Head Comparison Mode
Benchmark two videos or posts side-by-side:
- Compare raw URLs or select historical records directly from the database sidebar.
- Automatic metric delta computations ($\Delta$ Positive %, $\Delta$ Controversy Index, $\Delta$ Like-Weighted Compound).
- Side-by-side driver comparisons and engagement ratios.

### 7. 🔎 Interactive Comment Explorer
- Real-time client-side substring search.
- Multi-criteria sorting: **Most Liked**, **Most Negative**, **Most Positive**, and **Chronological**.
- Active topic badge filter with 1-click reset.
- Verifiable like counts and exact sentiment scores for every comment.

### 8. 📑 1-Click Executive Audit Report Export
- Copy a clean, formatted **Markdown Audit Report** directly to clipboard for executive reviews and client briefings.
- Download raw data as comprehensive **CSV** or structured **JSON**.

---

## 🏛️ Supported Platforms

| Platform | Extraction Strategy | Sentiment Scope | Dislike Metrics | Operational Status |
| :--- | :--- | :--- | :--- | :--- |
| **YouTube** | Public page scrape & Innertube API | Public comments & top replies | [Return YouTube Dislike (RYD)](https://returnyoutubedislike.com) (Labeled Statistical Estimate) | **Verified Production Ready** |
| **X.com / Twitter** | Public syndication & web endpoints | Accessible conversation replies | N/A (Platform has no native dislike feature) | **Verified Production Ready** |

> **Scope Boundary**: Per project specification, other platforms (Instagram, Reddit, TikTok) are excluded to ensure high diagnostic precision on video and public microblog discourse.

---

## 📐 System Architecture

```mermaid
flowchart TD
    User([User / Browser]) -->|Submit URL or Comparison| Frontend[React 19 + TypeScript SPA]
    
    subgraph Frontend Layer
        Frontend --> VerdictBanner[Executive Verdict & Controversy]
        Frontend --> DriverPills[Praise & Dislike Drivers]
        Frontend --> ResonanceCard[Like-Weighted Resonance]
        Frontend --> DistHistogram[5-Tier Polarity Histogram]
        Frontend --> CommentExplorer[Interactive Comment Explorer]
        Frontend --> CompareMode[Head-to-Head Benchmark]
        Frontend --> AuditExport[CSV / JSON / Markdown Exporter]
    end

    Frontend -->|HTTP / JSON API| Backend[FastAPI Application :8000]

    subgraph Backend Architecture
        Backend --> ScraperRouter{Platform Router}
        ScraperRouter -->|YouTube URL| YTScraper[YouTube Service & RYD API]
        ScraperRouter -->|X.com URL| XScraper[X Syndication Service]
        
        YTScraper --> DiagnosticCheck[Truth & Diagnostic Gate]
        XScraper --> DiagnosticCheck
        
        DiagnosticCheck -->|Comments Available| SentimentEngine[VADER Sentiment & Driver NLP]
        DiagnosticCheck -->|Restricted / Disabled| TruthReporter[Honest Diagnostic Status]
        
        subgraph Analytics Pipeline
            SentimentEngine --> VADER[VADER Polarity Scoring]
            SentimentEngine --> Drivers[N-Gram Keyphrase Extractor]
            SentimentEngine --> Entropy[Controversy Index / Shannon Entropy]
            SentimentEngine --> Weighted[Like-Weighted Resonance Model]
            SentimentEngine --> Verdict[Executive Diagnostic Synthesis]
        end
        
        Analytics Pipeline --> DB[(SQLite: data/dislikescope.db)]
        TruthReporter --> DB
    end

    Backend -->|Standardized Pydantic Response| Frontend
```

---

## 📁 Repository Structure

```
DislikeScope-AI/
├── .env.example                  # Environment configuration template
├── .env                          # Local environment variables
├── .gitignore                    # Excludes .venv, node_modules, SQLite databases, logs
├── package.json                  # Root npm scripts & dual-license metadata
├── pytest.ini                    # Pytest configuration & test markers
├── run.sh                        # Production-grade single-command launcher
├── LICENSE                       # Dual licensing declaration (MIT or GNU GPL v3)
├── LICENSE-MIT                   # Standard MIT License
├── LICENSE-GPL                   # Standard GNU General Public License v3.0
├── README.md                     # Comprehensive system documentation
│
├── backend/
│   ├── requirements.txt          # Python dependencies (FastAPI, VADER, Uvicorn, etc.)
│   ├── config.py                 # Application settings & environment loader
│   ├── database.py               # SQLite persistence & backward-compatible auto-enrichment
│   ├── main.py                   # FastAPI REST API, routing & error handlers
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py            # Pydantic v2 data models & request/response contracts
│   ├── services/
│   │   ├── __init__.py
│   │   ├── sentiment.py          # VADER engine, controversy index, drivers & resonance
│   │   ├── youtube.py            # YouTube Innertube extraction & RYD integration
│   │   ├── x_platform.py         # X.com syndication & login-wall diagnostic detection
│   │   └── exporter.py           # CSV and JSON report generators
│   └── tests/
│       ├── __init__.py
│       ├── conftest.py           # Isolated test database fixtures
│       ├── test_youtube.py       # YouTube extraction & error recovery tests
│       ├── test_x_platform.py    # X.com validation & diagnostic tests
│       ├── test_sentiment.py     # VADER scoring, drivers, controversy & resonance tests
│       ├── test_database.py      # SQLite CRUD & auto-enrichment integrity tests
│       ├── test_api.py           # REST endpoints, health checks & comparison tests
│       └── test_export.py        # CSV/JSON export tests
│
├── frontend/
│   ├── package.json              # React 19, TypeScript, Lucide, Vite & Oxlint
│   ├── tsconfig.json             # TypeScript configuration (verbatimModuleSyntax)
│   ├── vite.config.ts            # Vite dev server with proxy to FastAPI backend
│   ├── index.html                # Semantic HTML layout with SEO metadata
│   └── src/
│       ├── main.tsx              # React mounting entrypoint
│       ├── App.tsx               # Primary dashboard controller & tab state
│       ├── index.css             # Vanilla CSS design system (tokens, glassmorphism, responsive)
│       ├── api.ts                # Type-safe HTTP client with Axios/Fetch
│       ├── types.ts              # Frontend TypeScript interfaces
│       └── components/
│           ├── Header.tsx             # Brand header with Truth Policy indicator
│           ├── Icons.tsx              # Handcrafted lightweight SVG icons
│           ├── UrlInput.tsx           # URL submission with Quick Demo sample presets
│           ├── VerdictBanner.tsx      # Executive diagnostic verdict & controversy meter
│           ├── SentimentSummary.tsx   # Aggregated sentiment summary card
│           ├── SentimentDrivers.tsx   # Praise & Dislike driver badges with click-filtering
│           ├── SentimentDistribution.tsx # 5-tier polarity histogram
│           ├── CommunityResonance.tsx # Like-weighted sentiment resonance cards
│           ├── EngagementMetrics.tsx  # Views, likes, and dislike estimate disclosures
│           ├── DiagnosticsCard.tsx    # 4-stage reconciliation and status table
│           ├── CommentsList.tsx       # Comment Explorer with live search & sorting
│           ├── ComparisonView.tsx     # Head-to-Head benchmark side-by-side view
│           ├── HistoryPanel.tsx       # SQLite history sidebar with multi-select comparison
│           ├── ExportButtons.tsx      # CSV, JSON, and 1-Click Markdown export buttons
│           └── LimitationsNotice.tsx  # Platform boundaries & privacy notice
│
└── data/
    └── dislikescope.db           # Persistent SQLite database
```

---

## 🔒 Truth Policy & Diagnostic Transparency

DislikeScope-AI enforces strict data integrity rules:

### 1. The 4-Stage Reconciliation Pipeline
Every analysis execution audits the comment lifecycle across four explicit metrics:
1. **Platform Reported Comments**: The total comment count reported by the platform metadata.
2. **Retrieved Records**: Raw comments fetched over the wire.
3. **Usable Text Count**: Non-empty, human-readable comments after whitespace sanitization.
4. **Successfully Analyzed**: Comments scored by VADER.

$$\text{Positive Count} + \text{Neutral Count} + \text{Negative Count} = \text{Total Analyzed}$$

### 2. Honest Diagnostic Statuses
- **Login-Walled Content**: When X.com replies are protected behind authentication, DislikeScope-AI returns `status: "restricted"` with an explicit diagnostic explanation instead of inventing fake data.
- **Disabled Comments**: If a YouTube creator disables comments, DislikeScope-AI flags `comments_disabled: true` with 0 analyzed comments.
- **Dislike Transparency**: Return YouTube Dislike estimates are labeled as **3rd-Party Statistical Estimates**, providing direct methodology disclaimers.

---

## 🚀 Quick Start

### Prerequisites
- **Python**: Version 3.11, 3.12, 3.13, or 3.14
- **Node.js**: Version 18.x, 20.x, or 22.x with `npm`
- **Operating System**: Linux (Fedora, Ubuntu, Debian, Arch), macOS, or Windows (WSL2 recommended)

### 1. Clone & Enter Repository
```bash
git clone https://github.com/sujalkumar1029-gif/DislikeScope-AI.git
cd DislikeScope-AI
```

### 2. Run with Single Command (Recommended)
From the repository root, simply execute:
```bash
./run.sh
```
*(or via npm: `npm start`)*

The `run.sh` automation script:
- Verifies `.venv` existence and installs backend dependencies automatically.
- Checks frontend `node_modules` and runs `npm install` if required.
- Inspects ports `8000` and `5173` to prevent port collisions.
- Spawns both servers and validates their readiness through health probes.
- Streams colorized, tagged logs to your terminal (`[BACKEND]` and `[FRONTEND]`).
- Cleanly catches `SIGINT` / `SIGTERM` (`Ctrl+C`) to terminate both services without leaving orphaned processes.

| Service | Address |
| :--- | :--- |
| **Frontend Web App** | [http://localhost:5173](http://localhost:5173) |
| **FastAPI REST API** | [http://127.0.0.1:8000](http://127.0.0.1:8000) |
| **Interactive Swagger API Docs** | [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) |
| **Health Check Endpoint** | [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health) |

---

### Manual Setup (Multi-Terminal)

If you prefer launching components in separate terminal windows:

#### Terminal 1 — Backend (FastAPI):
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
cp .env.example .env
python3 -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

#### Terminal 2 — Frontend (Vite):
```bash
cd frontend
npm install
npm run dev
```

---

## 📡 REST API Reference

### 1. Analyze Social Target
`POST /api/analyze`
Extracts and performs complete sentiment, driver, and controversy diagnostics on a target URL.

**Request Body:**
```json
{
  "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
  "max_comments": 100
}
```

**Response (Summary):**
```json
{
  "id": 1,
  "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
  "platform": "youtube",
  "title": "Rick Astley - Never Gonna Give You Up (Official Music Video)",
  "verdict": {
    "verdict_type": "Overwhelmingly Positive Acclaim",
    "headline": "Overwhelmingly Positive Acclaim (88.2% positive)",
    "summary": "Audience response is enthusiastically positive...",
    "actionable_takeaway": "Audience reception is overwhelmingly favorable...",
    "badge_color": "emerald"
  },
  "controversy_index": 12.4,
  "sentiment_summary": {
    "positive_pct": 88.2,
    "neutral_pct": 7.8,
    "negative_pct": 4.0,
    "total_analyzed": 100
  },
  "like_weighted_metrics": {
    "weighted_compound": 0.824,
    "weighted_positive_pct": 92.1,
    "raw_vs_weighted_delta": 3.9
  },
  "positive_drivers": [
    { "phrase": "legendary song", "count": 14, "quote_sample": "Absolute legendary song!" }
  ],
  "negative_drivers": [],
  "score_distribution": [
    { "bucket_label": "Strong Positive", "min_score": 0.5, "max_score": 1.0, "count": 68, "percentage": 68.0 },
    { "bucket_label": "Mild Positive", "min_score": 0.05, "max_score": 0.5, "count": 20, "percentage": 20.0 },
    { "bucket_label": "Neutral", "min_score": -0.05, "max_score": 0.05, "count": 8, "percentage": 8.0 },
    { "bucket_label": "Mild Negative", "min_score": -0.5, "max_score": -0.05, "count": 3, "percentage": 3.0 },
    { "bucket_label": "Strong Negative", "min_score": -1.0, "max_score": -0.5, "count": 1, "percentage": 1.0 }
  ]
}
```

---

### 2. Head-to-Head Comparison
`POST /api/compare` (Raw URLs) or `GET /api/compare?id_a=1&id_b=2` (Historical IDs)

Compares two target URLs or historical analyses and calculates deltas across all key engagement and sentiment metrics.

---

### 3. Historical Analyses
- `GET /api/history`: List recent analyses with pagination and platform filters.
- `GET /api/history/{id}`: Retrieve a specific past analysis with all comments and diagnostics preserved.
- `DELETE /api/history/{id}`: Delete an entry from local SQLite storage.

---

### 4. Export Reports
- `GET /api/export/{id}?format=csv`: Download full report including comments, scores, drivers, and metadata as CSV.
- `GET /api/export/{id}?format=json`: Download full structured JSON report.

---

## 🧪 Testing Suite

DislikeScope-AI maintains a comprehensive automated testing suite with **30 passing tests** covering scrapers, edge cases, count reconciliation, controversy calculation, n-gram driver extraction, database operations, and exports.

### Run All Backend Tests
```bash
source .venv/bin/activate
pytest -v
```

**Test Coverage Highlights:**
- **URL Extraction & Normalization**: `test_youtube.py`, `test_x_platform.py`
- **Reconciliation & Mathematical Invariants**: `test_sentiment.py`
- **Controversy Index & Polarization Boundary Cases**: `test_sentiment.py`
- **N-Gram Keyphrase Driver Mining**: `test_sentiment.py`
- **Like-Weighted Resonance Amplification**: `test_sentiment.py`
- **SQLite Persistence & Auto-Enrichment**: `test_database.py`
- **API Endpoints & Comparison Logic**: `test_api.py`
- **CSV and JSON Exporter**: `test_export.py`

### Run Frontend Typecheck & Build
```bash
cd frontend
npm run build
```
*(Runs `tsc -b && vite build` ensuring 0 TypeScript errors and optimized production output)*

---

## 📜 Dual Licensing

DislikeScope-AI is proudly open-source software, dual-licensed under either:

1. **The MIT License** ([LICENSE-MIT](LICENSE-MIT))  
   *Permissive*: Permits reuse within proprietary and commercial software with minimal attribution requirements.
2. **The GNU General Public License v3.0** ([LICENSE-GPL](LICENSE-GPL))  
   *Strong Copyleft*: Guarantees that all derivative works, modifications, and enhancements remain free and open source.

You may choose whichever license best fits your use case or organization's compliance guidelines. For more information, see the [LICENSE](LICENSE) file.

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:
1. Fork the repository.
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Ensure all tests pass: `pytest -v && cd frontend && npm run build`
4. Commit your changes: `git commit -m "Add amazing feature"`
5. Push to the branch: `git push origin feature/amazing-feature`
6. Open a Pull Request.

---

## 👨‍💻 Author & Acknowledgments

- **Lead Developer**: Sujal Kumar ([@sujalkumar1029-gif](https://github.com/sujalkumar1029-gif))
- **VADER Sentiment**: C.J. Hutto & Eric Gilbert ([vaderSentiment](https://github.com/cjhutto/vaderSentiment))
- **Return YouTube Dislike**: Community-powered dislike estimation project ([RYD API](https://returnyoutubedislike.com))

<div align="center">
  <sub>Built with precision, honesty, and modern full-stack technologies.</sub>
</div>
