# Reading App - FastAPI + React

AI-powered multilingual reading comprehension app with text simplification, TTS audio, and interactive Q&A.

---

##  Features

- **Multi-language support:** English, Latvian, Spanish, Russian
- **AI-powered:**
  - Text simplification (DeepSeek)
  - Question generation (Gemini)
  - Answer evaluation with feedback
- **Text-to-Speech:** HuggingFace Spaces integration with word-level timing
- **Text upload:** Paste or upload stories
- **Adaptive difficulty:** Simple, Standard, Challenge modes

---

## Project Structure

```
AI_App/
├── backend/                    # FastAPI application
│   ├── app/
│   │   ├── core/              # Configuration, LLM factories, logging
│   │   ├── routers/           # API endpoints
│   │   ├── services/          # Business logic
│   │   └── main.py            # App entry point
│   └── wsgi.py                # PythonAnywhere WSGI config
├── frontend/                   # React + TypeScript + Vite
│   └── src/
│       ├── pages/             # Library, Upload
│       └── api/               # Backend client
├── scripts/                    # Utility scripts
│   ├── toJson.py              # Add texts to library
│   └── cleanup_venv.py        # Dependency cleanup
├── docs/                       # Documentation
│   └── notes.md               # Development notes
├── data/                       # JSON text storage
├── requirements-base.txt       # Production dependencies (~220MB)
├── requirements-dev.txt        # Development tools
├── requirements-optional.txt   # Future features (documented)
├── Makefile                    # Build automation
├── DEPLOYMENT.md               # PythonAnywhere guide
└── OPTIMIZATION.md             # Optimization details
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node 18+
- API Keys:
  - Google AI Studio (Gemini)
  - DeepSeek
  - HuggingFace

### Backend Setup

```bash
# 1. Clone repository
git clone https://github.com/Viktors-Vinogradovs/ReadApp2.git
cd ReadApp2

# 2. Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with your API keys

# 5. Run server
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload

# 6. Run Frontend
cd frontend
npm install
npm run dev

Frontend will be available at:
- http://localhost:5173
```

API will be available at:
- 🌐 http://localhost:8000
- 📚 http://localhost:8000/docs (Swagger UI)

## 📦 Dependencies

### Production (requirements.txt) - ~220MB
```
python-dotenv        # Environment configuration
fastapi              # Web framework
uvicorn              # ASGI server
pydantic             # Data validation
google-generativeai  # Gemini API
langchain            # LLM orchestration
langchain-google-genai
openai               # DeepSeek API
tiktoken             # Token counting
requests             # HTTP client
gradio_client        # HuggingFace Spaces TTS
```
---

## API Endpoints

### Core
- `GET /health` - Health check

### Texts
- `GET /texts?lang=English` - List library texts
- `POST /texts` - Upload new text (with auto-splitting)
- `POST /texts/preview` - Preview text fragments
- `GET /texts/{name}/parts?lang=` - Get text parts

### Q&A
- `POST /qa/simplify` - Simplify text
- `POST /qa/format` - Fix formatting
- `POST /qa/questions` - Generate questions
- `POST /qa/evaluate` - Evaluate answer (rate-limited)
- `POST /qa/audio` - Synthesize TTS audio

---


## 🧪 Testing

```bash
# Run all tests
make test

# Or manually
pytest tests/ -v

# Test specific endpoint
curl http://localhost:8000/health
curl http://localhost:8000/texts?lang=English
```

---

## 🔐 Environment Variables

Required in `.env` file:

```env
# Gemini API (Google AI Studio)
GEMINI_API_KEY=your_key_here
GEMINI_AUDIO_API_KEY=your_key_here

# DeepSeek API
DEEPSEEK_API_KEY=your_key_here

# HuggingFace Token
HF_API_TOKEN=your_token_here
```

## 📝 License

MIT License - See LICENSE file
