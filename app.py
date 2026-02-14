import streamlit as st
import google.generativeai as genai
import json
import re

# 1. הגדרות תצוגה - RTL אגרסיבי למובייל
st.set_page_config(page_title="מתווך בקליק", layout="wide")

st.markdown("""
<style>
    html, body, [data-testid="stAppViewContainer"], [data-testid="stVerticalBlock"] {
        direction: rtl !important;
        text-align: right !important;
    }
    
    /* תיקון לנייד - מניעת הצטמצמות */
    .main .block-container { 
        padding: 10px !important; 
        max-width: 100% !important; 
    }

    /* עיצוב כפתורי רדיו (תשובות) לימין */
    div[role="radiogroup"] { 
        direction: rtl !important; 
        text-align: right !important; 
    }
    
    /* תיבות תוכן */
    .lesson-content, .feedback-box {
        background-color: #ffffff; padding: 15px; border-radius: 10px;
        border-right: 5px solid #1E88E5; line-height: 1.6;
        margin-bottom: 15px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }

    /* כפתורים גדולים ללחיצה בנייד */
    .stButton > button { 
        width: 100% !important; 
        height: 3.5rem !important; 
        margin-bottom: 10px;
    }
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

# 3. רשימת הנושאים המלאה (סילבוס רשמי)
FULL_SYLLABUS = [
    "חוק המתווכים במקרקעין והתקנות",
    "חוק המקרקעין (בעלות, שכירות, משכנתא)",
    "חוק המכר (דירות) (הבטחת השקעות)",
    "חוק החוזים (חלק כללי ותרופות)",
    "חוק הגנת הצרכן",
    "חוק הגנת הדייר",
    "חוק התכנון והבנייה (פרקים נבחרים)",
    "חוק מיסוי מקרקעין (שבח ורכישה)",
    "חוק העונשין (עבירות מרמה וזיוף)",
    "חוק שמאי מקרקעין",
    "חוק הירושה",
    "חוק יחסי ממון בין בני זוג",
    "חוק איסור הלבנת הון",
    "פקודת הנזיקין (רשלנות ותרמית)",
    "מושגי יסוד בכלכלה ושמאות",
    "חוק מקרקעי ישראל ורשות מקרקעי ישראל"
]

# 4. פונקציות
def get_lesson_stream(topic):
    st.session_state.lesson_text = ""
    st.session_state.view = "lesson"
    placeholder = st.empty()
    full_response = ""
    try:
        responses = model.generate_content(f"כתוב שיעור מפורט למבחן המתווכים על {topic}.", stream=True)
        for chunk in responses:
            full_response += chunk.text
            placeholder.markdown(f'<div class="lesson-content">{full_response}</div>', unsafe_allow_html=True)
        st.session_state.lesson_text = full_response
    except: st.error("שגיאה בטעינה")

def generate_questions(topic):
    with st.spinner("מכין 10 שאלות..."):
        try:
            prompt = f"Create 10 MCQs in HEBREW about {topic}. Return ONLY JSON array: [{{'q':'שאלה','options':['1','2','3','4'],'correct':0,'explanation':'הסבר'}}] "
            resp = model.generate_content(prompt)
            clean_json = re.search(r'\[.*\]', resp.text.replace("'", '"'), re.DOTALL)
            if clean_json:
                st.session_state.questions = json.loads(clean_json.group())
                st.session_state.answers = {}
                st.session_state.current_idx = 0
                st.session_state.show_feedback = False
                st.session_state.view = "quiz"
                st.rerun()
        except: st.error("שגיאה בייצור שאלות")

# 5. זרימת דפים
if st.session_state.view == "login":
    st.markdown("<h2 style='text-align: center;'>🏠 מתווך בקליק</h2>", unsafe_allow_html=True)
    name = st.text_input("שם מלא:")
    if st.button("התחל ללמוד"):
        if name: st.session_state.user = name; st.session_state
