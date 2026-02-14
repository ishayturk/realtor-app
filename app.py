import streamlit as st
import google.generativeai as genai
import re
import time

# 1. הגדרות עיצוב RTL, לוגו מוגדל ואיפוס גלילה
st.set_page_config(page_title="מתווך בקליק", layout="wide")

st.markdown("""
    <style>
    .sidebar-logo {
        font-size: 34px !important; 
        font-weight: bold;
        text-align: center;
        margin-top: -60px !important; 
        color: #1E88E5;
        padding-bottom: 10px;
    }
    html, body, [data-testid="stAppViewContainer"], .main, .block-container {
        direction: rtl !important;
        text-align: right !important;
    }
    .stMarkdown, .stMarkdown p, .stMarkdown li {
        direction: rtl !important;
        text-align: right !important;
    }
    div.stButton > button { 
        width: 100%; border-radius: 8px; font-weight: bold;
        background-color: #1E88E5; color: white;
    }
    .quiz-card { 
        background-color: #ffffff; padding: 20px; border-radius: 12px; 
        border-right: 6px solid #1E88E5; box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    </style>
    <script>
        function forceScrollUp() {
            var mainSec = window.parent.document.querySelector('section.main');
            if (mainSec) { mainSec.scrollTo({top: 0, behavior: 'instant'}); }
        }
        forceScrollUp();
    </script>
    """, unsafe_allow_html=True)

# 2. ניהול משתני מערכת
if "user_name" not in st.session_state: st.session_state.user_name = ""
if "view_mode" not in st.session_state: st.session_state.view_mode = "login"
if "lesson_data" not in st.session_state: st.session_state.lesson_data = ""
if "quiz_data" not in st.session_state: st.session_state.quiz_data = []
if "history" not in st.session_state: st.session_state.history = []
if "lesson_count" not in st.session_state: st.session_state.lesson_count = 0
if "user_answers" not in st.session_state: st.session_state.user_answers = {}
if "current_topic" not in st.session_state: st.session_state.current_topic = ""

# חיבור ל-AI
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-2.0-flash')

def parse_quiz(quiz_text):
    questions = []
    raw_questions = re.findall(r"\[START_Q\](.*?)\[END_Q\]", quiz_text, re.DOTALL)
    for q_block in raw_questions:
        try:
            q_text = re.search(r"\[QUESTION\](.*?)\[OPTIONS\]", q_block, re.DOTALL).group(1).strip()
            opts_text = re.search(r"\[OPTIONS\](.*?)\[ANSWER\]", q_block, re.DOTALL).group(1).strip()
            ans_val = re.search(r"\[ANSWER\](.*?)\[LAW\]", q_block, re.DOTALL).group(1).strip()
            law_val = re.search(r"\[LAW\](.*?)$", q_block, re.DOTALL).group(1).strip()
            options = [re.sub(r"^\d+[\s\).\-]+", "", opt.strip()) for opt in opts_text.split('\n') if opt.strip()]
            questions.append({
                "q": q_text, "options": options[:4],
                "correct": int(re.search(r'\d', ans_val).group()) - 1, "ref": law_val
            })
        except: continue
    return questions

# 3. סרגל צידי (Sidebar)
if st.session_state.user_name:
    with st.sidebar:
        st.markdown('<div class="sidebar-logo">🎓 מתווך בקליק</div>',
