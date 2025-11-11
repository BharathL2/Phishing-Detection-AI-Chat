import json
import os
import csv
from typing import List, Tuple, Any

# We evaluate the demo (standalone) detector used by microservices_demo.py
# Note: This is a heuristics-based demo model, not trained. "Accuracy" here is illustrative.

try:
    # Import the demo detector without starting the Flask server
    import importlib
    ms = importlib.import_module('src.microservices_demo'.replace('/', '.').replace('\\', '.'))
    StandalonePhishingDetector = ms.StandalonePhishingDetector
except Exception as e:
    # Fallback: try relative import when running from repo root
    from microservices_demo import StandalonePhishingDetector


def evaluate(detector: Any, dataset: List[Tuple[str, int]]):
    """
    dataset: list of (message, label) where label=1 for phishing, 0 for clean
    Returns basic metrics dict
    """
    tp = tn = fp = fn = 0
    details = []
    for msg, y in dataset:
        pred = detector.detect_phishing(msg)
        yhat = 1 if pred.get('label') == 'phishing' else 0
        if y == 1 and yhat == 1:
            tp += 1
        elif y == 0 and yhat == 0:
            tn += 1
        elif y == 0 and yhat == 1:
            fp += 1
        elif y == 1 and yhat == 0:
            fn += 1
        details.append({
            'message': msg[:120],
            'true': 'phishing' if y==1 else 'clean',
            'pred': 'phishing' if yhat==1 else 'clean',
            'score': pred.get('score')
        })
    total = len(dataset)
    acc = (tp + tn) / total if total else 0.0
    prec = tp / (tp + fp) if (tp + fp) else 0.0
    rec = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2*prec*rec/(prec+rec) if (prec+rec) else 0.0
    return {
        'total': total,
        'tp': tp,
        'tn': tn,
        'fp': fp,
        'fn': fn,
        'accuracy': round(acc, 3),
        'precision': round(prec, 3),
        'recall': round(rec, 3),
        'f1': round(f1, 3),
        'samples': details
    }


if __name__ == '__main__':
    det = StandalonePhishingDetector()

    # If a CSV dataset exists at data/sample_dataset.csv, use it; else use built-in examples
    csv_path = os.path.join('data', 'sample_dataset.csv')
    dataset: List[Tuple[str, int]] = []
    if os.path.exists(csv_path):
        with open(csv_path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                text = (row.get('text') or '').strip()
                label_str = (row.get('label') or '').strip().lower()
                if not text or label_str not in ('phishing','clean'):
                    continue
                y = 1 if label_str == 'phishing' else 0
                dataset.append((text, y))
    else:
        # Tiny illustrative dataset (10 phishing, 10 clean) built from examples in the repo
        phishing = [
            "URGENT! Your account expires in 1 hour. Click here to verify immediately!",
            "Congratulations! You won $5000 cash prize! Claim your free reward now!",
            "Your PayPal account requires immediate verification. Login at fake-paypal.com",
            "Bank Alert: Suspicious login detected. Verify your account to avoid suspension!",
            "DHL: Your package is on hold due to unpaid customs. Pay the fee here to release delivery",
            "Refund available: You were overcharged. Submit your card details for instant refund",
            "Crypto Giveaway! Send 0.1 ETH and receive 1 ETH back instantly! Limited time offer!",
            "ACTION REQUIRED: Update your billing information immediately",
            "Your Netflix subscription will be suspended. Update your payment info to continue",
            "OTP: 482913. If you didn't request this, reset your password immediately"
        ]
        clean = [
            "Hi team! Meeting tomorrow at 2 PM in conference room A.",
            "Hello, how are you today?",
            "The meeting is scheduled for 3 PM tomorrow.",
            "Thanks for the great presentation yesterday.",
            "Let's discuss the project requirements next week.",
            "I uploaded the notes to the shared folder. Please review when you can.",
            "Lunch at 12:30?",
            "Reminder: Submit timesheets by Friday.",
            "Happy birthday! Wishing you a great year ahead.",
            "The server maintenance window is Sunday 1-3 AM."
        ]
        dataset = [(m, 1) for m in phishing] + [(m, 0) for m in clean]

    results = evaluate(det, dataset)
    print(json.dumps(results, indent=2))
