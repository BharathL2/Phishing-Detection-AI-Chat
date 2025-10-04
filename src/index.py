from flask import Flask, request, jsonify
from flask_cors import CORS
from phishing_module.phishing_service import PhishGuardService

app = Flask(__name__)
CORS(app)

# Initialize Phish Chat Guard service
phish_guard_service = PhishGuardService()

@app.route("/")
def home():
    """Serve the enhanced Phish Chat Guard interface"""
    return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Phish Chat Guard - Real-Time Phishing Detection</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="bg-light">
    <div class="container mt-5">
        <div class="row justify-content-center">
            <div class="col-md-8">
                <div class="card shadow">
                    <div class="card-header bg-primary text-white text-center">
                        <h1>🛡️ Phish Chat Guard</h1>
                        <p>AI-Powered Phishing Detection for Real-Time Communications</p>
                    </div>
                    <div class="card-body text-center">
                        <h3>System Status: <span class="text-success">ACTIVE</span></h3>
                        <p class="lead">The Phish Chat Guard detection engine is running and ready to analyze messages for phishing attempts.</p>
                        
                        <div class="row mt-4">
                            <div class="col-md-6">
                                <div class="card">
                                    <div class="card-body">
                                        <h5>API Endpoints</h5>
                                        <p><code>POST /detect</code> - Analyze messages</p>
                                        <p><code>GET /health</code> - System health</p>
                                        <p><code>GET /stats</code> - Detection statistics</p>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-6">
                                <div class="card">
                                    <div class="card-body">
                                        <h5>Detection Features</h5>
                                        <p>✅ Keyword Analysis</p>
                                        <p>✅ URL Pattern Detection</p>
                                        <p>✅ Behavioral Indicators</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <!-- INTERACTIVE MESSAGE TESTING SECTION -->
                        <div class="mt-5 border-top pt-4">
                            <h4 class="text-primary">🔍 Test Message Detection</h4>
                            <p class="text-muted">Enter any message below to check if it is safe or a phishing attempt</p>
                            
                            <form id="messageForm" class="mt-4">
                                <div class="mb-3 text-start">
                                    <label for="messageInput" class="form-label"><strong>Enter Message:</strong></label>
                                    <textarea class="form-control" id="messageInput" rows="4" 
                                        placeholder="Type or paste any message here to check if it is safe or phishing..."></textarea>
                                </div>
                                <button type="submit" class="btn btn-primary btn-lg">
                                    🔍 Analyze Message
                                </button>
                            </form>
                            
                            <!-- Results Display -->
                            <div id="results" class="mt-4" style="display: none;">
                                <div class="alert" id="resultAlert">
                                    <!-- Results appear here -->
                                </div>
                            </div>
                            
                            <!-- Quick Test Examples -->
                            <div class="mt-4">
                                <h6>Quick Test Examples:</h6>
                                <div class="btn-group-vertical d-grid gap-2">
                                    <button type="button" class="btn btn-outline-success" onclick="testExample('Hello! How was your weekend? Hope you had a great time!')">
                                        ✅ Test Safe Message
                                    </button>
                                    <button type="button" class="btn btn-outline-danger" onclick="testExample('URGENT! Your account will be suspended in 24 hours. Click here to verify your password immediately!')">
                                        🚨 Test Phishing Message
                                    </button>
                                    <button type="button" class="btn btn-outline-warning" onclick="testExample('Congratulations! You have won $5000 cash prize. Click this link to claim your reward now!')">
                                        ⚠️ Test Prize Scam
                                    </button>
                                </div>
                            </div>
                        </div>
                        
                        <div class="mt-5 border-top pt-3">
                            <a href="/health" class="btn btn-success me-2">Check Health</a>
                            <a href="/stats" class="btn btn-info">View Stats</a>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        // Handle form submission
        document.getElementById('messageForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const messageInput = document.getElementById('messageInput');
            const message = messageInput.value.trim();
            
            if (!message) {
                alert('Please enter a message to analyze');
                return;
            }
            
            showResult('🔄 Analyzing message, please wait...', 'alert-info');
            
            try {
                const response = await fetch('/detect', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: message, user: 'web-user' })
                });
                
                const result = await response.json();
                
                if (response.ok) {
                    displayResult(result, message);
                } else {
                    showResult('❌ Error: ' + (result.error || 'Unknown error'), 'alert-danger');
                }
            } catch (error) {
                showResult('❌ Connection error. Server may not be running.', 'alert-danger');
            }
        });
        
        // Quick test function
        function testExample(message) {
            document.getElementById('messageInput').value = message;
            document.getElementById('messageForm').dispatchEvent(new Event('submit'));
        }
        
        // Display detection results
        function displayResult(result, message) {
            let alertClass, icon, title, details;
            
            if (result.label === 'phishing') {
                alertClass = 'alert-danger';
                icon = '🚨';
                title = 'PHISHING DETECTED!';
                details = `
                    <div class="mt-3">
                        <strong>Risk Score:</strong> ${Math.round(result.score * 100)}%<br>
                        ${result.reasons && result.reasons.length > 0 ? 
                            '<strong>Detection Reasons:</strong> ' + result.reasons[0] + '<br>' : ''}
                        <div class="mt-2 p-2 bg-light rounded">
                            <small><strong>⚠️ WARNING:</strong> This message appears to be a phishing attempt. 
                            Do not click any links or provide personal information!</small>
                        </div>
                    </div>
                `;
            } else {
                alertClass = 'alert-success';
                icon = '✅';
                title = 'Message Appears Safe';
                details = `
                    <div class="mt-3">
                        <strong>Risk Score:</strong> ${Math.round(result.score * 100)}%<br>
                        <small>No phishing indicators detected in this message.</small>
                    </div>
                `;
            }
            
            const content = `
                <div class="d-flex align-items-start">
                    <div style="font-size: 2rem; margin-right: 15px;">${icon}</div>
                    <div class="flex-grow-1">
                        <h5 class="mb-3">${title}</h5>
                        <p><strong>Analyzed Message:</strong><br>"${message}"</p>
                        ${details}
                    </div>
                </div>
            `;
            
            showResult(content, alertClass);
        }
        
        // Show result
        function showResult(content, alertClass) {
            const resultsDiv = document.getElementById('results');
            const alertDiv = document.getElementById('resultAlert');
            
            alertDiv.className = 'alert ' + alertClass;
            alertDiv.innerHTML = content;
            resultsDiv.style.display = 'block';
            
            resultsDiv.scrollIntoView({ behavior: 'smooth' });
        }
    </script>
</body>
</html>'''

@app.route("/detect", methods=["POST"])
def detect():
    """Detect phishing in a message"""
    try:
        data = request.json
        if not data or 'message' not in data:
            return jsonify({"error": "Message is required"}), 400
        
        message = data.get("message", "")
        user = data.get("user", "anonymous")
        
        result = phish_guard_service.detect_phishing(message, user)
        return jsonify(result)
        
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500

@app.route("/stats", methods=["GET"])
def stats():
    """Get detection statistics"""
    try:
        stats_data = phish_guard_service.get_stats()
        return jsonify(stats_data)
    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500

@app.route("/debug", methods=["GET"])
def debug():
    """Debug route to check what home() returns"""
    home_content = home()
    return jsonify({
        "length": len(home_content),
        "has_messageForm": "messageForm" in home_content,
        "has_messageInput": "messageInput" in home_content,
        "has_script": "<script>" in home_content,
        "first_100_chars": home_content[:100],
        "last_100_chars": home_content[-100:]
    })

@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "Phish Chat Guard API", 
        "version": "1.0.0",
        "detection_engine": "active"
    })

if __name__ == "__main__":
    print("Phish Chat Guard API Server Started")
    app.run(host="0.0.0.0", port=5000, debug=False)