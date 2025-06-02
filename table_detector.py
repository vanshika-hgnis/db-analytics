# table_detector.py
import re
import difflib

def normalize(text):
    return re.sub(r'[^a-zA-Z0-9]', '', text.lower())

def detect_relevant_tables(user_question, all_tables):
    detected = []
    q = normalize(user_question)

    for table in all_tables:
        table_clean = normalize(table)

        # Check exact substring match (tolerate "schedule parameters" vs "ScheduleParameters")
        if table_clean in q:
            detected.append(table)
            continue

        # Apply fuzzy match fallback
        ratio = difflib.SequenceMatcher(None, table_clean, q).ratio()
        if ratio > 0.6:
            detected.append(table)

    return list(set(detected))
