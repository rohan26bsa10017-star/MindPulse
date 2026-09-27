"""
MindPulse: Statistical Wellbeing & Habit Correlation Engine
Implements Pearson correlation, moving averages, and Burnout Risk Index (BRI).
"""

import math
from typing import List, Dict, Any, Tuple
from src.core.models import MoodLog


class StatisticsEngine:
    """Provides statistical aggregations, habit correlations, and risk modeling."""

    @staticmethod
    def calculate_mean(values: List[float]) -> float:
        """Computes arithmetic mean."""
        if not values:
            return 0.0
        return sum(values) / len(values)

    @staticmethod
    def calculate_std_dev(values: List[float]) -> float:
        """Computes population standard deviation."""
        if len(values) < 2:
            return 0.0
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return math.sqrt(variance)

    @staticmethod
    def pearson_correlation(x: List[float], y: List[float]) -> float:
        """
        Computes Pearson correlation coefficient (r) between two continuous variables.
        Returns a value between -1.0 (perfect inverse) and +1.0 (perfect direct).
        """
        n = len(x)
        if n != len(y) or n < 2:
            return 0.0

        mean_x = sum(x) / n
        mean_y = sum(y) / n

        numerator = sum((xi - mean_x) * (yi - mean_y) for xi, yi in zip(x, y))
        var_x = sum((xi - mean_x) ** 2 for xi in x)
        var_y = sum((yi - mean_y) ** 2 for yi in y)

        denominator = math.sqrt(var_x * var_y)
        if denominator == 0:
            return 0.0

        r = numerator / denominator
        return round(max(-1.0, min(1.0, r)), 2)

    @classmethod
    def calculate_correlations(cls, logs: List[MoodLog]) -> Dict[str, float]:
        """Calculates key lifestyle-to-mental health correlations."""
        if len(logs) < 3:
            return {
                "sleep_vs_mood": 0.0,
                "study_vs_mood": 0.0,
                "exercise_vs_mood": 0.0,
                "sleep_vs_energy": 0.0,
            }

        sleep = [log.sleep_hours for log in logs]
        study = [log.study_hours for log in logs]
        exercise = [float(log.exercise_minutes) for log in logs]
        mood = [float(log.mood_score) for log in logs]
        energy = [float(log.energy_level) for log in logs]

        return {
            "sleep_vs_mood": cls.pearson_correlation(sleep, mood),
            "study_vs_mood": cls.pearson_correlation(study, mood),
            "exercise_vs_mood": cls.pearson_correlation(exercise, mood),
            "sleep_vs_energy": cls.pearson_correlation(sleep, energy),
        }

    @classmethod
    def calculate_burnout_risk(cls, logs: List[MoodLog]) -> Tuple[float, str, List[str]]:
        """
        Computes the Burnout Risk Index (BRI) as a percentage (0 - 100%)
        based on the user's recent habit and mood history (last 7 logs).
        Returns:
            (bri_score, risk_level, contributing_factors)
        """
        if not logs:
            return 0.0, "Insufficient Data", ["No mood or habit logs recorded yet."]

        recent_logs = logs[-7:]
        avg_mood = cls.calculate_mean([float(l.mood_score) for l in recent_logs])
        avg_sleep = cls.calculate_mean([l.sleep_hours for l in recent_logs])
        avg_study = cls.calculate_mean([l.study_hours for l in recent_logs])
        avg_energy = cls.calculate_mean([float(l.energy_level) for l in recent_logs])
        avg_exercise = cls.calculate_mean([float(l.exercise_minutes) for l in recent_logs])

        penalty = 0.0
        factors = []

        # Sleep deficiency penalty (< 6 hours)
        if avg_sleep < 5.0:
            penalty += 30.0
            factors.append(f"Severe sleep deficit (avg {avg_sleep:.1f} hrs/night)")
        elif avg_sleep < 6.5:
            penalty += 15.0
            factors.append(f"Sub-optimal sleep (avg {avg_sleep:.1f} hrs/night)")

        # Academic overload penalty (> 7 hours of daily intensive study)
        if avg_study > 8.0:
            penalty += 25.0
            factors.append(f"Prolonged high study workload ({avg_study:.1f} hrs/day)")
        elif avg_study > 6.0:
            penalty += 12.0
            factors.append(f"Elevated academic hours ({avg_study:.1f} hrs/day)")

        # Low emotional vitality penalty (mood < 5/10)
        if avg_mood < 4.0:
            penalty += 25.0
            factors.append(f"Persistently low mood state ({avg_mood:.1f}/10)")
        elif avg_mood < 6.0:
            penalty += 12.0
            factors.append(f"Moderate emotional drain ({avg_mood:.1f}/10)")

        # Energy exhaustion penalty (energy < 2.5/5)
        if avg_energy < 2.0:
            penalty += 15.0
            factors.append(f"Severe physical & mental fatigue ({avg_energy:.1f}/5)")
        elif avg_energy < 3.0:
            penalty += 8.0
            factors.append(f"Low vitality levels ({avg_energy:.1f}/5)")

        # Sedentary lifestyle penalty (< 15 mins exercise)
        if avg_exercise < 10.0:
            penalty += 10.0
            factors.append("Minimal physical movement / exercise")

        # Bound score to [0, 100]
        bri_score = round(min(100.0, penalty), 1)

        if bri_score < 25.0:
            level = "Low Risk (Healthy Equilibrium)"
        elif bri_score < 50.0:
            level = "Moderate Risk (Early Strain Detected)"
        elif bri_score < 75.0:
            level = "High Risk (Impending Burnout)"
        else:
            level = "Critical Risk (Severe Exhaustion & Distress)"

        if not factors:
            factors.append("Balanced study, rest, and emotional health patterns.")

        return bri_score, level, factors
