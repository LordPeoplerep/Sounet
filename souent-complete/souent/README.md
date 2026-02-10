# Souent AI Chatbot

**Developed by VelaPlex Systems**

Souent is a production-ready AI chatbot application powered by Souent Logic Models (SLMs), beginning with Anthroi-1 (SLM-A1), a logic-first reasoning model.

## Architecture Overview

```
┌─────────────────────────────────────────────────┐
│          Souent Interface Layer                 │
│  (User Interaction & UI Components)             │
└─────────────────┬───────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────┐
│       Tone Harmonization Layer                  │
│  (Response Style & Formatting)                  │
└─────────────────┬───────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────┐
│      Context Weave Memory System                │
│  ┌──────────────────────────────────────────┐   │
│  │ Ephemeral Session Memory                 │   │
│  │ Persistent User Preferences              │   │
│  │ Locked Canon Memory (read-only)          │   │
│  └──────────────────────────────────────────┘   │
└─────────────────┬───────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────┐
│           Model Engine                          │
│  SLM-A1 (Anthroi-1) - Logic-First Reasoning     │
│  Future: Model Selector for Anthroi Versions    │
└─────────────────────────────────────────────────┘
```

## Tech Stack

- **Backend**: FastAPI (Python 3.11+)
- **Frontend**: React 18 with TypeScript
- **State Management**: Zustand
- **Styling**: Tailwind CSS
- **Memory**: Redis (optional) + JSON file fallback
- **API**: RESTful + WebSocket support

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- npm or yarn
- Redis (optional, will fallback to file-based storage)

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Edit .env with your configuration
# Add your AI model API keys if using external providers

# Run database migrations (initialize memory storage)
python -m app.core.init_db

# Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at: `http://localhost:8000`
API documentation: `http://localhost:8000/docs`

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Copy environment template
cp .env.example .env

# Edit .env with backend URL
# VITE_API_URL=http://localhost:8000

# Start development server
npm run dev
```

Frontend will be available at: `http://localhost:5173`

### Production Build

```bash
# Backend
cd backend
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# Frontend
cd frontend
npm run build
# Serve the dist/ folder with nginx or your preferred web server
```

## Project Structure

```
souent/
├── backend/
│   ├── app/
│   │   ├── api/              # API endpoints
│   │   ├── core/             # Core configuration
│   │   ├── models/           # Data models
│   │   ├── services/         # Business logic
│   │   │   ├── ai_engine/    # AI model integration
│   │   │   ├── memory/       # Context Weave System
│   │   │   └── tone/         # Tone Harmonization
│   │   └── utils/            # Utilities
│   ├── tests/
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/       # React components
│   │   ├── services/         # API clients
│   │   ├── stores/           # State management
│   │   ├── types/            # TypeScript types
│   │   └── utils/            # Utilities
│   ├── public/
│   └── package.json
└── docs/                     # Documentation
```

## Configuration

### Backend Environment Variables

```env
# Application
APP_NAME=Souent
APP_VERSION=1.0.0
ENVIRONMENT=development

# Security
SECRET_KEY=your-secret-key-here
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000

# AI Model Configuration
AI_PROVIDER=openai  # or 'anthropic', 'custom'
AI_API_KEY=your-api-key-here
AI_MODEL=gpt-4  # Will be wrapped as SLM-A1

# Memory System
REDIS_URL=redis://localhost:6379/0
MEMORY_STORAGE_TYPE=redis  # or 'file'
CANON_MEMORY_PATH=./data/canon_memory.json

# Authorization Tiers
ADMIN_API_KEY=admin-key-here
```

### Frontend Environment Variables

```env
VITE_API_URL=http://localhost:8000
VITE_APP_NAME=Souent
VITE_ENABLE_DEBUG=false
```

## Features

### 1. Context Weave Memory System

- **Ephemeral Session Memory**: Cleared after session ends
- **Persistent User Preferences**: User settings, tone preferences
- **Locked Canon Memory**: System knowledge base (read-only without admin authorization)

### 2. Tone Harmonization Layer

Ensures responses are:
- Clear and restrained
- Logic-focused
- Free of emotional simulation
- Conservative with facts

### 3. Authorization Tiers

- **Basic**: Standard user interaction
- **Advisory**: Enhanced context access
- **Admin-Ready**: Canon memory write access

### 4. Model Engine (SLM-A1)

Anthroi-1 characteristics:
- Logic-first reasoning
- Explicit uncertainty handling
- Conservative inference
- No immersive roleplay
- No emotional claims

## API Endpoints

### Chat
- `POST /api/v1/chat/message` - Send a message
- `GET /api/v1/chat/history` - Get conversation history
- `DELETE /api/v1/chat/session` - Clear session

### Memory
- `GET /api/v1/memory/preferences` - Get user preferences
- `PUT /api/v1/memory/preferences` - Update preferences
- `GET /api/v1/memory/canon` - Read canon memory (requires auth)
- `PUT /api/v1/memory/canon` - Update canon memory (admin only)

### System
- `GET /api/v1/system/health` - Health check
- `GET /api/v1/system/models` - Available models
- `GET /api/v1/system/status` - System status

## Security

- Input validation on all endpoints
- Output filtering for sensitive data
- Role-based access control (RBAC)
- Canon memory write protection
- API key authentication
- CORS configuration
- Rate limiting

## Development

### Running Tests

```bash
# Backend
cd backend
pytest tests/ -v

# Frontend
cd frontend
npm test
```

### Code Style

```bash
# Backend
black app/
isort app/
mypy app/

# Frontend
npm run lint
npm run format
```

## Deployment

See `docs/deployment.md` for detailed deployment instructions for:
- Docker/Docker Compose
- AWS/GCP/Azure
- Kubernetes
- Traditional VPS

## License

Proprietary - VelaPlex Systems

## Support

For issues and questions, contact: support@velaplex.systems
