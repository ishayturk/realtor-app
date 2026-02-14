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

def extract_json(text):
    try:
        match = re.search(r'\[\s*{.*}\s*\]', text, re.DOTALL)
        if match: return json.loads(match.group())
        return json.loads(text)
    except: return None

# --- 3. לוגיקה ---
st.markdown("<h1>🏠 מתווך בקליק</h1>", unsafe_allow_html=True)

if not st.session_state.user or st.session_state.step == "login":
    name_input = st.text_input("הכנס שם מלא:")
    if st.button("כניסה"):
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
            st.session_state.step = "full_exam"
            st.rerun()

elif st.session_state.step == "study":
    st.markdown(f"**לומד כעת:** {st.session_state.user}")
    
    # רשימת נושאים מלאה ומורחבת
    topics = [
        "חוק המתווכים במקרקעין",
        "תקנות המתווכים (פרטי הזמנה בכתב)",
        "חוק המקרקעין (עסקאות, רישום, זכויות)",
        "חוק החוזים (חלק כללי ותרופות)",
        "חוק הגנת הצרכן (בהקשר של תיווך)",
        "חוק המכר (דירות)",
        "חוק התכנון והבנייה (מושגי יסוד)",
        "מיסוי מקרקעין (מס שבח, מס רכישה)",
        "חוק העונשין (עבירות מרמה וזיוף)",
        "אתיקה מקצועית למתווכים"
    ]
    
    selected_topic = st.selectbox("בחר נושא מורחב ללימוד:", topics)
    
    if not st.session_state.lesson_text:
        if st.button("📖 התחל שיעור"):
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            model = genai.GenerativeModel('gemini-2.0-flash')
            response = model.generate_content(f"כתוב שיעור מעמיק ומפורט על {selected_topic} למבחן רשם המתווכים.", stream=True)
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
                with st.spinner("מייצר 10 שאלות מהחומר..."):
                    model = genai.GenerativeModel('gemini-2.0-flash')
                    prompt = f"על בסיס הטקסט: {st.session_state.lesson_text}. צור 10 שאלות אמריקאיות בפורמט JSON בלבד: [{{'q': 'שאלה', 'options': ['א','ב','ג','ד'], 'correct': 'התשובה המדויקת', 'reason': 'הסבר', 'source': 'סעיף'}}] - החזר רק את ה-JSON."
                    quiz_response = model.generate_content(prompt)
                    data = extract_json(quiz_response.text)
                    if data:
                        st.session_state.quiz_questions = data
                        st.session_state.quiz_active = True
                        st.session_state.checked_questions = set()
                        st.session_state.quiz_idx = 0
                        st.rerun()
                    else:
                        st.error("נסיון יצירת שאלון נכשל, נסה שנית.")

    if st.session_state.quiz_active:
        idx = st.session_state.quiz_idx
        q = st.session_state.quiz_questions[idx]
        st.markdown(f"#### שאלה {idx+1}/10")
        ans = st.radio(q['q'], q['options'], key=f"q_{idx}", index=None)
        
        if ans and idx not in st.session_state.checked_questions:
            if st.button("🔍 בדוק תשובה"):
                st.session_state.quiz_answers[idx] = ans
                st.session_state.checked_questions.add(idx)
                st.rerun()

        if idx in st.session_state.checked_questions:
            user_ans = st.session_state.quiz_answers.get(idx)
            is_correct = user_ans == q['correct']
            style = "success" if is_correct else "error"
            st.markdown(f"<div class='explanation-box {style}'><b>{'✅ נכון!' if is_correct else '❌ טעות.'}</b><br>{q['reason']}<br><b>מקור:</b> {q['source']}</div>", unsafe_allow_html=True)
        
        c1, c2 = st.columns(2)
        if c1.button("⬅️ הקודם") and idx > 0: st.session_state.quiz_idx -= 1; st.rerun()
        if idx
