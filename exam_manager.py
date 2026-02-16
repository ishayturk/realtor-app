# ==========================================
# Project: מתווך בקליק
# File: exam_manager.py
# Version: 1124
# Last Updated: 2026-02-16 | 18:25
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
            st.warning("⚠️ עומס זמני ב-AI. אנא נסה ללחוץ שוב בעוד דקה.")
        return None

def get_lesson_titles(topic):
    prompt = f"צור 3 כותרות לפרקים בשיעור על {topic} עבור מתווכים. החזר JSON בלבד: ['כותרת1', 'כותרת2', 'כותרת3']"
    res = ask_ai(prompt)
    try:
        match = re.search(r'\[.*\]', res, re.DOTALL)
        return json.loads(match.group())
    except: return ["חלק א'", "חלק ב'", "חלק ג'"]

def get_sub_topic_content(main_topic, sub_title):
    """ייצור תוכן מעמיק ומפורט ללימוד לבחינה"""
    prompt = f"""
    כתוב שיעור מקצועי ומפורט מאוד על '{sub_title}' כחלק מהנושא הכללי '{main_topic}'.
    התוכן מיועד למתכוננים לבחינת רשם המתווכים.
    דרישות:
    1. הסבר מפורט על סעיפי החוק הרלוונטיים.
    2. הבא דוגמאות מעשיות (Case Studies) מעולם התיווך.
    3. השתמש בפורמט Markdown ברור (בולטים, כותרות משנה, הדגשות).
    4. וודא שהחומר מספק ומקיף לצורך הבנת הנושא לעומק.
    """
    return ask_ai(prompt)

def get_topic_exam_questions(topic):
    prompt = f"צור 10 שאלות אמריקאיות ברמה גבוהה על {topic}. לכל שאלה: q, options, correct. החזר JSON בלבד."
    res = ask_ai(prompt)
    try:
        match = re.search(r'\[.*\]', res, re.DOTALL)
        return json.loads(match.group())
    except: return []

def init_exam_state():
    defaults = {
        "step": "login", "user": None, "selected_topic": None,
        "lesson_titles": [], "lesson_contents": {}, "current_sub_idx": None,
        "show_topic_exam": False, "topic_exam_questions": [],
        "exam_active": False, "current_exam_q_idx": 0
    }
    for k, v in defaults.items():
        if k not in st.session_state: st.session_state[k] = v
