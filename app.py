import streamlit as st
import google.generativeai as genai
import json
import re

# 1. הגדרות תצוגה - כפיית RTL אגרסיבית (מתוקן לנייד)
st.set_page_config(page_title="מתווך בקליק", layout="wide")

st.markdown("""
<style>
    html, body, [data-testid="stAppViewContainer"], [data-testid="stVerticalBlock"] {
        direction: rtl !important;
        text-align: right !important;
    }
    div[data-testid="stMarkdownContainer"] > p {
        text-align: right !important;
        direction: rtl !important;
    }
    .main .block-container { max-width: 800px; margin: 0 auto; }
    
    /* עיצוב תיבת השיעור והמשוב */
    .lesson-content, .feedback-box {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        border-right: 5px solid #1E88E5;
        line-height: 1.6;
        font-size: 1.1rem;
        direction: rtl !important;
        text-align: right !important;
        margin-bottom: 20px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    .stButton > button { width: 100%; border-radius: 8px; font-weight: bold; height: 3.5em; }
</style>
""", unsafe_allow_html=True)

# 2. ניהול State
if "view" not in st.session_state:
    st.session_state.update({
        "view": "login", "user": "", "topic": "", "lesson_text": "",
        "questions": [], "answers": {}, "current_idx": 0, "show_feedback": False
    })

if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-2.0-flash')

# 3. פונקציות ליבה
def get_lesson_stream(topic):
    st.session_state.lesson_text = ""
    st.session_state.view = "lesson"
    placeholder = st.empty()
    full_response = ""
    try:
        responses = model.generate_content(
            f"כתוב שיעור מקצועי ומפורט בעברית למבחן המתווכים על: {topic}. השתמש בכותרות וסעיפים.",
            stream=True
        )
        for chunk in responses:
            full_response += chunk.text
            placeholder.markdown(f'<div class="lesson-content">{full_response}</div>', unsafe_allow_html=True)
        st.session_state.lesson_text = full_response
    except: st.error("תקלה בטעינה.")

def generate_questions(topic):
    with st.spinner("מייצר שאלות תרגול..."):
        try:
            prompt = f"צור 10 שאלות אמריקאיות בעברית על {topic}. החזר אך ורק פורמט JSON: [{{'q':'שאלה','options':['1','2','3','4'],'correct':0,'explanation':'הסבר'}}] "
            resp = model.generate_content(prompt)
            clean_json = re.search(r'\[.*\]', resp.text.replace("'", '"'), re.DOTALL)
            if clean_json:
                st.session_state.questions = json.loads(clean_json.group())
                st.session_state.answers = {}
                st.session_state.current_idx = 0
                st.session_state.view = "quiz"
                st.session_state.show_feedback = False
                st.rerun()
        except: st.error("שגיאה בייצור שאלות.")

# 4. זרימת דפים
if st.session_state.view == "login":
    st.markdown("<h1 style='text-align: center; color: #1E88E5;'>🏠 מתווך בקליק</h1>", unsafe_allow_html=True)
    name = st.text_input("הכנס שם מלא:")
    if st.button("התחל ללמוד"):
        if name: st.session_state.user = name; st.session_state.view = "menu"; st.rerun()

elif st.session_state.view == "menu":
    st.write(f"### שלום {st.session_state.user}, בחר נושא:")
    syllabus = ["חוק המתווכים", "חוק המקרקעין", "חוק המכר", "חוק החוזים", "חוק הגנת הצרכן", "מיסוי מקרקעין", "תכנון ובנייה"]
    selected = st.selectbox("הסילבוס הרשמי:", ["בחר..."] + syllabus)
    if selected != "בחר...":
        st.session_state.topic = selected
        c1, c2 = st.columns(2)
        with c1: 
            if st.button("📖 פתח שיעור"): get_lesson_stream(selected)
        with c2: 
            if st.button("✍️ תרגול שאלות"): generate_questions(selected)

elif st.session_state.view == "lesson":
    st.write(f"### שיעור: {st.session_state.topic}")
    if st.button("🏠 חזרה לתפריט"): st.session_state.view = "menu"; st.rerun()
    if st.session_state.lesson_text:
        st.markdown(f'<div class="lesson-content">{st.session_state.lesson_text}</div>', unsafe_allow_html=True)
    if st.button("✍️ עבור לתרגול שאלות בשיעור זה"): generate_questions(st.session_state.topic)

elif st.session_state.view == "quiz":
    idx = st.session_state.current_idx
    q = st.session_state.questions[idx]
    
    st.write(f"### תרגול: {st.session_state.topic}")
    if st.button("🏠 תפריט"): st.session_state.view = "menu"; st.rerun()
    
    # לוח ניווט
    nav_cols = st.columns(10)
    for i in range(10):
        with nav_cols[i]:
            if st.button(f"{i+1}", key=f"btn_{i}", type="primary" if i == idx else "secondary"):
                st.session_state.current_idx = i
                st.session_state.show_feedback = False
                st.rerun()

    st.info(f"**שאלה {idx+1}:** {q['q']}")
    
    # בחירת תשובה
    user_choice = st.radio("בחר את התשובה הנכונה:", q['options'], key=f"radio_{idx}")
    
    col_check, col_next = st.columns(2)
    with col_check:
        if st.button("בדוק תשובה ✅"):
            st.session_state.show_feedback
