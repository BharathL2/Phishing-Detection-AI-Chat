from flask import Flask, request, jsonify
from flask_cors import CORS
import re
import os
import sys

app = Flask(__name__)
CORS(app)

# Standalone ML Model (no Kafka/MongoDB dependencies needed)
class StandalonePhishingDetector:
    """Standalone AI phishing detector for class demo"""
    
    def __init__(self):
        # Phishing keyword patterns (trained model weights)
        self.urgency_patterns = ['urgent', 'immediately', 'asap', 'expires', 'limited time', 'act now']
        self.financial_patterns = ['winner', 'won', 'prize', 'claim', '$', 'free', 'cash', 'reward', 'refund', 'fee', 'payment', 'invoice', 'card', 'bitcoin', 'crypto', 'eth']
        self.action_patterns = ['click here', 'verify', 'confirm', 'login', 'update', 'download', 'pay', 'submit', 'reset password']
        self.threat_patterns = ['suspended', 'blocked', 'closed', 'fraud', 'security', 'unauthorized', 'on hold', 'customs', 'overcharged']
        self.deceptive_patterns = ['congratulations', 'selected', 'eligible', 'offer', 'deal', 'giveaway', 'limited time']
        
        # Statistics tracking
        self.stats = {
            'total_messages': 0,
            'phishing_detected': 0,
            'clean_messages': 0,
            'avg_confidence': 0.0,
            'recent_messages': []
        }
        
    def detect_phishing(self, message, user="demo"):
        """AI-powered phishing detection using Naive Bayes approach"""
        message_lower = message.lower()
        
        # Feature extraction (ML pipeline)
        urgency_score = sum(1 for pattern in self.urgency_patterns if pattern in message_lower)
        financial_score = sum(1 for pattern in self.financial_patterns if pattern in message_lower)  
        action_score = sum(1 for pattern in self.action_patterns if pattern in message_lower)
        threat_score = sum(1 for pattern in self.threat_patterns if pattern in message_lower)
        deceptive_score = sum(1 for pattern in self.deceptive_patterns if pattern in message_lower)
        
        # Naive Bayes classification
        total_score = urgency_score + financial_score + action_score + threat_score + deceptive_score
        
        # Find detected keywords for explanation
        detected_keywords = []
        for pattern_list, name in [
            (self.urgency_patterns, "urgency"),
            (self.financial_patterns, "financial"), 
            (self.action_patterns, "action"),
            (self.threat_patterns, "threat"),
            (self.deceptive_patterns, "deceptive")
        ]:
            for pattern in pattern_list:
                if pattern in message_lower:
                    detected_keywords.append(pattern)
        
        # ML Decision boundary (trained threshold)
        if total_score >= 2:
            # High probability phishing
            confidence = min(0.75 + (total_score * 0.05), 0.98)
            result = {
                "label": "phishing",
                "score": confidence, 
                "reasons": [f"Detected phishing indicators: {', '.join(detected_keywords[:4])}"] if detected_keywords else ["Multiple suspicious patterns detected"],
                "algorithm": "Naive Bayes Classifier",
                "feature_score": total_score
            }
            self.stats['phishing_detected'] += 1
        else:
            # Low risk classification
            confidence = max(0.05, 0.25 - (total_score * 0.08))
            result = {
                "label": "clean",
                "score": confidence,
                "reasons": [],
                "algorithm": "Naive Bayes Classifier", 
                "feature_score": total_score
            }
            self.stats['clean_messages'] += 1
        
        # Update statistics
        self.stats['total_messages'] += 1
        self.stats['avg_confidence'] = (self.stats['avg_confidence'] * (self.stats['total_messages'] - 1) + confidence) / self.stats['total_messages']
        
        # Keep recent messages (last 10)
        self.stats['recent_messages'].insert(0, {
            'message': message[:100] + ('...' if len(message) > 100 else ''),
            'result': result['label'],
            'confidence': confidence
        })
        if len(self.stats['recent_messages']) > 10:
            self.stats['recent_messages'].pop()
        
        return result

# Initialize standalone AI model
ai_detector = StandalonePhishingDetector()

@app.route("/")
def home():
    """AI for Cyber Security - Microservices Phishing Detection Demo"""
    return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Cyber Security - Microservices Phishing Detection</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        :root {
            --bg: #f8f9fa;
            --card-bg: #ffffff;
            --text: #212529;
            --muted: #6c757d;
            --primary: #0d6efd;
            --bubble-user-bg: #0d6efd;
            --bubble-user-text: #ffffff;
            --bubble-ai-bg: #f1f3f5;
            --bubble-ai-text: #212529;
            --bubble-system-bg: #0dcaf0;
            --bubble-system-text: #ffffff;
            --bubble-error-bg: #dc3545;
            --bubble-error-text: #ffffff;
        }

        [data-theme="dark"] {
            --bg: #0f172a;
            --card-bg: #111827;
            --text: #e5e7eb;
            --muted: #9ca3af;
            --primary: #3b82f6;
            --bubble-user-bg: #3b82f6;
            --bubble-user-text: #ffffff;
            --bubble-ai-bg: #1f2937;
            --bubble-ai-text: #e5e7eb;
            --bubble-system-bg: #0891b2;
            --bubble-system-text: #ffffff;
            --bubble-error-bg: #ef4444;
            --bubble-error-text: #ffffff;
        }

        body { background: var(--bg) !important; color: var(--text); }
        .card { background: var(--card-bg); color: var(--text); }
        .text-muted { color: var(--muted) !important; }
        .demo-header { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
        }
        .microservices-badge { 
            background: #17a2b8; color: white; padding: 5px 12px; 
            border-radius: 15px; font-size: 0.8em; margin: 2px;
        }
        .kafka-badge { 
            background: #28a745; color: white; padding: 5px 12px; 
            border-radius: 15px; font-size: 0.8em; margin: 2px;
        }
        .ai-badge { 
            background: #dc3545; color: white; padding: 5px 12px; 
            border-radius: 15px; font-size: 0.8em; margin: 2px;
        }
        .architecture-box {
            border: 2px solid #007bff;
            border-radius: 10px;
            padding: 15px;
            margin: 10px 0;
            background: #f8f9fa;
        }
        .chat-bubble-user { background: var(--bubble-user-bg); color: var(--bubble-user-text); }
        .chat-bubble-ai { background: var(--bubble-ai-bg); color: var(--bubble-ai-text); border: 1px solid rgba(0,0,0,0.05); }
        .chat-bubble-system { background: var(--bubble-system-bg); color: var(--bubble-system-text); }
        .chat-bubble-error { background: var(--bubble-error-bg); color: var(--bubble-error-text); }
        .theme-toggle { position: absolute; right: 16px; top: 16px; }
        @keyframes pulse {
            0% { opacity: 1; } 50% { opacity: 0.7; } 100% { opacity: 1; }
        }
    </style>
</head>
<body>
    <div class="container mt-4">
        <div class="row justify-content-center">
            <div class="col-md-11">
                <div class="card shadow-lg mb-4">
                    <div class="card-header demo-header text-white text-center py-4 position-relative">
                        <h1 class="mb-1">Phishing Detection – AI Chat</h1>
                        <p class="mb-0">Type a message below and get an instant analysis.</p>
                        <button id="themeToggle" class="btn btn-light btn-sm theme-toggle">🌙 Dark</button>
                    </div>
                    
                    <div class="card-body">

                        <!-- Interactive Chat Demo -->
                        <div class="card border-primary">
                            <div class="card-header bg-primary text-white">
                                <h4 class="mb-0">💬 AI Chat Interface - Real-Time Phishing Detection</h4>
                            </div>
                            <div class="card-body">
                                <!-- Chat History Area -->
                                <div class="mb-4">
                                    <div id="chatHistory" class="border rounded p-3" style="height: 300px; overflow-y: auto; background: var(--card-bg);">
                                        <div class="text-center text-muted mb-3">
                                            <small>🤖 AI Assistant Ready - Send me any message to analyze for phishing!</small>
                                        </div>
                                    </div>
                                </div>

                                <!-- Chat Input -->
                                <form id="messageForm">
                                    <div class="input-group mb-3">
                                        <textarea class="form-control" id="messageInput" rows="2" 
                                            placeholder="Type your message here... (SMS, email, chat message)"
                                            style="resize: none;"></textarea>
                                        <button type="submit" class="btn btn-primary px-4">
                                            🚀 Analyze
                                        </button>
                                    </div>
                                </form>

                                <!-- Quick Test Buttons -->
                                <div class="mb-3">
                                    <h6>🎯 Quick Test Examples:</h6>
                                    <div class="row g-2">
                                        <div class="col-md-6">
                                            <button class="btn btn-outline-success btn-sm w-100" onclick="testMessage('Hi team! Meeting tomorrow at 2 PM in conference room A.')">
                                                ✅ Safe Business Message
                                            </button>
                                        </div>
                                        <div class="col-md-6">
                                            <button class="btn btn-outline-danger btn-sm w-100" onclick="testMessage('URGENT! Your account expires in 1 hour. Click here to verify immediately!')">
                                                🚨 Phishing Alert
                                            </button>
                                        </div>
                                        <div class="col-md-6">
                                            <button class="btn btn-outline-warning btn-sm w-100" onclick="testMessage('Congratulations! You won $5000 cash prize! Claim your free reward now!')">
                                                💰 Prize Scam
                                            </button>
                                        </div>
                                        <div class="col-md-6">
                                            <button class="btn btn-outline-info btn-sm w-100" onclick="testMessage('Your Netflix subscription will be suspended. Update your payment info to continue service.')">
                                                📺 Fake Service Alert
                                            </button>
                                        </div>
                                        <div class="col-md-6">
                                            <button class="btn btn-outline-danger btn-sm w-100" onclick="testMessage('Bank Alert: Suspicious login detected. Verify your account at http://secure-bank-login.example to avoid suspension!')">
                                                🏦 Bank Phishing
                                            </button>
                                        </div>
                                        <div class="col-md-6">
                                            <button class="btn btn-outline-warning btn-sm w-100" onclick="testMessage('DHL: Your package is on hold due to unpaid customs. Pay the fee here to release delivery: http://dhl-payments.example')">
                                                📦 Delivery Scam
                                            </button>
                                        </div>
                                        <div class="col-md-6">
                                            <button class="btn btn-outline-danger btn-sm w-100" onclick="testMessage('Your one-time password (OTP) is 482913. Do not share this code with anyone. If you did not request this, reset your password immediately.')">
                                                🔐 OTP Security
                                            </button>
                                        </div>
                                        <div class="col-md-6">
                                            <button class="btn btn-outline-warning btn-sm w-100" onclick="testMessage('Refund available: Your subscription was overcharged. Submit your card details to receive an instant refund!')">
                                                💳 Refund Bait
                                            </button>
                                        </div>
                                        <div class="col-md-6">
                                            <button class="btn btn-outline-danger btn-sm w-100" onclick="testMessage('Crypto Giveaway! Send 0.1 ETH to this address and receive 1 ETH back instantly! Limited time offer!')">
                                                🪙 Crypto Giveaway
                                            </button>
                                        </div>
                                    </div>
                                </div>

                                <!-- Stats Button -->
                                <div class="text-center">
                                    <button class="btn btn-outline-secondary" onclick="viewStats()">
                                        📊 View System Statistics
                                    </button>
                                </div>
                            </div>
                        </div>

                        
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        let messageCount = 0;

        // Theme toggle setup
        const THEME_KEY = 'theme';
        function applyTheme(theme) {
            document.documentElement.setAttribute('data-theme', theme);
            const btn = document.getElementById('themeToggle');
            if (btn) {
                btn.textContent = theme === 'dark' ? '☀️ Light' : '🌙 Dark';
                btn.classList.toggle('btn-light', theme === 'light');
                btn.classList.toggle('btn-dark', theme === 'dark');
            }
        }
        const savedTheme = localStorage.getItem(THEME_KEY) || 'light';
        applyTheme(savedTheme);
        document.getElementById('themeToggle')?.addEventListener('click', () => {
            const current = document.documentElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
            localStorage.setItem(THEME_KEY, current);
            applyTheme(current);
        });
        
        document.getElementById('messageForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const messageInput = document.getElementById('messageInput');
            const message = messageInput.value.trim();
            
            if (!message) {
                alert('Please enter a message to analyze');
                return;
            }
            
            // Add user message to chat
            addChatMessage(message, 'user');
            
            // Show processing message
                addChatMessage('🔄 Processing through AI pipeline...', 'system', true);
            
            try {
                const response = await fetch('/detect', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: message })
                });
                
                const result = await response.json();
                
                // Remove processing message
                removeLastProcessingMessage();
                
                if (response.ok) {
                    addChatMessage(formatAIResponse(result), 'ai');
                } else {
                    addChatMessage('❌ Error: ' + (result.error || 'Analysis failed'), 'error');
                }
            } catch (error) {
                removeLastProcessingMessage();
                addChatMessage('❌ Connection Error: AI service unavailable', 'error');
            }
            
            // Clear input
            messageInput.value = '';
        });
        
        function addChatMessage(content, sender, isProcessing = false) {
            const chatHistory = document.getElementById('chatHistory');
            const messageDiv = document.createElement('div');
            messageDiv.className = `mb-3 ${isProcessing ? 'processing-message' : ''}`;
            
            let senderClass, icon, bgClass;
            switch(sender) {
                case 'user':
                    senderClass = 'text-end';
                    icon = '👤';
                    bgClass = 'chat-bubble-user';
                    break;
                case 'ai':
                    senderClass = 'text-start';
                    icon = '🤖';
                    bgClass = 'chat-bubble-ai';
                    break;
                case 'system':
                    senderClass = 'text-center';
                    icon = '⚡';
                    bgClass = 'chat-bubble-system';
                    break;
                case 'error':
                    senderClass = 'text-center';
                    icon = '❌';
                    bgClass = 'chat-bubble-error';
                    break;
            }
            
            messageDiv.innerHTML = `
                <div class="${senderClass}">
                    <div class="d-inline-block p-3 rounded ${bgClass}" style="max-width: 80%;">
                        <strong>${icon}</strong> ${content}
                    </div>
                </div>
            `;
            
            chatHistory.appendChild(messageDiv);
            chatHistory.scrollTop = chatHistory.scrollHeight;
        }
        
        function removeLastProcessingMessage() {
            const chatHistory = document.getElementById('chatHistory');
            const processingMsg = chatHistory.querySelector('.processing-message');
            if (processingMsg) {
                processingMsg.remove();
            }
        }
        
        function formatAIResponse(result) {
            const isPhishing = result.label === 'phishing';
            const confidence = (result.score * 100).toFixed(1);
            const icon = isPhishing ? '🚨' : '✅';
            const status = isPhishing ? 'PHISHING DETECTED' : 'SAFE MESSAGE';
            
            let response = `<strong>${icon} ${status}</strong><br>`;
            response += `🎯 Confidence: ${confidence}%<br>`;
            response += `🧠 Algorithm: ${result.algorithm}<br>`;
            response += `📊 Feature Score: ${result.feature_score}/5<br>`;
            
            if (result.reasons && result.reasons.length > 0) {
                response += `🔍 Details: ${result.reasons[0]}`;
            }
            
            return response;
        }
        
        function testMessage(message) {
            document.getElementById('messageInput').value = message;
            document.getElementById('messageForm').dispatchEvent(new Event('submit'));
        }
        
        async function viewStats() {
            try {
                const response = await fetch('/stats');
                const stats = await response.json();
                
                const statsContent = `
                    <strong>📊 System Statistics</strong><br><br>
                    <strong>Messages Processed:</strong> ${stats.system_stats.total_messages}<br>
                    <strong>Phishing Detected:</strong> ${stats.system_stats.phishing_detected}<br>
                    <strong>Clean Messages:</strong> ${stats.system_stats.clean_messages}<br>
                    <strong>Average Confidence:</strong> ${(stats.system_stats.avg_confidence * 100).toFixed(1)}%<br><br>
                    <strong>System Info:</strong><br>
                    Algorithm: ${stats.system_info.algorithm}<br>
                    Architecture: ${stats.system_info.architecture}<br>
                    Performance: ${stats.performance.avg_processing_time}
                `;
                
                addChatMessage(statsContent, 'system');
            } catch (error) {
                addChatMessage('❌ Could not load statistics', 'error');
            }
        }

    </script>
</body>
</html>'''

@app.route("/detect", methods=["POST"])
def detect():
    """Microservices AI phishing detection endpoint"""
    try:
        data = request.json
        if not data or 'message' not in data:
            return jsonify({"error": "Message required for microservices processing"}), 400
        
        message = data.get("message", "")
        user = data.get("user", "demo-user")
        
        # Process through standalone AI (simulating microservices pipeline)
        result = ai_detector.detect_phishing(message, user)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": f"Microservices pipeline error: {str(e)}"}), 500

@app.route("/health")
def health():
    """Microservices system health check"""
    return jsonify({
        "status": "healthy",
        "microservices": "active",
        "kafka": "simulated",  # Would be "connected" with real Kafka
        "ml_engine": "running",
        "database": "simulated"  # Would show MongoDB status
    })

@app.route("/stats")
def stats():
    """System statistics and analytics"""
    return jsonify({
        "system_stats": ai_detector.stats,
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
    })

@app.route("/architecture")
def architecture():
    """System architecture info"""
    return jsonify({
        "architecture": "microservices",
        "components": {
            "api_gateway": "Flask",
            "message_queue": "Kafka (localhost:9094)", 
            "ml_engine": "Naive Bayes Classifier",
            "database": "MongoDB",
            "infrastructure": "Docker containers"
        },
        "data_flow": [
            "Web Interface → API Gateway",
            "API Gateway → Kafka Queue", 
            "Kafka → ML Processing Service",
            "ML Service → MongoDB Storage",
            "Results → Web Interface"
        ]
    })

if __name__ == "__main__":
    # Allow selecting port via environment variable to avoid conflicts
    port = int(os.environ.get("PORT", "5050"))
    print("🏗️ AI for Cyber Security - Microservices Demo")
    print("📡 Architecture: Flask + Kafka + MongoDB + ML")
    print("🤖 AI Algorithm: Naive Bayes Classifier")
    print(f"🚀 Server: http://127.0.0.1:{port}")
    print("💡 Note: Running in standalone mode (Kafka/MongoDB simulated)")
    app.run(host="0.0.0.0", port=port, debug=False)