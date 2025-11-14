"""
Dynamic (unsupervised) phishing risk server without labeled dataset.
- Builds a small in-memory normal baseline from messages that look safely clean.
- Fits anomaly models on the fly: One-Class SVM, Isolation Forest, Local Outlier Factor, and KMeans center.
- Produces per-model outlier risk and a majority-vote decision.
- Always includes heuristic reasons for explainability.

Run:
  python src/dynamic_unsupervised_server.py
Then, in the docs/demo.html UI, set API Base URL to http://127.0.0.1:5071 and Save.
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
from collections import deque
import os
import numpy as np

from sklearn.feature_extraction.text import HashingVectorizer
from sklearn.svm import OneClassSVM
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor
from sklearn.cluster import KMeans

# Reuse heuristic base for reasons/feature_score
from microservices_demo import StandalonePhishingDetector
import pandas as pd
import json

app = Flask(__name__)
CORS(app)

# Config
PORT = int(os.environ.get('PORT', '5071'))
NORMAL_BUFFER_SIZE = 200            # keep last N clean-looking messages as baseline
MIN_NORMAL_TO_FIT = 30              # need at least this many to fit anomaly models
REFIT_EVERY = 10                    # refit models every N new normal samples
N_FEATURES = 2048                   # hashing dimensions
PHISHING_MEMORY_SIZE = 200          # keep last N user-confirmed phishing messages
MIN_PHISHING_TO_USE = 3             # need at least this many to use phishing memory signal

# State
heuristic = StandalonePhishingDetector()
normal_texts = deque(maxlen=NORMAL_BUFFER_SIZE)

# Phishing memory (user-labelled phishing examples) – kept separate from clean baseline
phishing_texts = deque(maxlen=PHISHING_MEMORY_SIZE)
_phishing_centroid = None  # running mean of phishing vectors (dense)
_phishing_seen = 0

vectorizer = HashingVectorizer(ngram_range=(1,2), n_features=N_FEATURES, alternate_sign=False)

# Models (recreated when (re)fitting)
one_class_svm = None
iso_forest = None
lof = None
kmeans = None

_last_fit_count = 0
_fit_count = 0


def _vec(texts):
    return vectorizer.transform(texts)

def _to_dense_row(sparse_row):
    """Convert a 1xN sparse row to dense float32 vector."""
    return sparse_row.toarray().astype(np.float32)[0]

def _should_add_to_normal(base_result: dict) -> bool:
    # Only learn from messages that look clearly clean to reduce contamination
    return base_result.get('label') == 'clean' and base_result.get('feature_score', 0) == 0

def _add_phishing_memory(text: str):
    """Add a confirmed phishing message into memory and update centroid incrementally."""
    global _phishing_centroid, _phishing_seen
    text = str(text).strip()
    if not text:
        return
    v = _vec([text])
    v_dense = _to_dense_row(v)
    # Update running mean centroid
    if _phishing_centroid is None:
        _phishing_centroid = v_dense
        _phishing_seen = 1
    else:
        _phishing_centroid = (_phishing_centroid * _phishing_seen + v_dense) / float(_phishing_seen + 1)
        _phishing_seen += 1
    phishing_texts.append(text)

def _phishing_memory_risk(sample_vec_dense: np.ndarray):
    """Return a risk in [0,1] based on cosine similarity to phishing centroid, if available."""
    if _phishing_centroid is None or len(phishing_texts) < MIN_PHISHING_TO_USE:
        return None
    c = _phishing_centroid
    # cosine similarity
    num = float(np.dot(sample_vec_dense, c))
    den = float(np.linalg.norm(sample_vec_dense) * np.linalg.norm(c) + 1e-8)
    sim = 0.0 if den == 0.0 else max(0.0, min(1.0, num / den))
    # Use similarity directly as risk (closer to known phishing ⇒ higher risk)
    return sim


def _fit_models():
    global one_class_svm, iso_forest, lof, kmeans, _last_fit_count
    if len(normal_texts) < MIN_NORMAL_TO_FIT:
        return False
    X = _vec(list(normal_texts))
    # Convert to dense for KMeans and sometimes for SVM depending on kernel implementation
    X_dense = X.astype(np.float32)

    # One-Class SVM (RBF)
    one_class_svm = OneClassSVM(kernel='rbf', gamma='scale', nu=0.1)
    one_class_svm.fit(X_dense)

    # Isolation Forest
    iso_forest = IsolationForest(n_estimators=50, contamination=0.1, random_state=42)
    iso_forest.fit(X_dense.toarray())

    # Local Outlier Factor (novelty=True to allow predict on new samples)
    lof_local = LocalOutlierFactor(n_neighbors=20, novelty=True)
    lof_local.fit(X_dense.toarray())
    lof = lof_local

    # KMeans center distance (k=1 to model a single normal centroid)
    km = KMeans(n_clusters=1, n_init=5, random_state=42)
    km.fit(X_dense.toarray())
    kmeans = km

    _last_fit_count = len(normal_texts)
    return True


def _maybe_refit():
    global _fit_count
    # Refit if no models or enough new normals accumulated
    needs_refit = (
        (one_class_svm is None or iso_forest is None or lof is None or kmeans is None)
        or (len(normal_texts) - _last_fit_count) >= REFIT_EVERY
    )
    if needs_refit and len(normal_texts) >= MIN_NORMAL_TO_FIT:
        if _fit_models():
            _fit_count += 1


def _load_baseline_if_available(path_csv: str = 'data/normal_baseline.csv'):
    try:
        # Try CSV first
        if os.path.exists(path_csv):
            df = pd.read_csv(path_csv)
            if 'text' in df.columns:
                for t in df['text']:
                    t = str(t).strip()
                    if t:
                        normal_texts.append(t)
        # Fallback options: TXT, JSONL, Kaggle CSVs, SMS Spam CSV
        path_txt = 'data/normal_baseline.txt'
        path_jsonl = 'data/normal_baseline.jsonl'
        path_kaggle = 'data/kaggle_phishing.csv'
        path_sample = 'data/sample_dataset.csv'
        path_sms = 'data/spam.csv'  # SMS Spam Collection

        if len(normal_texts) == 0 and os.path.exists(path_txt):
            with open(path_txt, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        normal_texts.append(line)
        if len(normal_texts) == 0 and os.path.exists(path_jsonl):
            with open(path_jsonl, 'r', encoding='utf-8') as f:
                for line in f:
                    line=line.strip()
                    if not line:
                        continue
                    try:
                        obj=json.loads(line)
                        t=str(obj.get('text','')).strip()
                        if t:
                            normal_texts.append(t)
                    except Exception:
                        continue
        if len(normal_texts) == 0 and os.path.exists(path_kaggle):
            try:
                df = pd.read_csv(path_kaggle)
                if {'text','label'}.issubset(df.columns):
                    for t in df[df['label'].str.lower()=='clean']['text']:
                        t = str(t).strip()
                        if t:
                            normal_texts.append(t)
            except Exception:
                pass
        if len(normal_texts) == 0 and os.path.exists(path_sample):
            try:
                df = pd.read_csv(path_sample)
                if {'text','label'}.issubset(df.columns):
                    for t in df[df['label'].str.lower()=='clean']['text']:
                        t = str(t).strip()
                        if t:
                            normal_texts.append(t)
            except Exception:
                pass
        if len(normal_texts) == 0 and os.path.exists(path_sms):
            try:
                # SMS Spam CSV format typically has columns v1 (ham/spam), v2 (message)
                df = pd.read_csv(path_sms, encoding='latin-1')
                # Some versions have extra unnamed columns; ignore them
                cols = {c.lower(): c for c in df.columns}
                label_col = cols.get('v1') or cols.get('label')
                text_col = cols.get('v2') or cols.get('text')
                if label_col and text_col:
                    clean_df = df[df[label_col].astype(str).str.lower().isin(['ham','clean','legitimate','0','false','no'])]
                    for t in clean_df[text_col]:
                        t = str(t).strip()
                        if t:
                            normal_texts.append(t)
            except Exception:
                pass
        if len(normal_texts) >= MIN_NORMAL_TO_FIT:
            _fit_models()
        return len(normal_texts) > 0
    except Exception:
        return False


def _risk_from_scores(sample_vec):
    """Compute per-model outlier risk in [0,1] where higher means more likely phishing."""
    algos = []

    # One-Class SVM: decision_function > 0 = inlier; < 0 = outlier
    if one_class_svm is not None:
        df = float(one_class_svm.decision_function(sample_vec)[0])
        # Map: df <= 0 → risk toward 1; df >= 1 → risk ~0
        risk = float(1.0 / (1.0 + np.exp(df)))  # sigmoid(-df)
        algos.append(('One-Class SVM', risk))

    # Isolation Forest: higher decision_function = more normal
    if iso_forest is not None:
        df = float(iso_forest.decision_function(sample_vec.toarray())[0])
        # Typical range ~[-0.5, 0.5]; map to risk in [0,1]
        risk = float(1.0 - (df + 0.5))  # df=-0.5→1, df=0.5→0
        risk = max(0.0, min(1.0, risk))
        algos.append(('Isolation Forest', risk))

    # Local Outlier Factor: decision_function > 0 = inlier; < 0 = outlier
    if lof is not None:
        df = float(lof.decision_function(sample_vec.toarray())[0])
        risk = float(1.0 / (1.0 + np.exp(df)))  # sigmoid(-df)
        algos.append(('Local Outlier Factor', risk))

    # KMeans distance to centroid → normalize by a heuristic scale
    if kmeans is not None:
        center = kmeans.cluster_centers_[0]
        v = sample_vec.toarray()[0]
        dist = float(np.linalg.norm(v - center))
        # Normalize: assume typical inlier dist below median_inlier ~ use training inertia scale
        scale = float(np.sqrt(max(kmeans.inertia_ / max(1, len(normal_texts)), 1e-6)))
        risk = max(0.0, min(1.0, dist / (3.0 * scale)))  # >~3 sigma → near 1
        algos.append(('KMeans (Centroid Dist)', risk))

    return algos


@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'normal_buffer': len(normal_texts),
        'dynamic_ready': len(normal_texts) >= MIN_NORMAL_TO_FIT,
        'fits': _fit_count
    })


@app.route('/stats')
def stats():
    return jsonify({
        'system_stats': {
            'total_messages': None,
            'phishing_detected': None,
            'clean_messages': None,
            'avg_confidence': None,
            'recent_messages': []
        },
        'dynamic': {
            'normal_buffer': len(normal_texts),
            'ready': len(normal_texts) >= MIN_NORMAL_TO_FIT,
            'fits': _fit_count,
            'vector_dim': N_FEATURES
        },
        'learning': {
            'phishing_memory_count': len(phishing_texts),
            'phishing_centroid_ready': _phishing_centroid is not None and len(phishing_texts) >= MIN_PHISHING_TO_USE
        },
        'performance': {
            'avg_processing_time': '< 50ms (approx)',
            'throughput': 'messages/sec (demo)'
        }
    })


@app.route('/')
def root():
        # Interactive landing page with quick links and /detect tester
        return (
                """<!doctype html>
<html lang=\"en\">\n<head>\n<meta charset=\"utf-8\" />\n<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\" />\n<title>Phishing Detection – Dynamic API</title>\n<style>body{font-family:system-ui,Segoe UI,Arial;margin:0;padding:24px;line-height:1.45;background:#fdfdfd}h2{margin-top:0}.row{display:flex;gap:8px;max-width:900px}.input{flex:1;padding:10px;font-size:15px;border:1px solid #ccc;border-radius:6px}.btn{background:#0d6efd;color:#fff;border:none;padding:10px 16px;font-size:14px;border-radius:6px;cursor:pointer}.btn:hover{background:#0b5ed7}.badge{display:inline-block;padding:4px 10px;border-radius:20px;font-weight:600;color:#fff;margin-right:6px}.safe{background:#198754}.phish{background:#dc3545}pre{background:#f6f8fa;padding:14px;border-radius:6px;overflow:auto;font-size:13px}a{color:#0d6efd;text-decoration:none}a:hover{text-decoration:underline}.small{color:#6c757d;font-size:12px;margin-top:4px}</style>\n</head>\n<body>\n<h2>Phishing Detection – Dynamic (Unsupervised) API</h2>\n<p>This server learns a normal baseline (only clean messages) and flags anomalies as potential phishing attempts.</p>\n<ul>\n<li><a href=\"/health\">/health</a> – health & readiness</li>\n<li><a href=\"/stats\">/stats</a> – dynamic stats</li>\n<li>POST <code>/detect</code> – JSON body: { \"message\": \"...\" }</li>\n</ul>\n<div class=\"row\" style=\"margin:18px 0;\">\n  <input id=\"msg\" class=\"input\" placeholder=\"Type a message (e.g., 'URGENT! Your account expires in 1 hour. Click here to verify.')\" />\n  <button class=\"btn\" onclick=\"detect()\">Analyze</button>\n</div>\n<div id=\"result\"></div>\n<pre id=\"json\" style=\"display:none\"></pre>\n<p class=\"small\">Full UI: <a href=\"http://127.0.0.1:8081/index.html\">http://127.0.0.1:8081/index.html</a> (API Base: 5071)</p>\n<script>async function detect(){const m=document.getElementById('msg').value.trim();if(!m){alert('Enter a message');return;}const box=document.getElementById('json');const resDiv=document.getElementById('result');box.style.display='block';box.textContent='Analyzing...';resDiv.innerHTML='';try{const r=await fetch('/detect',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:m})});const j=await r.json();box.textContent=JSON.stringify(j,null,2);const label=(j.overall_label||j.label)==='phishing'?'PHISHING':'SAFE';const cls=label==='PHISHING'?'badge phish':'badge safe';resDiv.innerHTML=`<span class="${cls}">${label}</span><span class="small">vote: ${j.ensemble_vote||''}</span>`;}catch(e){box.textContent='Error: '+e;}}</script>\n</body>\n</html>""",
                200,
                {"Content-Type": "text/html; charset=utf-8"}
        )


@app.route('/detect', methods=['POST','GET'])
def detect():
    # Parse input
    data = {}
    if request.is_json:
        tmp = request.get_json(silent=True)
        if isinstance(tmp, dict):
            data.update(tmp)
    if 'message' not in data and 'message' in request.args:
        data['message'] = request.args.get('message')
    # Mode selection: 'hybrid' (default) or 'dynamic' for dynamic-only decision proof (ignores heuristic keywords for final label)
    mode = data.get('mode') or request.args.get('mode') or 'hybrid'
    mode = mode.lower().strip()
    if 'message' not in data or not str(data['message']).strip():
        return jsonify({'error': 'message required'}), 400

    message = str(data['message'])

    # Heuristic pass (still used to decide if a message is clearly clean for baseline growth)
    base = heuristic.detect_phishing(message)

    # Update normal buffer if clearly clean
    if _should_add_to_normal(base):
        normal_texts.append(message)

    # Try (re)fitting models if enough data
    _maybe_refit()

    # Vectorize sample
    X = _vec([message])
    X_dense = _to_dense_row(X)

    dynamic_algorithms = []
    dynamic_ready = len(normal_texts) >= MIN_NORMAL_TO_FIT and all(m is not None for m in [one_class_svm, iso_forest, lof, kmeans])

    combined_risk = None
    algo_risks = []
    # Add baseline-driven anomaly models if ready
    if dynamic_ready:
        algo_risks.extend(_risk_from_scores(X))
    # Add phishing memory similarity if available (works even when baseline is warming up)
    pm_risk = _phishing_memory_risk(X_dense)
    if pm_risk is not None:
        algo_risks.append(("Phishing Memory (Similarity)", pm_risk))

    if algo_risks:
        # Convert risks to labels with 0.5 threshold
        for name, risk in algo_risks:
            dynamic_algorithms.append({
                'name': name,
                'risk': round(risk, 3),
                'label': 'phishing' if risk >= 0.5 else 'clean'
            })
        combined_risk = round(float(sum(r for _, r in algo_risks) / max(len(algo_risks),1)), 3)
        votes = sum(1 for a in dynamic_algorithms if a['label'] == 'phishing')
        overall_dynamic = 'phishing' if votes > len(dynamic_algorithms)/2 else 'clean'
        ensemble_vote = f"{votes}/{len(dynamic_algorithms)} phishing"
    else:
        combined_risk = None
        overall_dynamic = base.get('label')
        ensemble_vote = "N/A (no algorithms ready)"

    # Final decision depends on mode:
    # hybrid: use dynamic if ready else heuristic
    # dynamic: always use dynamic models if available, else report warming state
    if mode == 'dynamic':
        decision_mode = 'dynamic-only'
        final_label = overall_dynamic if algo_risks else 'clean'  # while no algorithms, treat as clean to avoid false positives
    else:
        decision_mode = 'hybrid'
        # Simple precedence: if dynamic ready use dynamic outcome else heuristic
        final_label = overall_dynamic if algo_risks else base.get('label')

    return jsonify({
        'overall_label': final_label,
        'ensemble_vote': ensemble_vote,
        'algorithms': dynamic_algorithms,
        'combined_risk': combined_risk,
        'decision_mode': decision_mode,
        'heuristic_label': base.get('label'),
        'heuristic_confidence': base.get('score'),
        'feature_score': base.get('feature_score'),
        'reasons': base.get('reasons'),
        'dynamic_ready': dynamic_ready,
        'normal_buffer': len(normal_texts),
        'phishing_memory': {
            'count': len(phishing_texts),
            'active': pm_risk is not None
        }
    })


@app.route('/feedback', methods=['POST'])
def feedback():
    """Accept user feedback to learn from messages.
    Body JSON: {"message": "...", "label": "phishing"|"clean"}
    - clean: added to normal baseline immediately and may trigger refit
    - phishing: added to phishing memory (separate from baseline)
    """
    if not request.is_json:
        return jsonify({'error': 'JSON body required'}), 400
    payload = request.get_json(silent=True) or {}
    msg = str(payload.get('message', '')).strip()
    label = str(payload.get('label', '')).strip().lower()
    if not msg or label not in {'phishing', 'clean'}:
        return jsonify({'error': 'Provide message and label in {phishing|clean}'}), 400

    if label == 'clean':
        normal_texts.append(msg)
        _maybe_refit()
        return jsonify({'ok': True, 'added_to': 'normal_baseline', 'normal_buffer': len(normal_texts), 'fits': _fit_count})
    else:
        _add_phishing_memory(msg)
        return jsonify({'ok': True, 'added_to': 'phishing_memory', 'phishing_memory_count': len(phishing_texts)})


if __name__ == '__main__':
    print(f"Dynamic unsupervised server on http://127.0.0.1:{PORT}")
    print("Note: Models warm up after ~", MIN_NORMAL_TO_FIT, "clean messages.")
    if _load_baseline_if_available():
        print(f"Loaded baseline: {len(normal_texts)} normal samples. Ready={len(normal_texts) >= MIN_NORMAL_TO_FIT}")
    app.run(host='0.0.0.0', port=PORT, debug=False)
