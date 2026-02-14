import streamlit as st
import google.generativeai as genai
import json
import re

# 1. הגדרות תצוגה - כפייה של RTL על כל רכיב אפשרי
st.set_page_config(page_title="מתווך בקליק", layout="wide")

st.markdown("""
<style>
    /* כפייה גלובלית על כל האפליקציה */
    html, body, [data-testid="stAppViewContainer"], .main, .block-container {
        direction: rtl !important;
        text-align: right !important;
    }

    /* יישור ספציפי לטקסטים, כותרות ותיבות */
    h1, h2, h3, h4, p, li, label, div, span {
        text-align: right !important;
        direction: rtl !important;
    }

    /* מרכוז הקונטיינר הראשי */
    .main .block-container {
        max-width: 850px !important;
        margin: 0 auto !important;
    }

    /* תיקון יישור לתיבות בחירה (Selectbox) וקלט */
    .stSelectbox div, .stTextInput div, .stRadio div {
        direction: rtl !important;
        text-align: right !important;
    }
    
    /* עיצוב תיבת השיעור */
    .lesson-box { 
        background-color: #ffffff; 
        padding: 30px; 
        border-radius: 15px; 
        border-right: 8px solid #1E88E5; 
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        font-size: 1.15rem; 
        line-height: 1.8; 
        margin-bottom: 25px;
        text-align: right !important;
    }

    /* כפתורים - יישור טקסט בתוכם */
    .stButton > button {
        width: 100% !important;
        border-radius: 10px !important;
        font-weight: bold !important;
        height: 3.5em !important;
        direction: rtl !important;
    }
    
    /* הסתרת תפריטים מיותרים */
    [data-testid="stSidebar"] { display: none; }
</style>
""", unsafe_allow_html=True)

# 2. ניהול State
if "view" not in st.session_state:
    st.session_state.update({
        "view": "login", "user": "", "topic": "", "lesson": "",
        "questions": [], "answers": {}, "current_idx": 0, "feedback": False
    })

if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-2.0-flash')

# 3. פונקציות ליבה
def generate_lesson(topic):
    with st.spinner(f"כותב שיעור על {topic}..."):
        try:
            prompt = f"כתוב שיעור מפורט בעברית למבחן המתווכים על: {topic}. כלול סעיפי חוק והסברים."
            resp = model.generate_content(prompt)
            st.session_state.lesson = resp.text
            st.session_state.view = "lesson"
            st.rerun()
        except Exception as e:
            st.error(f"שגיאה: {e}")

def generate_questions(topic):
    with st.spinner("מייצר שאלות תרגול..."):
        try:
            # שימוש ב-Double Brackets למניעת ValueError
            prompt = f"""
            Create 10 multiple-choice questions in HEBREW about {topic}. 
            Return ONLY a JSON array with this structure: 
            [ {{"q": "שאלה", "options": ["תשובה 1", "2", "3", "4"], "correct": 0, "explanation": "הסבר"}} ]
            """
            resp = model.generate_content(prompt)
            match = re.search(r'\[.*\]', resp.text, re.DOTALL)
            if match:
                st.session_state.questions = json.loads(match.group())
                st.session_state.answers = {}
                st.session_state.current_idx = 0
                st.session_state.feedback = False
                st.session_state.view = "quiz"
                st.rerun()
        except Exception as e:
            st.error(f"שגיאה בייצור שאלות: {e}")

# 4. דפים
st.markdown('<h1 style="text-align: center; color: #1E88E5;">🏠 מתווך בקליק</h1>', unsafe_allow_html=True)

if st.session_state.view == "login":
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        name = st.text_input("הכנס שם מלא:")
        if st.button("כניסה"):
            if name: st.session_state.user = name; st.session_state.view = "menu"; st.rerun()

elif st.session_state.view == "menu":
    st.write(f"### שלום {st.session_state.user}")
    list_topics = ["חוק המתווכים במקרקעין", "חוק המקרקעין", "חוק המכר (דירות)", "חוק החוזים", "חוק הגנת הצרכן", "חוק מיסוי מקרקעין"]
    selected = st.selectbox("בחר נושא ללימוד:", ["בחר..."] + list_topics)
    if selected != "בחר...":
        st.session_state.topic = selected
        c1, c2 = st.columns(2)
        with c1: 
            if st.button("📖 קרא שיעור"): generate_lesson(selected)
        with c2: 
            if st.button("✍️ תרגול שאלות"): generate_questions(selected)

elif st.session_state.view == "lesson":
    st.header(st.session_state.topic)
    st.markdown(f'<div class="lesson-box">{st.session_state.lesson}</div>', unsafe_allow_html=True)
    if st.button(f"סיימתי לקרוא - עבור לתרגול ✍️"):
        generate_questions(st.session_state.topic)
    if st.button("חזרה לתפריט"): st.session_state.view = "menu"; st.rerun()

elif st.session_state.view == "quiz":
    idx = st.session_state.current_idx
    q = st.session_state.questions[idx]
    
    # לוח ניווט
    st.write(f"**שאלה {idx+1} מתוך {len(st.session_state.questions)}**")
    cols = st.columns(10)
    for i in range(len(st.session_state.questions)):
        with cols[i]:
            if st.button(f"{i+1}", key=f"n_{i}", type="primary" if i == idx else "secondary"):
                st.session_state.current_idx = i; st.session_state.feedback = False; st.rerun()

    st.info(q['q'])
    user_ans = st.session_state.answers.get(idx)
