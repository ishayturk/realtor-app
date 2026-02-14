import streamlit as st
import google.generativeai as genai
import re

# 1. עיצוב ויישור
st.set_page_config(page_title="מתווך בקליק", layout="wide")

st.markdown("""
<style>
html, body, [data-testid="stAppViewContainer"], .main, .block-container, 
div[data-testid="stMarkdownContainer"], h1, h2, h3, p, li, span, label {
    direction: rtl !important; text-align: right !important;
}
.sidebar-logo {
    font-size: 34px !important; font-weight: bold; text-align: center !important;
    margin-top: -50px !important; color: #1E88E5; display: block; width: 100%;
}
[data-testid="stSidebar"] button, div.stButton > button {
    width: 100% !important; border-radius: 8px; font-weight: bold;
    background-color: #1E88E5; color: white;
}
.quiz-card { 
    background-color: #f9f9f9; padding: 20px; border-radius: 12px; 
    border-right: 6px solid #1E88E5; margin-bottom: 20px;
}
</style>
""", unsafe_allow_html=True)

# 2. נושאים ומשתנים
TOPICS = [
    "בחר נושא...",
    "חוק המתווכים במקרקעין",
    "חוק המקרקעין",
    "חוק המכר (דירות)",
    "חוק הגנת הצרכן",
    "חוק החוזים",
    "דיני תכנון ובנייה",
    "מיסוי מקרקעין",
    "חוק העונשין",
    "חוק שמאי מקרקעין"
]

if "user_name" not in st.session_state: st.session_state.user_name = ""
if "view_mode" not in st.session_state: st.session_state.view_mode = "login"
if "lesson_data" not in st.session_state: st.session_state.lesson_data = ""
if "quiz_data" not in st.session_state: st.session_state.quiz_data = []
if "history" not in st.session_state: st.session_state.history = []
if "current_topic" not in st.session_state: st.session_state.current_topic = ""
if "quiz_ready" not in st.session_state: st.session_state.quiz_ready = False

if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-2.0-flash')

def parse_quiz(text):
    qs = []
    blocks = re.findall(r"\[START_Q\](.*?)\[END_Q\]", text, re.DOTALL)
    for b in blocks:
        try:
            q = re.search(r"\[QUESTION\](.*?)\[OPTIONS\]", b, re.DOTALL).group(1).strip()
            opts_raw = re.search(r"\[OPTIONS\](.*?)\[ANSWER\]", b, re.DOTALL).group(1).strip()
            ans_val = re.search(r"\[ANSWER\](.*?)(?:\[LAW\]|$)", b, re.DOTALL).group(1).strip()
            law_val = re.search(r"\[LAW\](.*?)$", b, re.DOTALL).group(1).strip()
            opts = [re.sub(r"^\d+[\s\).\-]+", "", o.strip()) for o in opts_raw.split('\n') if o.strip()]
            idx = int(re.search(r'\d', ans_val).group()) - 1
            qs.append({"q": q, "options": opts[:4], "correct": idx, "ref": law_val})
        except: continue
    return qs

# 3. סרגל צידי
if st.session_state.user_name:
    with st.sidebar:
        st.markdown('<div class="sidebar-logo">🎓 מתווך בקליק</div>', unsafe_allow_html=True)
        st.write(f"שלום, **{st.session_state.user_name}**")
        if st.button("➕ נושא חדש"):
            st.session_state.view_mode = "setup"
            st.session_state.current_topic = ""
            st.session_state.quiz_ready = False
            st.rerun()
        if st.session_state.current_topic:
            st.markdown(f"**נושא: {st.session_state.current_topic}**")
            if st.session_state.view_mode == "quiz":
                if st.button("📖 חזרה לשיעור"):
                    st.session_state.view_mode = "lesson"; st.rerun()
            if st.session_state.quiz_ready and st.session_state.view_mode != "quiz":
                if st.button("📝 מעבר למבחן"):
                    st.session_state.view_mode = "quiz"; st.rerun()
        st.markdown("---")
        for h in st.session_state.history: st.caption(f"• {h}")

# 4. ניהול דפים
m = st.session_state.view_
