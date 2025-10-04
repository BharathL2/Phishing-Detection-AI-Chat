import os
from datetime import datetime
from pymongo import MongoClient
from .phishing_detector import detect_phishing_content


class PhishGuardService:
    empty_message = 'Empty message!'
    
    def __init__(self):
        # MongoDB setup
        mongo_uri = os.getenv('MONGO_URI', 'mongodb://mongo:27017/')
        self.client = MongoClient(mongo_uri)
        self.db = self.client["phish_chat_guard_db"]
        self.messages_collection = self.db["messages"]

    def detect_phishing(self, message, user="anonymous"):
        """
        Detect phishing in message and save to MongoDB
        Returns detection result
        """
        if not message:
            raise ValueError(self.empty_message)

        # Get phishing detection result
        result = detect_phishing_content(message)
        
        # Save to MongoDB
        entry = {
            "user": user,
            "message": message,
            "timestamp": datetime.utcnow(),
            "label": result["label"],
            "score": result["score"],
            "reasons": result["reasons"]
        }
        
        self.messages_collection.insert_one(entry)
        return result

    def get_stats(self):
        """
        Get statistics from MongoDB
        Returns total messages and phishing count
        """
        total = self.messages_collection.count_documents({})
        phishing = self.messages_collection.count_documents({"label": "phishing"})
        clean = self.messages_collection.count_documents({"label": "clean"})
        
        return {
            "total_messages": total,
            "total_phishing": phishing,
            "total_clean": clean,
            "phishing_percentage": round((phishing / total * 100) if total > 0 else 0, 2)
        }
