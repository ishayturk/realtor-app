import streamlit as st
import google.generativeai as genai
import json
import re
import time
import random

# ==========================================
# 1. הגדרות ועיצוב
# ==========================================
def apply_design():
    st.set_page_config(page_title="מתווך בקליק", layout="wide")
    st.markdown("""
    <style>
        html, body, [data-testid="stAppViewContainer"], .main, .block-container {
            direction: rtl !important; text-align: right !important;
            background-color: #f4f7f9;
        }
        .main-header {
            text-align: center !important; background: linear-gradient(90deg, #1E88E5, #1565C0);
            color: white !important; padding: 20px; border-radius: 15px; margin-bottom: 20px;
        }
        .lesson-box {
            background-color: #ffffff !important; color: #1a1a1a !important; padding: 25px; 
            border-radius: 15px; border-right: 8px solid #1E88E5; box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            line-height: 1.8; font-size: 1.1rem; margin-bottom: 20px;
        }
        .timer-text {
            font-size: 22px; font-weight: bold; color: #d32f2f; text-align: center;
            background: #ffebee; padding: 12px; border-radius: 12px; border: 2px solid #d32f2f;
        }
        .stButton button { width: 100% !important; border-radius: 10px !important; height: 3.5em; font-weight: bold; }
        [data-testid="stSidebar"] { display: none; }
        .score-display { background: #e3f2fd; padding: 12px; border-radius: 10px; text-align: center; font-weight: bold; color: #1565C0; margin-bottom: 15px; }
        p, span, label { color: #1a1a1a !important; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. נתונים
# ==========================================
FULL_SYLLABUS = [
    "חוק המתווכים במקרקעין", "חוק המקרקעין", "חוק המכר (דירות)",
    "חוק החוזים", "חוק הגנת הצרכן", "חוק הגנת הדייר",
    "חוק התכנון והבנייה", "חוק מיסוי מקרקעין", "חוק הירושה"
]

def get_official_questions():
    # שאלות לדוגמה - כאן תכניס את כל השאלות מהלינקים שלך
    q_list = [
        {"q": "מתווך פעל ללא רישיון בתוקף. האם הוא זכאי לדמי תיווך?", "options": ["כן, אם עשה עבודה טובה", "לא, הרישיון הוא תנאי סף חקוק", "רק אם הלקוח הסכים", "רק חצי מהסכום"], "correct": 1, "explanation": "חוק המתווכים קובע כי רק בעל רישיון בתוקף זכאי לדמי תיווך."},
        {"q": "מהו 'הגורם היעיל' לפי הפסיקה?", "options": ["מי שהחתים ראשון", "מי שהיה הסיבה המכרעת לכריתת החוזה", "מי שהראה הכי הרבה דירות", "עורך הדין של העסקה"], "correct": 1, "explanation": "מתווך זכאי לדמי תיווך רק אם היה הגורם היעיל שהוביל להסכם מחייב."}
    ]
    # השלמה ל-25 שאלות
    return (q_list * 13)[:25]

# ==========================================
# 3. מנוע AI
# ==========================================
def init_gemini():
    if "GEMINI_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        return genai.GenerativeModel('gemini-1.5-flash')
    return None

def fetch_quiz(model, topic):
    if not model: return None
    prompt = f"צור 10 שאלות אמריקאיות בעברית על {topic}. החזר רק JSON: [{{'q':'','options':['','','',''],'correct':0,'explanation':''}}]"
    try:
        resp = model.generate_content(prompt)
        match = re.search(r'\[\s*\{.*\}\s*\]', resp.text, re.DOTALL)
        return json.loads(match.group()) if match else None
    except: return None

# ==========================================
# 4. ניהול האפליקציה
# ==========================================
def main():
    apply_design()
    model = init_gemini()
    
    if "view" not in st.session_state:
        st.session_state.update({
            "view": "login", "user": "", "topic": "", "lesson": "", 
            "questions": [], "idx": 0, "show_f": False, "correct_answers": 0,
            "exam_questions": [], "user_answers": {}, "start_time": None
        })

    st.markdown('<div class="main-header"><h1 style="margin:0; font-size: 26px; color: white;">🏠 מתווך בקליק</h1></div>', unsafe_allow_html=True)

    if st.session_state.view == "login":
        st.write("### ברוכים הבאים למערכת ההכנה למבחן המתווכים")
        name = st.text_input("הכנס את שמך כדי להתחיל:", key="login_input")
        if st.button("כניסה למערכת 🔓"):
            if name:
                st.session_state.user = name
                st.session_state.view = "menu"
                st.rerun()

    elif st.session_state.view == "menu":
        st.write(f"### שלום, {st.session_state.user} 👋")
        t1, t2 = st.tabs(["📚 למידה מודרכת", "⏱️ סימולציית מבחן"])
        
        with t1:
            st.write("בחר נושא לקבלת שיעור מה-AI ותרגול ממוקד.")
            selected = st.selectbox("בחר נושא:", ["בחר..."] + FULL_SYLLABUS)
            if selected != "בחר...":
                st.session_state.topic = selected
                if st.button("📖 התחל שיעור"):
                    st.session_state.lesson = ""
                    st.session_state.view = "lesson"
                    st.rerun()
        
        with t2:
            st.write("מבחן מלא של 25 שאלות מהמאגר הרשמי.")
            if st.button("🚀 התחל מבחן רישוי"):
                st.session_state.exam_questions = get_official_questions()
