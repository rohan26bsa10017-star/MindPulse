"""
Unit tests for psychometric clinical scales (PSS-10, PHQ-9, GAD-7) and CopingRecommender.
"""

import unittest
from src.core.exceptions import ValidationError, AssessmentNotFoundError
from src.assessments.clinical_scales import (
    PSS10Scale,
    PHQ9Scale,
    GAD7Scale,
    get_scale_by_code,
)
from src.assessments.recommendations import CopingRecommender


class TestAssessments(unittest.TestCase):

    def test_pss10_reverse_scoring(self):
        # All 0s: items 4, 5, 7, 8 (indices 3, 4, 6, 7) reverse to 4 each -> total = 16 (Moderate Stress)
        responses = [0] * 10
        total, severity, _ = PSS10Scale.score_responses(responses)
        self.assertEqual(total, 16)
        self.assertEqual(severity, "Moderate Stress")

        # Optimal resilience: high confidence on reverse items (4), 0 on distress items -> total = 0
        responses_best = [0, 0, 0, 4, 4, 0, 4, 4, 0, 0]
        total_best, severity_best, _ = PSS10Scale.score_responses(responses_best)
        self.assertEqual(total_best, 0)
        self.assertEqual(severity_best, "Low Stress")

    def test_phq9_scoring(self):
        # Low score
        total, severity, _ = PHQ9Scale.score_responses([0] * 9)
        self.assertEqual(total, 0)
        self.assertEqual(severity, "Minimal / None")

        # Severe score
        total, severity, _ = PHQ9Scale.score_responses([3] * 9)
        self.assertEqual(total, 27)
        self.assertEqual(severity, "Severe Depression")

    def test_gad7_scoring(self):
        # Mild anxiety (total = 7)
        responses = [1] * 7
        total, severity, _ = GAD7Scale.score_responses(responses)
        self.assertEqual(total, 7)
        self.assertEqual(severity, "Mild Anxiety")

    def test_invalid_lengths_and_values(self):
        with self.assertRaises(ValidationError):
            PSS10Scale.score_responses([1, 2, 3])  # too short

        with self.assertRaises(ValidationError):
            PHQ9Scale.score_responses([5] * 9)  # out of bound 5

    def test_factory_and_recommender(self):
        scale = get_scale_by_code("GAD-7")
        self.assertEqual(scale.code, "GAD-7")

        with self.assertRaises(AssessmentNotFoundError):
            get_scale_by_code("NON_EXISTENT")

        tech = CopingRecommender.get_technique("box_breathing")
        self.assertEqual(tech["duration"], "4 Minutes")
        self.assertTrue(len(CopingRecommender.get_crisis_resources()) > 0)


if __name__ == "__main__":
    unittest.main()
