import streamlit as st
import google.generativeai as genai
import json
import re

# --- 1. הגדרות תצוגה RTL ---
st.set_page_config(page_title="מתווך בקליק", layout="centered")

st.markdown("""
    <style>
    [data-testid="stAppViewContainer"], .main, .block-container { direction: rtl !important; text-align: right !important; }
    h1, h2, h3, h4 { text-align: center !important; color: #1E88E5; width: 100%; }
    .stButton > button { width: 100%; font-weight: bold; height: 3.5em; border-radius: 10px; }
    .lesson-box { 
        background: #ffffff; padding: 25px; border-radius: 15px; 
        border-right: 6px solid #1E88E5; box-shadow: 0 4px 12px rgba(0,0,0,0.1); 
        line-height: 1.8; color: #333; text-align: right; direction: rtl; margin-bottom: 25px;
    }
    .explanation-box { padding: 15px; border-radius: 10px; margin-top: 10px; border-right: 5px solid; font-size: 0.95em; text-align: right; }
    .success { background-color: #e8f5e9; border-color: #4caf50; color: #2e7d32; }
    .error { background-color: #ffebee; border-color: #f44336; color: #c62828; }
    div[role="radiogroup"] { direction: rtl !important; text-align: right !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. אתחול משתנים ---
for key in ['user', 'step', 'lesson_text', 'quiz_active', 'quiz_idx', 'quiz_answers', 'quiz_questions', 'checked_questions', 'exam_idx', 'exam_answers', 'exam_questions']:
    if key not in st.session_state:
        st.session_state[key] = "" if key in ['user', 'step', 'lesson_text'] else (False if key == 'quiz_active' else (0 if 'idx' in key else ([] if 'questions' in key else ({} if 'answers' in key else set()))))

def extract_json(text):
    try:
        match = re.search(r'\[\s*{.*}\s*\]', text, re.DOTALL)
        if match: return json.loads(match.group())
        return json.loads(text)
    except: return None

# --- 3. לוגיקה ---
st.markdown("<h1>🏠 מתווך בקליק</h1>", unsafe_allow_html=True)

if st.session_state.user == "" or st.session_state.step == "login":
    name_in = st.text_input("הכנס שם מלא:")
    if st.button("כניסה למערכת"):
        if name_in:
            st.session_state.user = name_in
            st.session_state.step = "menu"
            st.rerun()

elif st.session_state.step == "menu":
    st.markdown(f"### שלום, {st.session_state.user} 👋")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("📚 שיעור עיוני + שאלון"):
            st.session_state.step = "study"
            st.session_state.lesson_text = ""
            st.session_state.quiz_active = False
            st.rerun()
    with c2:
        if st.button("📝 סימולציית 25 שאלות"):
            st.session_state.exam_questions = [{"q": f"שאלה {i+1}:", "options": ["א","ב","ג","ד"], "correct": "א", "reason": "הסבר", "source": "חוק"} for i in range(25)]
            st.session_state.step = "full_exam"
            st.session_state.exam_idx = 0
            st.session_state.checked_questions = set()
            st.rerun()

elif st.session_state.step == "study":
    # רשימת 16 הנושאים המלאה
    all_topics = [
        "חוק המתווכים במקרקעין", "תקנות המתווכים (פרטי הזמנה)", "חוק המקרקעין", 
        "חוק החוזים (כללי ותרופות)", "חוק הגנת הצרכן", "חוק המכר (דירות)", 
        "חוק התכנון והבנייה", "מיסוי מקרקעין", "חוק הגנת הדייר", 
        "חוק הירושה", "חוק המקרקעין (בתים משותפים)", "חוק השמאות",
        "חוק העונשין (מרמה וזיוף)", "דיני קניין", "אתיקה מקצועית", "חוק מקרקעי ישראל"
    ]
    sel_topic = st.selectbox("בחר נושא לימוד:", all_topics)
    
    if not st.session_state.lesson_text:
        if st.button("📖 התחל שיעור"):
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            model = genai.GenerativeModel('gemini-2.0-flash')
            resp = model.generate_content(f"כתוב שיעור מקיף על {sel_topic} למבחן המתווכים.", stream=True)
            ph = st.empty()
            full_t = ""
            for chunk in resp:
                full_t += chunk.text
                ph.markdown(f"<div class='lesson-box'>{full_t
