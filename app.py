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
if "user" not in st.session_state:
    st.session_state.user = ""
if "step" not in st.session_state:
    st.session_state.step = "login"
if "lesson_text" not in st.session_state:
    st.session_state.lesson_text = ""
if "quiz_active" not in st.session_state:
    st.session_state.quiz_active = False
if "quiz_idx" not in st.session_state:
    st.session_state.quiz_idx = 0
if "quiz_answers" not in st.session_state:
    st.session_state.quiz_answers = {}
if "quiz_questions" not in st.session_state:
    st.session_state.quiz_questions = []
if "checked_questions" not in st.session_state:
    st.session_state.checked_questions = set()
if "exam_idx" not in st.session_state:
    st.session_state.exam_idx = 0
if "exam_answers" not in st.session_state:
    st.session_state.exam_answers = {}
if "exam_questions" not in st.session_state:
    st.session_state.exam_questions = []

def extract_json(text):
    try:
        match = re.search(r'\[\s*{.*}\s*\]', text, re.DOTALL)
        if match:
            return json.loads(match.group())
        return json.loads(text)
    except:
        return None

# --- 3. לוגיקה מרכזית ---
st.markdown("<h1>🏠 מתווך בקליק</h1>", unsafe_allow_html=True)

# מסך כניסה
if st.session_state.user == "" or st.session_state.step == "login":
    name_input = st.text_input("הכנס שם מלא:")
    if st.button("כניסה למערכת"):
        if name_input:
            st.session_state.user = name_input
            st.session_state.step = "menu"
            st.rerun()

# תפריט ראשי
elif st.session_state.step == "menu":
    st.markdown(f"### שלום, {st.session_state.user} 👋")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("📚 שיעור + שאלון"):
            st.session_state.step = "study"
            st.session_state.lesson_text = ""
            st.session_state.quiz_active = False
            st.rerun()
    with c2:
        if st.button("📝 סימולציית 25 שאלות"):
            st.session_state.exam_questions = [{"q": f"שאלה {i+1}:", "options": ["א","ב","ג","ד"], "correct": "א", "reason": "הסבר", "source": "חוק"} for i in range(25)]
            st.session_state.exam_idx = 0
            st.session_state.checked_questions = set()
            st.session_state.step = "full_exam"
            st.rerun()

# לימוד ותרגול
elif st.session_state.step == "study":
    topics = ["חוק המתווכים", "חוק המקרקעין", "חוק החוזים", "חוק הגנת הצרכן", "חוק המכר (דירות)", "מיסוי מקרקעין"]
    sel_topic = st.selectbox("בחר נושא:", topics)
    
    if not st.session_state.lesson_text:
        if st.button("📖 התחל שיעור"):
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            model = genai.GenerativeModel('gemini-2.0-flash')
            resp = model.generate_content(f"כתוב שיעור על {sel_topic} למבחן המתווכים.", stream=True)
            ph = st.empty()
            txt = ""
            for chunk in resp:
                txt += chunk.text
                ph.markdown(f"<div class='lesson-box'>{txt}</div>", unsafe_allow_html=True)
            st.session_state.lesson_text = txt
            st.rerun()

    if st.session_state.lesson_text:
        st.markdown(f"<div class='lesson-box'>{st.session_state.lesson_text}</div>", unsafe_allow_html=True)
        if not st.session_state.quiz_active:
            if st.button("✍️ בנה שאלון על בסיס השיעור"):
                with st.spinner("מייצר שאלות..."):
                    model = genai.GenerativeModel('gemini-2.0-flash')
                    prompt = f"על בסיס הטקסט: {st.session_state.lesson_text}. צור 10 שאלות בפורמט JSON בלבד: [{{'q': 'שאלה', 'options': ['א','ב','ג','ד'], 'correct': 'תשובה', 'reason': 'הסבר', 'source': 'סעיף'}}]"
                    res = model.generate_content(prompt)
                    data = extract_json(res.text)
                    if data:
                        st.session_state.quiz_questions = data
                        st.session_state.quiz_active = True
                        st.session_state.checked_questions = set()
                        st.session_state.quiz_idx = 0
                        st.rerun()

    if st.session_state.quiz_active:
        cur_idx = st.session_state.quiz_idx
        item = st.session_state.quiz_questions[cur_idx]
        st.markdown(f"#### שאלה {cur_idx+1}/10")
        pick = st.radio(item['q'], item['options'], key=f"q_{cur_idx}", index=None)
        
        if pick and (cur_idx not in st.session_state.checked_questions):
            if st.button("🔍 בדוק תשובה"):
                st.session_state.quiz_answers[cur_idx] = pick
                st.session_state.checked_questions.add(cur_idx)
                st.rerun()

        if cur_idx in st.session_state.checked_questions:
            is_right = st.session_state.quiz_answers.get(cur_idx) == item['correct']
            cls = "success" if is_right else "error"
            sym = "✅ נכון!" if is_right else "❌ טעות."
            st.markdown(f'<div class="explanation-box {cls}"><b>{sym}</b><br>{item["reason"]}<br><b>מקור:</b> {item["source"]}</div>', unsafe_allow_html=True)
        
        col_prev, col_next = st.columns(2)
        if col_prev.button("⬅️ הקודם") and cur_idx > 0:
            st.session_state.quiz_idx -= 1
            st.rerun()
        if cur_idx < 9:
            if col_next.button("הבא ➡️"):
                st.session_state.quiz_idx += 1
                st.rerun()
        else:
            if st.button("🏁 סיום"):
                st.session_state.step = "menu"
                st.rerun()

# סימולציה
elif st.session_state.step == "full_exam":
    ex_idx = st.session_state.exam_idx
    ex_item = st.session_state.exam_questions[ex_idx]
    st.markdown(f"### סימולציה: שאלה {ex_idx+1} / 25")
    ex_pick = st.radio(ex_item['q'], ex_item['options'], key=f"ex_{ex_idx}", index=None)
    
    if ex_pick and (ex_idx not in st.session_state.checked_questions):
        if st.button("🔍 בדוק"):
            st.session_state.exam_answers[ex_idx] = ex_pick
            st.session_state.checked_questions.add(ex_idx)
            st.rerun()

    if ex_idx in st.session_state.checked_questions:
        ex_right = st.session_state.exam_answers.get(ex_idx) == ex_item['correct']
        ex_cls = "success" if ex_right else "error"
        st.markdown(f'<div class="explanation-box {ex_cls}"><b>{"✅" if ex_right else "❌"}</b> {ex_item["reason"]}</div>', unsafe_allow_html=True)
    
    b1, b2 = st.columns(2)
    if b1.button("⬅️ קודמת") and ex_idx > 0:
        st.session_state.exam_idx -= 1
        st.rerun()
    if ex_idx < 24:
        if b2.button("הבאה ➡️"):
            st.session_state.exam_idx += 1
            st.rerun()
    else:
        if st.button("סיים בחינה"):
            st.session_state.step = "menu"
            st.rerun()
