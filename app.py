import streamlit as st
import google.generativeai as genai
import json
import re

# 1. הגדרות RTL ועיצוב
st.set_page_config(page_title="מתווך בקליק - למידה חכמה", layout="wide")

st.markdown("""
<style>
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stMarkdownContainer"] {
        direction: rtl !important; text-align: right !important;
    }
    [data-testid="stSidebar"] { direction: rtl !important; text-align: right !important; }
    .stButton button { width: 100%; }
    .feedback-box { padding: 10px; border-radius: 5px; margin-top: 5px; }
    .correct { background-color: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
    .wrong { background-color: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
    .source-link { font-size: 0.9em; color: #1e88e5; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# 2. Session State
state_keys = {
    "view_mode": "login", "user_name": "", "current_topic": "", 
    "lesson_data": "", "quiz_questions": [], "answers_state": {}
}
for k, v in state_keys.items():
    if k not in st.session_state: st.session_state[k] = v

if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-2.0-flash')

TOPICS_LIST = [
    "חוק המתווכים במקרקעין", "חוק המקרקעין", "חוק המכר (דירות)", 
    "חוק הגנת הצרכן", "חוק החוזים", "מיסוי מקרקעין", "חוק הירושה"
]

def generate_quiz_json(topic):
    """יצירת שאלון בפורמט JSON יציב"""
    prompt = f"""
    Create a 5-question multiple choice quiz in HEBREW about {topic} for the Israeli Real Estate License exam.
    Return ONLY a valid JSON array of objects. Each object must have:
    "q": "The question",
    "options": ["opt1", "opt2", "opt3", "opt4"],
    "correct": 0, (index of correct option 0-3)
    "explanation": "Detailed explanation with specific law sections",
    "source": "Specific law and section number"
    """
    try:
        response = model.generate_content(prompt)
        # ניקוי הטקסט כדי להוציא רק את ה-JSON
        json_str = re.search(r'\[.*\]', response.text, re.DOTALL).group()
        return json.loads(json_str)
    except:
        return None

# --- ניווט ---
if st.session_state.view_mode == "login":
    st.title("🎓 מתווך בקליק")
    name = st.text_input("שם משתמש:")
    if st.button("כניסה"):
        if name: st.session_state.user_name = name; st.session_state.view_mode = "setup"; st.rerun()

elif st.session_state.view_mode == "setup":
    st.header("בחר נושא ללימוד ותרגול")
    t = st.selectbox("נושא:", TOPICS_LIST)
    if st.button("התחל ללמוד"):
        st.session_state.current_topic = t
        st.session_state.lesson_data = ""
        st.session_state.quiz_questions = []
        st.session_state.answers_state = {}
        st.session_state.view_mode = "lesson_view"; st.rerun()

elif st.session_state.view_mode == "lesson_view":
    st.header(st.session_state.current_topic)
    if not st.session_state.lesson_data:
        with st.spinner("מכין את השיעור..."):
            resp = model.generate_content(f"כתוב שיעור מפורט על {st.session_state.current_topic} למבחן המתווכים.")
            st.session_state.lesson_data = resp.text
    st.markdown(st.session_state.lesson_data)
    if st.button("עבור לתרגול עם פידבק מיידי 🎯"):
        st.session_state.view_mode = "lesson_quiz"; st.rerun()

elif st.session_state.view_mode == "lesson_quiz":
    st.header(f"בוחן חכם: {st.session_state.current_topic}")
    
    if not st.session_state.quiz_questions:
        with st.spinner("Gemini מייצר שאלות ומקורות משפטיים..."):
            questions = generate_quiz_json(st.session_state.current_topic)
            if questions:
                st.session_state.quiz_questions = questions
                st.rerun()
            else:
                st.error("נכשל ביצירת שאלון. נסה שוב.")
                if st.button("נסה שוב"): st.rerun()

    for i, q in enumerate(st.session_state.quiz_questions):
        st.markdown(f"### {i+1}. {q['q']}")
        
        # הצגת רדיו ללא פורם לפידבק מיידי
        choice = st.radio(f"בחר תשובה לשאלה {i+1}:", q['options'], key=f"ans_{i}", index=None)
        
        if choice:
            choice_idx = q['options'].index(choice)
            if choice_idx == q['correct']:
                st.markdown(f'<div class="feedback-box correct">✅ **כל הכבוד!** {q["explanation"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="feedback-box wrong">❌ **טעות.** התשובה הנכונה היא: {q["options"][q["correct"]]}<br>{q["explanation"]}</div>', unsafe_allow_html=True)
            
            st.markdown(f'<p class="source-link">📍 מקור: {q["source"]}</p>', unsafe_allow_html=True)
        st.markdown("---")

    if st.button("חזרה לשיעור"):
        st.session_state.view_mode = "lesson_view"; st.rerun()
