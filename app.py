import streamlit as st
import google.generativeai as genai
import re
import time
import os

# 1. עיצוב ו-CSS
st.set_page_config(page_title="מתווך בקליק", layout="wide")
st.markdown("""
    <style>
    html, body, [data-testid="stAppViewContainer"] { direction: rtl; text-align: right; }
    [data-testid="stMainBlockContainer"] { margin-right: auto; margin-left: 0; padding-right: 5rem; padding-left: 2rem; }
    [data-testid="stCodeBlock"], code, pre { direction: ltr !important; text-align: left !important; }
    .quiz-card { background-color: #ffffff; padding: 20px; border: 1px solid #e0e0e0; border-radius: 10px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    div.stButton > button { width: 100%; border-radius: 8px; font-weight: bold; background-color: #1E88E5; color: white; }
    </style>
    """, unsafe_allow_html=True)

# 2. ניהול מצב (Session State)
for key in ["user_name", "history", "lesson_data", "quiz_data", "current_title"]:
    if key not in st.session_state: st.session_state[key] = "" if "data" in key or "name" in key or "title" in key else []
if "view_mode" not in st.session_state: st.session_state.view_mode = "setup"

# 3. אתחול AI - תיקון ה-404 על ידי הגדרת גרסה יציבה
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    # יצירת המודל עם הגדרה מפורשת שמונעת שימוש ב-v1beta הישנה
    model = genai.GenerativeModel(
        model_name='gemini-1.5-flash'
    )

def parse_quiz(quiz_text):
    questions = []
    parts = re.split(r'שאלה \d+[:.)]?', quiz_text)[1:]
    for part in parts:
        lines = [l.strip() for l in part.strip().split('\n') if l.strip()]
        if len(lines) >= 3:
            q_text = lines[0]
            options = [l for l in lines if re.match(r'^[\d\)\.אבגד-]+\s', l)][:4]
            ans_match = re.search(r"(?:נכונה|היא|פתרון)[:\s]*(\d)", part)
            correct_idx = int(ans_match.group(1)) - 1 if ans_match else 0
            if len(options) >= 2:
                questions.append({"q": q_text, "options": options, "correct": correct_idx})
    return questions

# --- ממשק המשתמש ---
if not st.session_state.user_name:
    st.title("🎓 מתווך בקליק")
    name = st.text_input("הזן שם כדי להתחיל:")
    if st.button("כניסה"):
        if name: st.session_state.user_name = name; st.rerun()

elif st.session_state.view_mode == "setup":
    st.title("מה נלמד היום?")
    topic = st.selectbox("בחר נושא:", ["חוק המתווכים", "חוק המקרקעין", "דיני חוזים", "דיני תכנון ובנייה", "חוק הגנת הצרכן"])
    if st.button("כניסה לשיעור"):
        st.session_state.current_title = f"שיעור: {topic}"
        placeholder = st.empty()
        full_text = ""
        try:
            # ייצור שיעור
            res = model.generate_content(f"כתוב שיעור מפורט על {topic} למבחן המתווכים.")
            st.session_state.lesson_data = res.text
            # ייצור מבחן
            quiz_res = model.generate_content(f"צור 3 שאלות אמריקאיות על {topic}. פורמט: שאלה X: [טקסט] 1) [א] 2) [ב] 3) [ג] 4) [ד] תשובה נכונה: [מספר]")
            st.session_state.quiz_data = parse_quiz(quiz_res.text)
            
            if topic not in st.session_state.history: st.session_state.history.append(topic)
            st.session_state.view_mode = "lesson"
            st.rerun()
        except Exception as e:
            st.error(f"שגיאה בחיבור ל-AI: {e}")

elif st.session_state.view_mode == "lesson":
    st.title(st.session_state.current_title)
    st.markdown(st.session_state.lesson_data)
    if st.button("🔥 סיימתי ללמוד, אני רוצה להיבחן!"):
        st.session_state.view_mode = "quiz"
        st.rerun()

elif st.session_state.view_mode == "quiz":
    st.title(f"📝 מבחן: {st.session_state.current_title}")
    for i, q in enumerate(st.session_state.quiz_data):
        with st.container():
            st.markdown(f'<div class="quiz-card">', unsafe_allow_html=True)
            st.write(f"**{i+1}. {q['q']}**")
            choice = st.radio("בחר תשובה:", q['options'], key=f"q_{i}", index=None)
            if st.button("בדוק", key=f"b_{i}"):
                if choice:
                    idx = q['options'].index(choice)
                    if idx == q['correct']: st.success("נכון!")
                    else: st.error(f"טעות. התשובה הנכונה היא אופציה {q['correct']+1}")
                else: st.warning("בחר תשובה")
            st.markdown('</div>', unsafe_allow_html=True)
    if st.button("חזרה לשיעור"):
        st.session_state.view_mode = "lesson"; st.rerun()
