import streamlit as st
import google.generativeai as genai
import re

# 1. עיצוב ו-RTL
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

# 2. אתחול משתנים בצורה בטוחה
keys = ["user_name", "view_mode", "lesson_data", "quiz_data", 
        "history", "lesson_count", "user_answers", "current_topic", "quiz_ready"]

for k in keys:
    if k not in st.session_state:
        if k in ["quiz_data", "history", "user_answers"]: st.session_state[k] = []
        elif k == "lesson_count": st.session_state[k] = 0
        elif k == "quiz_ready": st.session_state[k] = False
        else: st.session_state[k] = ""

if "view_mode" not in st.session_state or not st.session_state.view_mode:
    st.session_state.view_mode = "login"

if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-2.0-flash')

def parse_quiz(text):
    questions = []
    blocks = re.findall(r"\[START_Q\](.*?)\[END_Q\]", text, re.DOTALL)
    for b in blocks:
        try:
            q = re.search(r"\[QUESTION\](.*?)\[OPTIONS\]", b, re.DOTALL).group(1).strip()
            opts_raw = re.search(r"\[OPTIONS\](.*?)\[ANSWER\]", b, re.DOTALL).group(1).strip()
            ans = re.search(r"\[ANSWER\](.*?)(?:\[LAW\]|$)", b, re.DOTALL).group(1).strip()
            law = re.search(r"\[LAW\](.*?)$", b, re.DOTALL).group(1).strip()
            options = [re.sub(r"^\d+[\s\).\-]+", "", o.strip()) for o in opts_raw.split('\n') if o.strip()]
            idx = int(re.search(r'\d', ans).group()) - 1
            questions.append({"q": q, "options": options[:4], "correct": idx, "ref": law})
        except: continue
    return questions

# 3. סרגל צידי
if st.session_state.user_name:
    with st.sidebar:
        st.markdown('<div class="sidebar-logo">🎓 מתווך בקליק</div>', unsafe_allow_html=True)
        st.write(f"שלום, **{st.session_state.user_name}**")
        if st.button("➕ נושא חדש"):
            st.session_state.view_mode = "setup"
            st.rerun()
        if st.session_state.current_topic:
            if st.button("📖 חזרה לשיעור"):
                st.session_state.view_mode = "lesson"; st.rerun()
            if st.session_state.quiz_ready:
                if st.button("📝 מעבר למבחן"):
                    st.session_state.view_mode = "quiz"; st.rerun()
        for h in st.session_state.history: st.caption(f"• {h}")

# 4. ניהול דפים
m = st.session_state.view_mode
if m == "login":
    st.title("🎓 מתווך בקליק")
    name = st.text_input("הזן שם:")
    if st.button("כניסה"):
        if name:
            st.session_state.user_name = name
            st.session_state.view_mode = "setup"
            st.rerun()

elif m == "setup":
    st.title(f"מה נלמד, {st.session_state.user_name}?")
    t = st.selectbox("נושא:", ["חוק המתווכים", "חוק המקרקעין", "דיני חוזים"])
    if st.button("התחל ללמוד"):
        st.session_state.current_topic = t
        st.session_state.lesson_count += 1
        st.session_state.view_mode = "streaming_lesson"
        st.rerun()

elif m == "streaming_lesson":
    st.title(f"שיעור: {st.session_state.current_topic}")
    placeholder = st.empty()
    full_text = ""
    res = model.generate_content(f"כתוב שיעור על {st.session_state.current_topic}", stream=True)
    for chunk in res:
        full_text += chunk.text
        placeholder.markdown(full_text)
    st.session_state.lesson_data = full_text
    
    with st.status("מכין שאלות..."):
        q_p = f"צור 3 שאלות על {st.session_state.current_topic}. פורמט: [START_Q] [QUESTION] שאלה [OPTIONS] 1) א 2) ב 3) ג 4) ד [ANSWER] מספר [LAW] סעיף [END_Q]"
        q_res = model.generate_content(q_p)
        st.session_state.quiz_data = parse_quiz(q_res.text)
        st.session_state.quiz_ready = True
    
    if st.session_state.current_topic not in st.session_state.history:
        st.session_state.history.append(st.session_state.current_topic)
