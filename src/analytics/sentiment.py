"""
MindPulse: Lexicon-Based Sentiment Analysis & Emotion Detection Engine
Analyzes journal text polarity, emotional valence, and extracts reflective keywords.
"""

import re
from typing import Tuple, List, Dict


class SentimentAnalyzer:
    """
    Evaluates emotional polarity and dominant psychological sentiment
    using a rule-based psychological lexicon with negation and amplifier modeling.
    """

    # Lexicon mapping words to polarity weights (-2.0 to +2.0)
    POLARITY_LEXICON: Dict[str, float] = {
        # Positive / Joy / Resilience
        "happy": 1.5, "joy": 1.8, "glad": 1.2, "excited": 1.7, "peaceful": 1.6,
        "calm": 1.4, "serene": 1.5, "grateful": 1.8, "thankful": 1.6, "hopeful": 1.5,
        "relieved": 1.3, "accomplished": 1.7, "confident": 1.6, "loved": 1.8, "content": 1.3,
        "productive": 1.4, "energetic": 1.5, "motivated": 1.6, "relaxed": 1.4, "blessed": 1.7,
        "optimistic": 1.5, "proud": 1.6, "thriving": 1.8, "inspired": 1.7, "wonderful": 1.8,
        "good": 1.0, "great": 1.6, "awesome": 1.8, "fantastic": 1.9, "bright": 1.2,
        
        # Negative / Anxiety / Stress
        "anxious": -1.5, "nervous": -1.2, "worried": -1.3, "panicked": -1.9, "stressed": -1.6,
        "overwhelmed": -1.8, "restless": -1.2, "dread": -1.8, "tense": -1.4, "frustrated": -1.5,
        "irritated": -1.3, "angry": -1.7, "furious": -1.9, "annoyed": -1.1, "bitter": -1.4,
        "sad": -1.4, "depressed": -1.9, "hopeless": -2.0, "miserable": -1.8, "lonely": -1.6,
        "exhausted": -1.6, "tired": -1.1, "drained": -1.5, "burnt": -1.6, "burnout": -1.8,
        "afraid": -1.5, "scared": -1.6, "guilty": -1.4, "worthless": -2.0, "unhappy": -1.5,
        "bad": -1.0, "terrible": -1.8, "awful": -1.8, "horrible": -1.9, "failed": -1.7
    }

    # Intensity multipliers
    AMPLIFIERS: Dict[str, float] = {
        "very": 1.5, "extremely": 1.8, "deeply": 1.6, "really": 1.4,
        "so": 1.3, "super": 1.4, "absolutely": 1.7, "completely": 1.6,
        "totally": 1.5, "exceptionally": 1.7
    }

    # Negation indicators
    NEGATIONS = {"not", "never", "no", "hardly", "barely", "scarcely", "cannot", "cant", "wont", "dont", "isnt"}

    # Emotion classification groups
    EMOTION_KEYWORDS: Dict[str, List[str]] = {
        "Joy": ["happy", "joy", "glad", "excited", "grateful", "blessed", "wonderful", "great", "proud", "motivated"],
        "Calm": ["peaceful", "calm", "serene", "relieved", "relaxed", "content", "balanced"],
        "Anxiety": ["anxious", "nervous", "worried", "panicked", "tense", "dread", "scared", "fear"],
        "Stress": ["stressed", "overwhelmed", "exhausted", "drained", "burnt", "burnout", "pressure", "burden"],
        "Sadness": ["sad", "depressed", "hopeless", "miserable", "lonely", "unhappy", "grief", "crying"],
        "Anger": ["angry", "frustrated", "irritated", "furious", "annoyed", "mad", "bitter"]
    }

    @classmethod
    def clean_text(cls, text: str) -> List[str]:
        """Normalizes and tokenizes text into lowercase word tokens."""
        clean = re.sub(r"[^a-zA-Z\s]", " ", text.lower())
        return [word for word in clean.split() if word]

    @classmethod
    def analyze(cls, text: str) -> Tuple[float, str, List[str]]:
        """
        Analyzes the text and returns:
        - normalized_score: float between -1.0 and 1.0
        - dominant_emotion: str (e.g. 'Joy', 'Stress', 'Anxiety', 'Neutral')
        - keywords: list of reflective topical words
        """
        tokens = cls.clean_text(text)
        if not tokens:
            return 0.0, "Neutral", []

        total_weight = 0.0
        matched_words = 0
        negate_next = False
        amplifier = 1.0

        emotion_counts: Dict[str, int] = {k: 0 for k in cls.EMOTION_KEYWORDS}

        for i, token in enumerate(tokens):
            if token in cls.NEGATIONS:
                negate_next = True
                continue

            if token in cls.AMPLIFIERS:
                amplifier = cls.AMPLIFIERS[token]
                continue

            if token in cls.POLARITY_LEXICON:
                weight = cls.POLARITY_LEXICON[token] * amplifier
                if negate_next:
                    weight = -weight * 0.75  # Inversion with mild attenuation
                    negate_next = False

                total_weight += weight
                matched_words += 1
                amplifier = 1.0  # Reset amplifier

            # Check emotion categorizations
            for emotion, words in cls.EMOTION_KEYWORDS.items():
                if token in words:
                    emotion_counts[emotion] += 1

        # Calculate normalized score between -1.0 and 1.0
        if matched_words > 0:
            raw_avg = total_weight / matched_words
            # Squash using tanh-like bounded normalizer
            normalized = max(-1.0, min(1.0, raw_avg / 1.8))
        else:
            normalized = 0.0

        # Determine dominant emotion
        top_emotion = "Neutral"
        highest_count = 0
        for emotion, count in emotion_counts.items():
            if count > highest_count:
                highest_count = count
                top_emotion = emotion

        if highest_count == 0:
            if normalized > 0.2:
                top_emotion = "Joy"
            elif normalized < -0.2:
                top_emotion = "Stress"
            else:
                top_emotion = "Neutral"

        # Extract topical tags (meaningful non-stopwords)
        stopwords = {
            "the", "and", "a", "to", "in", "is", "it", "i", "of", "that", "this",
            "for", "on", "with", "as", "at", "by", "from", "up", "about", "into",
            "was", "were", "my", "me", "we", "our", "you", "your", "he", "she", "they"
        }
        tags = []
        for token in tokens:
            if len(token) > 4 and token not in stopwords and token not in tags:
                tags.append(token)
            if len(tags) >= 5:
                break

        return round(normalized, 2), top_emotion, tags
