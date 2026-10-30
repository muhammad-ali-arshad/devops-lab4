import unittest
from unittest.mock import patch

from app import app
from news_sources import source_for
from summarizer import summarize


class ContractTests(unittest.TestCase):
    def test_assigned_source(self):
        self.assertEqual(source_for("FA23-BDS-024").name, "ProPakistani")

    def test_api_contract(self):
        with patch("app.fetch_first_article", return_value=("https://propakistani.pk/story", "Technology news continues to shape the market. A new technology project was announced today. Analysts expect the project to grow rapidly.")):
            response = app.test_client().get("/get?keyword=technology")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(set(response.json), {"registration", "newssource", "keyword", "url", "summary"})
        self.assertEqual(response.json["registration"], "FA23-BDS-024")
        self.assertEqual(response.json["newssource"], "ProPakistani")
        self.assertTrue(response.json["summary"])

    def test_missing_keyword(self):
        self.assertEqual(app.test_client().get("/get").status_code, 400)


if __name__ == "__main__":
    unittest.main()
