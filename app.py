import streamlit as st
import google.generativeai as genai
import json
import re

# 1. הגדרות RTL ועיצוב
st.set_page_config(page_title="מתווך בקליק", layout="wide")

st.markdown("""
<style>
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stMarkdownContainer"] {
        direction: rtl !important; text-align: right !important;
    }
    [data-testid="stSidebar"] { direction: rtl !important; text-align: right !important; }
    
    .app-header {
        background-color: #f8f9fa; padding: 25px; border-radius: 12px;
        text-align: center; border-bottom: 5px solid #1E88E5; margin-bottom: 30px;
    }
    
    .feedback-box { padding: 15px; border-radius: 8px; margin: 10px 0; border: 1px solid #eee; }
    .correct { background-color: #e6ffed; color: #1e4620; border-color: #b2f2bb; }
    .wrong { background-color: #fff5f5; color: #a91e2c; border-color: #ffa8a8; }
    
    .score-banner {
        background: linear-gradient(90deg, #1E88E5, #1565C0);
        color: white; padding: 20px; border-radius: 15px;
        text-align: center; margin-top: 40px; font-size: 1.2em;
    }
    .source-tag { 
        display: inline-block; background: #e7f3ff; color: #0d6efd; 
        padding: 4px 12px; border-radius: 20px; font-size: 0.85em; margin-top: 8px;
    }
</style>
""", unsafe_allow_html=True)

# כותרת קבועה
st.markdown("""
<div class="app-header">
    <div style="font-size: 60px; margin-bottom: 10px;">🎓</div>
    <h1 style='color: #1E88E5; margin: 0;'>מתווך בקליק</h1>
    <p style='color: #666;'>הכנה למבחן המתווכים - גרסה יציבה</p>
</div>
""", unsafe_allow_html=True)

# 2. Session State
if "view_mode" not in st.session_state:
    st.session_state.update({
        "view_mode": "login", "user_name": "", "current_topic": "", 
        "lesson_data": "", "quiz_questions": []
    })

if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-2.0-flash')

def generate_quiz_json(topic):
    prompt = f"Create a 5-question quiz in HEBREW about {topic}. Return ONLY a JSON array."
    try:
        response = model.generate_content(prompt)
        json_str = re.search(r'\[.*\]', response.text, re.DOTALL).group()
        return json.loads(json_str)
    except: return None

# 3. Sidebar
if st.session_state.user_name:
    with st.sidebar:
        st.write(f"### שלום, {st.session_state.user_name}")
        if st.button("🏠 נושא חדש"):
            st.session_state.update({"view_mode": "setup", "quiz_questions": []})
            st.rerun()
        if st.session_state.current_topic:
            if st.button("📖 חזרה לשיעור"):
                st.session_state.view_mode = "lesson_view"; st.rerun()
        if st.button("🚪 יציאה"):
            st.session_state.clear(); st.rerun()

# 4. לוגיקה
if st.session_state.view_mode == "login":
    name = st.text_input("שם משתמש:")
    if st.button("כניסה"):
        if name: st.session_state.user_name = name; st.session_state.view_mode = "setup"; st.rerun()

elif st.session_state.view_mode == "setup":
    st.header("בחר נושא")
    topics = ["חוק המתווכים", "חוק המקרקעין", "חוק המכר (דירות)", "חוק הגנת הצרכן", "חוק החוזים", "מיסוי מקרקעין"]
    t = st.selectbox("נושא:", topics)
    if st.button("התחל"):
        st.session_state.update({"current_topic": t, "lesson_data": "", "quiz_questions": [], "view_mode": "lesson_view"})
        st.rerun()

elif st.session_state.view_mode == "lesson_view":
    st.header(st.session_state.current_topic)
    if not st.session_state.lesson_data:
        with st.spinner("מייצר שיעור..."):
            resp = model.generate_content(f"כתוב שיעור מפורט על {st.session_state.current_topic}.")
            st.session_state.lesson_data = resp.text
    st.markdown(st.session_state.lesson_data)
    if st.button("🎯 בוא נתרגל"):
        st.session_state.view_mode = "lesson_quiz"; st.rerun()

elif st.session_state.view_mode == "lesson_quiz":
    st.header(f"תרגול: {st.session_state.current_topic}")
    if not st.session_state.quiz_questions:
        with st.spinner("מייצר שאלות..."):
            st.session_state.quiz_questions = generate_quiz_json(st.session_state.current_topic)
            st.rerun()

    score = 0
    answered = 0
    for i, q in enumerate(st.session_state.quiz_questions):
        st.subheader(f"שאלה {i+1}")
        st.write(q['q'])
        choice = st.radio(f"בחר תשובה {i+1}:", q['options'], key=f"q_v52_{i}", index=None)
        if choice:
            answered += 1
            idx = q['options'].index(choice)
            if idx == q['correct']:
                st.markdown(f'<div class="feedback-box correct">✅ **נכון!** {q.get("explanation","")}</div>', unsafe_allow_html=True)
                score += 1
            else:
                st.markdown(f'<div class="feedback-box wrong">❌ **טעות.** הנכון: {q["options"][q["correct"]]}<br>{q.get("explanation","")}</div>', unsafe_allow_html=True)
        st.markdown("---")

    if answered > 0:
        st.markdown(f'<div class="score-banner">ציון: {score} מתוך {len(st.session_state.quiz_questions)}</div>', unsafe_allow_html=True)
        if score == len(st.session_state.quiz_questions):
            st.balloons()
            st.success("ציון מושלם!")
