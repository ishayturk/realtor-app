import streamlit as st
import google.generativeai as genai
import re
import time

# 1. הגדרות עיצוב RTL ויישור לימין
st.set_page_config(page_title="מתווך בקליק", layout="wide")

st.markdown("""
    <style>
    html, body, [data-testid="stAppViewContainer"], .main, .block-container {
        direction: rtl !important;
        text-align: right !important;
    }
    h1, h2, h3, h4, h5, h6, p, span, label {
        direction: rtl !important;
        text-align: right !important;
        display: block;
        width: 100%;
    }
    [data-testid="stSidebar"], [data-testid="stSidebar"] * {
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
else:
    st.error("API Key חסר בהגדרות!")

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

# --- סרגל צידי (ניווט) ---
if st.session_state.user_name:
    with st.sidebar:
        st.markdown(f"### שלום, {st.session_state.user_name}")
        st.markdown("---")
        st.markdown("#### 📍 ניווט מהיר")
        if st.button("➕ בחירת נושא חדש"):
            st.session_state.view_mode = "setup"
            st.rerun()
        if st.session_state.view_mode == "lesson" and st.session_state.quiz_data:
            if st.button("📝 מעבר למבחן התרגול"):
                st.session_state.view_mode = "quiz"
                st.rerun()
        if st.session_state.view_mode == "quiz":
            if st.button("📖 חזרה לטקסט הלימוד"):
                st.session_state.view_mode = "lesson"
                st.rerun()
        st.markdown("---")
        st.markdown("#### 📚 היסטוריה")
        for item in st.session_state.history:
            st.caption(f"• {item}")

# --- ניהול דפים ---
if st.session_state.view_mode == "login":
    st.markdown("<h1>🎓 מתווך בקליק</h1>", unsafe_allow_html=True)
    name = st.text_input("הזן שם כדי להתחיל:")
    if st.button("כניסה למערכת"):
        if name:
            st.session_state.user_name = name
            st.session_state.view_mode = "setup"
            st.rerun()

elif st.session_state.view_mode == "setup":
    st.markdown(f"<h1>מה נלמד היום, {st.session_state.user_name}?</h1>", unsafe_allow_html=True)
    topic = st.selectbox("בחר נושא מהרשימה:", ["חוק המתווכים", "חוק המקרקעין", "דיני חוזים", "דיני תכנון ובנייה"])
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
            q_prompt = f"צור 3 שאלות אמריקאיות על {topic}. פורמט: שאלה X: [טקסט] 1) [א] 2) [ב] 3) [ג] 4) [ד] תשובה נכונה: [מספר]"
            quiz_res = model.generate_content(q_prompt)
            st.session_state.quiz_data = parse_quiz(quiz_res.text)
            if topic not in st.session_state.history:
                st.session_state.history.append(topic)
            bar.progress(100)
            time.sleep(1)
            st.session_state.view_mode = "lesson"
            st.rerun()
        except Exception as e:
            st.error(f"שגיאה: {e}")

elif st.session_state.view_mode == "lesson":
    st.markdown(f"<h1>שיעור: {st.session_state.current_topic}</h1>", unsafe_allow_html=True)
    st.markdown(st.session_state.lesson_data)
    st.markdown("---")
    if st.button("אני מוכן למבחן! 📝"):
        st.session_state.view_mode = "quiz"
        st.rerun()

elif st.session_state.view_mode == "quiz":
    st.markdown(f"<h1>מבחן: {st.session_state.current_topic}</h1>", unsafe_allow_html=True)
    for i, q in enumerate(st.session_state.quiz_data):
        st.markdown('<div class="quiz-card">', unsafe_allow_html=True)
        st.write(f"**שאלה {i+1}:** {q['q']}")
        ans = st.radio(f"תשובה {i}:", q['options'], key=f"q{i}", index=None, label_visibility="collapsed")
        if st.button(f"בדוק שאלה {i+1}", key=f"b{i}"):
            if ans:
                idx = q['options'].index(ans)
                if idx == q['correct']: st.success("נכון!")
                else: st.error(f"טעות. התשובה הנכונה היא אופציה {q['correct']+1}")
        st.markdown('</div>', unsafe_allow_html=True)
