import streamlit as st
import google.generativeai as genai
import json
import re
import time
import random

# ==========================================
# 1. הגדרות ועיצוב
# ==========================================
def apply_design():
    st.set_page_config(page_title="מתווך בקליק", layout="wide")
    st.markdown("""
    <style>
        html, body, [data-testid="stAppViewContainer"], .main, .block-container {
            direction: rtl !important; text-align: right !important;
        }
        .main-header {
            text-align: center !important; background: linear-gradient(90deg, #1E88E5, #1565C0);
            color: white !important; padding: 15px; border-radius: 15px; margin-bottom: 15px;
        }
        .lesson-box {
            background-color: #ffffff !important; color: #1a1a1a !important; padding: 20px; 
            border-radius: 15px; border-right: 8px solid #1E88E5; box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            line-height: 1.8; direction: rtl !important; text-align: right !important;
        }
        .timer-text {
            font-size: 20px; font-weight: bold; color: #d32f2f; text-align: center;
            background: #ffebee; padding: 10px; border-radius: 10px; margin-bottom: 15px;
        }
        .stButton button { width: 100% !important; border-radius: 10px !important; }
        [data-testid="stSidebar"] { display: none; }
        .score-display { background: #e3f2fd; padding: 10px; border-radius: 10px; text-align: center; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. נתונים (סילבוס ומאגר בסיסי)
# ==========================================
FULL_SYLLABUS = [
    "חוק המתווכים במקרקעין", "חוק המקרקעין", "חוק המכר (דירות)",
    "חוק החוזים", "חוק הגנת הצרכן", "חוק הגנת הדייר",
    "חוק התכנון והבנייה", "חוק מיסוי מקרקעין", "חוק הירושה"
]

def get_official_questions():
    # כאן מוסיפים את השאלות מהלינק
    return [
        {"q": "מהי תקופת הבלעדיות המקסימלית בדירת מגורים?", "options": ["3 חודשים", "6 חודשים", "שנה", "9 חודשים"], "correct": 1, "explanation": "לפי חוק המתווכים, בלעדיות בדירת מגורים לא תעלה על 6 חודשים."},
        {"q": "האם הסכם תיווך חייב להיות בכתב?", "options": ["לא, מספיק בעל פה", "כן, חובה הזמנה בכתב", "רק אם העסקה מעל מיליון שח", "רק בבלעדיות"], "correct": 1, "explanation": "סעיף 9 לחוק מחייב הזמנה בכתב חתומה."},
    ] * 13 # שכפול לצורך הדגמת 25 שאלות

# ==========================================
# 3. מנוע AI
# ==========================================
def init_gemini():
    if "GEMINI_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        return genai.GenerativeModel('gemini-2.0-flash')
    return None

def fetch_quiz(model, topic):
    prompt = f"צור 10 שאלות אמריקאיות בעברית על {topic}. החזר רק JSON: [{{'q':'','options':['','','',''],'correct':0,'explanation':''}}]"
    try:
        resp = model.generate_content(prompt)
        match = re.search(r'\[\s*\{.*\}\s*\]', resp.text, re.DOTALL)
        return json.loads(match.group()) if match else None
    except: return None

# ==========================================
# 4. ניהול האפליקציה
# ==========================================
def main():
    apply_design()
    model = init_gemini()
    
    if "view" not in st.session_state:
        st.session_state.update({
            "view": "login", "user": "", "topic": "", "lesson": "", 
            "questions": [], "idx": 0, "show_f": False, "correct_answers": 0,
            "exam_questions": [], "user_answers": {}, "start_time": None
        })

    st.markdown('<div class="main-header"><h1 style="margin:0; font-size: 22px; color: white;">🏠 מתווך בקליק</h1></div>', unsafe_allow_html=True)

    # --- כניסה ---
    if st.session_state.view == "login":
        name = st.text_input("הכנס שם מלא:", key="login_name")
        if st.button("כניסה למערכת"):
            if name: st.session_state.user = name; st.session_state.view = "menu"; st.rerun()

    # --- תפריט ראשי ---
    elif st.session_state.view == "menu":
        st.write(f"### שלום {st.session_state.user}")
        t1, t2 = st.tabs(["📚 לימוד לפי נושא", "⏱️ מבחן רישוי"])
        
        with t1:
            selected = st.selectbox("בחר נושא ללימוד:", ["בחר..."] + FULL_SYLLABUS)
            if selected != "בחר...":
                st.session_state.topic = selected
                if st.button("📖 פתח שיעור"):
                    st.session_state.lesson = ""; st.session_state.view = "lesson"; st.rerun()
        
        with t2:
            st.write("סימולציה מלאה של 25 שאלות מהמאגר הרשמי.")
            if st.button("🚀 התחל מבחן (90 דק')"):
                st.session_state.exam_questions = get_official_questions()
                st.session_state.user_answers = {}; st.session_state.idx = 0; st.session_state.start_time = time.time(); st.session_state.view = "exam"; st.rerun()

    # --- דף שיעור ---
    elif st.session_state.view == "lesson":
        st.subheader(f"📍 שיעור: {st.session_state.topic}")
        if st.button("🏠 חזרה לתפריט"): st.session_state.view = "menu"; st.rerun()
        
        if not st.session_state.lesson:
            with st.spinner("ה-AI כותב את השיעור..."):
                resp = model.generate_content(f"כתוב שיעור מפורט למבחן המתווכים על {st.session_state.topic} בעברית.")
                st.session_state.lesson = resp.text
        
        st.markdown(f'<div class="lesson-box">{st.session_state.lesson}</div>', unsafe_allow_html=True)
        
        if st.button("עבור לתרגול שאלות ✍️"):
            with st.spinner("מכין שאלות..."):
                qs = fetch_quiz(model, st.session_state.topic)
                if qs:
                    st.session_state.questions = qs
                    st.session_state.correct_answers = 0
                    st.session_state.idx = 0
                    st.session_state.show_f = False
                    st.session_state.view = "quiz"; st.rerun()

    # --- שאלון סוף נושא ---
    elif st.session_state.view == "quiz":
        idx = st.session_state.idx
        q = st.session_state.questions[idx]
        st.markdown(f'<div class="score-display">שאלה {idx+1}/10 | נכון: {st.session_state.correct_answers}</div>', unsafe_allow_html=True)
        
        st.info(q['q'])
        choice = st.radio("בחר תשובה:", q['options'], key=f"q_{idx}", index=None)
        
        if st.button("בדוק תשובה ✅"):
            if choice: st.session_state.show_f = True
        
        if st.session_state.show_f:
            correct_text = q['options'][q['correct']]
            if choice == correct_text:
                if f"scored_{idx}" not in st.session_state:
                    st.session_state.correct_answers += 1
                    st.session_state[f"scored_{idx}"] = True
                st.success("נכון!")
            else: st.error(f"טעות. התשובה היא: {correct_text}")
            
            st.write(f"**הסבר:** {q['explanation']}")
            
            if idx < 9:
                if st.button("הבא ➡️"): st.session_state.idx += 1; st.session_state.show_f = False; st.rerun()
            else:
                st.balloons()
                st.write(f"### סיימת! הציון: {st.session_state.correct_answers * 10}")
                if st.button("חזרה לתפריט"): st.session_state.view = "menu"; st.rerun()

    # --- מבחן רישוי ---
    elif st.session_state.view == "exam":
        elapsed = time.time() - st.session_state.start_time
        rem = max(0, 90 * 60 - elapsed)
        st.markdown(f'<div class="timer-text">⏱️ זמן נותר: {int(rem//60):02d}:{int(rem%60):02d}</div>', unsafe_allow_html=True)
        
        idx = st.session_state.idx
        q = st.session_state.exam_questions[idx]
        st.write(f"**שאלה {idx + 1} מתוך 25**")
        st.info(q['q'])
        
        ans = st.session_state.user_answers.get(idx + 1)
        choice = st.radio("תשובה:", q['options'], key=f"ex_{idx}", index=None if ans is None else q['options'].index(ans))
        if choice: st.session_state.user_
