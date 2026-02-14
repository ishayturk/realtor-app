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
if "user" not in st.session_state: st.session_state.user = ""
if "step" not in st.session_state: st.session_state.step = "login"
if "lesson_text" not in st.session_state: st.session_state.lesson_text = ""
if "quiz_active" not in st.session_state: st.session_state.quiz_active = False
if "quiz_idx" not in st.session_state: st.session_state.quiz_idx = 0
if "quiz_answers" not in st.session_state: st.session_state.quiz_answers = {}
if "quiz_questions" not in st.session_state: st.session_state.quiz_questions = []
if "checked_questions" not in st.session_state: st.session_state.checked_questions = set()
if "exam_idx" not in st.session_state: st.session_state.exam_idx = 0
if "exam_answers" not in st.session_state: st.session_state.exam_answers = {}
if "exam_questions" not in st.session_state: st.session_state.exam_questions = []

def extract_json(text):
    try:
        match = re.search(r'\[\s*{.*}\s*\]', text, re.DOTALL)
        if match: return json.loads(match.group())
        return json.loads(text)
    except: return None

# --- 3. לוגיקה מרכזית ---
st.markdown("<h1>🏠 מתווך בקליק</h1>", unsafe_allow_html=True)

if st.session_state.user == "" or st.session_state.step == "login":
    name_input = st.text_input("הכנס שם מלא:")
    if st.button("כניסה למערכת"):
        if name_input:
            st.session_state.user = name_input
            st.session_state.step = "menu"
            st.rerun()

elif st.session_state.step == "menu":
    st.markdown(f"### שלום, {st.session_state.user} 👋")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📚 שיעור עיוני + שאלון"):
            st.session_state.step = "study"
            st.session_state.lesson_text = ""
            st.session_state.quiz_active = False
            st.rerun()
    with col2:
        if st.button("📝 סימולציית בחינה (25 שאלות)"):
            st.session_state.exam_questions = [{"q": f"שאלה {i+1} לסימולציה:", "options": ["א", "ב", "ג", "ד"], "correct": "א", "reason": "הסבר כללי.", "source": "חוק"} for i in range(25)]
            st.session_state.exam_idx = 0
            st.session_state.checked_questions = set()
            st.session_state.step = "full_exam"
            st.rerun()

elif st.session_state.step == "study":
    topics = ["חוק המתווכים", "חוק המקרקעין", "חוק החוזים", "חוק הגנת הצרכן", "חוק המכר (דירות)", "מיסוי מקרקעין"]
    selected_topic = st.selectbox("בחר נושא:", topics)
    
    if not st.session_state.lesson_text:
        if st.button("📖 התחל שיעור"):
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            model = genai.GenerativeModel('gemini-2.0-flash')
            response = model.generate_content(f"כתוב שיעור מפורט על {selected_topic} למבחן המתווכים.", stream=True)
            placeholder = st.empty()
            full_text = ""
            for chunk in response:
                full_text += chunk.text
                placeholder.markdown(f"<div class='lesson-box'>{full_text}</div>", unsafe_allow_html=True)
            st.session_state.lesson_text = full_text
            st.rerun()

    if st.session_state.lesson_text:
        st.markdown(f"<div class='lesson-box'>{st.session_state.lesson_text}</div>", unsafe_allow_html=True)
        if not st.session_state.quiz_active:
            if st.button("✍️ בנה שאלון על בסיס השיעור"):
                with st.spinner("מייצר שאלות..."):
                    model = genai.GenerativeModel('gemini-2.0-flash')
                    prompt = f"על בסיס הטקסט: {st.session_state.lesson_text}. צור 10 שאלות בפורמט JSON בלבד: [{{'q': 'שאלה', 'options': ['א','ב','ג','ד'], 'correct': 'תשובה', 'reason': 'הסבר', 'source': 'סעיף'}}]"
                    quiz_res = model.generate_content(prompt)
                    data = extract_json(quiz_res.text)
                    if data:
                        st.session_state.quiz_questions = data
                        st.session_state.quiz_active = True
                        st.session_state.checked_questions = set()
                        st.session_state.quiz_idx = 0
                        st.rerun()

    if st.session_state.quiz_active:
        idx = st.session_state.quiz_idx
        q = st.session_state.quiz_questions[idx]
        st.markdown(f"#### שאלה {idx+1}/10")
        ans = st.radio(q['q'], q['options'], key=f"q_{idx}", index=None)
        
        if
