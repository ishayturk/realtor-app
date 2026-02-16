import streamlit as st
import time
import google.generativeai as genai
import json, re

def ask_ai(prompt):
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-2.0-flash')
    response = model.generate_content(prompt)
    return response.text

def generate_lesson_content(topic):
    prompt = f"צור שיעור על {topic} למתווכים. חלק ל-3 תתי נושאים. לכל חלק הוסף שאלה אמריקאית אחת. החזר JSON בלבד עם מפתחות: sub_topics שבו לכל אובייקט יש title, content, question שבו יש q, options, correct"
    res = ask_ai(prompt)
    try:
        match = re.search(r'\{.*\}', res, re.DOTALL)
        if match:
            return json.loads(match.group())
    except:
        return None
    return None

def load_exam_chunk(start_idx, count=5):
    prompt = f"גש ל-https://www.reba.org.il/files/ וחלץ שאלות {start_idx} עד {start_idx+count-1} ממבחן רשמי. החזר JSON בלבד: id, q, options, correct, explanation"
    res = ask_ai(prompt)
    try:
        match = re.search(r'\[.*\]', res, re.DOTALL)
        if match:
            return json.loads(match.group())
    except:
        return None
    return None

def init_exam_state():
    if "step" not in st.session_state: st.session_state.step = "login"
    if "user" not in st.session_state: st.session_state.user = None
    if "exam_questions" not in st.session_state: st.session_state.exam_questions = []
    if "user_answers" not in st.session_state: st.session_state.user_answers = {}
    if "current_sub_idx" not in st.session_state: st.session_state.current_sub_idx = 0
    if "lesson_data" not in st.session_state: st.session_state.lesson_data = None
    if "start_time" not in st.session_state: st.session_state.start_time = None
    if "exam_idx" not in st.session_state: st.session_state.exam_idx = 0

def get_remaining_time():
    if "start_time" not in st.session_state or st.session_state.start_time is None:
        return "90:00"
    elapsed = time.time() - st.session_state.start_time
    rem = max(0, 90 * 60 - elapsed)
    m, s = divmod(int(rem), 60)
    return f"{m:02d}:{s:02d}"
