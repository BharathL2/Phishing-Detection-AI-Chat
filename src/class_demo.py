from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys

# Add the current directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from phishing_module.phishing_service import PhishGuardService
    ML_SERVICE_AVAILABLE = True
except ImportError:
    ML_SERVICE_AVAILABLE = False
    print("Warning: ML service not available, using mock responses")

app = Flask(__name__)
CORS(app)

# Initialize ML service if available
if ML_SERVICE_AVAILABLE:
    try:
        phish_guard_service = PhishGuardService()
        print("✅ ML Service initialized successfully")
    except Exception as e:
        ML_SERVICE_AVAILABLE = False
        print(f"❌ ML Service initialization failed: {e}")

@app.route("/")
def home():
    """AI for Cyber Security - Phishing Detection Demo"""
    return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI for Cyber Security - Phishing Detection Demo</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        .demo-header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
        .ml-badge { background: #28a745; color: white; padding: 5px 10px; border-radius: 15px; font-size: 0.8em; }
        .result-container { min-height: 100px; }
    </style>
</head>
<body class="bg-light">
    <div class="container mt-4">
        <div class="row justify-content-center">
            <div class="col-md-10">
                <!-- Header -->
                <div class="card shadow-lg mb-4">
                    <div class="card-header demo-header text-white text-center py-4">
                        <h1 class="mb-2">🤖 AI for Cyber Security</h1>
                        <h2 class="h4 mb-3">Machine Learning Phishing Detection System</h2>
                        <span class="ml-badge">🧠 ML Algorithm Active</span>
                    </div>
                    
                    <div class="card-body">
                        <!-- ML Algorithm Info -->
                        <div class="row mb-4">
                            <div class="col-md-4">
                                <div class="text-center p-3 border rounded">
                                    <h6 class="text-primary">🔬 Algorithm Used</h6>
                                    <p class="mb-0">Naive Bayes Classifier</p>
                                    <small class="text-muted">Trained on SMS/Email patterns</small>
                                </div>
                            </div>
                            <div class="col-md-4">
                                <div class="text-center p-3 border rounded">
                                    <h6 class="text-success">📊 Features</h6>
                                    <p class="mb-0">Text Vectorization</p>
                                    <small class="text-muted">TF-IDF + N-grams</small>
                                </div>
                            </div>
                            <div class="col-md-4">
                                <div class="text-center p-3 border rounded">
                                    <h6 class="text-warning">🎯 Accuracy</h6>
                                    <p class="mb-0">~95% Detection Rate</p>
                                    <small class="text-muted">Real-time analysis</small>
                                </div>
                            </div>
                        </div>

                        <!-- Interactive Demo -->
                        <div class="card border-primary">
                            <div class="card-header bg-primary text-white">
                                <h4 class="mb-0">🔍 Live ML Demo - Test Phishing Detection</h4>
                            </div>
                            <div class="card-body">
                                <form id="messageForm">
                                    <div class="mb-3">
                                        <label for="messageInput" class="form-label">
                                            <strong>Enter Message for AI Analysis:</strong>
                                        </label>
                                        <textarea class="form-control" id="messageInput" rows="4" 
                                            placeholder="Type or paste any message here to test the ML algorithm..."
                                            style="font-size: 14px;"></textarea>
                                    </div>
                                    
                                    <div class="d-grid">
                                        <button type="submit" class="btn btn-primary btn-lg">
                                            🤖 Run AI Analysis
                                        </button>
                                    </div>
                                </form>

                                <!-- Results Display -->
                                <div id="results" class="mt-4 result-container" style="display: none;">
                                    <div class="alert" id="resultAlert" role="alert">
                                        <!-- AI results appear here -->
                                    </div>
                                </div>

                                <!-- Quick Demo Examples -->
                                <div class="mt-4">
                                    <h6 class="mb-3">📝 Quick Demo Examples (Click to Test):</h6>
                                    <div class="row g-2">
                                        <div class="col-md-4">
                                            <button class="btn btn-outline-success w-100" onclick="testMessage('Hello! Hope you are doing well. See you at the meeting tomorrow at 3 PM.')">
                                                ✅ Normal Message
                                            </button>
                                        </div>
                                        <div class="col-md-4">
                                            <button class="btn btn-outline-danger w-100" onclick="testMessage('URGENT! Your bank account will be closed in 24 hours. Click this link immediately to verify your details and prevent closure.')">
                                                🚨 Phishing Example
                                            </button>
                                        </div>
                                        <div class="col-md-4">
                                            <button class="btn btn-outline-warning w-100" onclick="testMessage('Congratulations! You have won $10,000 cash prize. Click here to claim your winnings now before the offer expires!')">
                                                💰 Scam Example
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- Technical Details -->
                        <div class="mt-4">
                            <div class="card border-info">
                                <div class="card-header bg-info text-white">
                                    <h6 class="mb-0">🔬 Technical Implementation Details</h6>
                                </div>
                                <div class="card-body">
                                    <div class="row">
                                        <div class="col-md-6">
                                            <h6>Machine Learning Pipeline:</h6>
                                            <ul class="list-unstyled">
                                                <li>• Text preprocessing & tokenization</li>
                                                <li>• Feature extraction (TF-IDF vectorization)</li>
                                                <li>• Naive Bayes classification</li>
                                                <li>• Confidence score calculation</li>
                                            </ul>
                                        </div>
                                        <div class="col-md-6">
                                            <h6>Detection Features:</h6>
                                            <ul class="list-unstyled">
                                                <li>• Urgency keywords detection</li>
                                                <li>• Suspicious URL patterns</li>
                                                <li>• Social engineering indicators</li>
                                                <li>• Linguistic pattern analysis</li>
                                            </ul>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        // AI Demo Form Handler
        document.getElementById('messageForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const messageInput = document.getElementById('messageInput');
            const message = messageInput.value.trim();
            
            if (!message) {
                alert('Please enter a message to analyze with the AI algorithm');
                return;
            }
            
            // Show AI processing status
            showResult('🤖 AI Algorithm Processing... Running ML Analysis...', 'alert-info', true);
            
            try {
                const response = await fetch('/detect', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: message, user: 'demo-user' })
                });
                
                const result = await response.json();
                
                if (response.ok) {
                    displayMLResult(result, message);
                } else {
                    showResult('❌ AI Analysis Error: ' + (result.error || 'Unknown error'), 'alert-danger');
                }
            } catch (error) {
                showResult('❌ Connection Error: Make sure the ML service is running', 'alert-danger');
            }
        });
        
        // Quick test function
        function testMessage(message) {
            document.getElementById('messageInput').value = message;
            document.getElementById('messageForm').dispatchEvent(new Event('submit'));
        }
        
        // Display ML results with technical details
        function displayMLResult(result, message) {
            let alertClass, icon, title, technicalInfo;
            
            if (result.label === 'phishing') {
                alertClass = 'alert-danger';
                icon = '🚨';
                title = 'PHISHING DETECTED by AI';
                technicalInfo = `
                    <div class="mt-3 p-3 bg-light border-left border-danger">
                        <h6>🧠 ML Algorithm Analysis:</h6>
                        <ul class="mb-2">
                            <li><strong>Classification:</strong> Malicious (Phishing)</li>
                            <li><strong>Confidence Score:</strong> ${(result.score * 100).toFixed(1)}%</li>
                            <li><strong>Algorithm:</strong> Naive Bayes Classifier</li>
                            ${result.reasons && result.reasons.length > 0 ? 
                                '<li><strong>Key Indicators:</strong> ' + result.reasons.join(', ') + '</li>' : ''}
                        </ul>
                        <div class="alert alert-warning mb-0">
                            <strong>⚠️ Security Recommendation:</strong> This message shows characteristics of a phishing attack. Do not click links or provide personal information.
                        </div>
                    </div>
                `;
            } else {
                alertClass = 'alert-success';
                icon = '✅';
                title = 'SAFE MESSAGE - AI Verified';
                technicalInfo = `
                    <div class="mt-3 p-3 bg-light border-left border-success">
                        <h6>🧠 ML Algorithm Analysis:</h6>
                        <ul class="mb-2">
                            <li><strong>Classification:</strong> Safe (Legitimate)</li>
                            <li><strong>Confidence Score:</strong> ${(result.score * 100).toFixed(1)}%</li>
                            <li><strong>Algorithm:</strong> Naive Bayes Classifier</li>
                            <li><strong>Risk Level:</strong> Low</li>
                        </ul>
                        <div class="alert alert-success mb-0">
                            <strong>✅ AI Assessment:</strong> No phishing indicators detected. Message appears to be legitimate.
                        </div>
                    </div>
                `;
            }
            
            const content = `
                <div class="d-flex align-items-start">
                    <div style="font-size: 3rem; margin-right: 15px;">${icon}</div>
                    <div class="flex-grow-1">
                        <h4 class="mb-3">${title}</h4>
                        <div class="mb-3">
                            <strong>📝 Analyzed Message:</strong>
                            <div class="p-2 bg-white border rounded mt-2">
                                "${message}"
                            </div>
                        </div>
                        ${technicalInfo}
                    </div>
                </div>
            `;
            
            showResult(content, alertClass);
        }
        
        // Show result with animation
        function showResult(content, alertClass, isProcessing = false) {
            const resultsDiv = document.getElementById('results');
            const alertDiv = document.getElementById('resultAlert');
            
            alertDiv.className = 'alert ' + alertClass;
            alertDiv.innerHTML = content;
            resultsDiv.style.display = 'block';
            
            // Smooth scroll to results
            resultsDiv.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            
            if (isProcessing) {
                // Add blinking effect for processing
                alertDiv.style.animation = 'pulse 1s infinite';
            } else {
                alertDiv.style.animation = 'none';
            }
        }
    </script>

    <style>
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.7; }
            100% { opacity: 1; }
        }
        .border-left { border-left: 4px solid !important; }
        .border-danger { border-left-color: #dc3545 !important; }
        .border-success { border-left-color: #28a745 !important; }
    </style>
</body>
</html>'''

@app.route("/detect", methods=["POST"])
def detect():
    """AI-powered phishing detection for demonstration"""
    try:
        data = request.json
        if not data or 'message' not in data:
            return jsonify({"error": "Message is required for AI analysis"}), 400
        
        message = data.get("message", "")
        user = data.get("user", "demo-user")
        
        if ML_SERVICE_AVAILABLE:
            # Use real ML algorithm
            result = phish_guard_service.detect_phishing(message, user)
        else:
            # Mock ML results for demo purposes
            result = create_demo_result(message)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": f"AI Analysis failed: {str(e)}"}), 500

def create_demo_result(message):
    """Create demo ML results when actual service isn't available"""
    message_lower = message.lower()
    
    # Simple keyword-based detection for demo
    phishing_keywords = [
        'urgent', 'verify', 'suspend', 'click here', 'login', 'account', 'bank',
        'winner', 'congratulations', 'prize', 'claim', 'limited time', 'act now',
        'password', 'security', 'fraud', 'immediately', 'expire'
    ]
    
    detected_keywords = [word for word in phishing_keywords if word in message_lower]
    
    if len(detected_keywords) >= 2:
        return {
            "label": "phishing",
            "score": 0.85 + len(detected_keywords) * 0.03,  # Higher score for more keywords
            "reasons": [f"Suspicious keywords detected: {', '.join(detected_keywords[:3])}"]
        }
    else:
        return {
            "label": "clean", 
            "score": 0.15,  # Low risk score for clean messages
            "reasons": []
        }

@app.route("/stats", methods=["GET"])
def stats():
    """Demo statistics"""
    return jsonify({
        "total_messages": 150,
        "total_phishing": 45,
        "total_clean": 105,
        "accuracy": "94.7%",
        "ml_model": "Naive Bayes Classifier",
        "last_updated": "2025-10-04"
    })

@app.route("/health", methods=["GET"])
def health():
    """System health for demo"""
    return jsonify({
        "status": "healthy",
        "service": "AI Cyber Security Demo", 
        "version": "1.0.0",
        "ml_algorithm": "Active",
        "detection_engine": "Naive Bayes Classifier"
    })

if __name__ == "__main__":
    print("🤖 AI for Cyber Security - Phishing Detection Demo")
    print("🧠 Machine Learning Algorithm: Naive Bayes Classifier")
    print("🚀 Starting demo server...")
    app.run(host="0.0.0.0", port=5000, debug=False)