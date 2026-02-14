import streamlit as st
import google.generativeai as genai
import json
import re

# 1. הגדרות תצוגה
st.set_page_config(page_title="מתווך בקליק", layout="wide")

st.markdown("""
<style>
    .stApp { direction: rtl !important; text-align: right !important; }
    [data-testid="stSidebar"] { display: none; }
    .main .block-container { max-width: 900px; }
    .app-header { text-align: center; color: #1E88E5; border-bottom: 2px solid #eee; padding-bottom: 10px; }
    .lesson-box { 
        background-color: #ffffff; padding: 30px; border-radius: 15px; 
        border-right: 8px solid #1E88E5; box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        font-size: 1.1rem; line-height: 1.7; margin-bottom: 25px;
    }
    .stButton > button { width: 100%; border-radius: 10px; font-weight: bold; height: 3.5em; }
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

# 3. פונקציות ליבה (מתוקנות)
def generate_lesson(topic):
    with st.spinner(f"כותב שיעור על {topic}..."):
        try:
            prompt = f"כתוב שיעור מפורט בעברית למבחן המתווכים על: {topic}. כלול סעיפי חוק והסברים."
            resp = model.generate_content(prompt)
            st.session_state.lesson = resp.text
            st.session_state.view = "lesson"
            st.rerun()
        except Exception as e:
            st.error(f"שגיאה בייצור שיעור: {e}")

def generate_questions(topic):
    with st.spinner("מייצר שאלות תרגול..."):
        try:
            # תיקון ה-ValueError: שימוש ב-double brackets {{ }} כדי למנוע התנגשות עם f-string
            prompt = f"""
            Create 10 multiple-choice questions in HEBREW about {topic}. 
            Return ONLY a JSON array with this structure: 
            [ {{"q": "question", "options": ["a", "b", "c", "d"], "correct": 0, "explanation": "text"}} ]
            """
            resp = model.generate_content(prompt)
            # חילוץ נקי של ה-JSON
            match = re.search(r'\[.*\]', resp.text, re.DOTALL)
            if match:
                st.session_state.questions = json.loads(match.group())
                st.session_state.answers = {}
                st.session_state.current_idx = 0
                st.session_state.feedback = False
                st.session_state.view = "quiz"
                st.rerun()
            else:
                st.error("ה-AI לא החזיר פורמט תקין. נסה שוב.")
        except Exception as e:
            st.error(f"שגיאה בייצור שאלות: {e}")

# 4. זרימת הדפים
st.markdown('<div class="app-header"><h1>🏠 מתווך בקליק</h1></div>', unsafe_allow_html=True)

if st.session_state.view == "login":
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        name = st.text_input("שם מלא:")
        if st.button("כניסה"):
            if name: st.session_state.user = name; st.session_state.view = "menu"; st.rerun()

elif st.session_state.view == "menu":
    st.subheader(f"שלום {st.session_state.user}, בחר נושא ללימוד:")
    full_syllabus = [
        "חוק המתווכים במקרקעין", "חוק המקרקעין", "חוק המכר (דירות)", 
        "חוק החוזים", "חוק הגנת הצרכן", "חוק הגנת הדייר", 
        "חוק התכנון והבנייה", "חוק מיסוי מקרקעין", "מושגי יסוד בכלכלה ושמאות"
    ]
    selected = st.selectbox("הסילבוס הרשמי:", ["בחר נושא..."] + full_syllabus)
    if selected != "בחר נושא...":
        st.session_state.topic = selected
        c1, c2 = st.columns(2)
        with c1: 
            if st.button("📖 פתח שיעור"): generate_lesson(selected)
        with c2: 
            if st.button("✍️ תרגול בלבד"): generate_questions(selected)

elif st.session_state.view == "lesson":
    st.header(st.session_state.topic)
    st.markdown(f'<div class="lesson-box">{st.session_state.lesson}</div>', unsafe_allow_html=True)
    if st.button(f"עבור לתרגול שאלות ב-{st.session_state.topic} ✍️"):
        generate_questions(st.session_state.topic)
    if st.button("חזרה לתפריט"): st.session_state.view = "menu"; st.rerun()

elif st.session_state.view == "quiz":
    idx = st.session_state.current_idx
    questions = st.session_state.questions
    q = questions[idx]
    
    # ניווט שאלות
    cols = st.columns(10)
    for i in range(len(questions)):
        with cols[i]:
            if st.button(f"{i+1}{'✓' if i in st.session_state.answers else ''}", key=f"n_{i}", type="primary" if i == idx else "secondary"):
                st.session_state.current_idx = i; st.session_state.feedback = False; st.rerun()

    st.subheader(f"שאלה {idx+1}")
    st.info(q['q'])
    
    user_ans = st.session_state.answers.get(idx)
    choice = st.radio("בחר תשובה:", q['options'], key=f"q_{idx}", index=q['options'].index(user_ans) if user_ans in q['options'] else None)
    
    if choice: st.session_state.answers[idx] = choice

    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("⬅️ הקודם", disabled=idx==0): st.session_state.current_idx -= 1; st.session_state.feedback = False; st.rerun()
    with c2:
        if st.button("בדוק תשובה"): st.session_state.feedback = True
    with c3:
        if idx < len(questions) - 1:
            if st.button("הבא ➡️"): st.session_state.current_idx += 1; st.session_state.feedback = False; st.rerun()
        else:
            if st.button("סיום וציון 🏁"): st.session_state.view = "score"; st.rerun()

    if st.session_state.feedback and choice:
        if q['options'].index(choice) == q['correct']: st.success("✅ נכון!")
        else: st.error(f"❌ טעות. הנכון: {q['options'][q['correct']]}")
        st.write(f"**הסבר:** {q['explanation']}")

elif st.session_state.view == "score":
    correct = sum(1 for i, q in enumerate(st.session_state.questions) if st.session_state.answers.get(i) == q['options'][q['correct']])
    st.header("🏁 סיכום")
    st.metric("ציון:", f"{correct*10}/100")
    if st.button("חזרה לתפריט"): st.session_state.view = "menu"; st.rerun()
