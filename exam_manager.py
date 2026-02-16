# ==========================================
# Project: מתווך בקליק
# File: exam_manager.py
# Version: 1121
# Last Updated: 2026-02-16 | 15:10
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
        return response.text if response else None
    except Exception as e:
        st.error(f"שגיאת תקשורת: {str(e)}")
        return None

# לוגיקה למבחן רשמי (25 שאלות)
def load_exam_chunk(start_idx, count=5):
    current_moed = st.session_state.get("current_exam_name", "רנדומלי")
    prompt = f"""
    גש ללינק: https://www.reba.org.il/files/
    בחר מבחן רשמי מועד {current_moed}. חלץ שאלות {start_idx}-{start_idx + count - 1}.
    החזר JSON בלבד: [{{'id': {start_idx}, 'q': '', 'options': ['', '', '', ''], 'correct': '', 'explanation': ''}}]
    """
    res = ask_ai(prompt)
    if res:
        try:
            match = re.search(r'\[.*\]', res, re.DOTALL)
            return json.loads(match.group()) if match else None
        except: return None
    return None

# לוגיקה לשיעורים (גרסה 1118)
def generate_lesson_content(topic):
    prompt = f"""
    צור שיעור על '{topic}' למתווכי נדל"ן.
    חלק את התוכן ל-3 תתי-נושאים ברורים.
    עבור כל תת-נושא, הוסף שאלה אמריקאית אחת לתרגול מיידי.
    החזר בפורמט JSON בלבד:
    {{
      "sub_topics": [
        {{"title": "נושא 1", "content": "תוכן...", "question": {{"q": "...", "options": ["","","",""], "correct": "..."}}}},
        {{"title": "נושא 2", "content": "תוכן...", "question": {{"q": "...", "options": ["","","",""], "correct": "..."}}}},
        {{"title": "נושא 3", "content": "תוכן...", "question": {{"q": "...", "options": ["","","",""], "correct": "..."}}}}
      ]
    }}
    """
    res = ask_ai(prompt)
    if res:
        try:
            match = re.search(r'\{.*\}', res, re.DOTALL)
            return json.loads(match.group()) if match else None
        except: return None
    return None

def init_exam_state():
    defaults = {
        "exam_active": False, "exam_questions": [], "user_answers": {}, 
        "start_time": None, "exam_idx": 0, "step": "login",
        "lesson_data": None, "current_sub_idx": 0, "lesson_answers": {}
    }
    for k, v in defaults.items():
        if k not in st.session_state: st.session_state[k] = v

def render_exam_sidebar():
    st.sidebar.title("📌 ניווט")
    if st.session_state.start_time:
        st.sidebar.markdown(f"### ⏳ {get_remaining_time()}")
    st.sidebar.write("---")
    # ... (כפתורי הניווט של המבחן)

def get_remaining_time():
    if not st.session_state.start_time: return "90:00"
    elapsed = time.time() - st.session_state.start_time
    rem = max(0, 90 * 60 - elapsed)
    return f"{int(rem//60):02d}:{int(rem%60):02d}"
