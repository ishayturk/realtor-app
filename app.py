import streamlit as st
import google.generativeai as genai
import json
import re

# 1. הגדרות RTL ועיצוב
st.set_page_config(page_title="מתווך בקליק", layout="wide")

st.markdown("""
<style>
    /* הגדרות כיווניות כלליות */
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stMarkdownContainer"] {
        direction: rtl !important; text-align: right !important;
    }
    [data-testid="stSidebar"] { direction: rtl !important; text-align: right !important; }
    
    /* עיצוב הלוגו בתוך הסיידבר */
    .sidebar-header {
        text-align: center;
        padding: 20px 10px;
        background-color: #f8f9fa;
        border-radius: 10px;
        margin-bottom: 20px;
        border: 1px solid #e0e0e0;
    }
    .sidebar-logo { font-size: 50px; }
    .sidebar-title { color: #1E88E5; font-size: 22px; font-weight: bold; margin: 5px 0; }
    
    .feedback-box { padding: 15px; border-radius: 8px; margin: 10px 0; border: 1px solid #eee; }
    .correct { background-color: #e6ffed; color: #1e4620; border-color: #b2f2bb; }
    .wrong { background-color: #fff5f5; color: #a91e2c; border-color: #ffa8a8; }
</style>
""", unsafe_allow_html=True)

# 2. ניהול Session State
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

# 3. סיידבר - הלוגו והשם עוברים לכאן!
with st.sidebar:
    # לוגו ושם מופיעים תמיד בראש הפריים הימני
    st.markdown("""
    <div class="sidebar-header">
        <div class="sidebar-logo">🏠</div>
        <div class="sidebar-title">מתווך בקליק</div>
        <div style="font-size: 12px; color: #888;">הכנה למבחן המתווכים</div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.session_state.user_name:
        st.write(f"👤 **שלום, {st.session_state.user_name}**")
        st.markdown("---")
        if st.button("📚 נושא חדש"):
            st.session_state.update({"view_mode": "setup", "quiz_questions": []})
            st.rerun()
        if st.session_state.current_topic:
            if st.button("📖 חזרה לשיעור"):
                st.session_state.view_mode = "lesson_view"; st.rerun()
        if st.button("🚪 יציאה"):
            st.session_state.clear(); st.rerun()

# 4. לוגיקת דפים (מרכז המסך נקי)
if st.session_state.view_mode == "login":
    st.subheader("ברוכים הבאים - כניסה למערכת")
    name = st.text_input("הכנס שם מלא:")
    if st.button("התחל ללמוד"):
        if name: st.session_state.user_name = name; st.session_state.view_mode = "setup"; st.rerun()

elif st.session_state.view_mode == "setup":
    st.header("מה נלמד היום?")
    topics = ["חוק המתווכים", "חוק המקרקעין", "חוק המכר (דירות)", "חוק הגנת הצרכן", "חוק החוזים", "מיסוי מקרקעין"]
    t = st.selectbox("בחר נושא:", topics)
    if st.button("התחל שיעור"):
        st.session_state.update({"current_topic": t, "lesson_data": "", "quiz_questions": [], "view_mode": "lesson_view"})
        st.rerun()

elif st.session_state.view_mode == "lesson_view":
    st.header(st.session_state.current_topic)
    if not st.session_state.lesson_data:
        with st.spinner("Gemini מייצר שיעור מפורט..."):
            resp = model.generate_content(f"כתוב שיעור מפורט על {st.session_state.current_topic} למבחן המתווכים.")
            st.session_state.lesson_data = resp.text
    st.markdown(st.session_state.lesson_data)
    st.button("🎯 עבור לשאלון תרגול", on_click=lambda: st.session_state.update({"view_mode": "lesson_quiz"}))

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
        choice = st.radio(f"בחר תשובה {i+1}:", q['options'], key=f"q_vSidebar_{i}", index=None)
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
        st.info(f"ציון נוכחי: {score} מתוך {len(st.session_state.quiz_questions)}")
        if score == len(st.session_state.quiz_questions):
            st.balloons()
