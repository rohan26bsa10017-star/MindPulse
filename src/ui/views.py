"""
MindPulse: Terminal Presentation, Formatting & Visual Views
Includes ANSI styling, ASCII sparklines, and tabular layouts.
"""

import sys
from typing import List, Dict, Any
from src.core.models import JournalEntry, MoodLog, AssessmentResult


class Colors:
    """ANSI color codes for terminal styling."""
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    
    # Foreground colors
    CYAN = "\033[36m"
    BLUE = "\033[34m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    RED = "\033[31m"
    MAGENTA = "\033[35m"
    WHITE = "\033[37m"

    @classmethod
    def paint(cls, text: str, color: str) -> str:
        return f"{color}{text}{cls.RESET}"


class TerminalViews:
    """Handles rendering of ASCII components and formatted console views."""

    @staticmethod
    def render_sparkline(values: List[float], min_val: float = 1.0, max_val: float = 10.0) -> str:
        """Renders an ASCII/Unicode trend sparkline for numerical sequences."""
        if not values:
            return "No data"
        try:
            # Check if stdout can encode unicode block elements
            "▂".encode(getattr(sys.stdout, "encoding", "utf-8") or "utf-8")
            bars = [" ", "▂", "▃", "▄", "▅", "▆", "▇", "█"]
        except Exception:
            bars = [".", "_", "-", "~", "=", "*", "#", "^"]

        rendered = []
        span = max_val - min_val if max_val != min_val else 1.0

        for v in values:
            normalized = (v - min_val) / span
            idx = int(normalized * (len(bars) - 1))
            idx = max(0, min(len(bars) - 1, idx))
            rendered.append(bars[idx])
        return "".join(rendered)

    @staticmethod
    def print_banner() -> None:
        art = r"""
  __  __ _           _ _____       _          
 |  \/  (_)_ __   __| |  __ \ _   | |___  ___ 
 | |\/| | | '_ \ / _` | |__) | |  | / __|/ _ \
 | |  | | | | | | (_| |  ___/| |_ | \__ \  __/
 |_|  |_|_|_| |_|\__,_|_|     \___,_|___/\___|
"""
        print(f"{Colors.CYAN}{Colors.BOLD}{art}{Colors.RESET}{Colors.DIM}   Intelligent Student Mental Health & Cognitive Wellness System{Colors.RESET}\n")

    @staticmethod
    def print_mood_history(logs: List[MoodLog]) -> None:
        """Renders a formatted table of recent mood records."""
        if not logs:
            print(Colors.paint("\nNo mood records found yet. Begin by logging today's mood!\n", Colors.YELLOW))
            return

        print(Colors.paint(f"\n{'='*75}", Colors.CYAN))
        print(Colors.paint(f" {'DATE':<12} | {'MOOD':<8} | {'LABEL':<12} | {'SLEEP':<6} | {'STUDY':<6} | {'EXERCISE':<8} | {'ENERGY':<6}", Colors.BOLD))
        print(Colors.paint(f"{'='*75}", Colors.CYAN))

        for log in logs[-10:]:
            color = Colors.GREEN if log.mood_score >= 7 else (Colors.YELLOW if log.mood_score >= 5 else Colors.RED)
            mood_str = Colors.paint(f"{log.mood_score}/10", color)
            print(f" {log.date:<12} | {mood_str:<17} | {log.mood_label:<12} | {log.sleep_hours:<4}h  | {log.study_hours:<4}h  | {log.exercise_minutes:<6}m | {log.energy_level}/5")
        
        print(Colors.paint(f"{'='*75}", Colors.CYAN))
        mood_scores = [float(l.mood_score) for l in logs]
        spark = TerminalViews.render_sparkline(mood_scores)
        print(f" Trend Sparkline (last {len(mood_scores)} logs): {Colors.paint(spark, Colors.GREEN)}\n")

    @staticmethod
    def print_journal_entries(entries: List[JournalEntry]) -> None:
        """Renders recent reflective journal entries."""
        if not entries:
            print(Colors.paint("\nNo journal entries found. Express your thoughts freely!\n", Colors.YELLOW))
            return

        print(Colors.paint(f"\n{'='*75}", Colors.MAGENTA))
        print(Colors.paint(" RECENT REFLECTIVE JOURNAL ENTRIES", Colors.BOLD))
        print(Colors.paint(f"{'='*75}", Colors.MAGENTA))

        for entry in entries[:5]:
            date_str = entry.created_at.strftime("%Y-%m-%d %H:%M")
            pol_color = Colors.GREEN if entry.sentiment_score > 0.1 else (Colors.RED if entry.sentiment_score < -0.1 else Colors.YELLOW)
            pol_str = Colors.paint(f"{entry.sentiment_score:+.2f} ({entry.dominant_emotion})", pol_color)
            tags_str = " ".join([f"#{t}" for t in entry.tags])

            print(f"\n{Colors.BOLD}Title:{Colors.RESET} {entry.title}  |  {Colors.DIM}{date_str}{Colors.RESET}")
            print(f"{Colors.BOLD}Sentiment Analysis:{Colors.RESET} {pol_str}  |  {Colors.BOLD}Tags:{Colors.RESET} {Colors.CYAN}{tags_str}{Colors.RESET}")
            print(f"{Colors.DIM}Content:{Colors.RESET}\n  {entry.content}\n{'-'*75}")

    @staticmethod
    def print_assessment_history(results: List[AssessmentResult]) -> None:
        """Renders past psychometric evaluation outcomes."""
        if not results:
            print(Colors.paint("\nNo assessment history recorded. Try taking the PSS-10, PHQ-9, or GAD-7!\n", Colors.YELLOW))
            return

        print(Colors.paint(f"\n{'='*75}", Colors.BLUE))
        print(Colors.paint(f" {'DATE':<16} | {'SCALE':<8} | {'SCORE':<10} | {'SEVERITY':<24}", Colors.BOLD))
        print(Colors.paint(f"{'='*75}", Colors.BLUE))

        for res in results:
            date_str = res.completed_at.strftime("%Y-%m-%d %H:%M")
            score_str = f"{res.raw_score}/{res.max_score}"
            sev_color = Colors.GREEN if "Low" in res.severity_level or "Minimal" in res.severity_level else (Colors.YELLOW if "Moderate" in res.severity_level or "Mild" in res.severity_level else Colors.RED)
            sev_str = Colors.paint(res.severity_level, sev_color)
            print(f" {date_str:<16} | {res.assessment_type:<8} | {score_str:<10} | {sev_str:<32}")
        print(Colors.paint(f"{'='*75}\n", Colors.BLUE))
