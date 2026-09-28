# Project Statement - MindPulse

## 1. Problem Statement
Hostel life at college can get pretty exhausting. Between 8 AM lectures, lab FATs, continuous assignments, and prepping for CAT exams, most of us in the hostel end up staying awake until 3 or 4 in the morning. Next day, we wake up feeling drained, drink coffee, and try to push through another full day of classes. After doing this for a couple of weeks, burnout hits hard. 

The worst part is that we usually don't even realize how badly our chaotic sleep and study habits are messing with our mood until we're completely stressed out and falling behind.

Sure, there are dozens of habit and mood tracking apps on the Play Store. But almost none of them work well for a college student. First off, most of them lock their best features behind a 500-rupee monthly subscription after giving you a tiny 3-day trial. Worse, they make you upload your personal journal entries and private thoughts to their cloud servers. Nobody wants their private stress notes or emotional thoughts stored on some random company's database. On top of that, these apps usually just show a generic motivational quote instead of giving you real numbers or showing if your 4-hour sleep night is the real reason you felt miserable all day.

That is why I built MindPulse. 

I wanted a simple, distraction-free tool written in Python that runs right inside your laptop's terminal. Everything stays 100% on your machine inside a local SQLite database (`mindpulse.db`). You can log your daily hours, write honest reflections without worrying about privacy, take standard stress screening quizzes (like PSS-10), and let the program calculate the exact mathematical correlation between your sleep, study time, and daily mood.

---

## 2. Scope of the Project
Here is what I designed MindPulse to handle:

First, complete offline privacy. You don't need any internet connection to use this. Your login password gets hashed using PBKDF2 with salt, and all your journal entries and scores stay inside your local database folder. Nothing gets uploaded anywhere.

Second, daily routine logging. When you open the program, you can quickly enter your mood score from 1 to 10, how many hours you slept, how much you studied, exercise minutes, and how energetic you feel. The program checks your inputs so you can't accidentally type negative hours or a mood rating of 15.

Third, a private terminal journal with local sentiment analysis. You can write whatever happened during your day. Instead of calling paid cloud APIs, I wrote a local dictionary-based sentiment analyzer in pure Python. It picks up positive and negative emotional words, handles negations like "not good" or "never felt this tired", and gives you a score from -1.0 to +1.0 along with common theme tags.

Fourth, standard psychological self-check questionnaires. The app includes three recognized screening tools:
- PSS-10 (Perceived Stress Scale) to check how overloaded you feel with college work.
- PHQ-9 (Patient Health Questionnaire) for checking depression symptoms.
- GAD-7 (Generalized Anxiety Disorder) to check general anxiety.
All three calculate scores automatically, invert reverse-coded items, and show your clinical range from Minimal to Severe.

Fifth, lifestyle correlation math. MindPulse takes your past logs and uses the Pearson correlation formula ($r$) to tell you if more sleep actually boosts your mood, or if study sessions over 7 hours start tanking your energy. It also keeps an eye on your rolling 7-day average to warn you if you're heading toward burnout.

Finally, quick grounding exercises and data export. If you're having an anxious study session, the app walks you through 4x4 Box Breathing or the 5-4-3-2-1 sensory technique. If you want to view your numbers in Excel or submit them to a mentor, you can export your entire history into a CSV file with one command.

---

## 3. Who This Is Built For
- College and University Students: Specifically students tackling engineering coursework, project deadlines, and rough sleep schedules who need a zero-distraction terminal tool to keep themselves accountable.
- People Who Value Data Privacy: Anyone who likes journaling but hates the idea of third-party apps mining their personal journal entries.
- Student Mentors and Counselors: Faculty advisors or college wellness counselors who want students to bring in an exported CSV log to look at genuine sleep and habit patterns during one-on-one sessions.

---

## 4. Key Program Features
- PBKDF2 salted password authentication so accounts are properly protected locally.
- Quick daily habit entry with input validation guards.
- Offline rule-based sentiment analysis that works without any internet or API keys.
- Automatic scoring for PSS-10, PHQ-9, and GAD-7 clinical questionnaires.
- ASCII trend sparklines and Pearson correlation statistics.
- 7-day Burnout Risk warnings.
- Interactive step-by-step breathing exercises right in the terminal.
- One-click CSV export saved directly to the local data directory.
