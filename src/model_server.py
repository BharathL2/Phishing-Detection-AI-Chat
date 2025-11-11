"""Flask server using trained Logistic Regression model (models/phish_logreg.pkl).
Fallbacks to heuristic StandalonePhishingDetector if model not found.
Run: python src/model_server.py
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import joblib

# Reuse heuristic detector for fallback and reasons.
from microservices_demo import StandalonePhishingDetector

MODEL_PATH = os.path.join('models', 'phish_logreg.pkl')

app = Flask(__name__)
CORS(app)

heuristic = StandalonePhishingDetector()
ml_model = None
if os.path.exists(MODEL_PATH):
    try:
        ml_model = joblib.load(MODEL_PATH)
        print(f"Loaded trained model: {MODEL_PATH}")
    except Exception as e:
        print(f"Failed to load model, using heuristic only: {e}")

@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'model_loaded': bool(ml_model),
        'mode': 'trained-logreg' if ml_model else 'heuristic-fallback'
    })

@app.route('/detect', methods=['POST','GET'])
def detect():
    # Unified message intake
    data = {}
    if request.is_json:
        tmp = request.get_json(silent=True)
        if isinstance(tmp, dict):
            data.update(tmp)
    if 'message' not in data and 'message' in request.args:
        data['message'] = request.args.get('message')
    if 'message' not in data:
        return jsonify({'error': 'message required'}), 400
    message = str(data['message'])

    # Always get heuristic explanation
    base = heuristic.detect_phishing(message)

    if ml_model:
        # Predict probability with trained model
        proba = ml_model.predict_proba([message])[0]
        phishing_prob = float(proba[1])  # class 1 = phishing
        label = 'phishing' if phishing_prob >= 0.5 else 'clean'
        response = {
            'label': label,
            'probability': round(phishing_prob, 4),
            'heuristic_feature_score': base.get('feature_score'),
            'heuristic_reasons': base.get('reasons'),
            'heuristic_label': base.get('label'),
            'source': 'trained+heuristic'
        }
    else:
        response = {
            'label': base.get('label'),
            'probability': base.get('score'),
            'heuristic_feature_score': base.get('feature_score'),
            'heuristic_reasons': base.get('reasons'),
            'source': 'heuristic-only'
        }
    return jsonify(response)

if __name__ == '__main__':
    port = int(os.environ.get('PORT','5070'))
    print(f"Model server running on http://127.0.0.1:{port}")
    app.run(host='0.0.0.0', port=port, debug=False)
