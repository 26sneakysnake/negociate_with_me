# NegotiAI v0 🤝

**Pitch**: "Préparez vos négociations comme un pro et apprenez de vos erreurs"

NegotiAI is an AI-powered negotiation training platform that helps you:
1. Upload contract context (PDF/text)
2. Generate a complete negotiation strategy with tactics
3. Analyze your negotiation performance after the fact
4. Get AI-powered feedback with voice summaries

## 🏗️ Architecture

```
Frontend (React) ←→ Backend (FastAPI) ←→ External Services
                                         ├─ Mistral AI (Strategy & Analysis)
                                         ├─ Qdrant (Tactics Vector DB)
                                         └─ ElevenLabs (Voice Feedback)
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose (optional)

### 1. Clone and Setup

```bash
cd negotiai-v0
cp .env.example .env
# Edit .env with your API keys
```

### 2. Get API Keys

You'll need:
- **Mistral AI**: https://console.mistral.ai/
- **Qdrant Cloud**: https://cloud.qdrant.io/
- **ElevenLabs**: https://elevenlabs.io/

### 3. Run with Docker (Recommended)

```bash
docker-compose up
```

Access the app at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### 4. Or Run Manually

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

**Frontend:**
```bash
cd frontend
npm install
npm start
```

## 📖 User Flow

### Step 1: Preparation Phase
- Upload PDF contract or paste text context
- Define your objective (e.g., "Secure 50K€ annual contract")
- Set minimum acceptable outcome
- Optional: Add counterparty name

### Step 2: Strategy Generation
AI generates:
- Executive summary
- Opening position
- Key arguments (4-5 points)
- Concession plan (progressive steps)
- Red lines (non-negotiables)
- Expected objections with counter-arguments
- BATNA (Best Alternative)

### Step 3: Post-Negotiation Analysis
- Paste full conversation transcript
- Enter actual outcome
- Get performance scores (0-100):
  - Overall
  - Preparation
  - Tactics execution
  - Outcome achievement
- Detected tactics with effectiveness ratings
- Strengths & weaknesses
- Key recommendations
- Audio feedback summary

## ✨ V1 Features (NEW!)

### 📦 Session Persistence
- All negotiations automatically saved to PostgreSQL database
- Complete session history with context, strategy, and analysis
- Retrieve past negotiations anytime

### 📄 PDF Export
- Download professional PDF reports for:
  - Negotiation strategy (pre-negotiation brief)
  - Performance analysis (post-negotiation report)
- Formatted with colors, charts, and detailed breakdowns

### 📊 Performance Tracking
- View all past negotiations in History page
- Interactive charts showing score progression over time
- Statistics: total negotiations, average score, improvement tracking
- Compare performance across multiple sessions
- See message: "You've improved by +15 points!"

### 📝 Context Templates
5 pre-configured templates for quick start:
- **SaaS Enterprise License** - Software contract negotiations
- **Real Estate Purchase** - Property buying negotiations (French/English)
- **Salary Negotiation** - Job offer and raise discussions
- **Freelance Contract** - Consulting and freelance agreements
- **Vendor/Supplier Contract** - B2B procurement negotiations

Each template includes:
- Pre-filled context structure
- Objective templates
- Minimum acceptable outcome templates

## 🗂️ Project Structure

```
negotiai-v0/
├── backend/
│   ├── main.py                    # FastAPI app + routes
│   ├── config.py                  # Configuration
│   ├── models.py                  # Pydantic models
│   ├── database.py                # SQLAlchemy setup (V1)
│   ├── db_models.py               # Database models (V1)
│   ├── crud.py                    # Database operations (V1)
│   ├── init_db.py                 # DB initialization + templates (V1)
│   ├── services/
│   │   ├── mistral_service.py     # AI strategy & analysis
│   │   ├── qdrant_service.py      # Vector search for tactics
│   │   ├── elevenlabs_service.py  # Voice generation
│   │   └── pdf_service.py         # PDF export generation (V1)
│   ├── routers/
│   │   ├── sessions.py            # Session management API (V1)
│   │   └── templates.py           # Template management API (V1)
│   ├── data/
│   │   └── negotiation_tactics.json # 15 tactics database
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.jsx                # Main component
│   │   ├── pages/
│   │   │   ├── PrepPage.jsx       # Context upload + templates
│   │   │   ├── StrategyPage.jsx   # Strategy display + PDF export
│   │   │   ├── AnalysisPage.jsx   # Performance analysis + PDF
│   │   │   └── HistoryPage.jsx    # Session history + charts (V1)
│   │   ├── services/
│   │   │   └── api.js             # Backend API calls
│   │   └── App.css                # All styles
│   └── package.json
├── docker-compose.yml             # Includes PostgreSQL (V1)
└── README.md
```

## 🎯 Demo Scenario

A sample negotiation scenario is included for testing:

**Context**: SaaS platform license negotiation
- Budget: 30-40K€
- Your ask: 55K€ annual
- Minimum: 45K€
- Competition: DataViz Pro at 35K€

**Demo Transcript**: See `demo/sample-transcript.txt`

## 🛠️ Tech Stack

**Backend:**
- FastAPI (REST API)
- Mistral AI (LLM for strategy & analysis)
- Qdrant (Vector database for tactics)
- ElevenLabs (Text-to-speech)
- PyPDF2 (PDF parsing)
- PostgreSQL (Session persistence - V1)
- SQLAlchemy (ORM - V1)
- Reportlab (PDF generation - V1)
- Matplotlib (Charts for PDFs - V1)

**Frontend:**
- React 18
- CSS3 (gradient UI)
- Fetch API

**Infrastructure:**
- Docker & Docker Compose
- PostgreSQL 15
- Python 3.11
- Node.js 18

## 🔑 Key Features

### RAG-Enhanced Strategy
- Context embeddings sent to Qdrant
- Relevant tactics retrieved for each negotiation
- Personalized strategy based on 15+ negotiation tactics

### Tactic Detection
15 tactics in database:
- Anchoring, Mirroring, Calibrated Questions
- BATNA Reveal, Silence, Trade-offs
- Good Cop/Bad Cop, False Urgency
- And more...

### Voice Feedback
- ElevenLabs TTS generates audio summary
- Professional "Rachel" voice
- Performance overview in natural language

## 📊 API Endpoints

**Core Negotiation Flow:**
```
POST /api/upload-context              # Upload PDF/text context
POST /api/generate-strategy           # Generate negotiation strategy
POST /api/analyze-negotiation         # Analyze performance
GET  /api/session/{session_id}        # Get session data
```

**V1 - Session Management:**
```
GET  /api/sessions/                   # List all sessions
GET  /api/sessions/{id}               # Get session details
GET  /api/sessions/performance/history # Performance comparison data
GET  /api/sessions/{id}/export/strategy  # Download strategy PDF
GET  /api/sessions/{id}/export/analysis  # Download analysis PDF
```

**V1 - Templates:**
```
GET  /api/templates/                  # List all context templates
GET  /api/templates/{id}              # Get specific template
```

**Assets:**
```
GET  /audio/{filename}                # Audio feedback files
GET  /exports/{filename}              # PDF export files
```

## 🧪 Testing

1. Start the app
2. Go to http://localhost:3000
3. Use the demo scenario from `demo/` folder
4. Upload context, generate strategy
5. Paste demo transcript
6. Review analysis and listen to audio feedback

## 📝 Environment Variables

```bash
MISTRAL_API_KEY=       # Mistral AI API key
QDRANT_URL=            # Qdrant cluster URL
QDRANT_API_KEY=        # Qdrant API key
ELEVENLABS_API_KEY=    # ElevenLabs API key
```

## 🚧 Roadmap

**V1 - Completed ✅**
- [x] Session persistence (PostgreSQL)
- [x] Multiple negotiation sessions with history
- [x] Export reports to PDF (strategy + analysis)
- [x] Performance tracking and comparison
- [x] Context templates for common scenarios

**Future Enhancements:**
- [ ] User authentication & multi-user support
- [ ] Live negotiation mode with real-time AI suggestions
- [ ] Advanced analytics dashboard with trends
- [ ] Team collaboration features
- [ ] Custom tactic database creation
- [ ] Multi-language support (FR, EN, ES, DE)
- [ ] Mobile app (React Native)
- [ ] Integration with calendar/CRM tools

## 📄 License

MIT License

## 🤝 Contributing

This is a v0 hackathon project. Feel free to fork and improve!

## 📞 Support

For issues or questions, please open a GitHub issue.

---

Built with ❤️ using Mistral AI, Qdrant, and ElevenLabs
