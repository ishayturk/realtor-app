# גרסה: 1097 | תאריך: 16/02/2026 | שעה: 10:55 | סטטוס: תיקון מסך כניסה (Login) ושמירה על מהירות

import streamlit as st
import google.generativeai as genai
import json, re, time

st.set_page_config(page_title="מתווך בקליק", layout="centered")

# עיצוב UI
st.markdown("""
<style>
    * { direction: rtl !important; text-align: right !important; }
    .stApp { background-color: #ffffff; }
    .welcome-text { color: #1E88E5; font-weight: bold; margin-bottom: 10px; }
    .lesson-title { color: #1E88E5; border-bottom: 2px solid #1E88E5; padding-bottom: 10px; margin-bottom: 20px; font-size: 1.8rem; }
    .lesson-box { 
        background-color: #f9f9f9; padding: 30px; 
        border-right: 6px solid #1E88E5; border-radius: 4px; 
        line-height: 1.8; font-size: 1.1rem;
    }
    .question-card { background-color: #ffffff; padding: 25px; border: 1px solid #e0e0e0; border-radius: 12px; margin-bottom: 20px; }
    .stButton>button { width: auto; min-width: 140px; }
    .version-footer { color: #bbbbbb; font-size: 0.7rem; text-align: center !important; margin-top: 50px; }
</style>
""", unsafe_allow_html=True)

# אתחול קשיח של Session State
if 'step' not in st.session_state:
    st.session_state.step = 'login'
if 'user' not in st.session_state:
    st.session_state.user = ''
if 'sub_topics' not in st.session_state:
    st.session_state.sub_topics = []
if 'lt' not in st.session_state:
    st.session_state.lt = ''
if 'current_topic' not in st.session_state:
    st.session_state.current_topic = ''
if 'current_sub' not in st.session_state:
    st.session_state.current_sub = ''
if 'qq' not in st.session_state:
    st.session_state.qq = []
if 'qi' not in st.session_state:
    st.session_state.qi = 0
if 'score' not in st.session_state:
    st.session_state.score = 0
if 'answered' not in st.session_state:
    st.session_state.answered = False

S = st.session_state

# פונקציית תקשורת
def fetch_content(prompt):
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-2.0-flash')
    try:
        r = model.generate_content(prompt)
        return r.text
    except: return None

# מפת נושאים מהירה
TOPIC_MAP = {
    "חוק המתווכים במקרקעין": ["דרישת הכתב ופעולה יעילה", "איסור פעולות משפטיות", "דמי תיווך ובלעדיות"],
    "חוק המקרקעין": ["סוגי בעלות ושיתוף", "עסקאות ורישום בטאבו", "הערות אזהרה"],
    "חוק המכר (דירות)": ["מפרט המכר", "תקופת בדק ואחריות", "חובת גילוי של המוכר"],
    "אתיקה מקצועית": ["חובת הגינות וזהירות", "ניגוד עניינים", "פרסום והתנהגות מקצועית"],
    "חוק החוזים": ["הצעה וקיבול", "טעות והטעיה", "תרופות בשל הפרת חוזה"],
    "מיסוי מקרקעין": ["מס שבח", "מס רכישה", "פטורים לדירה יחידה"]
}

st.title("🏠 מתווך בקליק")

# --- לוגיקת צעדים ---

if S.step == "login":
    st.write("### ברוכים הבאים! אנא הזדהו כדי להתחיל.")
    u_input = st.text_input("שם מלא:")
    if st.button("כניסה למערכת"):
        if u_input:
            S.user = u_input
            S.step = "menu"
            st.rerun()
        else:
            st.warning("יש להזין שם כדי להמשיך.")

elif S.step == "menu":
    st.markdown(f"<h2 class='welcome-text'>שלום, {S.user}</h2>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.
