import streamlit as st
import google.generativeai as genai
import re
import time

# 1. הגדרות עיצוב RTL
st.set_page_config(page_title="מתווך בקליק", layout="wide")

st.markdown("""
    <style>
    html, body, [data-testid="stAppViewContainer"], .main, .block-container {
        direction: rtl !important;
        text-align: right !important;
    }
    h1, h2, h3, h4, p, span, label {
        direction: rtl !important; text-align: right !important;
    }
    [data-testid="stSidebar"] { direction: rtl !important; text-align: right !important; }
    
    div.stButton > button { 
        width: 100%; border-radius: 8px; font-weight: bold;
        background-color: #1E88E5; color: white;
    }
    .quiz-card { 
        background-color: #ffffff; padding: 20px; border-radius: 12px; 
        border-right: 6px solid #1E88E5; box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    .score-box {
        background-color: #e3f2fd; padding: 20px; border-radius: 10px;
        text-align: center; font-size: 24px; font-weight: bold; color: #1E88E5;
        border: 2px solid #1E88E5;
    }
    </style>
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

# 3. אתחול AI
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-2.0-flash')

def parse_quiz(quiz_text):
    questions = []
    # פיצול לפי מבנה קבוע שהכתבנו ל-AI
    blocks = quiz_text.split("---")
    for block in blocks:
        if "שאלה:" in block and "אפשרויות:" in block:
            try:
                q_part = re.search(r"שאלה:(.*?)אפשרויות:", block, re.DOTALL).group(1).strip()
                opts_part = re.search(r"אפשרויות:(.*?)תשובה נכונה:", block, re.DOTALL).group(1).strip()
                ans_part = re.search(r"תשובה נכונה:(.*?)סעיף חוק:", block, re.DOTALL).group(1).strip()
                ref_part = block.split("סעיף חוק:")[1].strip()
                
                options = [opt.strip() for opt in opts_part.split("\n") if opt.strip() and (opt.startswith(("1", "2", "3", "4")) or ")" in opt)]
                options = options[:4] # מוודא שיש רק 4
                
                questions.append({
                    "q": q_part,
                    "options": options,
                    "correct": int(ans_part) - 1,
                    "ref": ref_part
                })
            except:
                continue
    return questions

# --- סרגל צידי ---
if st.session_state.user_name:
    with st.sidebar:
        st.markdown("<h2 style='text-align: center;'>🎓 מתווך בקליק</h2>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center;'>שלום, <b>{st.session_state.user_name}</b></p>", unsafe_allow_html=True)
        st.markdown("---")
        if st.button("➕ בחירת נושא לימוד חדש"):
            st.session_state.view_mode = "setup"; st.rerun()
        if st.session_state.view_mode == "lesson" and st.session_state.quiz_data:
            if st.button(f"📝 מעבר למבחן: {st.session_state.current_topic}"):
                st.session_state.view_mode = "quiz"; st.rerun()
        if st.session_state.view_mode == "quiz":
            if st.button(f"📖 חזרה לשיעור: {st.session_state.current_topic}"):
                st.session_state.view_mode = "lesson"; st.rerun()
        st.markdown("---")
        for item in st.session_state.history: st.caption(f"• {item}")

# --- דפים ---
if st.session_state.view_mode == "login":
    st.markdown("<h1>🎓 מתווך בקליק</h1>", unsafe_allow_html=True)
    name = st.text_input("הזן שם כדי להתחיל:")
    if st.button("כניסה למערכת"):
        if name: st.session_state.user_name = name; st.session_state.view_mode = "setup"; st.rerun()

elif st.session_state.view_mode == "setup":
    st.markdown(f"<h1>מה נלמד היום, {st.session_state.user_name}?</h1>", unsafe_allow_html=True)
    topic = st.selectbox("בחר נושא:", ["חוק המתווכים", "חוק המקרקעין", "דיני חוזים", "דיני תכנון ובנייה"])
    if st.button("הכן שיעור"):
        st.session_state.lesson_count += 1
        st.session_state.current_topic = topic
        st.session_state.user_answers = {} 
        bar = st.progress(0)
        try:
            bar.progress(30)
            res = model.generate_content(f"כתוב שיעור מפורט על {topic} למבחן המתווכים.")
            st.session_state.lesson_data = res.text
            bar.progress(70)
            # הנחיה קשיחה לפורמט ה-AI
            q_prompt = f"""צור 3 שאלות אמריקאיות על {topic}. חובה להשתמש בפורמט הבא בדיוק, עם קו מפריד --- בין שאלה לשאלה:
            שאלה: [טקסט השאלה כאן]
            אפשרויות:
            1) [אופציה 1]
            2) [אופציה 2]
            3) [אופציה 3]
            4) [אופציה 4]
            תשובה נכונה: [מספר בלבד]
            סעיף חוק: [מספר הסעיף והסבר קצר]
            ---"""
            quiz_res = model.generate_content(q_prompt)
            st.session_state.quiz_data = parse_quiz(quiz_res.text)
            if topic not in [h.split(". ", 1)[-1] for h in st.session_state.history]:
                st.session_state.history.append(f"{st.session_state.lesson_count}. {topic}")
            bar.progress(100); st.session_state.view_mode = "lesson"; st.rerun()
        except Exception as e: st.error(f"שגיאה: {e}")

elif st.session_state.view_mode == "lesson":
    st.markdown(f"<h1>שיעור {st.session_state.lesson_count}: {st.session_state.current_topic}</h1>", unsafe_allow_html=True)
    st.markdown(st.session_state.lesson_data)
    if st.button(f"סיימתי ללמוד! למבחן על {st.session_state.current_topic} 📝"):
        st.session_state.view_mode = "quiz"; st.rerun()

elif st.session_state.view_mode == "quiz":
    st.markdown(f"<h1>תרגול: {st.session_state.current_topic}</h1>",
