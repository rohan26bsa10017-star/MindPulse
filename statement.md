# Project Statement - MindPulse

## 1. Problem Statement
College life comes with a lot of pressure—continuous assignments, lab exams, long study nights, and erratic sleep schedules. Most students struggle with stress and fatigue at some point in the semester, but rarely realize how badly their habits are affecting their mental health until they feel completely burnt out.

While there are many wellness and mood tracking apps on mobile app stores, almost all of them come with major downsides:
1. They require expensive monthly subscriptions.
2. They force users to upload deeply personal journals and thoughts to external cloud servers, which raises privacy concerns.
3. They give generic motivational quotes instead of showing actual links between daily habits and mood.

There is a real need for a simple, completely private, and practical tool built specifically for college students. MindPulse solves this by running 100% locally on the student's laptop through Python. It lets students record their daily habits, write private journal reflections, take recognized stress and anxiety screening quizzes, and mathematically see how their sleep and study hours are directly impacting their mood.

---

## 2. Scope of the Project
The scope of MindPulse covers:
- Local Storage & Privacy: All accounts, journals, habit logs, and test results are stored exclusively on the user's computer inside a local SQLite database (`mindpulse.db`). No personal data ever leaves the machine.
- Daily Habit & Mood Tracking: A quick daily log for mood (1 to 10), sleep duration (in hours), study time, exercise time, and general energy level.
- Private Reflective Journaling: A built-in terminal text entry system where students can write freely about their day. A Python algorithm checks positive and negative word patterns (handling words like "not happy" or "really stressed") to score mood sentiment and extract main keywords.
- Standard Psychological Self-Assessments:
  1. PSS-10 (Perceived Stress Scale): Measures how unpredictable or overwhelming life feels right now.
  2. PHQ-9 (Patient Health Questionnaire): A standard 9-question depression screening questionnaire.
  3. GAD-7 (Generalized Anxiety Disorder): A 7-question anxiety severity questionnaire.
- Habit Correlation & Burnout Warnings: Uses the Pearson correlation formula ($r$) to calculate whether more sleep actually correlates with higher mood scores, and checks rolling 7-day averages to flag warning signs of burnout.
- Grounding & Relaxation Guides: Quick step-by-step calming exercises like 4x4 Box Breathing and the 5-4-3-2-1 sensory grounding exercise, along with helpline contacts for immediate assistance.
- CSV Data Export: Allows students to export their logged data to a clean CSV spreadsheet whenever they want to keep a personal backup or view it in Microsoft Excel.

---

## 3. Target Users
1. College & University Students: Engineering and science students dealing with academic workloads, upcoming exams, project deadlines, and irregular sleep patterns who want a quick, distraction-free tool to monitor their well-being.
2. Privacy-Conscious Individuals: Anyone who wants to keep an honest personal journal and habit log without trusting a third-party company or cloud service with their private thoughts.
3. Mentors & Student Counselors: Academic counselors who can ask students to export their habit data over a few weeks to look at real study and sleep patterns during counseling sessions.

---

## 4. High-Level Features
- Student Account Authentication: Register and login system with passwords secured using salted PBKDF2 hashing so passwords are never stored in plain text.
- Daily Log Management: Fast interactive terminal inputs with checks to prevent invalid numbers (like negative hours or mood scores over 10).
- Offline Sentiment Evaluation: Custom dictionary-based sentiment scoring that calculates mood tone from text without needing any paid AI APIs or external network calls.
- Standard Psychometric Scoring: Automated score calculators for PSS-10, PHQ-9, and GAD-7 with clinical ranges (Minimal, Mild, Moderate, Severe) and practical suggestions.
- Trend Sparklines & Correlation Statistics: Inline ASCII sparkline graphs to show recent mood trends at a glance, plus mathematical correlation calculations between habits and mood.
- Burnout Risk Alert: A warning check that combines recent low sleep, long study hours, and low mood to warn the student before burnout hits.
- Relaxation Guides: Quick calming exercises that can be completed right at the desk during study breaks.
- CSV Exporting: One-click export to `data/<username>_export.csv` for easy viewing in spreadsheet software.
