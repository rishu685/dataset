# 🚀 Deployment Guide

## Quick Deploy Options

### 1. Streamlit Community Cloud (Recommended)

**Simple Deployment:**
1. Fork this repository to your GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub account
4. Deploy using `streamlit_standalone.py` as the main file

**With AI Features:**
1. Use the full application with `frontend/streamlit_app.py`
2. Add your Gemini API key in Streamlit Cloud secrets:
   ```
   GEMINI_API_KEY = "your_api_key_here"
   ```

### 2. Railway

```bash
# Install Railway CLI
npm install -g @railway/cli

# Deploy
railway login
railway init
railway add
railway deploy
```

### 3. Heroku

Create `Procfile`:
```
web: streamlit run streamlit_standalone.py --server.port=$PORT --server.address=0.0.0.0
```

### 4. Render

Create `render.yaml`:
```yaml
services:
- type: web
  name: titanic-chatbot
  env: python
  buildCommand: pip install -r requirements.txt
  startCommand: streamlit run streamlit_standalone.py --server.port $PORT --server.address 0.0.0.0
```

## Troubleshooting

### Requirements Issues
If you get deployment errors, try:
1. Use `requirements-minimal.txt` instead
2. Update to latest package versions
3. Remove version constraints

### Common Fixes
- **Memory errors**: Use `streamlit_standalone.py` (lighter version)
- **Package conflicts**: Use minimal requirements
- **API errors**: Set environment variables correctly
- **Port issues**: Use platform's default ports

### Environment Variables
Always set:
```
GEMINI_API_KEY=your_actual_api_key
```