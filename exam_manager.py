# ==========================================
# Project: מתווך בקליק
# File: exam_manager.py
# Version: 1123
# Last Updated: 2026-02-16 | 17:40
# ==========================================

import streamlit as st
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
            st.warning("⚠️ מכסת ה-AI הסתיימה זמנית. אנא המתן דקה ונסה שוב.")
        else:
            st.error(f"שגיאת תקשורת: {str(e)}")
        return None

def get_lesson_titles(topic):
    """מייצר 3 כותרות לתתי-נושאים"""
    prompt = f"צור 3 כותרות קצרות ומקצועיות לתתי-נושאים בתוך הנושא: {topic} עבור מתווכי מקרקעין. החזר JSON בלבד: ['כותרת1', 'כותרת2', 'כותרת3']"
    res = ask_ai(prompt)
    if not res: return ["חלק א'", "חלק ב'", "חלק ג'"]
    try:
        match = re.search(r'\[.*\]', res, re.DOTALL)
        return json.loads(match.group())
    except: return ["חלק א'", "חלק ב'", "חלק ג'"]

def get_sub_topic_content(main_topic, sub_title):
    """מייצר תוכן מפורט לתת-נושא ספציפי"""
    prompt = f"כתוב תוכן לימודי מקצועי, מעמיק ומפורט בפורמט Markdown על הנושא '{sub_title}' כחלק מהשיעור הכללי על '{main_topic}'. התמקד בחוק ובתקנות הרלוונטיים לישראל."
    return ask_ai(prompt)

def get_topic_exam_questions(topic):
    """מייצר 10 שאלות על הנושא הכללי"""
    prompt = f"צור 10 שאלות אמריקאיות קשות ומאתגרות על {topic}. לכל שאלה: q (השאלה), options (4 אפשרויות), correct (התשובה המדויקת). החזר JSON בלבד."
    res = ask_ai(prompt)
    if not res: return []
    try:
        match = re.search(r'\[.*\]', res, re.DOTALL)
        return json.loads(match.group())
    except: return []

def init_exam_state():
    defaults = {
        "step": "login", "user": None, "selected_topic": None,
        "lesson_titles": [], "lesson_contents": {}, "current_sub_idx": None,
        "show_topic_exam": False, "topic_exam_questions": [],
        "exam_questions": [], "user_answers": {}, "current_exam_q_idx": 0,
        "exam_active": False
    }
    for k, v in defaults.items():
        if k not in st.session_state: st.session_state[k] = v
