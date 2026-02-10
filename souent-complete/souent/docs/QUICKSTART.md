# Souent Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Step 1: Clone or Download
```bash
cd souent
```

### Step 2: Configure Environment

#### Backend Configuration
```bash
cd backend
cp .env.example .env
```

Edit `.env` and set:
```bash
AI_PROVIDER=openai  # or 'anthropic'
AI_API_KEY=your-api-key-here
AI_MODEL=gpt-4  # or 'claude-3-opus-20240229'
```

#### Frontend Configuration
```bash
cd ../frontend
cp .env.example .env
```

Edit `.env`:
```bash
VITE_API_URL=http://localhost:8000
```

### Step 3: Start Backend

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate (Linux/Mac)
source venv/bin/activate
# Or Windows
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
python -m app.core.init_db

# Start server
uvicorn app.main:app --reload
```

✅ Backend running at: http://localhost:8000

### Step 4: Start Frontend

Open a new terminal:

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

✅ Frontend running at: http://localhost:5173

### Step 5: Open in Browser

Navigate to: **http://localhost:5173**

You should see the Souent chat interface!

---

## 🐳 Docker Alternative (Even Faster!)

If you have Docker installed:

```bash
# Create .env file with your API key
echo "AI_PROVIDER=openai" > .env
echo "AI_API_KEY=your-api-key-here" >> .env
echo "AI_MODEL=gpt-4" >> .env
echo "SECRET_KEY=$(openssl rand -hex 32)" >> .env

# Start everything
docker-compose up -d
```

- Backend: http://localhost:8000
- Frontend: http://localhost:3000

---

## 🎯 First Steps

1. **Ask a question**: Type anything in the chat input
2. **New conversation**: Click "New Chat" to start fresh
3. **View API docs**: Visit http://localhost:8000/docs

---

## ⚙️ Configuration Options

### Tone Preferences

Set in user preferences:
- **concise**: Short, direct responses
- **balanced**: Standard detail level (default)
- **detailed**: Comprehensive explanations

### Authorization Tiers

- **basic**: Standard access (default)
- **advisory**: Enhanced context (requires ADVISORY_API_KEY)
- **admin_ready**: System admin (requires ADMIN_API_KEY)

---

## 📚 Next Steps

- [Read the full README](../README.md)
- [API Documentation](api.md)
- [Deployment Guide](deployment.md)

---

## 🐛 Troubleshooting

**Backend won't start?**
- Check your API key is set in `.env`
- Verify Python 3.11+ is installed: `python --version`

**Frontend can't connect?**
- Verify backend is running: `curl http://localhost:8000/health`
- Check VITE_API_URL in `frontend/.env`

**Port already in use?**
- Backend: Change port in `uvicorn` command
- Frontend: Change port in `vite.config.ts`

**Still stuck?**
Check the logs:
```bash
# Backend
cd backend && uvicorn app.main:app --reload

# Frontend  
cd frontend && npm run dev
```

---

## 💡 Tips

1. **API Keys**: Never commit `.env` files with real API keys
2. **Development**: Use `--reload` flag for hot reloading
3. **Production**: See [deployment.md](deployment.md) for production setup

---

**Ready to build with Souent? Start chatting!** 🎉
