# ==========================================
# Project: מתווך בקליק
# File: exam_manager.py
# Version: 1119
# Last Updated: 2026-02-16 | 14:40
# ==========================================

import streamlit as st
import time
import random
import google.generativeai as genai
import json, re

def ask_ai_for_exam(prompt):
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content(prompt)
        if response and response.text:
            return response.text
        return None
    except Exception as e:
        st.error(f"שגיאת תקשורת: {str(e)}")
        return None

def load_exam_chunk(start_idx, count=5):
    current_moed = st.session_state.get("current_exam_name", "רנדומלי")
    prompt = f"""
    גש ללינק: https://www.reba.org.il/files/
    בחר מבחן רשמי של רשם המתווכים (מועד {current_moed}).
    חלץ את שאלות מספר {start_idx} עד {start_idx + count - 1}.
    וודא שהתשובה הנכונה נלקחת לפי גרסת מבחן רנדומלית (1-4).
    החזר JSON בלבד במבנה הבא: 
    [{{"id": {start_idx}, "q": "שאלה", "options": ["א","ב","ג","ד"], "correct": "תשובה", "explanation": "הסבר"}}]
    """
    res = ask_ai_for_exam(prompt)
    if res:
        try:
            match = re.search(r'\[.*\]', res, re.DOTALL)
            if match:
                return json.loads(match.group())
        except:
            return None
    return None

def init_exam_state():
    if "exam_active" not in st.session_state: st.session_state.exam_active = False
    if "exam_questions" not in st.session_state: st.session_state.exam_questions = []
    if "user_answers" not in st.session_state: st.session_state.user_answers = {}
    if "start_time" not in st.session_state: st.session_state.start_time = None
    if "exam_idx" not in st.session_state: st.session_state.exam_idx = 0

def render_exam_sidebar():
    st.sidebar.title("📌 ניווט בבחינה")
    st.sidebar.markdown(f"### ⏳ זמן נותר: {get_remaining_time()}")
    st.sidebar.write("---")
    for r in range(5):
        cols = st.sidebar.columns(5)
        for c in range(5):
            q_num = r * 5 + c + 1
            idx = q_num - 1
            is_loaded = idx < len(st.session_state.exam_questions)
            if is_loaded:
                label = f"✅ {q_num}" if idx in st.session_state.user_answers else f"{q_num}"
                if cols[c].button(label, key=f"nav_{q_num}"):
                    st.session_state.exam_idx = idx
                    st.rerun()
            else:
                cols[c].button(f"{q_num}", key=f"nav_{q_num}", disabled=True)

def get_remaining_time():
    if st.session_state.start_time is None: return "90:00"
    elapsed = time.time() - st.session_state.start_time
    rem = max(0, 90 * 60 - elapsed)
    m, s = divmod(int(rem), 60)
    return f"{m:02d}:{s:02d}"
