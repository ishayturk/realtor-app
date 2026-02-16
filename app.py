# ==========================================
# Project: מתווך בקליק
# File: app.py
# Version: 1133
# Last Updated: 2026-02-16 | 20:20
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
        return response.text
    except Exception as e:
        if "429" in str(e): st.warning("⚠️ עומס במערכת. נסה שוב בעוד דקה.")
        return None

# --- לוגיקת תוכן ושאלות ---
def fetch_titles(topic):
    p = f"צור 3 כותרות קצרות (2-3 מילים) לתתי-נושאים בתוך {topic}. ללא המילים 'חלק' או 'פרק'. החזר JSON בלבד: ['כותרת1', 'כותרת2', 'כותרת3']"
    res = ask_ai(p)
    try:
        match = re.search(r'\[.*\]', res, re.DOTALL)
        return json.loads(match.group())
    except: return ["הגדרות וסמכויות", "חובות המתווך", "פסיקה ויישום"]

def fetch_content(main_topic, sub_title):
    p = f"כתוב שיעור מפורט בפורמט Markdown על '{sub_title}' בתוך '{main_topic}'. כלול סעיפי חוק ודוגמאות."
    return ask_ai(p)

def fetch_single_question(topic):
    p = f"צור שאלה אמריקאית אחת קשה על {topic}. לכל שאלה: q (שאלה), options (רשימת 4 אפשרויות), correct (התשובה המדויקת). החזר JSON בלבד."
    res = ask_ai(p)
    try:
        match = re.search(r'\{.*\}', res, re.DOTALL)
        return json.loads(match.group())
    except: return None

# --- ניהול Session State ---
if "step" not in st.session_state:
    st.session_state.update({
        "step": "login", "user": None, "selected_topic": None,
        "lesson_titles": [], "lesson_contents": {}, "current_sub_idx": None,
        "quiz_active": False, "current_q_data": None, "next_q_buffer": None,
        "q_counter": 0, "score": 0, "user_choice": None
    })

# --- CSS ---
st.markdown("""
<style>
    * { direction: rtl; text-align: right; }
    .user-strip { background-color: rgba(255,255,255,0.1); padding: 10px; border-radius: 8px; margin-bottom: 20px; font-weight: bold; text-align: left; border: 1px solid #ddd; }
    .stButton>button { width: 100%; border-radius: 8px; height: 3.5em; font-weight: bold; }
    .question-box { background-color: #f9f9f9; padding: 20px; border-radius: 10px; border: 1px solid #eee; margin-top: 20px; }
</style>
""", unsafe_allow_html=True)

if st.session_state.user:
    st.markdown(f'<div class="user-strip">👤 שלום, {st.session_state.user}</div>', unsafe_allow_html=True)

st.title("🏠 מתווך בקליק")

# --- ניתוב דפים ---

if st.session_state.step == 'login':
    u_name = st.text_input("הזן שם מלא:")
    if st.button("כניסה"):
        if u_name: st.session_state.user = u_name; st.session_state.step = 'menu'; st.rerun()

elif st.session_state.step == 'menu':
    c1, c2 = st.columns(2)
    if c1.button("📚 לימוד לפי נושאים"): st.session_state.step = 'study'; st.rerun()
    if c2.button("⏱️ סימולציית בחינה"): st.session_state.step = 'exam_run'; st.rerun()

elif st.session_state.step == 'study':
    all_topics = ["בחר נושא...", "חוק המתווכים במקרקעין", "חוק המקרקעין", "ח
