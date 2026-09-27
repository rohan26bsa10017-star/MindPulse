"""
MindPulse: Intelligent Student Mental Health & Cognitive Wellness Management System
Main Entry Point
"""

import sys
import os

# Ensure UTF-8 output across all Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Ensure project root is in python search path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.ui.cli import MindPulseCLI


def main():
    try:
        app = MindPulseCLI()
        app.run()
    except KeyboardInterrupt:
        print("\n\nOperation interrupted by user. Exiting MindPulse gracefully.")
        sys.exit(0)
    except Exception as e:
        print(f"\n[Fatal Error] An unexpected error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
