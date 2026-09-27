"""
MindPulse: Clinical & Psychometric Assessment Scales
Implements validated psychometric instruments: PSS-10, PHQ-9, and GAD-7.
"""

from typing import List, Dict, Tuple
from src.core.exceptions import ValidationError, AssessmentNotFoundError


class PsychometricScale:
    """Base definition for standardized self-report mental health scales."""
    name: str
    code: str
    max_score: int
    questions: List[str]

    @classmethod
    def score_responses(cls, responses: List[int]) -> Tuple[int, str, str]:
        """Calculates raw score, severity tier, and clinical recommendation."""
        raise NotImplementedError


class PSS10Scale(PsychometricScale):
    """
    Perceived Stress Scale (PSS-10) by Sheldon Cohen.
    Standardized tool measuring degree of appraised stress in daily situations.
    Items 4, 5, 7, and 8 are reverse scored.
    """
    name = "Perceived Stress Scale (PSS-10)"
    code = "PSS-10"
    max_score = 40
    reverse_indices = {3, 4, 6, 7}  # 0-indexed corresponding to items 4, 5, 7, 8

    questions = [
        "How often have you been upset because of something that happened unexpectedly?",
        "How often have you felt that you were unable to control the important things in your life?",
        "How often have you felt nervous and stressed?",
        "How often have you felt confident about your ability to handle personal problems? (Reverse)",
        "How often have you felt that things were going your way? (Reverse)",
        "How often have you found that you could not cope with all the things you had to do?",
        "How often have you been able to control irritations in your life? (Reverse)",
        "How often have you felt that you were on top of things? (Reverse)",
        "How often have you been angered because of things that happened outside of your control?",
        "How often have you felt difficulties were piling up so high that you could not overcome them?"
    ]

    options = [
        "0 - Never",
        "1 - Almost Never",
        "2 - Sometimes",
        "3 - Fairly Often",
        "4 - Very Often"
    ]

    @classmethod
    def score_responses(cls, responses: List[int]) -> Tuple[int, str, str]:
        if len(responses) != 10:
            raise ValidationError(f"PSS-10 requires exactly 10 responses, got {len(responses)}.")

        total = 0
        for i, val in enumerate(responses):
            if val < 0 or val > 4:
                raise ValidationError(f"Score for item {i+1} must be between 0 and 4.")
            if i in cls.reverse_indices:
                total += (4 - val)
            else:
                total += val

        if total <= 13:
            severity = "Low Stress"
            rec = "Your stress levels are within healthy resilience limits. Maintain good sleep, study-life balance, and routine exercise."
        elif total <= 26:
            severity = "Moderate Stress"
            rec = "You are experiencing moderate stress. Consider structured breaks, daily grounding exercises, and delegating or prioritizing academic tasks."
        else:
            severity = "High Stress"
            rec = "Elevated stress detected. Actively reduce non-essential commitments, practice guided box breathing, and connect with university counseling services."

        return total, severity, rec


class PHQ9Scale(PsychometricScale):
    """
    Patient Health Questionnaire-9 (PHQ-9) for depression symptom screening.
    Validated clinical scoring system (Kroenke et al., 2001).
    """
    name = "Patient Health Questionnaire (PHQ-9)"
    code = "PHQ-9"
    max_score = 27

    questions = [
        "Little interest or pleasure in doing things?",
        "Feeling down, depressed, or hopeless?",
        "Trouble falling or staying asleep, or sleeping too much?",
        "Feeling tired or having little energy?",
        "Poor appetite or overeating?",
        "Feeling bad about yourself — or that you are a failure?",
        "Trouble concentrating on things, such as reading or assignments?",
        "Moving or speaking noticeably slowly, or being fidgety/restless?",
        "Thoughts that you would be better off dead or hurting yourself?"
    ]

    options = [
        "0 - Not at all",
        "1 - Several days",
        "2 - More than half the days",
        "3 - Nearly every day"
    ]

    @classmethod
    def score_responses(cls, responses: List[int]) -> Tuple[int, str, str]:
        if len(responses) != 9:
            raise ValidationError(f"PHQ-9 requires exactly 9 responses, got {len(responses)}.")

        total = sum(responses)
        for i, val in enumerate(responses):
            if val < 0 or val > 3:
                raise ValidationError(f"Score for item {i+1} must be between 0 and 3.")

        if total <= 4:
            severity = "Minimal / None"
            rec = "Sub-clinical range. Continue engaging in positive social interactions, hobbies, and balanced academic pursuits."
        elif total <= 9:
            severity = "Mild Depression"
            rec = "Mild emotional distress. Prioritize regular physical activity, sunlight, sleep hygiene, and expressive journaling."
        elif total <= 14:
            severity = "Moderate Depression"
            rec = "Moderate depressive symptoms. Evidence suggests benefits from structured CBT reflection, behavioral activation, and peer support."
        elif total <= 19:
            severity = "Moderately Severe Depression"
            rec = "Considerable depressive burden. Strongly recommended to consult a campus healthcare counselor or mental health professional."
        else:
            severity = "Severe Depression"
            rec = "Critical symptom severity. Immediate clinical consultation advised. Please reach out to student welfare services or national crisis helplines."

        return total, severity, rec


class GAD7Scale(PsychometricScale):
    """
    Generalized Anxiety Disorder 7-item (GAD-7) scale (Spitzer et al., 2006).
    Standardized screening tool for generalized anxiety severity.
    """
    name = "Generalized Anxiety Disorder (GAD-7)"
    code = "GAD-7"
    max_score = 21

    questions = [
        "Feeling nervous, anxious, or on edge?",
        "Not being able to stop or control worrying?",
        "Worrying too much about different things?",
        "Trouble relaxing?",
        "Being so restless that it's hard to sit still?",
        "Becoming easily annoyed or irritable?",
        "Feeling afraid, as if something awful might happen?"
    ]

    options = [
        "0 - Not at all",
        "1 - Several days",
        "2 - More than half the days",
        "3 - Nearly every day"
    ]

    @classmethod
    def score_responses(cls, responses: List[int]) -> Tuple[int, str, str]:
        if len(responses) != 7:
            raise ValidationError(f"GAD-7 requires exactly 7 responses, got {len(responses)}.")

        total = sum(responses)
        for i, val in enumerate(responses):
            if val < 0 or val > 3:
                raise ValidationError(f"Score for item {i+1} must be between 0 and 3.")

        if total <= 4:
            severity = "Minimal Anxiety"
            rec = "Anxiety levels are within normal physiological bounds. Practice regular mindfulness to sustain resilience."
        elif total <= 9:
            severity = "Mild Anxiety"
            rec = "Mild anxiety detected. Cognitive grounding (5-4-3-2-1 technique) and limiting caffeine intake can help."
        elif total <= 14:
            severity = "Moderate Anxiety"
            rec = "Moderate anxiety level. Scheduled 'worry-time', diaphragmatic breathing exercises, and reduced screen exposure are recommended."
        else:
            severity = "Severe Anxiety"
            rec = "Clinically significant anxiety. Seeking guidance from a certified counselor or psychologist is highly recommended."

        return total, severity, rec


def get_scale_by_code(code: str) -> PsychometricScale:
    """Factory retrieving the requested scale class."""
    scales = {
        "PSS-10": PSS10Scale,
        "PHQ-9": PHQ9Scale,
        "GAD-7": GAD7Scale
    }
    if code not in scales:
        raise AssessmentNotFoundError(f"Unknown assessment scale code '{code}'. Supported: {list(scales.keys())}")
    return scales[code]
