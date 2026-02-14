import streamlit as st
import google.generativeai as genai
import re
import time

# 1. הגדרות עיצוב ו-RTL - תיקון כפתורים
st.set_page_config(page_title="מתווך בקליק", layout="wide")

st.markdown("""
    <style>
    /* כפיית כיוון ימין-לשמאל על כל האפליקציה */
    .stApp, .main, .block-container { 
        direction: rtl !important; 
        text-align: right !important; 
    }
    
    /* הצמדת כפתורים לימין - כולל כפתור הכניסה */
    div.stButton {
        text-align: right !important;
        display: flex;
        justify-content: flex-start; /* בימין בגלל ה-RTL */
    }

    div.stButton > button { 
        width: 100%; 
        max-width: 400px; /* הגבלת רוחב כדי שלא ימתח מדי */
        border-radius: 8px; 
        height: 3em; 
        background-color: #1E88E5; 
        color: white; 
        font-weight: bold;
        margin-right: 0 !important;
        margin-left: auto !important;
    }

    /* תיקון שדות קלט (Input) */
    .stTextInput > div > div > input {
        text-align: right !important;
        direction: rtl !important;
    }

    [data-testid="stSidebar"] { direction: rtl; text-align: right; }
    h1, h2, h3, p, li, span, label { direction: rtl !important; text-align: right !important; }
    
    .quiz-card { 
        background-color: #f9f9f9; 
        padding: 20px; 
        border-radius: 12px; 
        border-right: 5px solid #1E88E5;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. ניהול הזיכרון (Session State)
if "user_name" not in st.session_state: st.session_state.user_name = ""
if "view_mode" not in st.session_state: st.session_state.view_mode = "login"
if "lesson_data" not in st.session_state: st.session_state.lesson_data = ""
if "quiz_data" not in st.session_state: st.session_state.quiz_data = []
if "history" not in st.session_state: st.session_state.history = []
if "current_topic" not in st.session_state: st.session_state.current_topic = ""

# 3. אתחול AI
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-2.0-flash')

def parse_quiz(quiz_text):
    questions = []
    parts = re.split(r'שאלה \d+[:.)]?', quiz_text)[1:]
    for part in parts:
        lines = [l.strip() for l in part.strip().split('\n') if l.strip()]
        if len(lines) >= 5:
            q_text = lines[0]
            options = lines[1:5]
            ans_match = re.search(r"תשובה נכונה[:\s]*(\d)", part)
            correct_idx = int(ans_match.group(1)) - 1 if ans_match else 0
            questions.append({"q": q_text, "options": options, "correct": correct_idx})
    return questions

# --- סרגל צד ---
if st.session_state.user_name:
    with st.sidebar:
        st.header(f"שלום, {st.session_state.user_name}")
        if st.button("➕ נושא חדש"):
            st.session_state.view_mode = "setup"
            st.rerun()
        st.markdown("---")
        st.subheader("📚 נושאים שלמדת:")
        for item in st.session_state.history:
            st.write(f"✅ {item}")

# --- ניווט ---

if st.session_state.view_mode == "login":
    st.title("🎓 מתווך בקליק")
    st.subheader("הכנה למבחן המתווכים")
    # מיכל שממרכז/מיימין את הכניסה
    with st.container():
        name = st.text_input("הזן שם כדי להתחיל:")
        if st.button("כניסה למערכת"):
            if name
