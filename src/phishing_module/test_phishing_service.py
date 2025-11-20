import unittest
from unittest.mock import MagicMock, patch

from phishing_module.phishing_service import PhishGuardService


class TestPhishGuardService(unittest.TestCase):
    def setUp(self):
        self.sample_message = "This is a test"
        self.mock_detection = {
            "label": "clean",
            "score": 0.0,
            "reasons": []
        }

    @patch("phishing_module.phishing_service.MongoClient")
    @patch("phishing_module.phishing_service.detect_phishing_content")
    def test_detect_phishing_saves_result(self, mock_detector, mock_client):
        mock_detector.return_value = self.mock_detection

        collection_mock = MagicMock()
        db_mock = MagicMock()
        db_mock.__getitem__.return_value = collection_mock
        client_mock = MagicMock()
        client_mock.__getitem__.return_value = db_mock
        mock_client.return_value = client_mock

        service = PhishGuardService()
        result = service.detect_phishing(self.sample_message, user="tester")

        mock_detector.assert_called_once_with(self.sample_message)
        collection_mock.insert_one.assert_called_once()
        inserted_doc = collection_mock.insert_one.call_args[0][0]
        self.assertEqual(inserted_doc["user"], "tester")
        self.assertEqual(inserted_doc["message"], self.sample_message)
        self.assertEqual(result, self.mock_detection)

    def test_detect_phishing_empty_message(self):
        service = PhishGuardService.__new__(PhishGuardService)
        service.messages_collection = MagicMock()

        with self.assertRaises(ValueError) as ctx:
            PhishGuardService.detect_phishing(service, "")
        self.assertEqual(str(ctx.exception), PhishGuardService.empty_message)

    @patch("phishing_module.phishing_service.MongoClient")
    def test_get_stats_returns_counts(self, mock_client):
        collection_mock = MagicMock()
        counts = {
            "total": 10,
            "phishing": 4,
            "clean": 6
        }
        collection_mock.count_documents.side_effect = [
            counts["total"], counts["phishing"], counts["clean"]
        ]

        db_mock = MagicMock()
        db_mock.__getitem__.return_value = collection_mock
        client_mock = MagicMock()
        client_mock.__getitem__.return_value = db_mock
        mock_client.return_value = client_mock

        service = PhishGuardService()
        stats = service.get_stats()

        self.assertEqual(stats["total_messages"], counts["total"])
        self.assertEqual(stats["total_phishing"], counts["phishing"])
        self.assertEqual(stats["total_clean"], counts["clean"])
        self.assertEqual(stats["phishing_percentage"], 40.0)


if __name__ == "__main__":
    unittest.main()
