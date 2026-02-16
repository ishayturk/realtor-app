# ==========================================
# Project: מתווך בקליק
# File: app.py
# Version: 1141
# Last Updated: 2026-02-16 | 22:15
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
    p = f"צור 3 כותרות ספציפיות ומקצועיות לתתי-נושאים בתוך {topic}. אל תשתמש במילים כלליות. החזר JSON בלבד: ['נושא1', 'נושא2', 'נושא3']"
    res = ask_ai(p)
    try:
        match = re.search(r'\[.*\]', res, re.DOTALL)
        return json.loads(match.group())
    except: 
        return ["הוראות חוק מרכזיות", "חובות ואיסורים", "פסיקה רלוונטית"]

def fetch_content(main_topic, sub_title):
    p = f"כתוב שיעור מפורט בפורמט Markdown על '{sub_title}' בתוך '{main_topic}'. כלול סעיפי חוק ודוגמאות."
    content = ask_ai(p)
    return content if content else "⚠️ שגיאה בטעינת התוכן. נסה ללחוץ שוב על כפתור הנושא."

def fetch_single_question(topic):
    p = f"צור שאלה אמריקאית אחת על {topic}. מבנה JSON: {{'q': '...', 'options': ['...','...','...','...'], 'correct': '...'}}"
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
        "quiz_active": False, "current_q_data": None, "next_q_buffer": None,
        "q_counter": 0, "score": 0
    })

# --- CSS (Dark Mode & Right Align) ---
st.markdown("""
<style>
    * { direction: rtl; text-align: right; }
    .user-strip { 
        background-color: transparent; 
        padding: 0; margin-top: -15px; margin-bottom: 20px;
        font-weight: bold; text-align: right; color: inherit;
        font-size: 1.1em;
    }
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; }
    [data-testid="stSidebar"] { direction: rtl; }
</style>
""", unsafe_allow_html=True)

# --- כותרות בראש הדף ---
st.title("🏠 מתווך בקליק")
if st.session_state.user:
    st.markdown(f'<div class="user-strip">👤 שלום, {st.session_state.user}</div>', unsafe_allow_html=True)

# --- ניתוב דפים ---
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
        st.session_state.step = 'study'
        st.rerun()
    if c2.button("⏱️ סימולציית בחינה"):
        st.info("בפיתוח...")

elif st.session_state.step == 'study':
    all_topics = [
        "בחר נושא מהרשימה...", "חוק המתווכים במקרקעין", "תקנות המתווכים (פרטי הזמנה)", 
        "תקנות המתווכים (פעולות שיווק)", "חוק המקרקעין", "חוק הגנת הדייר", 
        "חוק המכר (דירות)", "חוק החוזים (חלק כללי)", "חוק החוזים (תרופות)", 
        "חוק הגנת הצרכן", "חוק עבירות עונשין", "חוק שמאי מקרקעין", 
        "חוק התכנון והבנייה", "חוק מיסוי מקרקעין", "חוק הירושה", 
        "חוק הוצאה לפועל", "פקודת הנזיקין"
    ]
    sel = st.selectbox("נושא לימוד:", all_topics
