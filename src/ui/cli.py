"""
MindPulse: Interactive Command-Line Interface Controller
Handles user interaction, input validation loops, and navigation state.
"""

import sys
import csv
import datetime
from typing import Optional
from src.core.models import User, JournalEntry, MoodLog, AssessmentResult
from src.core.exceptions import ValidationError, AuthenticationError, UserAlreadyExistsError
from src.storage.database import DatabaseManager
from src.storage.repository import UserRepository, JournalRepository, MoodRepository, AssessmentRepository
from src.security.auth import AuthService
from src.analytics.sentiment import SentimentAnalyzer
from src.analytics.statistics import StatisticsEngine
from src.assessments.clinical_scales import get_scale_by_code
from src.assessments.recommendations import CopingRecommender
from src.ui.views import Colors, TerminalViews


class MindPulseCLI:
    """Controller orchestrating the terminal user experience."""

    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        self.db = db_manager or DatabaseManager()
        self.user_repo = UserRepository(self.db)
        self.journal_repo = JournalRepository(self.db)
        self.mood_repo = MoodRepository(self.db)
        self.assessment_repo = AssessmentRepository(self.db)
        self.auth = AuthService(self.user_repo)

    def run(self) -> None:
        """Main application lifecycle entry point."""
        TerminalViews.print_banner()
        while True:
            if not self.auth.get_current_user():
                if not self.auth_menu():
                    print(Colors.paint("\nThank you for using MindPulse. Stay mindful and resilient!\n", Colors.CYAN))
                    break
            else:
                self.main_menu()

    def auth_menu(self) -> bool:
        """Displays authentication screen. Returns False if user chooses to exit."""
        print(f"\n{Colors.BOLD}=== AUTHENTICATION ==={Colors.RESET}")
        print("1. Login to Existing Account")
        print("2. Register New Student Account")
        print("3. Exit System")

        choice = input(Colors.paint("\nSelect option (1-3): ", Colors.CYAN)).strip()
        if choice == "1":
            self.handle_login()
            return True
        elif choice == "2":
            self.handle_register()
            return True
        elif choice == "3":
            return False
        else:
            print(Colors.paint("Invalid option. Please choose 1, 2, or 3.", Colors.RED))
            return True

    def handle_register(self) -> None:
        print(f"\n{Colors.BOLD}--- Student Registration ---{Colors.RESET}")
        username = input("Choose a username (3-20 characters): ").strip()
        password = input("Choose a password (min 6 characters): ").strip()
        try:
            user = self.auth.register(username, password)
            print(Colors.paint(f"✔ Registration successful! Welcome, {user.username}. Please log in.", Colors.GREEN))
        except (ValidationError, UserAlreadyExistsError) as e:
            print(Colors.paint(f"✖ Registration failed: {e}", Colors.RED))

    def handle_login(self) -> None:
        print(f"\n{Colors.BOLD}--- Student Login ---{Colors.RESET}")
        username = input("Username: ").strip()
        password = input("Password: ").strip()
        try:
            user = self.auth.login(username, password)
            print(Colors.paint(f"✔ Logged in as {user.username} successfully!", Colors.GREEN))
        except AuthenticationError as e:
            print(Colors.paint(f"✖ Login failed: {e}", Colors.RED))

    def main_menu(self) -> None:
        user = self.auth.get_current_user()
        print(Colors.paint(f"\n=======================================================", Colors.CYAN))
        print(Colors.paint(f"  MindPulse Dashboard  |  Active User: {user.username}", Colors.BOLD))
        print(Colors.paint(f"=======================================================", Colors.CYAN))
        print("1. 📊 Log Daily Mood & Habits (Sleep, Study, Exercise)")
        print("2. 📈 View Mood & Lifestyle Analytics (Trends & Correlations)")
        print("3. 📝 Write Reflective Journal Entry (Sentiment Analysis)")
        print("4. 📖 View Reflective Journal History")
        print("5. 🧠 Take Psychological Assessment (PSS-10, PHQ-9, GAD-7)")
        print("6. 🚨 View Burnout Risk Index (BRI) & Warnings")
        print("7. 🧘 Evidence-Based Coping Strategies (CBT / Box Breathing)")
        print("8. 🆘 Crisis Support & University Counseling Contacts")
        print("9. 💾 Export Wellness Summary to CSV")
        print("10. 🔒 Logout")
        print("0.  ❌ Exit MindPulse")

        choice = input(Colors.paint("\nEnter your choice (0-10): ", Colors.CYAN)).strip()

        if choice == "1":
            self.handle_log_mood()
        elif choice == "2":
            self.handle_view_mood_analytics()
        elif choice == "3":
            self.handle_write_journal()
        elif choice == "4":
            self.handle_view_journal()
        elif choice == "5":
            self.handle_take_assessment()
        elif choice == "6":
            self.handle_view_burnout_risk()
        elif choice == "7":
            self.handle_coping_strategies()
        elif choice == "8":
            self.handle_crisis_resources()
        elif choice == "9":
            self.handle_export_csv()
        elif choice == "10":
            self.auth.logout()
            print(Colors.paint("✔ Successfully logged out.", Colors.GREEN))
        elif choice == "0":
            self.auth.logout()
            print(Colors.paint("\nThank you for prioritizing your mental health. Goodbye!\n", Colors.CYAN))
            sys.exit(0)
        else:
            print(Colors.paint("Invalid selection. Please choose an option from 0 to 10.", Colors.RED))

    def handle_log_mood(self) -> None:
        user = self.auth.get_current_user()
        print(f"\n{Colors.BOLD}--- Daily Wellbeing & Habit Tracker ---{Colors.RESET}")
        today_str = datetime.date.today().strftime("%Y-%m-%d")
        date_input = input(f"Date (press Enter for today: {today_str}): ").strip()
        date = date_input if date_input else today_str

        # Validate Mood Score (1-10)
        while True:
            try:
                mood_score = int(input("Overall Mood Score (1=Severely Distressed to 10=Peak Joy): ").strip())
                if 1 <= mood_score <= 10:
                    break
                print(Colors.paint("Please enter an integer between 1 and 10.", Colors.YELLOW))
            except ValueError:
                print(Colors.paint("Invalid numeric value.", Colors.YELLOW))

        mood_label = input("Mood descriptor (e.g. Hopeful, Anxious, Calm, Exhausted, Energetic): ").strip()
        if not mood_label:
            mood_label = "Neutral"

        # Validate Energy (1-5)
        while True:
            try:
                energy_level = int(input("Physical & Mental Energy Level (1=Drained to 5=High): ").strip())
                if 1 <= energy_level <= 5:
                    break
                print(Colors.paint("Please enter an integer between 1 and 5.", Colors.YELLOW))
            except ValueError:
                print(Colors.paint("Invalid numeric value.", Colors.YELLOW))

        # Sleep Hours
        while True:
            try:
                sleep_hours = float(input("Sleep duration last night (hours, e.g., 7.5): ").strip())
                if 0.0 <= sleep_hours <= 24.0:
                    break
                print(Colors.paint("Sleep must be between 0 and 24 hours.", Colors.YELLOW))
            except ValueError:
                print(Colors.paint("Invalid number.", Colors.YELLOW))

        # Study Hours
        while True:
            try:
                study_hours = float(input("Hours spent studying/coding today: ").strip())
                if 0.0 <= study_hours <= 24.0:
                    break
                print(Colors.paint("Study hours must be between 0 and 24 hours.", Colors.YELLOW))
            except ValueError:
                print(Colors.paint("Invalid number.", Colors.YELLOW))

        # Exercise Minutes
        while True:
            try:
                exercise_minutes = int(input("Exercise or physical movement (minutes, e.g., 30): ").strip())
                if 0 <= exercise_minutes <= 1440:
                    break
                print(Colors.paint("Invalid exercise duration.", Colors.YELLOW))
            except ValueError:
                print(Colors.paint("Invalid number.", Colors.YELLOW))

        notes = input("Reflective notes or triggers (optional): ").strip()

        log = MoodLog(
            log_id=None,
            user_id=user.user_id,
            date=date,
            mood_score=mood_score,
            mood_label=mood_label,
            energy_level=energy_level,
            sleep_hours=sleep_hours,
            study_hours=study_hours,
            exercise_minutes=exercise_minutes,
            notes=notes if notes else None
        )
        self.mood_repo.log_mood(log)
        print(Colors.paint(f"\n✔ Daily log for {date} recorded successfully!", Colors.GREEN))

    def handle_view_mood_analytics(self) -> None:
        user = self.auth.get_current_user()
        logs = self.mood_repo.get_logs_by_user(user.user_id, days=30)
        TerminalViews.print_mood_history(logs)

        if len(logs) >= 3:
            corr = StatisticsEngine.calculate_correlations(logs)
            print(f"{Colors.BOLD}Statistical Correlation Insights (Pearson r):{Colors.RESET}")
            print(f" • Sleep vs. Mood:    {corr['sleep_vs_mood']:+.2f} (Positive indicates more sleep improves mood)")
            print(f" • Study vs. Mood:    {corr['study_vs_mood']:+.2f} (Negative suggests heavy workload lowers mood)")
            print(f" • Exercise vs. Mood: {corr['exercise_vs_mood']:+.2f} (Positive shows physical activity boosts spirits)")
            print(f" • Sleep vs. Energy:  {corr['sleep_vs_energy']:+.2f}")
        else:
            print(Colors.paint("Tip: Log at least 3 days to unlock personalized statistical correlation analysis!", Colors.DIM))

    def handle_write_journal(self) -> None:
        user = self.auth.get_current_user()
        print(f"\n{Colors.BOLD}--- Reflective Journaling ---{Colors.RESET}")
        title = input("Entry Title: ").strip()
        if not title:
            title = f"Reflection on {datetime.date.today()}"

        print("Write your journal entry below (Press Enter when done):")
        content = input("> ").strip()
        if not content:
            print(Colors.paint("Journal entry cannot be empty.", Colors.RED))
            return

        score, dominant_emotion, tags = SentimentAnalyzer.analyze(content)
        entry = JournalEntry(
            entry_id=None,
            user_id=user.user_id,
            title=title,
            content=content,
            sentiment_score=score,
            dominant_emotion=dominant_emotion,
            tags=tags
        )
        self.journal_repo.add_entry(entry)

        pol_color = Colors.GREEN if score > 0.1 else (Colors.RED if score < -0.1 else Colors.YELLOW)
        print(Colors.paint("\n✔ Journal entry preserved locally!", Colors.GREEN))
        print(f"Detected Emotional Tone: {Colors.paint(dominant_emotion, pol_color)} (Polarity Score: {score:+.2f})")
        if tags:
            print(f"Extracted Topical Themes: {Colors.paint(', '.join(tags), Colors.CYAN)}")

    def handle_view_journal(self) -> None:
        user = self.auth.get_current_user()
        entries = self.journal_repo.get_entries_by_user(user.user_id)
        TerminalViews.print_journal_entries(entries)

    def handle_take_assessment(self) -> None:
        user = self.auth.get_current_user()
        print(f"\n{Colors.BOLD}=== Psychological & Psychometric Assessments ==={Colors.RESET}")
        print("1. PSS-10 : Perceived Stress Scale (Evaluate daily stress perception)")
        print("2. PHQ-9  : Patient Health Questionnaire (Screen depression symptoms)")
        print("3. GAD-7  : Generalized Anxiety Disorder Scale (Assess anxiety levels)")
        print("4. View Past Assessment Results")

        choice = input(Colors.paint("\nSelect scale (1-4): ", Colors.CYAN)).strip()
        code_map = {"1": "PSS-10", "2": "PHQ-9", "3": "GAD-7"}

        if choice in code_map:
            scale_code = code_map[choice]
            scale_cls = get_scale_by_code(scale_code)
            print(f"\n{Colors.BOLD}Starting {scale_cls.name}{Colors.RESET}")
            print("Please answer each item candidly based on your experience over the past 2 weeks:\n")

            responses = []
            for idx, q in enumerate(scale_cls.questions, start=1):
                print(f"Q{idx}. {q}")
                for opt in scale_cls.options:
                    print(f"   {opt}")
                while True:
                    try:
                        ans = int(input(Colors.paint(f"Your answer (0-{len(scale_cls.options)-1}): ", Colors.CYAN)).strip())
                        if 0 <= ans < len(scale_cls.options):
                            responses.append(ans)
                            break
                        print(Colors.paint(f"Enter an integer between 0 and {len(scale_cls.options)-1}.", Colors.YELLOW))
                    except ValueError:
                        print(Colors.paint("Invalid number.", Colors.YELLOW))

            raw_score, severity, rec = scale_cls.score_responses(responses)
            result = AssessmentResult(
                assessment_id=None,
                user_id=user.user_id,
                assessment_type=scale_code,
                raw_score=raw_score,
                max_score=scale_cls.max_score,
                severity_level=severity,
                recommendation=rec
            )
            self.assessment_repo.save_result(result)

            sev_color = Colors.GREEN if "Low" in severity or "Minimal" in severity else (Colors.YELLOW if "Moderate" in severity or "Mild" in severity else Colors.RED)
            print(f"\n{Colors.BOLD}=== Assessment Complete ==={Colors.RESET}")
            print(f"Raw Score: {raw_score}/{scale_cls.max_score}")
            print(f"Classification: {Colors.paint(severity, sev_color)}")
            print(f"Clinical Recommendation: {rec}\n")

        elif choice == "4":
            results = self.assessment_repo.get_results_by_user(user.user_id)
            TerminalViews.print_assessment_history(results)
        else:
            print(Colors.paint("Invalid option.", Colors.RED))

    def handle_view_burnout_risk(self) -> None:
        user = self.auth.get_current_user()
        logs = self.mood_repo.get_logs_by_user(user.user_id, days=14)
        bri_score, level, factors = StatisticsEngine.calculate_burnout_risk(logs)

        risk_color = Colors.GREEN if bri_score < 25 else (Colors.YELLOW if bri_score < 50 else Colors.RED)
        print(Colors.paint(f"\n{'='*70}", Colors.CYAN))
        print(Colors.paint(" BURNOUT RISK INDEX (BRI) EVALUATION", Colors.BOLD))
        print(Colors.paint(f"{'='*70}", Colors.CYAN))
        print(f" Burnout Risk Score: {Colors.paint(f'{bri_score}%', risk_color + Colors.BOLD)}")
        print(f" Status Category:    {Colors.paint(level, risk_color)}")
        print(f"\n {Colors.BOLD}Key Contributing Lifestyle Factors:{Colors.RESET}")
        for factor in factors:
            print(f"  • {factor}")
        print(Colors.paint(f"{'='*70}\n", Colors.CYAN))

    def handle_coping_strategies(self) -> None:
        techniques = CopingRecommender.get_all_techniques()
        print(f"\n{Colors.BOLD}=== Evidence-Based Coping Strategies ==={Colors.RESET}")
        keys = list(techniques.keys())
        for idx, key in enumerate(keys, start=1):
            tech = techniques[key]
            print(f"{idx}. {tech['title']} ({tech['category']} - {tech['duration']})")

        choice = input(Colors.paint(f"\nSelect technique (1-{len(keys)}): ", Colors.CYAN)).strip()
        try:
            sel_idx = int(choice) - 1
            if 0 <= sel_idx < len(keys):
                t = techniques[keys[sel_idx]]
                print(Colors.paint(f"\n--- {t['title']} ---", Colors.BOLD + Colors.GREEN))
                print(f"Category: {t['category']} | Expected Time: {t['duration']}\n")
                for s in t["steps"]:
                    print(f"  {s}")
                print()
            else:
                print(Colors.paint("Invalid selection.", Colors.RED))
        except ValueError:
            print(Colors.paint("Please enter a valid number.", Colors.RED))

    def handle_crisis_resources(self) -> None:
        resources = CopingRecommender.get_crisis_resources()
        print(Colors.paint(f"\n{'='*70}", Colors.RED))
        print(Colors.paint(" 🆘 EMERGENCY & MENTAL HEALTH SUPPORT HOTLINES", Colors.BOLD + Colors.RED))
        print(Colors.paint(f"{'='*70}", Colors.RED))
        print(" If you are in severe distress or feeling overwhelmed, free support is available:\n")
        for r in resources:
            print(f" • {Colors.BOLD}{r['name']}{Colors.RESET}")
            print(f"   Contact: {Colors.paint(r['contact'], Colors.CYAN)}\n")
        print(Colors.paint(f"{'='*70}\n", Colors.RED))

    def handle_export_csv(self) -> None:
        user = self.auth.get_current_user()
        logs = self.mood_repo.get_logs_by_user(user.user_id, days=90)
        if not logs:
            print(Colors.paint("No mood logs to export.", Colors.YELLOW))
            return

        filename = f"data/{user.username}_wellbeing_export.csv"
        try:
            with open(filename, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Date", "MoodScore", "MoodLabel", "EnergyLevel", "SleepHours", "StudyHours", "ExerciseMinutes", "Notes"])
                for l in logs:
                    writer.writerow([l.date, l.mood_score, l.mood_label, l.energy_level, l.sleep_hours, l.study_hours, l.exercise_minutes, l.notes or ""])
            print(Colors.paint(f"✔ Exported {len(logs)} records to '{filename}' successfully!", Colors.GREEN))
        except Exception as e:
            print(Colors.paint(f"Failed to export data: {e}", Colors.RED))
