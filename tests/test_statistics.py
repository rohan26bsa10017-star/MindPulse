"""
Unit tests for statistical calculations, Pearson correlation, and Burnout Risk Index.
"""

import unittest
from src.core.models import MoodLog
from src.analytics.statistics import StatisticsEngine


class TestStatisticsEngine(unittest.TestCase):

    def test_mean_and_std_dev(self):
        values = [2.0, 4.0, 4.0, 4.0, 5.0, 5.0, 7.0, 9.0]
        mean = StatisticsEngine.calculate_mean(values)
        std_dev = StatisticsEngine.calculate_std_dev(values)
        self.assertEqual(mean, 5.0)
        self.assertAlmostEqual(std_dev, 2.0, places=2)

    def test_pearson_correlation(self):
        # Perfect positive correlation
        x = [1.0, 2.0, 3.0, 4.0, 5.0]
        y = [2.0, 4.0, 6.0, 8.0, 10.0]
        r = StatisticsEngine.pearson_correlation(x, y)
        self.assertEqual(r, 1.0)

        # Perfect negative correlation
        y_neg = [10.0, 8.0, 6.0, 4.0, 2.0]
        r_neg = StatisticsEngine.pearson_correlation(x, y_neg)
        self.assertEqual(r_neg, -1.0)

    def test_burnout_risk_healthy_vs_distressed(self):
        # Healthy logs (8h sleep, 4h study, 30m exercise, 8/10 mood, 4/5 energy)
        healthy_logs = [
            MoodLog(None, 1, f"2026-09-0{i}", 8, "Good", 4, 8.0, 4.0, 30, None)
            for i in range(1, 8)
        ]
        score, level, factors = StatisticsEngine.calculate_burnout_risk(healthy_logs)
        self.assertLess(score, 25.0)
        self.assertIn("Healthy", level)

        # Distressed logs (4h sleep, 9h study, 0m exercise, 3/10 mood, 1/5 energy)
        distressed_logs = [
            MoodLog(None, 1, f"2026-09-0{i}", 3, "Exhausted", 1, 4.0, 9.0, 0, None)
            for i in range(1, 8)
        ]
        score_bad, level_bad, factors_bad = StatisticsEngine.calculate_burnout_risk(distressed_logs)
        self.assertGreater(score_bad, 70.0)
        self.assertTrue("Risk" in level_bad)
        self.assertTrue(len(factors_bad) >= 3)


if __name__ == "__main__":
    unittest.main()
