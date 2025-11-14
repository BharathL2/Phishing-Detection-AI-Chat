"""Flask server serving XGBoost phishing detector (models/phish_xgb.pkl).
Run: python src/xgb_model_server.py  (default port 5072)
Endpoints:
  GET /health -> readiness & model status
  POST /detect {"message": "..."}
Falls back to heuristic detector if model not present.
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import joblib
import json
from microservices_demo import StandalonePhishingDetector

MODEL_PATH = os.path.join('models','phish_xgb.pkl')
PORT = int(os.environ.get('PORT','5072'))

app = Flask(__name__)
CORS(app)

heuristic = StandalonePhishingDetector()
ml_model = None
metrics = None
METRICS_PATH = os.path.join('models','phish_xgb_metrics.json')

def load_metrics_if_available():
    global metrics
    try:
        if os.path.exists(METRICS_PATH):
            with open(METRICS_PATH,'r',encoding='utf-8') as f:
                metrics = json.load(f)
            return True
    except Exception as e:
        print("Failed to load metrics file:", e)
    return False
try:
    if os.path.exists(MODEL_PATH):
        ml_model = joblib.load(MODEL_PATH)
        print(f"Loaded XGBoost model: {MODEL_PATH}")
        if load_metrics_if_available():
            print(f"Loaded metrics: {metrics}")
    else:
        print("XGBoost model not found; heuristic fallback only.")
except Exception as e:
    print(f"Failed loading XGBoost model: {e}")

@app.route('/health')
def health():
    if metrics is None:
        load_metrics_if_available()
    return jsonify({
        'status': 'healthy',
        'model_loaded': bool(ml_model),
        'mode': 'xgboost+heuristic' if ml_model else 'heuristic-only',
        'training_metrics': metrics
    })

@app.route('/metrics')
def model_metrics():
    if metrics is None:
        load_metrics_if_available()
    if not metrics:
        return jsonify({'error':'metrics unavailable'}), 404
    return jsonify(metrics)

@app.route('/detect', methods=['POST','GET'])
def detect():
    data = {}
    if request.is_json:
        tmp = request.get_json(silent=True)
        if isinstance(tmp, dict):
            data.update(tmp)
    if 'message' not in data and 'message' in request.args:
        data['message'] = request.args.get('message')
    if 'message' not in data or not str(data['message']).strip():
        return jsonify({'error': 'message required'}), 400
    msg = str(data['message'])

    base = heuristic.detect_phishing(msg)

    if ml_model:
        if metrics is None:
            load_metrics_if_available()
        proba = ml_model.predict_proba([msg])[0]
        model_prob = float(proba[1])
        final_prob = model_prob
        label = 'phishing' if model_prob >= 0.5 else 'clean'
        decision_source = 'xgboost+heuristic'
        if base.get('label') == 'phishing':
            label = 'phishing'
            final_prob = max(model_prob, 0.85)
            decision_source = 'heuristic_override'
        return jsonify({
            'label': label,
            'phishing_probability': round(final_prob,4),
            'model_probability': round(model_prob,4),
            'accuracy': metrics.get('accuracy') if metrics else None,
            'precision': metrics.get('precision') if metrics else None,
            'recall': metrics.get('recall') if metrics else None,
            'f1': metrics.get('f1') if metrics else None,
            'samples': metrics.get('samples') if metrics else None,
            'heuristic_label': base.get('label'),
            'heuristic_reasons': base.get('reasons'),
            'feature_score': base.get('feature_score'),
            'source': decision_source
        })
    else:
        return jsonify({
            'label': base.get('label'),
            'heuristic_reasons': base.get('reasons'),
            'feature_score': base.get('feature_score'),
            'source': 'heuristic-only'
        })

if __name__ == '__main__':
    print(f"XGBoost model server running on http://127.0.0.1:{PORT}")
    app.run(host='0.0.0.0', port=PORT, debug=False)
