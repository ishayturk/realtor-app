import streamlit as st
import google.generativeai as genai
import json
import re

# 1. הגדרות תצוגה RTL
st.set_page_config(page_title="מתווך בקליק", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    .stApp { direction: rtl !important; text-align: right !important; }
    [data-testid="stSidebar"] { display: none; }
    .stButton > button { width: 100%; border-radius: 10px; font-weight: bold; height: 3em; }
    .lesson-box { 
        background-color: #ffffff; 
        padding: 30px; 
        border-radius: 15px; 
        border-right: 8px solid #1E88E5; 
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        font-size: 1.2rem;
        line-height: 1.6;
        margin-bottom: 20px;
    }
    h1, h2, h3, h4 { text-align: right !important; }
</style>
""", unsafe_allow_html=True)

# 2. ניהול State
if "view_mode" not in st.session_state:
    st.session_state.update({
        "view_mode": "login", "user_name": "", "current_topic": "", "lesson_content": "",
        "exam_questions": [], "user_answers": {}, "current_exam_idx": 0, "show_feedback": False
    })

# חיבור ל-AI
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-2.0-flash')

# 3. פונקציות AI
def get_lesson(topic):
    with st.spinner(f"מכין שיעור על {topic}..."):
        try:
            prompt = f"כתוב שיעור קצר וממוקד בעברית למבחן המתווכים על: {topic}. כלול נקודות מפתח בלבד."
            resp = model.generate_content(prompt)
            st.session_state.lesson_content = resp.text
            st.session_state.view_mode = "lesson_view"
            st.rerun()
        except: st.error("שגיאה בייצור השיעור")

def load_exam(topic, count=10):
    with st.spinner(f"מייצר {count} שאלות תרגול..."):
        try:
            prompt = f"Create a {count}-question quiz in HEBREW about {topic}. Return ONLY JSON array."
            resp = model.generate_content(prompt)
            match = re.search(r'\[\s*\{.*\}\s*\]', resp.text, re.DOTALL)
            if match:
                st.session_state.exam_questions = json.loads(match.group())
                st.session_state.update({"user_answers": {}, "current_exam_idx": 0, "view_mode": "exam_mode", "show_feedback": False})
                st.rerun()
        except: st.error("שגיאה בייצור המבחן")

# 4. לוגיקת דפים
if st.session_state.view_mode == "login":
    st.title("מתווך בקליק 🏠")
    name = st.text_input("הכנס שם מלא:")
    if st.button("התחל ללמוד"):
        if name: st.session_state.user_name = name; st.session_state.view_mode = "setup"; st.rerun()

else:
    # תפריט עליון
    c1, c2 = st.columns([4,1])
    with c1: st.write(f"שלום, **{st.session_state.user_name}**")
    with c2: 
        if st.button("יציאה"): st.session_state.clear(); st.rerun()
    st.markdown("---")

    if st.session_state.view_mode == "setup":
        st.header("בחר נושא:")
        # הוספת ה-Callback: ברגע שבוחרים נושא, המערכת מריצה את get_lesson מיד
        topic = st.selectbox("בחר מהסילבוס:", [
            "בחר נושא...", "חוק המתווכים", "חוק המקרקעין", "חוק המכר", 
            "חוק הגנת הצרכן", "חוק החוזים", "מיסוי מקרקעין"
        ])
        
        if topic != "בחר נושא...":
            st.session_state.current_topic = topic
            get_lesson(topic) # טעינה אוטומטית ברגע הבחירה

    elif st.session_state.view_mode == "lesson_view":
        st.header(st.session_state.current_topic)
        st.markdown(f'<div class="lesson-box">{st.session_state.lesson_content}</div>', unsafe_allow_html=True)
        if st.button(f"התחל תרגול על {st.session_state.current_topic}"):
            load_exam(st.session_state.current_topic)

    elif st.session_state.view_mode == "exam_mode":
        idx = st.session_state.current_exam_idx
        q = st.session_state.exam_questions[idx]
        st.subheader(f"שאלה {idx+1}")
        st.write(q['q'])
        ans = st.radio("תשובה:", q['options'], key=f"ans_{idx}")
        if st.button("בדוק"): st.session_state.show_feedback = True
        if st.session_state.show_feedback:
            if q['options'].index(ans) == q['correct']: st.success("נכון!")
            else: st.error("טעות")
            if st.button("הבא"): 
                if idx < len(st.session_state.exam_questions)-1:
                    st.session_state.current_exam_idx += 1; st.session_state.show_feedback = False; st.rerun()
                else: st.session_state.view_mode = "setup"; st.rerun()
