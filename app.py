import streamlit as st
import google.generativeai as genai
import re

# 1. הגדרות עיצוב ויישור RTL
st.set_page_config(page_title="מתווך בקליק", layout="wide")

st.markdown("""
<style>
html, body, [data-testid="stAppViewContainer"], .main, .block-container, 
div[data-testid="stMarkdownContainer"], h1, h2, h3, p, li, span, label {
    direction: rtl !important; text-align: right !important;
}
.sidebar-logo {
    font-size: 34px !important; font-weight: bold; text-align: center !important;
    margin-top: -50px !important; color: #1E88E5; display: block; width: 100%;
}
[data-testid="stSidebar"] button, div.stButton > button {
    width: 100% !important; border-radius: 8px; font-weight: bold;
    background-color: #1E88E5; color: white;
}
.quiz-card { 
    background-color: #f9f9f9; padding: 20px; border-radius: 12px; 
    border-right: 6px solid #1E88E5; margin-bottom: 20px;
}
</style>
""", unsafe_allow_html=True)

# 2. רשימת נושאים
TOPICS = [
    "בחר נושא...",
    "חוק המתווכים במקרקעין",
    "חוק המקרקעין",
    "חוק המכר (דירות)",
    "חוק הגנת הצרכן",
    "חוק החוזים",
    "דיני תכנון ובנייה",
    "מיסוי מקרקעין",
    "חוק העונשין",
    "חוק שמאי מקרקעין"
]

# 3. ניהול משתני Session State - אתחול מלא
if "user_name" not in st.session_state: st.session_state.user_name = ""
if "view_mode" not in st.session_state: st.session_state.view_mode = "login"
if "lesson_data" not in st.session_state: st.session_state.lesson_data = ""
if "quiz_data" not in st.session_state: st.session_state.quiz_data = []
if "history" not in st.session_state: st.session_state.history = []
if "current_topic" not in st.session_state: st.session_state.current_topic = ""
if "quiz_ready" not in st.session_state: st.session_state.quiz_ready = False

# הגדרת ה-AI
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-2.0-flash')

def parse_quiz(text):
    qs = []
    blocks = re.findall(r"\[START_Q\](.*?)\[END_Q\]", text, re.DOTALL)
    for b in blocks:
        try:
            q = re.search(r"\[QUESTION\](.*?)\[OPTIONS\]", b, re.DOTALL).group(1).strip()
            opts_raw = re.search(r"\[OPTIONS\](.*?)\[ANSWER\]", b, re.DOTALL).group(1).strip()
            ans_val = re.search(r"\[ANSWER\](.*?)(?:\[LAW\]|$)", b, re.DOTALL).group(1).strip()
            law_val = re.search(r"\[LAW\](.*?)$", b, re.DOTALL).group(1).strip()
            opts = [re.sub(r"^\d+[\s\).\-]+", "", o.strip()) for o in opts_raw.split('\n') if o.strip()]
            idx = int(re.search(r'\d', ans_val).group()) - 1
            qs.append({"q": q, "options": opts[:4], "correct": idx, "ref": law_val})
        except: continue
    return qs

# 4. סרגל צידי - ניווט
if st.session_state.user_name:
    with st.sidebar:
        st.markdown('<div class="sidebar-logo">🎓 מתווך בקליק</div>', unsafe_allow_html=True)
        st.write(f"שלום, **{st.session_state.user_name}**")
        if st.button("➕ נושא חדש"):
            st.session_state.view_mode = "setup"
            st.session_state.current_topic = ""
            st.session_state.quiz_ready = False
            st.rerun()
        if st.session_state.current_topic:
            st.markdown(f"**נושא: {st.session_state.current_topic}**")
            if st.session_state.view_mode == "quiz":
                if st.button("📖 חזרה לשיעור"):
                    st.session_state.view_mode = "lesson"; st.rerun()
            if st.session_state.quiz_ready and st.session_state.view_mode != "quiz":
                if st.button("📝 מעבר למבחן"):
                    st.session_state.view_mode = "quiz"; st.rerun()
        st.markdown("---")
        for h in st.session_state.history: st.caption(f"• {h}")

# 5. ניהול דפים לפי view_mode
current_mode = st.session_state.view_mode

if current_mode == "login":
    st.title("🎓 מתווך בקליק")
    name = st.text_input("הזן שם כדי להתחיל:")
    if st.button("כניסה"):
        if name:
            st.session_state.user_name = name
            st.session_state.view_mode = "setup"; st.rerun()

elif current_mode == "setup":
    st.title(f"מה נלמד היום, {st.session_state.user_name}?")
    t = st.selectbox("בחר נושא להתחלת למידה מיידית:", TOPICS)
    if t != "בחר נושא...":
        st.session_state.current_topic = t
        st.session_state.quiz_ready = False
        st.session_state.view_mode = "streaming_lesson"; st.rerun()

elif current_mode == "streaming_lesson":
    st.title(f"שיעור: {st.session_state.current_topic}")
    placeholder = st.empty()
    full_txt = ""
    try:
        res = model.generate_content(f"כתוב שיעור מפורט על {st.session_state.current_topic} למבחן המתווכים.", stream=True)
        for chunk in res:
            full_txt += chunk.text
            placeholder.markdown(full_txt)
        st.session_state.lesson_data = full_txt
        with st.status("מכין שאלות תרגול בתפריט הצד..."):
            q_p = f"צור 3 שאלות על {st.session_state.current_topic}. פורמט: [START_Q] [QUESTION] שאלה [OPTIONS] 1) א 2) ב 3) ג 4) ד [ANSWER] מספר [LAW] סעיף [END_Q]"
            q_res = model.generate_content(q_p)
            st.session_state.quiz_data = parse_quiz(q_res.text)
            st.session_state.quiz_ready = True
        if st.session_state.current_topic not in st.session_state.history:
            st.session_state.history.append(st.session_state.current_topic)
        st.session_state.view_mode = "lesson"; st.rerun()
    except Exception as e:
        st.error(f"שגיאה בייצור תוכן: {e}")

elif current_mode == "lesson":
    st.title(st.session_state.current_topic)
    st.markdown(st.session_state.lesson_data)
    st.info("השיעור מוכן. כפתור המבחן זמין כעת בתפריט הצד מימין.")

elif current_mode == "quiz":
    st.title(f"תרגול: {st.session_state.current_topic}")
    for i, q in enumerate(st.session_state.quiz_data):
        st.markdown('<div class="quiz-card">', unsafe_allow_html=True)
        st.write(f"**{i+1}. {q['q']}**")
        ans = st.radio("בחר תשובה:", q['options'], key=f"quiz_q_{i}", index=None)
        if st.button(f"בדוק תשובה {i+1}", key=f"quiz_b_{i}"):
            if ans:
                if q['options'].index(ans) == q['correct']: st.success("נכון מאוד!")
                else: st.error(f"טעות. התשובה הנכונה היא: {q['options'][q['correct']]}")
                st.info(f"⚖️ {q['ref']}")
        st.markdown('</div>', unsafe_allow_html=True)
