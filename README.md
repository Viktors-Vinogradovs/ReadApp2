# Reading App - FastAPI + React

AI-powered multilingual reading comprehension app with text simplification, TTS audio, and interactive Q&A.

**🚀 Optimized for deployment:** ~220MB (was 3.7GB) | PythonAnywhere ready | Production-tested

---

## ✨ Features

- 📚 **Multi-language support:** English, Latvian, Spanish, Russian
- 🤖 **AI-powered:**
  - Text simplification (DeepSeek)
  - Question generation (Gemini)
  - Answer evaluation with feedback
- 🔊 **Text-to-Speech:** HuggingFace Spaces integration with word-level timing
- ✍️ **Text upload:** Paste or upload stories
- 🎯 **Adaptive difficulty:** Simple, Standard, Challenge modes

---

## 📁 Project Structure

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
git clone https://github.com/Viktors-Vinogradovs/ReadApp2
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
```

**For development tools** (optional):
```bash
pip install -r requirements-dev.txt
```

API will be available at:
- 🌐 http://localhost:8000
- 📚 http://localhost:8000/docs (Swagger UI)

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend will be available at:
- 🌐 http://localhost:5173

---

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

## Makefile Commands

```bash
# Setup
make install-prod    # Install production deps (~220MB)

# Running
make run             # Start production server
make run-dev         # Start with auto-reload

# Maintenance
make clean           # Remove __pycache__, build artifacts
make clean-venv      # Delete virtual environment
make lint            # Run flake8
make format          # Run black
make test            # Run pytest

# Deployment
make deploy-check    # Verify deployment readiness
make size-check      # Check installed package sizes
```

---

##  Deployment

### PythonAnywhere (Recommended)

**Complete guide:** See [DEPLOYMENT.md](DEPLOYMENT.md)

**Quick summary:**
1. Upload code to PythonAnywhere
2. Install: `pip install -r requirements-base.txt`
3. Configure WSGI to point to `backend/wsgi.py`
4. Set environment variables
5. Reload app

**Size verification:**
- ✅ ~220MB fits in free tier (512MB limit)
- ✅ ~400MB total with venv

### Alternative Platforms

**Docker:**
```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements-base.txt .
RUN pip install -r requirements-base.txt
COPY backend/ ./backend/
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0"]
```

**Vercel/Netlify (Frontend only):**
```bash
cd frontend
npm run build
vercel deploy  # or netlify deploy
```

---

## 🔧 Optimization Summary

### Before → After
- **Size:** 3.7GB → 220MB (94% reduction ✨)
- **Packages:** 45 → 15
- **Startup:** ~8s → ~2s
- **Code duplication:** High → Eliminated
- **PythonAnywhere:** ❌ Too large → ✅ Ready

### What Was Optimized
- ❌ Removed unused ML packages (torch, transformers, spacy)
- ✨ Centralized LLM initialization (eliminated 3× duplication)
- ✨ Added structured logging (replaced 53 print statements)
- ✨ Reorganized project structure
- ✨ Created deployment automation

**Details:** See [OPTIMIZATION.md](OPTIMIZATION.md)

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

**Template:** See [.env.example](.env.example)

---

## 📚 Documentation

- [DEPLOYMENT.md](DEPLOYMENT.md) - PythonAnywhere deployment guide
- [OPTIMIZATION.md](OPTIMIZATION.md) - Optimization details
- [docs/notes.md](docs/notes.md) - Development notes & ideas
- [API Docs](http://localhost:8000/docs) - Swagger UI (when running)

---

## 🤝 Contributing

1. Install dev dependencies: `make install-dev`
2. Format code: `make format`
3. Run linter: `make lint`
4. Run tests: `make test`
5. Submit PR

---

## 📝 License

MIT License - See LICENSE file

---

## 🙏 Acknowledgments

- **LLMs:** Google Gemini, DeepSeek
- **TTS:** HuggingFace Spaces (MohamedRashad/Multilingual-TTS, RaivisDejus/Latvian-Piper-TTS)
- **Frameworks:** FastAPI, React, LangChain

---

## 📞 Support

- **Issues:** [GitHub Issues](your-repo/issues)
- **PythonAnywhere Help:** https://help.pythonanywhere.com
- **API Docs:** `/docs` endpoint

---

**🎉 Optimized and ready for deployment!**
