# ==========================================
# Project: מתווך בקליק
# File: exam_manager.py
# Version: 1122
# Last Updated: 2026-02-16 | 15:15
# ==========================================

import streamlit as st
import time
import google.generativeai as genai
import json, re

def ask_ai(prompt):
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        if "429" in str(e) or "ResourceExhausted" in str(e):
            st.warning("⚠️ מכסת הבקשות ל-AI הסתיימה זמנית (Quota). אנא המתן דקה ונסה שוב.")
        else:
            st.error(f"שגיאה בתקשורת: {str(e)}")
        return None

def generate_lesson_content(topic):
    prompt = f"צור שיעור על {topic} למתווכים. חלק ל-3 תתי נושאים. לכל חלק הוסף שאלה אמריקאית אחת. החזר JSON בלבד עם מפתחות: sub_topics (title, content, question (q, options, correct))"
    res = ask_ai(prompt)
    if not res: return None
    try:
        match = re.search(r'\{.*\}', res, re.DOTALL)
        return json.loads(match.group()) if match else None
    except:
        return None

def load_exam_chunk(start_idx, count=5):
    prompt = f"גש ל-https://www.reba.org.il/files/ וחלץ שאלות {start_idx} עד {start_idx+count-1} ממבחן רשמי. החזר JSON בלבד: id, q, options, correct, explanation"
    res = ask_ai(prompt)
    if not res: return None
    try:
        match = re.search(r'\[.*\]', res, re.DOTALL)
        return json.loads(match.group()) if match else None
    except:
        return None

def init_exam_state():
    defaults = {
        "step": "login", "user": None, "exam_questions": [], 
        "user_answers": {}, "current_sub_idx": 0, "lesson_data": None,
        "start_time": None, "exam_idx": 0
    }
    for k, v in defaults.items():
        if k not in st.session_state: st.session_state[k] = v

def get_remaining_time():
    if "start_time" not in st.session_state or st.session_state.start_time is None:
        return "90:00"
    elapsed = time.time() - st.session_state.start_time
    rem = max(0, 90 * 60 - elapsed)
    m, s = divmod(int(rem), 60)
    return f"{m:02d}:{s:02d}"
