
# Phishing Detection – AI Chat

An interactive chat-style phishing detection demo built with Flask. It analyzes messages in real-time and explains the decision with confidence and reasons. Includes a simple UI with a dark/light theme toggle and JSON APIs for programmatic use.

## ✨ Highlights

- Real-time phishing analysis with explainability (label, confidence, reasons)
- Clean chat UI with quick example buttons and theme toggle (dark/light)
- Simple, self-contained “demo mode” (no Kafka/MongoDB required)
- JSON endpoints for automation: `/detect`, `/stats`, `/health`

## 🧰 Tools Used

- Python 3.10+ (works with 3.8+)
- Flask (web server and API)
- flask-cors (CORS support)
- Bootstrap 5 (via CDN) for UI styling
- Optional: Docker (container build), MongoDB/Kafka (legacy/original microservices path)

## 📁 Project Structure

```
.
├─ Dockerfile
├─ README.md
├─ setup.py
└─ src/
         ├─ microservices_demo.py        # Standalone demo app (recommended to run)
         ├─ index.py                     # Original server (references legacy components)
         ├─ infrastructure/
         │  ├─ config.py
         │  └─ kafka.py                  # Legacy placeholder
         └─ phishing_module/
                        ├─ phishing_detector.py
                        ├─ phishing_service.py       # Legacy Mongo integration
                        └─ test_*.py
```

Note: For classroom/demo use, run `microservices_demo.py`. It’s self-contained and doesn’t require Kafka or MongoDB.
## 🏗️ Architecture Overview

```
┌─────────────────┐       ┌─────────────────┐
│  Chat Application │       │   Web Dashboard   │
│   (Your App)      │       │  (Admin Panel)   │
└────────┬────────┘       └────────┬────────┘
         │                          │
         │ HTTP POST /detect        │ HTTP GET /stats
         │                          │
         │       ┌─────────────────────────────────┐
         └───────┤   Phishing Detection – AI Chat │
                 │   (Flask + Detection Engine)   │
                 └─────────┬───────────────────────┘
                           │
                           │ Store Results
                           │
                 ┌─────────┴───────────────────────┐
                 │      MongoDB Database           │
                 │  (Messages + Analytics)         │
                 └─────────────────────────────────┘
```
### 🔄 Data Flow
- Web UI or client calls POST /detect with a message
- Server analyzes text via the standalone ML detector
- Results update in-memory stats and are returned as JSON
- Optional legacy path (Docker/index.py) shows microservice architecture
## 🚀 Quick Start (Windows PowerShell)

Run the standalone demo on port 5050:

```powershell
# From the project folder
# Ensure dependencies are installed (one-time):
python -m pip install --upgrade pip
pip install -r requirements.txt

# Run the server
$env:PORT=5050; python src\microservices_demo.py
```

Open: http://127.0.0.1:5050

If port 5050 is busy, try a different port (e.g., 5060):

```powershell
$env:PORT=5060; python src\microservices_demo.py
```

## 🖥️ Using the UI

- Type a message and click “Analyze” to see the result
- Click preset example buttons to try common phishing scenarios
- Use the theme toggle in the header to switch light/dark mode (it persists)
- Click “View System Statistics” to see activity summary

## 🔌 API Reference

Base URL (demo): `http://127.0.0.1:<PORT>`

1) POST `/detect` – Analyze message

Request body:

```json
{ "message": "URGENT! Your account expires in 1 hour. Click here to verify!" }
```

Response (example):

```json
{
        "label": "phishing",
        "score": 0.92,
        "reasons": ["Detected phishing indicators: urgent, expires, verify"],
        "algorithm": "Naive Bayes Classifier",
        "feature_score": 4
}
```

2) GET `/stats` – System statistics

```json
{
        "system_stats": {
                "total_messages": 12,
                "phishing_detected": 7,
                "clean_messages": 5,
                "avg_confidence": 0.71,
                "recent_messages": [
                        { "message": "Hi team...", "result": "clean", "confidence": 0.21 }
                ]
        },
        "system_info": {
                "algorithm": "Naive Bayes Classifier",
                "architecture": "Microservices",
                "version": "v1.0.0",
                "uptime": "Active"
        },
        "performance": {
                "avg_processing_time": "< 50ms",
                "throughput": "1000+ messages/sec",
                "accuracy": "94.2%"
        }
}
```

3) GET `/health` – Health check

```json
{ "status": "healthy", "microservices": "active", "kafka": "simulated", "ml_engine": "running", "database": "simulated" }
```

## 🧪 Quick API Tests (PowerShell)

```powershell
# POST /detect
$headers = @{ 'Content-Type' = 'application/json' }
$body = '{"message": "Test message from PowerShell"}'
Invoke-RestMethod -Uri 'http://127.0.0.1:5050/detect' -Method POST -Headers $headers -Body $body | ConvertTo-Json -Depth 5

# GET /stats
Invoke-RestMethod -Uri 'http://127.0.0.1:5050/stats' -Method GET | ConvertTo-Json -Depth 5

# GET /health
Invoke-RestMethod -Uri 'http://127.0.0.1:5050/health' -Method GET | ConvertTo-Json -Depth 5

Tip: If you’re running the server and requesting from the same PowerShell terminal, the output can get
interleaved with server logs. Open a new PowerShell window for API tests.
```

## 🐳 Run with Docker (optional)

This repo includes a Dockerfile that runs the original server (`src/index.py`) on port 5000. It’s more “microservice-y” and references legacy components. For the simple demo, prefer running `microservices_demo.py` locally as shown above.

Build and run:

```powershell
docker build -t phishing-ai-chat .
docker run -p 5000:5000 phishing-ai-chat
```

Open: http://127.0.0.1:5000

Health check: http://127.0.0.1:5000/health

## ⚙️ Configuration

- `PORT` (env var): HTTP port for the demo server (default 5050). Example: `$env:PORT=5060`.
- `MONGO_URI`, `FLASK_ENV` (used by the Docker/index.py path for legacy components)

Path note (Windows): This project folder name contains an en dash (–). When changing directories in
PowerShell, use Set-Location with -LiteralPath to avoid encoding issues:

```powershell
Set-Location -LiteralPath 'C:\Users\<you>\Phishing Detection – AI Chat'
```

## 🧑‍💻 Development

Create a virtual environment and install:

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1; pip install -e .
```

Run the demo app:

```powershell
$env:PORT=5050; python src\microservices_demo.py
```

Run tests (if present):

```powershell
python -m unittest discover
```

## 🛠️ Troubleshooting

- “127.0.0.1 refused to connect”
        - Try another port: `$env:PORT=5060; python src\microservices_demo.py`
        - Stop stray processes: `Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force`
        - Check port usage: `netstat -ano | findstr LISTENING | findstr :5050`
        - Allow Python in Windows Firewall (Private networks)

- “Module not found”
        - Ensure you run from the project folder so `src` is discoverable
        - Activate your venv and `pip install -e .`

- “Invoke-WebRequest/Invoke-RestMethod fails while server is running”
        - Open a second PowerShell window and re-run the request there
        - Or use your browser at http://127.0.0.1:5050/health

## 📄 License

MIT (see LICENSE if present).
