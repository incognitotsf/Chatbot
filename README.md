# Glass Chat

Liquid glass AI chatbot powered by Groq, with optional DuckDuckGo web search for the latest information.

## Run locally
```bash
pip install -r requirements.txt
uvicorn app:app --reload
```
Open http://localhost:8000
Set `GROQ_API_KEY` in a local `.env` file before starting the server.

## Deploy
- **Frontend (GitHub Pages):** Settings → Pages → Deploy from branch → `main` / `/(root)`.
- **Backend (Render):** New → Blueprint → select this repo, then set `GROQ_API_KEY` in the service environment.
- Open the Pages site, tap **Server**, and paste your Render URL.

Never commit `.env`.
