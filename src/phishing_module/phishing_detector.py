import re
from urllib.parse import urlparse
import tldextract

# Phish Chat Guard Detection Keywords
PHISHING_KEYWORDS = [
    "login", "verify", "bank", "password", "click", "urgent", "account", "reset",
    "suspended", "expire", "confirm", "secure", "update", "billing", "payment",
    "winner", "congratulations", "prize", "claim", "limited", "offer", "free"
]

def analyze_suspicious_urls(text):
    """
    Analyze URLs in text for suspicious patterns
    Returns list of reasons if suspicious URLs found
    """
    urls = re.findall(r'(https?://[^\s]+)', text)
    reasons = []
    
    for url in urls:
        try:
            parsed = urlparse(url)
            ext = tldextract.extract(url)
            
            # Check for IP-based URL
            if parsed.hostname and re.match(r'^\d{1,3}(\.\d{1,3}){3}$', parsed.hostname):
                reasons.append(f"IP-based URL detected: {url}")
            
            # Check for too many subdomains (more than 2)
            if ext.subdomain and len(ext.subdomain.split('.')) > 2:
                reasons.append(f"Excessive subdomains in URL: {url}")
            
            # Check for hyphens in domain (common in phishing)
            if ext.domain and '-' in ext.domain:
                reasons.append(f"Hyphenated domain detected: {url}")
                
            # Check for suspicious TLDs
            suspicious_tlds = ['.tk', '.ml', '.ga', '.cf']
            if ext.suffix and any(tld in ext.suffix for tld in suspicious_tlds):
                reasons.append(f"Suspicious TLD in URL: {url}")
                
        except Exception:
            # If URL parsing fails, it might be malformed
            reasons.append(f"Malformed URL detected: {url}")
    
    return reasons

def analyze_phishing_patterns(text):
    """
    Check for additional suspicious patterns beyond keywords
    """
    reasons = []
    
    # Check for multiple exclamation marks (urgency tactics)
    if re.search(r'!{2,}', text):
        reasons.append("Excessive exclamation marks indicating urgency")
    
    # Check for all caps words (shouting/urgency)
    caps_words = re.findall(r'\b[A-Z]{3,}\b', text)
    if len(caps_words) > 2:
        reasons.append(f"Excessive capitalization: {', '.join(caps_words[:3])}")
    
    # Check for phone numbers (often used in scams)
    phone_pattern = r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
    if re.search(phone_pattern, text):
        reasons.append("Phone number detected in message")
    
    return reasons

def detect_phishing_content(message):
    """
    Main phishing detection function
    Returns: dict with label, score, and reasons
    """
    if not message or not message.strip():
        return {
            "label": "clean",
            "score": 0.0,
            "reasons": []
        }
    
    reasons = []
    score = 0.0
    message_lower = message.lower()
    
    # Check for suspicious keywords
    found_keywords = [kw for kw in PHISHING_KEYWORDS if kw in message_lower]
    if found_keywords:
        keyword_score = min(len(found_keywords) * 0.15, 0.6)  # Cap at 0.6
        score += keyword_score
        reasons.append(f"Suspicious keywords detected: {', '.join(found_keywords)}")
    
    # Check for suspicious URLs
    url_reasons = analyze_suspicious_urls(message)
    if url_reasons:
        url_score = min(len(url_reasons) * 0.2, 0.5)  # Cap at 0.5
        score += url_score
        reasons.extend(url_reasons)
    
    # Check for additional suspicious patterns
    pattern_reasons = analyze_phishing_patterns(message)
    if pattern_reasons:
        pattern_score = min(len(pattern_reasons) * 0.1, 0.3)  # Cap at 0.3
        score += pattern_score
        reasons.extend(pattern_reasons)
    
    # Ensure score doesn't exceed 1.0
    score = min(score, 1.0)
    
    # Determine label based on score threshold
    label = "phishing" if score >= 0.4 else "clean"
    
    return {
        "label": label,
        "score": round(score, 2),
        "reasons": reasons
    }