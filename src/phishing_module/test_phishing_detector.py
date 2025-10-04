import unittest
from phishing_module.phishing_detector import detect_phishing_content, analyze_suspicious_urls, analyze_phishing_patterns


class TestPhishChatGuardDetector(unittest.TestCase):
    
    def test_clean_message(self):
        """Test that clean messages are classified correctly"""
        result = detect_phishing_content("Hi! How are you doing today?")
        self.assertEqual(result["label"], "clean")
        self.assertEqual(result["score"], 0.0)
        self.assertEqual(result["reasons"], [])
    
    def test_phishing_keywords(self):
        """Test detection of phishing keywords"""
        result = detect_phishing_content("Please login to verify your account password")
        self.assertEqual(result["label"], "phishing")
        self.assertGreater(result["score"], 0.4)
        self.assertIn("Suspicious keywords detected", result["reasons"][0])
    
    def test_ip_based_url(self):
        """Test detection of IP-based URLs"""
        result = detect_phishing_content("Click here: http://192.168.1.1/login")
        self.assertEqual(result["label"], "phishing")
        self.assertGreater(result["score"], 0.4)
        self.assertTrue(any("IP-based URL" in reason for reason in result["reasons"]))
    
    def test_hyphenated_domain(self):
        """Test detection of hyphenated domains"""
        result = detect_phishing_content("Visit paypal-secure.com for verification")
        self.assertGreater(result["score"], 0.0)
        self.assertTrue(any("Hyphenated domain" in reason for reason in result["reasons"]))
    
    def test_urgency_patterns(self):
        """Test detection of urgency patterns"""
        result = detect_phishing_content("URGENT!!! Your account will be SUSPENDED!!!")
        self.assertGreater(result["score"], 0.0)
        self.assertTrue(any("exclamation marks" in reason for reason in result["reasons"]))
    
    def test_combined_indicators(self):
        """Test high score with multiple indicators"""
        result = detect_phishing_content("URGENT! Your bank account password needs verification. Click http://192.168.1.1/bank-login")
        self.assertEqual(result["label"], "phishing")
        self.assertGreater(result["score"], 0.6)
        self.assertGreater(len(result["reasons"]), 1)
    
    def test_empty_message(self):
        """Test empty message handling"""
        result = detect_phishing_content("")
        self.assertEqual(result["label"], "clean")
        self.assertEqual(result["score"], 0.0)
    
    def test_suspicious_url_function(self):
        """Test the URL analysis function directly"""
        urls_with_ip = analyze_suspicious_urls("Visit http://192.168.1.1/test")
        self.assertGreater(len(urls_with_ip), 0)
        
        urls_with_hyphens = analyze_suspicious_urls("Visit http://fake-bank.com/login")
        self.assertGreater(len(urls_with_hyphens), 0)
    
    def test_suspicious_patterns_function(self):
        """Test the pattern analysis function directly"""
        patterns = analyze_phishing_patterns("CALL NOW!!! URGENT!!!")
        self.assertGreater(len(patterns), 0)
        
        patterns_caps = analyze_phishing_patterns("YOUR ACCOUNT WILL BE CLOSED")
        self.assertGreater(len(patterns_caps), 0)


if __name__ == '__main__':
    unittest.main()