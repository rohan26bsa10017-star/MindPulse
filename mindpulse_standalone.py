from math import *
import sqlite3
import hashlib
import os
import hmac
import datetime
import csv
import sys
import re

DB_NAME = "data/mindpulse.db"

# connect to database
def open_db():
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    return conn, cur

# initialize tables
def init_db():
    conn, cur = open_db()
    cur.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, uname TEXT UNIQUE, pw_hash TEXT, salt TEXT, created_at TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS logs (id INTEGER PRIMARY KEY AUTOINCREMENT, uid INTEGER, log_date TEXT, mood_val INTEGER, mood_lbl TEXT, eng_val INTEGER, slp_val REAL, std_val REAL, exe_val INTEGER, note_txt TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS entries (id INTEGER PRIMARY KEY AUTOINCREMENT, uid INTEGER, title_txt TEXT, body_txt TEXT, sent_val REAL, emo_lbl TEXT, tag_txt TEXT, created_at TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS tests (id INTEGER PRIMARY KEY AUTOINCREMENT, uid INTEGER, test_name TEXT, score_val INTEGER, max_val INTEGER, sev_lbl TEXT, advice_txt TEXT, taken_at TEXT)")
    conn.commit()
    conn.close()

# hash user password
def hash_val(pw, salt=None):
    if not salt:
        salt = os.urandom(16).hex()
    h = hashlib.pbkdf2_hmac("sha256", pw.encode("utf-8"), bytes.fromhex(salt), 100000).hex()
    return h, salt

# check user password
def check_pw(pw, h, salt):
    calc_h, _ = hash_val(pw, salt)
    return hmac.compare_digest(calc_h, h)

# register user
def reg_user(uname, pw):
    u = uname.strip()
    p = pw.strip()
    if len(u) < 3 or len(p) < 6:
        return False, "Input too short."
    conn, cur = open_db()
    cur.execute("SELECT id FROM users WHERE uname = ?", (u,))
    if cur.fetchone():
        conn.close()
        return False, "Username exists."
    h, salt = hash_val(p)
    now_txt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cur.execute("INSERT INTO users (uname, pw_hash, salt, created_at) VALUES (?, ?, ?, ?)", (u, h, salt, now_txt))
    conn.commit()
    uid = cur.lastrowid
    conn.close()
    return True, {"id": uid, "uname": u}

# login user
def log_user(uname, pw):
    conn, cur = open_db()
    cur.execute("SELECT id, uname, pw_hash, salt FROM users WHERE uname = ?", (uname.strip(),))
    row = cur.fetchone()
    conn.close()
    if not row:
        return False, "Invalid uname."
    if not check_pw(pw.strip(), row[2], row[3]):
        return False, "Wrong password."
    return True, {"id": row[0], "uname": row[1]}

# sentiment lexicon
LEX_MAP = {
    "happy": 1.5, "glad": 1.2, "joy": 1.8, "excited": 1.7, "calm": 1.4,
    "peaceful": 1.6, "grateful": 1.8, "hopeful": 1.5, "relieved": 1.4,
    "productive": 1.5, "motivated": 1.6, "great": 1.6, "good": 1.0,
    "stressed": -1.6, "anxious": -1.5, "worried": -1.3, "overwhelmed": -1.8,
    "exhausted": -1.6, "tired": -1.1, "drained": -1.5, "sad": -1.5,
    "depressed": -1.9, "hopeless": -2.0, "frustrated": -1.5, "angry": -1.7
}

# analyze text
def calc_sent(txt):
    wrds = re.findall(r"\b[a-zA-Z]+\b", txt.lower())
    if not wrds:
        return 0.0, "Neutral", []
    tot = 0.0
    cnt = 0
    neg = False
    emo = {"Joy": 0, "Calm": 0, "Stress": 0, "Anxiety": 0, "Sadness": 0}
    for w in wrds:
        if w in ["not", "never", "no", "cant", "dont"]:
            neg = True
            continue
        if w in LEX_MAP:
            val = LEX_MAP[w]
            if neg:
                val = -val * 0.75
                neg = False
            tot += val
            cnt += 1
            if w in ["happy", "glad", "joy", "excited", "grateful", "good", "great"]:
                emo["Joy"] += 1
            elif w in ["calm", "peaceful", "relieved"]:
                emo["Calm"] += 1
            elif w in ["stressed", "overwhelmed", "exhausted", "drained", "tired"]:
                emo["Stress"] += 1
            elif w in ["anxious", "worried"]:
                emo["Anxiety"] += 1
            elif w in ["sad", "depressed", "hopeless"]:
                emo["Sadness"] += 1
    scr = round(max(-1.0, min(1.0, (tot / cnt) / 1.8)), 2) if cnt > 0 else 0.0
    top_emo = max(emo, key=emo.get)
    if emo[top_emo] == 0:
        if scr > 0.2:
            top_emo = "Joy"
        elif scr < -0.2:
            top_emo = "Stress"
        else:
            top_emo = "Neutral"
    stop = ["this", "that", "with", "have", "from", "tday", "felt", "were"]
    tags = [w for w in wrds if len(w) > 4 and w not in stop]
    tags = list(dict.fromkeys(tags))[:5]
    return scr, top_emo, tags

# calculate pearson r
def calc_r(x, y):
    n = len(x)
    if n < 2 or len(y) != n:
        return 0.0
    mx = sum(x) / n
    my = sum(y) / n
    num = sum((x[i] - mx) * (y[i] - my) for i in range(n))
    dx = sum((val - mx) ** 2 for val in x)
    dy = sum((val - my) ** 2 for val in y)
    denom = sqrt(dx * dy)
    if denom == 0:
        return 0.0
    return round(num / denom, 2)

# calculate burnout risk
def calc_risk(rows):
    if not rows:
        return 0.0, "No Data", ["Log habits for a few days to compute burnout risk."]
    rec = rows[-7:]
    avg_slp = sum(r[6] for r in rec) / len(rec)
    avg_std = sum(r[7] for r in rec) / len(rec)
    avg_mod = sum(r[3] for r in rec) / len(rec)
    avg_eng = sum(r[5] for r in rec) / len(rec)
    avg_exe = sum(r[8] for r in rec) / len(rec)
    scr = 0.0
    fac = []
    if avg_slp < 5.0:
        scr += 30.0
        fac.append("Severe sleep shortage: %s hrs/night" % str(round(avg_slp, 1)))
    elif avg_slp < 6.5:
        scr += 15.0
        fac.append("Sub-optimal sleep: %s hrs/night" % str(round(avg_slp, 1)))
    if avg_std > 8.0:
        scr += 25.0
        fac.append("Heavy study load: %s hrs/day" % str(round(avg_std, 1)))
    if avg_mod < 4.0:
        scr += 25.0
        fac.append("Low mood: %s/10" % str(round(avg_mod, 1)))
    if avg_eng < 2.0:
        scr += 15.0
        fac.append("Low energy: %s/5" % str(round(avg_eng, 1)))
    if avg_exe < 15:
        scr += 10.0
        fac.append("Minimal exercise")
    scr = min(100.0, scr)
    if scr < 25.0:
        cat = "Low Risk (Healthy)"
    elif scr < 50.0:
        cat = "Moderate Risk (Fatigue)"
    elif scr < 75.0:
        cat = "High Risk (Burnout)"
    else:
        cat = "Critical Risk (Distress)"
    return round(scr, 1), cat, fac

# sparkline
def get_spark(vals):
    if not vals:
        return ""
    chrs = [".", "_", "-", "~", "=", "*", "#", "^"]
    out = []
    min_v, max_v = 1.0, 10.0
    for v in vals:
        idx = int(((v - min_v) / (max_v - min_v)) * (len(chrs) - 1))
        idx = max(0, min(len(chrs) - 1, idx))
        out.append(chrs[idx])
    return "".join(out)

# pss10 questionnaire
def take_pss10():
    print("--- Perceived Stress Scale (PSS-10) ---")
    qs = [
        "1. Upset by unexpected event?",
        "2. Unable to control important things?",
        "3. Felt nervous and stressed?",
        "4. Confident handling problems? (Reverse)",
        "5. Things going your way? (Reverse)",
        "6. Could not cope with tasks?",
        "7. Able to control irritations? (Reverse)",
        "8. On top of things? (Reverse)",
        "9. Angered by outside events?",
        "10. Difficulties piling up high?"
    ]
    rev = [3, 4, 6, 7]
    tot = 0
    for i, q in enumerate(qs):
        while True:
            try:
                ans = int(input(q + " (0-4) -> "))
                if 0 <= ans <= 4:
                    tot += (4 - ans) if i in rev else ans
                    break
                print("Enter 0 to 4.")
            except ValueError:
                print("Invalid input.")
    if tot <= 13:
        sev = "Low Stress"
        rec = "Resilience is strong."
    elif tot <= 26:
        sev = "Moderate Stress"
        rec = "Take Pomodoro breaks."
    else:
        sev = "High Stress"
        rec = "Reduce workload."
    return tot, 40, sev, rec

# phq9 questionnaire
def take_phq9():
    print("--- Patient Health Questionnaire (PHQ-9) ---")
    qs = [
        "1. Little interest or pleasure?",
        "2. Feeling down, depressed, hopeless?",
        "3. Trouble with sleep?",
        "4. Feeling tired or low energy?",
        "5. Poor appetite or overeating?",
        "6. Feeling bad about yourself?",
        "7. Trouble concentrating?",
        "8. Noticeably slow or fidgety?",
        "9. Hurting yourself thoughts?"
    ]
    tot = 0
    for q in qs:
        while True:
            try:
                ans = int(input(q + " (0-3) -> "))
                if 0 <= ans <= 3:
                    tot += ans
                    break
                print("Enter 0 to 3.")
            except ValueError:
                print("Invalid input.")
    if tot <= 4:
        sev = "Minimal / None"
        rec = "Within normal healthy range."
    elif tot <= 9:
        sev = "Mild Depression"
        rec = "Regular exercise helps."
    elif tot <= 14:
        sev = "Moderate Depression"
        rec = "Peer support recommended."
    elif tot <= 19:
        sev = "Moderately Severe"
        rec = "Counseling advised."
    else:
        sev = "Severe Depression"
        rec = "Immediate medical support advised."
    return tot, 27, sev, rec

# gad7 questionnaire
def take_gad7():
    print("--- Generalized Anxiety Disorder (GAD-7) ---")
    qs = [
        "1. Feeling nervous or on edge?",
        "2. Not able to stop worrying?",
        "3. Worrying too much?",
        "4. Trouble relaxing?",
        "5. Hard to sit still?",
        "6. Easily annoyed?",
        "7. Feeling afraid?"
    ]
    tot = 0
    for q in qs:
        while True:
            try:
                ans = int(input(q + " (0-3) -> "))
                if 0 <= ans <= 3:
                    tot += ans
                    break
                print("Enter 0 to 3.")
            except ValueError:
                print("Invalid input.")
    if tot <= 4:
        sev = "Minimal Anxiety"
        rec = "Normal baseline limits."
    elif tot <= 9:
        sev = "Mild Anxiety"
        rec = "Try deep breathing."
    elif tot <= 14:
        sev = "Moderate Anxiety"
        rec = "Structured study helps."
    else:
        sev = "Severe Anxiety"
        rec = "Speaking with counselor advised."
    return tot, 21, sev, rec

# log mood record
def log_mood(usr):
    print("--- Log Daily Mood ---")
    tday = datetime.date.tday().strftime("%Y-%m-%d")
    d_in = input("Date (Enter for tday: %s): " % tday).strip()
    log_d = d_in if d_in else tday
    while True:
        try:
            scr = int(input("Mood Score (1-10): "))
            if 1 <= scr <= 10:
                break
            print("Enter 1 to 10.")
        except ValueError:
            print("Enter integer.")
    lbl = input("Mood label (Hopeful, Tired, Stressed, Calm): ").strip()
    if not lbl:
        lbl = "Neutral"
    while True:
        try:
            eng = int(input("Energy Level (1-5): "))
            if 1 <= eng <= 5:
                break
            print("Enter 1 to 5.")
        except ValueError:
            print("Enter integer.")
    while True:
        try:
            slp = float(input("Sleep duration (hours): "))
            if 0 <= slp <= 24:
                break
            print("Enter 0 to 24.")
        except ValueError:
            print("Enter number.")
    while True:
        try:
            std = float(input("Study hours: "))
            if 0 <= std <= 24:
                break
            print("Enter 0 to 24.")
        except ValueError:
            print("Enter number.")
    while True:
        try:
            exe = int(input("Exercise mins: "))
            if 0 <= exe <= 1440:
                break
            print("Invalid mins.")
        except ValueError:
            print("Enter integer.")
    note = input("Reflection note: ").strip()
    conn, cur = open_db()
    cur.execute("INSERT INTO logs (uid, log_date, mood_val, mood_lbl, eng_val, slp_val, std_val, exe_val, note_txt) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (usr["id"], log_d, scr, lbl, eng, slp, std, exe, note))
    conn.commit()
    conn.close()
    print("[OK] Saved mood for %s." % log_d)

# view mood recs
def view_mood(usr):
    conn, cur = open_db()
    cur.execute("SELECT id, uid, log_date, mood_val, mood_lbl, eng_val, slp_val, std_val, exe_val FROM logs WHERE uid = ? ORDER BY log_date ASC", (usr["id"],))
    rows = cur.fetchall()
    conn.close()
    if not rows:
        print("No logs yet.")
        return
    print("----------------------------------------------------------------------")
    print("DATE         | MOOD   | LABEL        | SLEEP  | STUDY  | EXERCISE")
    print("----------------------------------------------------------------------")
    for r in rows[-10:]:
        print("%s   | %s/10  | %-12s | %s h  | %s h  | %s m" % (r[2], r[3], r[4], str(round(r[6], 1)), str(round(r[7], 1)), str(r[8])))
    print("----------------------------------------------------------------------")
    mods = [r[3] for r in rows]
    print("Trend Sparkline: " + get_spark(mods))
    if len(rows) >= 3:
        slp_v = [r[6] for r in rows]
        std_v = [r[7] for r in rows]
        mod_v = [float(r[3]) for r in rows]
        r_slp = calc_r(slp_v, mod_v)
        r_std = calc_r(std_v, mod_v)
        print("Correlations: Sleep vs Mood: %s, Study vs Mood: %s" % (str(r_slp), str(r_std)))

# write journal record
def write_jrn(usr):
    print("--- Reflective Journaling ---")
    ttl = input("Title: ").strip()
    if not ttl:
        ttl = "Reflection on %s" % str(datetime.date.tday())
    text = input("Write thoughts: ").strip()
    if not text:
        print("Empty text.")
        return
    scr, emo, tags = calc_sent(text)
    now_txt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    tag_str = ", ".join(tags)
    conn, cur = open_db()
    cur.execute("INSERT INTO entries (uid, title_txt, body_txt, sent_val, emo_lbl, tag_txt, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)", (usr["id"], ttl, text, scr, emo, tag_str, now_txt))
    conn.commit()
    conn.close()
    print("[OK] Entry saved. Emotion: %s (%s)" % (emo, str(scr)))

# view journal recs
def view_jrn(usr):
    conn, cur = open_db()
    cur.execute("SELECT title_txt, body_txt, sent_val, emo_lbl, tag_txt, created_at FROM entries WHERE uid = ? ORDER BY created_at DESC LIMIT 5", (usr["id"],))
    rows = cur.fetchall()
    conn.close()
    if not rows:
        print("No journal recs.")
        return
    print("----------------------------------------------------------------------")
    for r in rows:
        print("Title: %s | %s | Emotion: %s (%s)" % (r[0], r[5], r[3], str(r[2])))
        print("Content: %s" % r[1])
        print("----------------------------------------------------------------------")

# run psychological test
def run_test(usr):
    print("1. PSS-10 Stress | 2. PHQ-9 Depression | 3. GAD-7 Anxiety | 4. View History")
    ch = input("Choose (1-4): ").strip()
    if ch == "1":
        scr, max_s, sev, rec = take_pss10()
        name = "PSS-10"
    elif ch == "2":
        scr, max_s, sev, rec = take_phq9()
        name = "PHQ-9"
    elif ch == "3":
        scr, max_s, sev, rec = take_gad7()
        name = "GAD-7"
    elif ch == "4":
        conn, cur = open_db()
        cur.execute("SELECT test_name, score_val, max_val, sev_lbl, taken_at FROM tests WHERE uid = ? ORDER BY taken_at DESC", (usr["id"],))
        rows = cur.fetchall()
        conn.close()
        for r in rows:
            print("%s | %s | %s/%s | %s" % (r[4], r[0], r[1], r[2], r[3]))
        return
    else:
        print("Invalid choice.")
        return
    now_txt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn, cur = open_db()
    cur.execute("INSERT INTO tests (uid, test_name, score_val, max_val, sev_lbl, advice_txt, taken_at) VALUES (?, ?, ?, ?, ?, ?, ?)", (usr["id"], name, scr, max_s, sev, rec, now_txt))
    conn.commit()
    conn.close()
    print("Outcome: %s scr %d/%d -> %s" % (name, scr, max_s, sev))

# show burnout risk
def show_risk(usr):
    conn, cur = open_db()
    cur.execute("SELECT id, uid, log_date, mood_val, mood_lbl, eng_val, slp_val, std_val, exe_val FROM logs WHERE uid = ? ORDER BY log_date ASC", (usr["id"],))
    rows = cur.fetchall()
    conn.close()
    scr, cat, fac = calc_risk(rows)
    print("Burnout Risk: %s%% (%s)" % (str(scr), cat))
    for f in fac:
        print(" - " + f)

# export csv file
def export_csv(usr):
    conn, cur = open_db()
    cur.execute("SELECT log_date, mood_val, mood_lbl, eng_val, slp_val, std_val, exe_val, note_txt FROM logs WHERE uid = ? ORDER BY log_date ASC", (usr["id"],))
    rows = cur.fetchall()
    conn.close()
    if not rows:
        print("No logs to export.")
        return
    fnm = "data/%s_export.csv" % usr["uname"]
    with open(fnm, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["Date", "MoodScore", "MoodLabel", "EnergyLevel", "SleepHours", "StudyHours", "ExerciseMins", "Notes"])
        for r in rows:
            w.writerow([r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7] or ""])
    print("[OK] Exported to %s" % fnm)

# dashboard loop
def run_dash(usr):
    while True:
        print("\n--- MindPulse Dashboard: %s ---" % usr["uname"])
        print("1. Log Mood | 2. View History | 3. Write Journal | 4. View Journal")
        print("5. Psychometric Test | 6. Burnout Risk | 7. Export CSV | 8. Logout")
        ch = input("Choose (1-8): ").strip()
        if ch == "1":
            log_mood(usr)
        elif ch == "2":
            view_mood(usr)
        elif ch == "3":
            write_jrn(usr)
        elif ch == "4":
            view_jrn(usr)
        elif ch == "5":
            run_test(usr)
        elif ch == "6":
            show_risk(usr)
        elif ch == "7":
            export_csv(usr)
        elif ch == "8":
            print("Logged out.")
            break

# main application entry
def main():
    init_db()
    print("=== MindPulse Student Wellness System ===")
    while True:
        print("1. Login | 2. Register | 3. Exit")
        ch = input("Select: ").strip()
        if ch == "1":
            u = input("Username: ")
            p = input("Password: ")
            ok, res = log_user(u, p)
            if ok:
                run_dash(res)
            else:
                print(res)
        elif ch == "2":
            u = input("Choose Username: ")
            p = input("Choose Password: ")
            ok, res = reg_user(u, p)
            if ok:
                print("Registered %s! Please log in." % res["uname"])
            else:
                print(res)
        elif ch == "3":
            print("Goodbye!")
            break

if __name__ == "__main__":
    main()