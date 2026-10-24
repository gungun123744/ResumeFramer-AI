# ResumeFramer AI — Groq API version

Streamlit app to compare a resume with a job description, identify evidence gaps, draft a truthful tailored resume, and build a learning roadmap. Uses Groq through LangChain. API access, model availability, rate limits and free-tier terms can change.

## 1. Get a Groq API key

1. Sign in at https://console.groq.com/keys and create a key.
2. Check currently available model IDs at https://console.groq.com/docs/models. Default model in this project: `openai/gpt-oss-20b`. If your account does not have access, select an available chat model and use its exact ID in the app sidebar.
3. Copy `.env.example` to `.env` and replace the placeholder with your key. Never paste the key into chat or commit `.env` to GitHub.

## 2. Windows PowerShell setup

```powershell
cd resumeframer_ai_groq_final
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
notepad .env
streamlit run app.py
```

If `Copy-Item` says `.env` already exists, do not overwrite your existing key; edit `.env` manually.

## 3. macOS/Linux setup

```bash
cd resumeframer_ai_groq_final
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
nano .env
streamlit run app.py
```

## Features

- Upload resume and job description as PDF, DOCX, or TXT; or paste the JD
- Analyze requirements and resume evidence
- Generate an ATS-readable tailored resume, with editable text and PDF/DOCX export
- Generate a study roadmap and retrieve curated learning resources from `data/resources.csv`
- Save analyses locally in SQLite (`resumeframer.db`)

## Important notes

- The model can make mistakes. Verify all resume claims before applying; the app's prompts instruct the model not to fabricate experience or skills.
- Resume and JD text are sent to Groq's API. Review provider privacy terms before using sensitive information.
- The app uses the model ID shown in the sidebar. If you get `model_not_found`, copy an exact currently supported model ID from Groq's model documentation.
