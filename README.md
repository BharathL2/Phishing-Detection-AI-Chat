
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

Preferred dynamic setup: run the unsupervised backend on port 5071 and the static UI on 8081 (the UI defaults to 5071). You can still run the classic demo on 5050 if needed.

1) Install dependencies (one-time):

```powershell
python -m pip install --upgrade pip
python -m pip install flask flask-cors requests
```

2) Start the backend (Dynamic unsupervised on 5071):

```powershell
cd "C:\Users\l670b\Phishing Detection – AI Chat"
python src\dynamic_unsupervised_server.py
```

Open health: http://127.0.0.1:5071/health

If port 5071 is busy, pick a different one:

```powershell
$env:PORT=5075; python src\dynamic_unsupervised_server.py
```

3) Start the static demo UI (docs/ on 8081):

```powershell
cd "C:\Users\l670b\Phishing Detection – AI Chat\docs"
python -m http.server 8081
```

Open the login page: http://127.0.0.1:8081/login.html (sign in with any email; it redirects to the demo UI and sets the API base to http://127.0.0.1:5071).

Alternatively, open the static demo directly: http://127.0.0.1:8081/index.html (you can set the API base URL there, default is http://127.0.0.1:5071).

Note: If you later host `docs/` over HTTPS (e.g., GitHub Pages), browsers block calls to a local HTTP API. Use an HTTPS tunnel (e.g., ngrok) for the backend to avoid mixed content.

## 🖥️ Using the UI

- Type a message and click “Analyze” to see the result
- Click preset example buttons to try common phishing scenarios
- Use the theme toggle in the header to switch light/dark mode (it persists)
- Click “View System Statistics” to see activity summary

### Live demo flow
- Visit http://127.0.0.1:8081/login.html and sign in with any email (demo only).
- You’ll be redirected to docs UI (index.html) which targets http://127.0.0.1:5071 by default.
- Paste a phishing example like “URGENT! Your account expires in 1 hour. Click here to verify immediately!” → expect a red PHISHING badge and a high ensemble vote.
- Paste a normal message like “Meeting moved to 3 PM tomorrow.” → expect a green SAFE badge with low/zero ensemble vote.

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
        "feature_score": 4,
        "overall_label": "phishing",
        "ensemble_vote": "7/10 phishing",
        "algorithms": [
                { "name": "Naive Bayes", "label": "phishing", "confidence": 0.92, "accuracy": 0.90 },
                { "name": "Linear Classifier", "label": "phishing", "confidence": 0.94, "accuracy": 0.93 },
                { "name": "KNN", "label": "phishing", "confidence": 0.88, "accuracy": 0.88 },
                { "name": "Random Forest", "label": "phishing", "confidence": 0.96, "accuracy": 0.95 },
                { "name": "Decision Tree", "label": "clean", "confidence": 0.49, "accuracy": 0.89 }
        ]
}
```

### 🧠 Multi-Algorithm Classroom Demo

The `/detect` endpoint now returns an *ensemble* view simulating multiple algorithms often discussed in class:

| Algorithm                  | What It Represents (Demo)                        | Accuracy* |
|---------------------------|---------------------------------------------------|-----------|
| Naive Bayes               | Keyword feature probability model                | 90%       |
| Linear Classifier         | Logistic-style thresholding of feature score     | 93%       |
| KNN                       | Neighbor agreement on risk score                 | 88%       |
| Random Forest             | Multiple decision splits voting                  | 95%       |
| Decision Tree             | Single interpretable branching path              | 89%       |
| KMeans (Cluster Dist)     | Distance from “safe” cluster centroid            | 75%       |
| DBSCAN (Outlier Density)  | Density-based anomaly flagging                   | 72%       |
| Linear Regression (Score) | Continuous risk regression → threshold           | 70%       |
| One-Class SVM             | Boundary separation for inlier/outlier           | 85%       |
| Local Outlier Factor      | Local density comparison for anomaly             | 82%       |

Returned fields:

```json
{
        "overall_label": "phishing",          // majority vote outcome
        "ensemble_vote": "7/10 phishing",     // voting breakdown
        "algorithms": [                        // per-algorithm simulated results
                { "name": "Random Forest", "label": "phishing", "confidence": 0.96, "accuracy": 0.95 }
        ]
}
```

*Accuracy values are illustrative classroom placeholders (no dataset training in this lightweight demo). Replace with real evaluation metrics if you integrate actual model training.

Phishing results are presented with a red badge; safe results with green. Each algorithm row shows:

- Prediction (phishing/clean)
- Confidence (normalized from heuristic feature score)
- Static reference accuracy (for discussion)

To experiment programmatically, inspect the `algorithms` array in the JSON response.
### 🧪 PowerShell & curl POST Examples

PowerShell (Invoke-RestMethod):

```powershell
$headers = @{ 'Content-Type' = 'application/json' }
$body = '{"message":"URGENT! Your account expires in 1 hour. Click here to verify immediately!"}'
Invoke-RestMethod -Uri 'http://127.0.0.1:5071/detect' -Method POST -Headers $headers -Body $body | ConvertTo-Json -Depth 6
```

Windows curl.exe:

```powershell
curl.exe -H "Content-Type: application/json" -d "{\"message\":\"Hello team meeting moved to 3 PM tomorrow.\"}" http://127.0.0.1:5071/detect
```

GET with query (no body):

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:5071/detect?message=Test%20message" -Method GET | ConvertTo-Json -Depth 6
```

### 🌐 Enable GitHub Pages (docs/)

1. Commit and push the latest `docs/` folder to `main`.
2. In GitHub: Settings → Pages.
3. Select Branch: `main` and Folder: `/docs` then Save.
4. Wait ~2–5 minutes; site becomes available at: `https://<username>.github.io/<repository>/`.
5. If calling your local Flask API from the hosted pages, use an HTTPS tunnel (e.g., `ngrok http 5050`) to avoid mixed content errors.

Optional: Add a custom domain (CNAME) by creating `docs/CNAME` with your domain name.

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
Invoke-RestMethod -Uri 'http://127.0.0.1:5071/detect' -Method POST -Headers $headers -Body $body | ConvertTo-Json -Depth 5

# GET /stats
Invoke-RestMethod -Uri 'http://127.0.0.1:5071/stats' -Method GET | ConvertTo-Json -Depth 5

# GET /health
Invoke-RestMethod -Uri 'http://127.0.0.1:5071/health' -Method GET | ConvertTo-Json -Depth 5

Tip: If you’re running the server and requesting from the same PowerShell terminal, the output can get
interleaved with server logs. Open a new PowerShell window for API tests.
```

## 📈 Evaluation (illustrative)

This demo includes a small script to compute an illustrative accuracy on a tiny synthetic set (10 phishing + 10 clean) using the standalone detector:

```powershell
python src\eval_demo_accuracy.py
```

Example output (will vary if you change samples): Accuracy ~95%, Precision 100%, Recall ~90%, F1 ~0.95. This is for demonstration only and not a benchmark; replace with real datasets and models for production-grade metrics.

## 🐳 Run with Docker (optional)

This repo includes a Dockerfile that runs the original server (`src/index.py`) on port 5000. It’s more “microservice-y” and references legacy components. For the simple demo, prefer running `microservices_demo.py` locally as shown above.

Build and run:

```powershell
docker build -t phishing-ai-chat .
docker run -p 5000:5000 phishing-ai-chat
```

Open: http://127.0.0.1:5000

Health check: http://127.0.0.1:5000/health

## ⚙️ CI/CD with Jenkins

This repo includes a declarative pipeline (`Jenkinsfile`) so Jenkins can automatically lint, test, build, and archive artifacts.

1. Install plugins: **Pipeline**, **Git**, **JUnit**, **AnsiColor**, and **Docker Pipeline** (if building images on the agent).
2. Create a Pipeline job (or Multibranch job) and point SCM to `https://github.com/BharathL2/Phishing-Detection-AI-Chat.git`.
3. Jenkins will execute these stages:
        - **Checkout** – cleans workspace and clones the repo.
        - **Set up Python** – creates a virtual environment, upgrades `pip`, and installs `requirements.txt` plus `pytest`.
        - **Static Analysis** – runs `python -m compileall src` to catch syntax errors early.
        - **Unit Tests** – runs `pytest src/phishing_module` and publishes the JUnit report at `reports/junit.xml`.
        - **Package Model Server** – builds the Docker image `phishing-ai-chat:${BUILD_NUMBER}` if Docker is available.
        - **Archive Artifacts** – stores trained model files under `models/` and static docs under `docs/` for download.
4. Configure credentials/tokens if the repo is private. For public repos no credentials are required.
5. (Optional) Add a GitHub webhook so pushes trigger Jenkins automatically.

## ☸️ Kubernetes deployment

The `k8s/` folder ships manifests to run both the model API and the static UI inside a cluster.

### 1. Build and push the container image

```bash
docker build -t <registry>/phishing-ai-chat:latest .
docker push <registry>/phishing-ai-chat:latest
```

Update `k8s/backend.yaml` and `k8s/ui.yaml` to use your registry path (`<registry>/phishing-ai-chat:latest`).

### 2. Apply manifests

```bash
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/backend.yaml
kubectl apply -f k8s/ui.yaml
```

- `xgb-backend` Deployment: runs `python src/xgb_model_server.py` on port 5072 with readiness/liveness probes hitting `/health`.
- `ui-host` Deployment: reuses the same image but runs `python -m http.server 8081 --directory docs` to serve the static login/demo UI.
- Both Services default to `ClusterIP`. Change `spec.type` to `NodePort` or `LoadBalancer` if you need external access.

### 3. Access the services

- Inside the cluster: reference services as `http://xgb-backend.phishing-detection.svc.cluster.local` and `http://ui-host.phishing-detection.svc.cluster.local`.
- From outside: expose via an ingress controller or set `spec.type: LoadBalancer` and grab the provisioned IP.

### 4. Customize

- Adjust `replicas` for the backend (default `2`).
- Tune resource `requests/limits` per cluster capacity.
- Mount external model files via PVCs if you retrain frequently.

## ⚙️ Configuration

- `PORT` (env var): HTTP port for the dynamic server (default 5071). Example: `$env:PORT=5075`.
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
$env:PORT=5071; python src\dynamic_unsupervised_server.py
```

Run tests (if present):

```powershell
python -m unittest discover
```

## 🛠️ Troubleshooting

- “127.0.0.1 refused to connect”
        - Try another port: `$env:PORT=5060; python src\microservices_demo.py`
        - Stop stray processes: `Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force`
        - Check port usage: `netstat -ano | findstr LISTENING | findstr :5071`
        - Allow Python in Windows Firewall (Private networks)

- “Module not found”
        - Ensure you run from the project folder so `src` is discoverable
        - Activate your venv and `pip install -e .`

- “Invoke-WebRequest/Invoke-RestMethod fails while server is running”
        - Open a second PowerShell window and re-run the request there
        - Or use your browser at http://127.0.0.1:5071/health

## 📄 License

MIT (see LICENSE if present).

## 📚 Kaggle Dataset Integration (Optional)

You can integrate a larger public dataset from Kaggle for experimentation or improved supervised training.

### 1. Kaggle API Setup
1. Create / log into your Kaggle account: https://www.kaggle.com/
2. Profile (top right) → Account → API → Create New Token (downloads `kaggle.json`).
3. Place `kaggle.json` at (Windows): `%USERPROFILE%\.kaggle\kaggle.json`.
4. (Alternative) Set environment variables instead:
   - `KAGGLE_USERNAME` = your Kaggle username
   - `KAGGLE_KEY` = the API key from the JSON file

Install package:

```powershell
pip install kaggle
```

### 2. Download a Dataset
Use the generic downloader (does not hard-code a specific dataset):

```powershell
python -m src.data_fetch.kaggle_download --dataset owner/dataset-slug

# Example (adjust to your chosen dataset):
python -m src.data_fetch.kaggle_download --dataset ninjaapt/phishing-email-dataset
```

Files appear under: `data/raw/owner_dataset-slug/`

Re-run with `--force` to re-download. Add `--no-unzip` if you want the raw archive.

### 3. Normalize to a Unified CSV
Goal: produce `data/kaggle_phishing.csv` with columns: `text,label` where label ∈ {`phishing`,`clean`}.

If the dataset contains multiple CSVs, auto-detect columns via a helper snippet (edit heuristics as needed):

```powershell
python - <<'PY'
import pandas as pd, glob, os
root = 'data/raw'
out = 'data/kaggle_phishing.csv'
paths = glob.glob(os.path.join(root, '**', '*.csv'), recursive=True)
rows = []
TEXT_CANDIDATES = {'text','email text','body','content','message'}
LABEL_CANDIDATES = {'label','phishing','is_phishing','class','target'}
for p in paths:
        try:
                df = pd.read_csv(p, encoding='utf-8', errors='ignore')
        except Exception:
                continue
        cols_lower = {c.lower(): c for c in df.columns}
        text_col = next((cols_lower[c] for c in cols_lower if c in TEXT_CANDIDATES), None)
        subj_col = cols_lower.get('subject')
        label_col = next((cols_lower[c] for c in cols_lower if c in LABEL_CANDIDATES), None)
        if not text_col and subj_col:
                text_col = subj_col
        if not text_col or not label_col:
                continue
        for _, r in df.iterrows():
                raw_text = str(r.get(text_col,'')).strip()
                if subj_col:
                        raw_text = (str(r.get(subj_col,'')) + ' ' + raw_text).strip()
                if not raw_text:
                        continue
                raw_label = str(r.get(label_col,'')).strip().lower()
                if raw_label in ('phishing','spam','malicious','1','true','yes'):
                        mapped = 'phishing'
                elif raw_label in ('ham','legitimate','clean','0','false','no'):
                        mapped = 'clean'
                else:
                        continue
                rows.append({'text': raw_text, 'label': mapped})
print('Collected', len(rows), 'rows')
pd.DataFrame(rows).drop_duplicates().to_csv(out, index=False)
print('Wrote', out)
PY
```

Sanity check the first lines:

```powershell
Select-String -Path data\kaggle_phishing.csv -Pattern "" -Context 0,0 -ErrorAction SilentlyContinue | Select-Object -First 10
```

### 4. Train (Uses Existing Script)
Rename or copy the unified file to `data/sample_dataset.csv` OR adjust `DATA_PATH` inside `src/train_simple_model.py` to point to `data/kaggle_phishing.csv`, then:

```powershell
python src\train_simple_model.py
```

Result: `models/phish_logreg.pkl`

### 5. Evaluate

```powershell
python src\eval_demo_accuracy.py
```

If you retained the name `sample_dataset.csv` it will pick it up automatically; otherwise adapt the script.

### 6. (Optional) Unsupervised Mode
If the Kaggle dataset has inconsistent labels, skip normalization and run the anomaly-based server:

```powershell
python src\dynamic_unsupervised_server.py
```

Use POST /detect the same way; the response includes per-model anomaly scores.

Baseline seeding (to show dynamic approach without labels):

```powershell
# Build a baseline of normal (clean) messages
python -m src.data_fetch.build_normal_baseline  # creates data\normal_baseline.csv

# Or start with the provided sample baseline (data/normal_baseline.csv)

# Start the dynamic server (it auto-loads baseline if present)
python src\dynamic_unsupervised_server.py
```

What to show: the file `data/normal_baseline.csv` contains only normal chat texts (no phishing labels). The server learns a normal boundary from these and flags anomalies at runtime. This demonstrates a dynamic, unlabeled approach (no static supervised training required).

#### Alternate Baseline Formats
You can also provide the baseline as:
* `data/normal_baseline.txt`   (one clean message per line)
* `data/normal_baseline.jsonl` (one JSON object per line: {"text": "..."})

The dynamic server auto-detects CSV first, then TXT, then JSONL.

### 7. (Optional) Synthetic Augmentation
You can generate extra phishing variants by templating keywords; keep originals separate to avoid data leakage in evaluation. (Script placeholder to be added.)

### Notes
* Respect dataset license & attribution requirements.
* For large datasets, consider sampling first (e.g., `head -n 20000` via WSL or PowerShell filtering) to iterate quickly.
* Adjust vectorizer and model type as needed for better recall/precision trade-offs.
* For ML features (training/eval/dynamic server), you may need: `pip install scikit-learn pandas numpy joblib`.

