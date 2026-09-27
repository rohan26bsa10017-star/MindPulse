"""
Unit tests for the sentiment analysis and emotion classification engine.
"""

import unittest
from src.analytics.sentiment import SentimentAnalyzer


class TestSentimentAnalyzer(unittest.TestCase):

    def test_positive_sentiment(self):
        text = "I felt very happy and grateful today because everything went wonderful."
        score, emotion, tags = SentimentAnalyzer.analyze(text)
        self.assertGreater(score, 0.3)
        self.assertEqual(emotion, "Joy")
        self.assertTrue("happy" in tags or "grateful" in tags or "wonderful" in tags)

    def test_negative_sentiment(self):
        text = "I am deeply stressed, overwhelmed, and completely exhausted by exams."
        score, emotion, tags = SentimentAnalyzer.analyze(text)
        self.assertLess(score, -0.3)
        self.assertEqual(emotion, "Stress")
        self.assertTrue("stressed" in tags or "overwhelmed" in tags or "exhausted" in tags)

    def test_negation_handling(self):
        # "not happy" should not be classified as positive joy
        text = "I was not happy with the test results."
        score, emotion, _ = SentimentAnalyzer.analyze(text)
        self.assertLessEqual(score, 0.0)

    def test_calm_emotion(self):
        text = "Spent the afternoon in a peaceful and serene park feeling calm and relaxed."
        score, emotion, tags = SentimentAnalyzer.analyze(text)
        self.assertGreater(score, 0.2)
        self.assertEqual(emotion, "Calm")

    def test_empty_or_neutral_text(self):
        score, emotion, tags = SentimentAnalyzer.analyze("")
        self.assertEqual(score, 0.0)
        self.assertEqual(emotion, "Neutral")
        self.assertEqual(tags, [])


if __name__ == "__main__":
    unittest.main()
