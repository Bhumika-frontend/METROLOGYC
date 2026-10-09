# METROLOGYC

Automated Legal Metrology (Packaged Commodities) Rules, 2011 Compliance Verification System.

## Features
- **Predictive Risk Watchlist**: Live dashboard stats and watchlist tracking repeat offenders.
- **Agentic Workflow Logs**: Real-time transparency tracking OCR and Rule Engine execution.
- **Field Reports**: Internal portal for enforcement officers to submit observations.
- **Rule-Matching Transparency**: Direct citation of statutory rules for each validation check.

## Setup

### Install dependencies

Run these commands from the repository root (the directory containing `start.py`).

#### Windows PowerShell
```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r backend\requirements.txt
Copy-Item backend\.env.example backend\.env
Set-Location frontend
npm install
Set-Location ..
```

#### macOS/Linux
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r backend/requirements.txt
cp backend/.env.example backend/.env
cd frontend
npm install
cd ..
```

The `.env` file is only needed for optional integrations such as Twilio. Replace
the placeholder values in it before using those integrations.

### Start the application

From the repository root, with the virtual environment activated:
```bash
python start.py
```

This starts the backend at `http://localhost:8080` and the frontend at
`http://localhost:3000`. The launcher starts both services, so do not run it
from inside `backend` or `frontend`.

## Testing
Run backend unit tests:
```bash
cd backend
python -m pytest tests/
cd ..
```
