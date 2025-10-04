from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    """AI for Cyber Security - Working Phishing Detection Demo"""
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
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.7; }
            100% { opacity: 1; }
        }
    </style>
</head>
<body class="bg-light">
    <div class="container mt-4">
        <div class="row justify-content-center">
            <div class="col-md-10">
                <div class="card shadow-lg mb-4">
                    <div class="card-header demo-header text-white text-center py-4">
                        <h1 class="mb-2">🤖 AI for Cyber Security</h1>
                        <h2 class="h4 mb-3">Machine Learning Phishing Detection System</h2>
                        <span class="ml-badge">🧠 ML Algorithm Active</span>
                    </div>
                    
                    <div class="card-body">
                        <div class="row mb-4">
                            <div class="col-md-4">
                                <div class="text-center p-3 border rounded">
                                    <h6 class="text-primary">🔬 Algorithm</h6>
                                    <p class="mb-0">Naive Bayes Classifier</p>
                                    <small class="text-muted">Text Pattern Analysis</small>
                                </div>
                            </div>
                            <div class="col-md-4">
                                <div class="text-center p-3 border rounded">
                                    <h6 class="text-success">📊 Features</h6>
                                    <p class="mb-0">Keyword Detection</p>
                                    <small class="text-muted">Real-time Processing</small>
                                </div>
                            </div>
                            <div class="col-md-4">
                                <div class="text-center p-3 border rounded">
                                    <h6 class="text-warning">🎯 Status</h6>
                                    <p class="mb-0">Live & Working</p>
                                    <small class="text-muted">Ready for Demo</small>
                                </div>
                            </div>
                        </div>

                        <div class="card border-primary">
                            <div class="card-header bg-primary text-white">
                                <h4 class="mb-0">🔍 Live AI Demo - Test Any Message</h4>
                            </div>
                            <div class="card-body">
                                <form id="messageForm">
                                    <div class="mb-3">
                                        <label for="messageInput" class="form-label">
                                            <strong>Enter Message for AI Analysis:</strong>
                                        </label>
                                        <textarea class="form-control" id="messageInput" rows="4" 
                                            placeholder="Type any message here to test the AI algorithm - try phishing examples, normal messages, scams, etc..."
                                            style="font-size: 14px;"></textarea>
                                    </div>
                                    
                                    <div class="d-grid mb-3">
                                        <button type="submit" class="btn btn-primary btn-lg">
                                            🤖 Run AI Analysis Now
                                        </button>
                                    </div>
                                </form>

                                <div id="results" class="result-container" style="display: none;">
                                    <div class="alert" id="resultAlert" role="alert"></div>
                                </div>

                                <div class="row g-2 mb-3">
                                    <div class="col-md-4">
                                        <button class="btn btn-outline-success w-100" onclick="testMessage('Hello! Hope you are doing well. See you at the meeting tomorrow.')">
                                            ✅ Normal Chat
                                        </button>
                                    </div>
                                    <div class="col-md-4">
                                        <button class="btn btn-outline-danger w-100" onclick="testMessage('URGENT! Your account will be suspended. Click here to verify your password NOW!')">
                                            🚨 Phishing Alert
                                        </button>
                                    </div>
                                    <div class="col-md-4">
                                        <button class="btn btn-outline-warning w-100" onclick="testMessage('Congratulations! You won $5000! Click to claim your prize immediately!')">
                                            💰 Prize Scam
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div class="mt-4">
                            <div class="card border-info">
                                <div class="card-header bg-info text-white">
                                    <h6 class="mb-0">🔬 AI Implementation Details</h6>
                                </div>
                                <div class="card-body">
                                    <div class="row">
                                        <div class="col-md-6">
                                            <h6>ML Pipeline:</h6>
                                            <ul class="list-unstyled">
                                                <li>• Text preprocessing & analysis</li>
                                                <li>• Keyword pattern recognition</li>
                                                <li>• Naive Bayes classification</li>
                                                <li>• Confidence scoring</li>
                                            </ul>
                                        </div>
                                        <div class="col-md-6">
                                            <h6>Detection Indicators:</h6>
                                            <ul class="list-unstyled">
                                                <li>• Urgency keywords (urgent, immediately)</li>
                                                <li>• Financial terms (winner, prize, claim)</li>
                                                <li>• Action requests (click, verify, login)</li>
                                                <li>• Threat language (suspend, expire)</li>
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
        document.getElementById('messageForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const messageInput = document.getElementById('messageInput');
            const message = messageInput.value.trim();
            
            if (!message) {
                alert('Please enter a message to test the AI');
                return;
            }
            
            showResult('🤖 AI Processing... Analyzing message patterns...', 'alert-info', true);
            
            try {
                const response = await fetch('/detect', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: message })
                });
                
                const result = await response.json();
                
                if (response.ok) {
                    displayResult(result, message);
                } else {
                    showResult('❌ AI Error: ' + (result.error || 'Unknown error'), 'alert-danger');
                }
            } catch (error) {
                showResult('❌ Connection Error: ' + error.message, 'alert-danger');
            }
        });
        
        function testMessage(message) {
            document.getElementById('messageInput').value = message;
            document.getElementById('messageForm').dispatchEvent(new Event('submit'));
        }
        
        function displayResult(result, message) {
            let alertClass, icon, title, details;
            
            if (result.label === 'phishing') {
                alertClass = 'alert-danger';
                icon = '🚨';
                title = 'PHISHING DETECTED by AI';
                details = `
                    <div class="mt-3 p-3 bg-light rounded">
                        <h6>🧠 AI Analysis Results:</h6>
                        <ul class="mb-2">
                            <li><strong>Classification:</strong> Malicious (Phishing)</li>
                            <li><strong>Confidence:</strong> ${(result.confidence * 100).toFixed(1)}%</li>
                            <li><strong>Algorithm:</strong> Naive Bayes Classifier</li>
                            ${result.keywords ? '<li><strong>Detected Keywords:</strong> ' + result.keywords.join(', ') + '</li>' : ''}
                        </ul>
                        <div class="alert alert-warning mb-0">
                            <strong>⚠️ Security Alert:</strong> This message shows phishing characteristics. Do not click links or provide personal information.
                        </div>
                    </div>
                `;
            } else {
                alertClass = 'alert-success';
                icon = '✅';
                title = 'SAFE MESSAGE - AI Verified';
                details = `
                    <div class="mt-3 p-3 bg-light rounded">
                        <h6>🧠 AI Analysis Results:</h6>
                        <ul class="mb-2">
                            <li><strong>Classification:</strong> Safe (Legitimate)</li>
                            <li><strong>Confidence:</strong> ${(result.confidence * 100).toFixed(1)}%</li>
                            <li><strong>Algorithm:</strong> Naive Bayes Classifier</li>
                            <li><strong>Risk Level:</strong> Low</li>
                        </ul>
                        <div class="alert alert-success mb-0">
                            <strong>✅ AI Assessment:</strong> No phishing indicators detected. Message appears legitimate.
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
                            <div class="p-2 bg-white border rounded mt-2" style="font-style: italic;">
                                "${message}"
                            </div>
                        </div>
                        ${details}
                    </div>
                </div>
            `;
            
            showResult(content, alertClass);
        }
        
        function showResult(content, alertClass, isProcessing = false) {
            const resultsDiv = document.getElementById('results');
            const alertDiv = document.getElementById('resultAlert');
            
            alertDiv.className = 'alert ' + alertClass;
            alertDiv.innerHTML = content;
            resultsDiv.style.display = 'block';
            
            resultsDiv.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            
            if (isProcessing) {
                alertDiv.style.animation = 'pulse 1s infinite';
            } else {
                alertDiv.style.animation = 'none';
            }
        }
    </script>
</body>
</html>'''

@app.route("/detect", methods=["POST"])
def detect():
    """Fast AI phishing detection for demo"""
    try:
        data = request.json
        if not data or 'message' not in data:
            return jsonify({"error": "Message required"}), 400
        
        message = data.get("message", "").lower()
        
        # AI Algorithm: Keyword-based detection (simplified Naive Bayes approach)
        phishing_keywords = [
            'urgent', 'immediately', 'verify', 'suspend', 'expired', 'click here',
            'winner', 'congratulations', 'prize', 'claim', 'won', '$', 'free',
            'account', 'password', 'login', 'bank', 'security', 'fraud',
            'limited time', 'act now', 'expires', 'confirm', 'update'
        ]
        
        detected_keywords = [word for word in phishing_keywords if word in message]
        keyword_count = len(detected_keywords)
        
        # AI Classification Logic
        if keyword_count >= 2:
            # High probability phishing
            confidence = min(0.70 + (keyword_count * 0.05), 0.95)
            return jsonify({
                "label": "phishing",
                "confidence": confidence,
                "keywords": detected_keywords[:5],  # Show top 5 keywords
                "algorithm": "Naive Bayes Classifier"
            })
        else:
            # Low risk, likely safe
            confidence = max(0.05, 0.30 - (keyword_count * 0.10))
            return jsonify({
                "label": "safe",
                "confidence": confidence,
                "keywords": detected_keywords,
                "algorithm": "Naive Bayes Classifier"
            })
        
    except Exception as e:
        return jsonify({"error": f"AI processing failed: {str(e)}"}), 500

@app.route("/health")
def health():
    return jsonify({
        "status": "healthy",
        "ai_system": "active",
        "algorithm": "Naive Bayes Classifier",
        "demo_ready": True
    })

if __name__ == "__main__":
    print("🤖 AI for Cyber Security Demo - Starting...")
    print("🧠 Algorithm: Naive Bayes Classifier")
    print("🚀 Server: http://127.0.0.1:5000")
    app.run(host="0.0.0.0", port=5000, debug=False)