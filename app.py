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
    .question-card { background-color: #f8f9fa; padding: 20px; border-radius: 15px; border-right: 6px solid #1E88E5; }
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
else:
    st.error("חסר מפתח API ב-Secrets")

# 3. פונקציות AI (שיעור ושאלות)

def get_lesson(topic):
    """מייצר תוכן לימודי על הנושא שנבחר"""
    with st.spinner(f"ה-AI כותב לך שיעור מקיף על {topic}..."):
        try:
            prompt = f"כתוב שיעור מפורט בעברית עבור מבחן המתווכים על הנושא: {topic}. כלול סעיפי חוק חשובים ודוגמאות מעשיות."
            resp = model.generate_content(prompt)
            st.session_state.lesson_content = resp.text
            st.session_state.view_mode = "lesson_view"
            st.rerun()
        except Exception as e:
            st.error(f"שגיאה ביצירת השיעור: {e}")

def load_exam(topic, count=10):
    """מייצר שאלות תרגול"""
    with st.spinner(f"מייצר שאלות תרגול..."):
        try:
            prompt = f"Create a {count}-question quiz in HEBREW about {topic}. Return ONLY a JSON array. Format: [{'q':'','options':['','','',''],'correct':0,'explanation':'','source':''}]"
            resp = model.generate_content(prompt)
            match = re.search(r'\[\s*\{.*\}\s*\]', resp.text, re.DOTALL)
            if match:
                data = json.loads(match.group())
                st.session_state.update({
                    "exam_questions": data, "user_answers": {}, "current_exam_idx": 0,
                    "view_mode": "exam_mode", "show_feedback": False
                })
                st.rerun()
            else:
                st.error("ה-AI לא החזיר שאלות תקינות. נסה שוב.")
        except Exception as e:
            st.error(f"שגיאה ביצירת המבחן: {e}")

# 4. מבנה הדפים

# דף כניסה
if st.session_state.view_mode == "login":
    st.title("מתווך בקליק 🏠")
    name = st.text_input("הכנס שם מלא לכניסה:")
    if st.button("התחל ללמוד"):
        if name:
            st.session_state.user_name = name
            st.session_state.view_mode = "setup"; st.rerun()

else:
    # תפריט עליון פשוט
    c1, c2 = st.columns([4,1])
    with c1: st.write(f"שלום, **{st.session_state.user_name}**")
    with c2: 
        if st.button("יציאה"): 
            st.session_state.clear(); st.rerun()
    st.markdown("---")

    # דף בחירת נושא (Dropdown)
    if st.session_state.view_mode == "setup":
        st.header("מה נלמד היום?")
        topic = st.selectbox("בחר נושא מהסילבוס:", [
            "בחר נושא...", "חוק המתווכים", "חוק המקרקעין", "חוק המכר", 
            "חוק הגנת הצרכן", "חוק החוזים", "מיסוי מקרקעין", "תכנון ובנייה"
        ])
        if topic != "בחר נושא...":
            st.session_state.current_topic = topic
            if st.button(f"פתח שיעור ב-{topic}"):
                get_lesson(topic)

    # דף הצגת השיעור
    elif st.session_state.view_mode == "lesson_view":
        st.header(st.session_state.current_topic)
        st.markdown(f'<div class="lesson-box">{st.session_state.lesson_content}</div>', unsafe_allow_html=True)
        
        col_back, col_exam = st.columns(2)
        with col_back:
            if st.button("⬅️ חזרה לבחירת נושא"):
                st.session_state.view_mode = "setup"; st.rerun()
        with col_exam:
            if st.button(f"התחל תרגול על {st.session_state.current_topic} ✍️"):
                load_exam(st.session_state.current_topic)

    # דף המבחן
    elif st.session_state.view_mode == "exam_mode":
        idx = st.session_state.current_exam_idx
        q = st.session_state.exam_questions[idx]
        
        st.subheader(f"תרגול: {st.session_state.current_topic} (שאלה {idx+1})")
        st.markdown(f'<div class="question-card"><h4>{q["q"]}</h4></div>', unsafe_allow_html=True)
        
        ans = st.radio("בחר תשובה:", q['options'], key=f"ans_{idx}")
        
        if st.button("בדוק תשובה"):
            st.session_state.show_feedback = True
            st.session_state.user_answers[idx] = ans

        if st.session_state.show_feedback:
            if q['options'].index(ans) == q['correct']: st.success("נכון!")
            else: st.error(f"טעות. הנכון: {q['options'][q['correct']]}")
            st.info(f"הסבר: {q['explanation']}")
            
            if st.button("לשאלה הבאה ➡️"):
                if idx < len(st.session_state.exam_questions) - 1:
                    st.session_state.current_exam_idx += 1
                    st.session_state.show_feedback = False; st.rerun()
                else:
                    st.balloons(); st.session_state.view_mode = "setup"; st.rerun()
