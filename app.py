import streamlit as st
import google.generativeai as genai
import time

# --- 1. הגדרות תצוגה RTL ---
st.set_page_config(page_title="מתווך בקליק", layout="centered")

st.markdown("""
    <style>
    [data-testid="stAppViewContainer"], .main, .block-container { direction: rtl !important; text-align: right !important; }
    h1, h2, h3, h4 { text-align: center !important; color: #1E88E5; width: 100%; }
    .stButton > button { width: 100%; font-weight: bold; height: 3.5em; border-radius: 10px; }
    .lesson-box { 
        background: #ffffff; padding: 25px; border-radius: 15px; 
        border-right: 6px solid #1E88E5; box-shadow: 0 4px 12px rgba(0,0,0,0.1); 
        line-height: 1.8; color: #333; text-align: right; direction: rtl; margin-bottom: 25px;
    }
    .explanation-box { padding: 15px; border-radius: 10px; margin-top: 10px; border-right: 5px solid; font-size: 0.95em; text-align: right; }
    .success { background-color: #e8f5e9; border-color: #4caf50; color: #2e7d32; }
    .error { background-color: #ffebee; border-color: #f44336; color: #c62828; }
    .source-tag { font-weight: bold; color: #1565c0; }
    div[role="radiogroup"] { direction: rtl !important; text-align: right !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. אתחול משתנים ---
if "step" not in st.session_state:
    st.session_state.update({
        "step": "login", "user": "", "lesson_text": "",
        "quiz_active": False, "quiz_idx": 0, "quiz_answers": {}, "quiz_questions": [], "quiz_done": False,
        "checked_questions": set()
    })

# --- 3. לוגיקה ---
st.markdown("<h1>🏠 מתווך בקליק</h1>", unsafe_allow_html=True)

if st.session_state.step == "login":
    name = st.text_input("הכנס שם מלא:")
    if st.button("כניסה"):
        if name:
            st.session_state.user = name
            st.session_state.step = "menu"
            st.rerun()

elif st.session_state.step == "menu":
    st.markdown(f"### שלום, {st.session_state.user} 👋")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📚 לימוד עיוני + שאלון"):
            st.session_state.step = "study"
            st.rerun()
    with col2:
        if st.button("📝 סימולציית בחינה (25 שאלות)"):
             st.info("סימולציה מלאה")

elif st.session_state.step == "study":
    topic = st.selectbox("בחר נושא:", ["חוק המתווכים", "חוק המקרקעין", "חוק החוזים"])
    
    if not st.session_state.lesson_text:
        if st.button("📖 התחל שיעור"):
            try:
                genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                model = genai.GenerativeModel('gemini-2.0-flash')
                response = model.generate_content(f"כתוב שיעור מפורט על {topic} למבחן המתו
