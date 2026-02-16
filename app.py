# ==========================================
# Project: מתווך בקליק
# File: app.py
# Version: 1146
# Last Updated: 2026-02-16 | 23:20
# ==========================================

import streamlit as st
import google.generativeai as genai
import json, re

# --- הגדרות דף ---
st.set_page_config(page_title="מתווך בקליק", layout="wide")

def ask_ai(prompt):
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content(prompt)
        if response and response.text:
            return response.text
        return None
    except Exception:
        return None

# --- לוגיקה ---
def fetch_titles(topic):
    p = (
        f"צור 3 כותרות ספציפיות לתתי-נושאים בתוך {topic}. "
        "החזר JSON בלבד: ['נושא1', 'נושא2', 'נושא3']"
    )
    res = ask_ai(p)
    try:
        match = re.search(r'\[.*\]', res, re.DOTALL)
        return json.loads(match.group())
    except: 
        return ["הוראות חוק מרכזיות", "חובות המתווך", "פסיקה ודוגמאות"]

def fetch_content(main_topic, sub_title):
    p = (
        f"כתוב שיעור מפורט בפורמט Markdown על '{sub_title}' "
        f"בתוך '{main_topic}'. כלול סעיפי חוק ודוגמאות."
    )
    content = ask_ai(p)
    return content if content else "⚠️ לא ניתן לטעון את התוכן כרגע. נסה שוב."

def fetch_question(topic):
    p = (
        f"צור שאלה אמריקאית קצרה על כל נושא {topic}. "
        "מבנה JSON: {'q': 'השאלה', 'options': ['א','ב','ג','ד'], "
        "'correct': 'התשובה המדויקת', 'explain': 'הסבר קצר כולל סעיף חוק'}"
    )
    res = ask_ai(p)
    try:
        match = re.search(r'\{.*\}', res, re.DOTALL)
        return json.loads(match.group())
    except: return None

# --- Session State ---
if "step" not in st.session_state:
    st.session_state.update({
        "step": "login", "user": None, "selected_topic": None,
        "lesson_titles": [], "lesson_contents": {}, "current_sub_idx": None,
        "quiz_active": False, "q_counter": 0, "score": 0,
        "current_q_data": None, "show_feedback": False
    })

# --- CSS ---
st.markdown("""
<style>
    * { direction: rtl; text-align: right; }
    .user-strip { 
        padding: 0; margin-top: -15px; margin-bottom: 20px;
        font-weight: bold; text-align: right; font-size: 1.1em;
    }
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; }
    .nav-box { margin-top: 50px; border-top: 1px solid #ddd; padding-top: 20px; }
</style>
""", unsafe_allow_html=True)

# --- כותרות ---
st.title("🏠 מתווך בקליק")
if st.session_state.user:
    st.markdown(
        f'<div class="user-strip">👤 שלום, {st.session_state.user}</div>', 
        unsafe_allow_html=True
    )

# --- ניתוב ---
if st.session_state.step == 'login':
    u_name = st.text_input("הזן שם מלא:")
    if st.button("כניסה"):
        if u_
