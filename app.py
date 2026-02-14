import streamlit as st
import google.generativeai as genai
import re
import time

# 1. הגדרות עיצוב RTL וקיבוע תפריטים
st.set_page_config(page_title="מתווך בקליק", layout="wide")

st.markdown("""
    <style>
    .stApp, .main, .block-container { direction: rtl !important; text-align: right !important; }
    [data-testid="stSidebar"] { direction: rtl !important; text-align: right !important; }
    
    /* עיצוב כפתורי הניווט בסיידבר */
    .sidebar .stButton button {
        background-color: #ffffff !important;
        color: #1E88E5 !important;
        border: 2px solid #1E88E5 !important;
    }

    div.stButton > button { 
        width: 100%; border-radius: 8px; font-weight: bold;
    }
    
    .quiz-card { 
        background-color: #ffffff; padding: 20px; border-radius: 12px; 
        border-right: 6px solid #1E88E5; box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. ניהול משתני מערכת
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

# --- סרגל צידי (תפריט ניווט חכם) ---
if st.session_state.user_name:
    with st.sidebar:
        st.title(f"שלום, {st.session_state.user_name}")
        st.markdown("---")
        
        st.subheader("📍 ניווט מהיר")
        if st.button("➕ בחירת נושא חדש"):
            st.session_state.view_mode = "setup"
            st.rerun()
            
        # מעברים דינמיים בתפריט
        if st.session_state.view_mode == "lesson" and st.session_state.quiz_data:
            if st.button("📝 מעבר למבחן התרגול"):
                st.session_state.view_mode = "quiz"
                st.rerun()
        
        if st.session_state.view_mode == "quiz":
            if st.button("📖 חזרה לטקסט הלימוד"):
                st.session_state.view_mode = "lesson"
                st.rerun()
        
        st.markdown("---")
        st.subheader("📚 היסטוריה")
        for item in st.session_state.history:
            st.caption(f"• {item}")

# --- עמודי האפליקציה ---

if st.session_state.view_mode == "login":
    st.title("🎓 מתווך בקליק")
    name = st.text_input("הזן שם:")
    if st.button("כניסה"):
        if name:
            st.session_state.user_name = name
            st.session_state.view_mode = "setup"
            st.rerun()

elif st.session_state.view_mode == "setup":
    st.title("מה נלמד היום?")
    topic = st.selectbox("בחר נושא:", ["חוק המתווכים", "חוק המקרקעין", "דיני חוזים", "דיני תכנון ובנייה"])
    if st.button("הכן שיעור"):
        st.session_state.current_topic = topic
        bar = st.progress(0)
        msg = st.empty()
        try:
            msg.text("מייצר שיעור...")
            bar.progress(30)
            res = model.generate_content(f"כתוב שיעור מפורט על {topic} למבחן המתווכים.")
            st.session_state.lesson_data = res.text
            
            bar.progress(70)
            msg.text("בונה מבחן תרגול...")
            # השורה המתוקנת:
            quiz_res = model.generate_content(f"צור 3 שאלות אמריקאיות על {topic}. פורמט: שאלה X: [טקסט] 1) [א] 2) [ב] 3) [ג] 4) [ד] תשובה נכונה: [מספר]")
            st.session_
