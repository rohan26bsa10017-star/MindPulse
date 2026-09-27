"""
MindPulse: Evidence-Based Coping Strategies and Emergency Support Dispatcher
Provides actionable CBT techniques, grounding exercises, and crisis hotline details.
"""

from typing import Dict, List, Any


class CopingRecommender:
    """Delivers targeted micro-interventions and psychological self-regulation tools."""

    TECHNIQUES: Dict[str, Dict[str, Any]] = {
        "box_breathing": {
            "title": "Box Breathing (Navy SEAL Calming Protocol)",
            "category": "Physiological Regulation",
            "duration": "4 Minutes",
            "steps": [
                "1. Inhale slowly through your nose for a count of 4 seconds.",
                "2. Hold your lungs full of air for a count of 4 seconds.",
                "3. Exhale smoothly through your mouth for 4 seconds.",
                "4. Hold empty lungs for 4 seconds before repeating.",
                "Cycle this 4 times to stimulate the vagus nerve and reduce heart rate."
            ]
        },
        "grounding_54321": {
            "title": "5-4-3-2-1 Sensory Grounding Technique",
            "category": "Acute Anxiety / Panic Management",
            "duration": "3 Minutes",
            "steps": [
                "Look around your physical space and name:",
                "• 5 things you can SEE (e.g., your desk lamp, pen, tree outside)",
                "• 4 things you can TOUCH (e.g., your cotton shirt, cool tabletop)",
                "• 3 things you can HEAR (e.g., fan hum, distant cars, your breath)",
                "• 2 things you can SMELL (e.g., coffee, fresh air, paper)",
                "• 1 thing you can TASTE (e.g., mint, water, tea)"
            ]
        },
        "cognitive_reframing": {
            "title": "CBT Thought Restructuring",
            "category": "Cognitive Flexibility",
            "duration": "5 Minutes",
            "steps": [
                "1. Identify the automatic catastrophic thought (e.g., 'I will fail this exam and ruin everything').",
                "2. Examine the empirical evidence: What facts prove this? What facts disprove it?",
                "3. Check for cognitive distortions: All-or-nothing thinking? Catastrophizing?",
                "4. Formulate an objective balanced alternative: 'This exam is challenging, but I have prepared, and one test does not determine my worth.'"
            ]
        },
        "progressive_relaxation": {
            "title": "Progressive Muscle Relaxation (PMR)",
            "category": "Somatic Tension Relief",
            "duration": "6 Minutes",
            "steps": [
                "1. Sit comfortably. Clench your toes tightly for 5 seconds, then release and feel the warmth.",
                "2. Tense your calves, then thighs, holding 5 seconds each before relaxing.",
                "3. Clench your fists, tighten your arms, and release.",
                "4. Shrug your shoulders up to your ears, hold, and drop them down.",
                "5. Notice the deep contrast between physical tension and relaxation."
            ]
        }
    }

    CRISIS_RESOURCES = [
        {"name": "Tele-MANAS (Govt of India 24x7 Mental Health Helpline)", "contact": "14416 / 1800-891-4416 (Toll-Free)"},
        {"name": "Vandrevala Foundation 24x7 Crisis Support", "contact": "+91 9999 666 555"},
        {"name": "NIMHANS Psychological Support Line", "contact": "080-46110007"},
        {"name": "VIT Campus Counseling & Student Welfare Desk", "contact": "Counseling Cell / healthcenter@vit.ac.in"}
    ]

    @classmethod
    def get_technique(cls, key: str) -> Dict[str, Any]:
        return cls.TECHNIQUES.get(key, cls.TECHNIQUES["box_breathing"])

    @classmethod
    def get_all_techniques(cls) -> Dict[str, Dict[str, Any]]:
        return cls.TECHNIQUES

    @classmethod
    def get_crisis_resources(cls) -> List[Dict[str, str]]:
        return cls.CRISIS_RESOURCES
