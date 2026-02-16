# ==========================================
# Project: מתווך בקליק
# File: app.py
# Version: 1152
# Last Updated: 2026-02-16 | 23:55
# ==========================================

import streamlit as st
import google.generativeai as genai
import json, re

# --- הגדרות דף ---
st.set_page_config(page_title="מתווך בקליק", layout="wide")

# אנקור לראש הדף
st.markdown('<div id="top"></div>', unsafe_allow_html=True)

def ask_ai(prompt):
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content(prompt)
        return response.text if (response and response.text) else None
    except: return None

# --- לוגיקה ---
def fetch_titles(topic):
    p = f"צור 3 כותרות לתתי-נושאים בתוך {topic}. JSON: ['א','ב','ג']"
    res = ask_ai(p)
    try:
        match = re.search(r'\[.*\]', res, re.DOTALL)
        titles = json.loads(match.group())
        # וידוא שכל כותרת היא טקסט ולא None
        return [str(t) for t in titles if t]
    except: return ["שיעור א", "שיעור ב", "שיעור ג"]

def fetch_content(main_topic, sub_title):
    p = (f"כתוב שיעור Markdown על '{sub_title}' בתוך '{main_topic}'. "
         "בלי הסברים על המבנה. רק תוכן מקצועי.")
    content = ask_ai(p)
    return content if content else "⚠️ שגיאה בטעינת התוכן."

def fetch_question(topic):
    p = (f"צור שאלה אמריקאית על {topic}. "
         "JSON: {{'q':'..','options':['..'],'correct':'..','explain':'..'}}")
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
    /* ריווח מוגדל בין הכותרת לשם המשתמש */
    .user-strip { 
        margin-top: 40px; 
        margin-bottom: 30px; 
        font-weight: bold; 
        color: #444;
        font-size: 1.1em;
    }
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# --- כותרות ---
st.title("🏠 מתווך בקליק")
if st.session_state.user:
    st.markdown(f'<div class="user-strip">👤 שלום, {st.session_state.user}</div>', 
                unsafe_allow_html=True)

# --- ניתוב ---
if st.session_state.step == 'login':
    u_name = st.text_input("הזן שם מלא:")
    if st.button("כניסה"):
        if u_name:
            st.session_state.user = u_name
            st.session_state.step = 'menu'
            st.rerun()

elif st.session_state.step == 'menu':
    c1, c2 = st.columns(2)
    if c1.button("📚 לימוד לפי נושאים"):
        st.session_state.step = 'study'; st.rerun()
    if c2.button("⏱️ סימולציית בחינה"): st.info("בפיתוח...")

elif st.session_state.step == 'study':
    topics = ["בחר נושא...", "חוק המתווכים במקרקעין", "חוק המקרקעין", 
              "חוק המכר (דירות)", "חוק החוזים", "חוק הגנת הצרכן"]
    sel = st.selectbox("נושא לימוד:", topics)
    if sel != "בחר נושא..." and st.button("טען שיעור"):
        st.session_state.update({
            "selected_topic": sel, "lesson_titles": fetch_titles(sel),
            "lesson_contents": {}, "current_sub_idx": None,
            "quiz_active": False, "step": "lesson_run"
        })
