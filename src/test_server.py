from flask import Flask
app = Flask(__name__)

@app.route("/")
def home():
    return "TEST: This is a simple test response"

@app.route("/test")  
def test():
    # Return exactly the same content as the current home() function
    from phishing_module.phishing_service import PhishGuardService
    service = PhishGuardService()
    
    # This should be the exact same HTML content
    return '''
<!DOCTYPE html>
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
                        <p class="lead">Testing Interactive Interface</p>
                        
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
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
    '''

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=False)