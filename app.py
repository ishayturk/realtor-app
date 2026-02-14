import streamlit as st
import google.generativeai as genai
import re
import time

# 1. הגדרות עיצוב ו-RTL
st.set_page_config(page_title="מתווך בקליק", layout="wide")

st.markdown("""
    <style>
    .sidebar-logo {
        font-size: 34px !important; font-weight: bold; text-align: center;
        margin-top: -60px !important; color: #1E88E5; padding-bottom: 10px;
    }
    html, body, [data-testid="stAppViewContainer"], .main, .block-container {
        direction: rtl !important; text-align: right !important;
    }
    .stMarkdown, .stMarkdown p, .stMarkdown li {
        direction: rtl !important; text-align: right !important;
    }
    div.stButton > button { 
        width: 100%; border-radius: 8px; font-weight: bold;
        background-color: #1E88E5; color: white;
    }
    .quiz-card { 
        background-color: #ffffff; padding: 20px; border-radius: 12px; 
        border-right: 6px solid #1E88E5; box-shadow: 0 2px 4px rgba(0,0,0,0.05); margin-bottom: 20px;
    }
    </style>
    <script>
        function forceScrollUp() {
            var mainSec = window.parent.document.querySelector('section.main');
            if (mainSec) { mainSec.scrollTo({top: 0, behavior: 'instant'}); }
        }
        forceScrollUp();
    </script>
    """, unsafe_allow_html=True)

# 2. אתחול משתנים
for key, default in [
    ("user_name", ""), ("view_mode", "login"), ("lesson_data", ""), 
    ("quiz_data", []), ("history", []), ("lesson_count", 0), 
    ("user_answers", {}), ("current_topic", "")
]:
    if key not in st.session_state: st.session_state[key] = default

# חיבור ל-AI
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-2.0-flash')

def parse_quiz(quiz_text):
    questions = []
    blocks = re.findall(r"\[START_Q\](.*?)\[END_Q\]", quiz_text, re.DOTALL)
    for b in blocks:
        try:
            q = re.search(r"\[QUESTION\](.*?)\[OPTIONS\]", b, re.DOTALL).group(1).strip()
            opts_raw = re.search(r"\[OPTIONS\](.*?)\[ANSWER\]", b, re.DOTALL).group(1).strip()
            ans = re.search(r"\[ANSWER\](.*?)\[LAW\]", b, re.DOTALL).group(1).strip()
            law = re.search(r"\[LAW\](.*?)$", b, re.DOTALL).group(1).strip()
            options = [re.sub(r"^\d+[\s\).\-]+", "", o.strip()) for o in opts_raw.split('\n') if o.strip()]
            questions.append({"q": q, "options": options[:4], "correct": int(re.search(r'\d', ans).group())-1, "ref": law})
        except: continue
    return questions

# 3. סרגל צידי
if st.session_state.user_name:
    with st.sidebar:
        st.markdown('<div class="sidebar-logo">🎓 מתווך בקליק</div>', unsafe_allow_html=True)
        st.write(f"שלום, **{st.session_state.user_name}**")
        if st.button("➕ נושא חדש"):
            st.session_state.update({"lesson_data": "", "quiz_data": [], "user_answers": {}, "view_mode": "setup"})
            st.rerun()
        if st.session_state.quiz_data:
            btn_label = "📝 למבחן" if st.session_state.view_mode != "quiz" else "📖 לשיעור"
            if st.button(btn_label):
                st.session_state.view_mode = "quiz" if st.session_state.view_mode != "quiz" else "lesson"
                st.rerun()
        st.markdown("---")
        for h in st.session_state.history: st.caption(f"• {h}")

# 4. ניהול דפים
mode = st.session_state.view_mode

if mode == "login":
    st.title("🎓 מתווך בקליק")
    name = st.text_input("הזן שם:")
    if st.button("כניסה"):
        if name: st.session_state.user_name = name; st.session_state.view_mode = "setup"; st.rerun()

elif mode == "setup":
    st.title(f"מה נלמד, {st.session_state.user_name}?")
    topic = st.selectbox("נושא:", ["חוק המתווכים", "חוק המקרקעין", "דיני חוזים", "דיני תכנון ובנייה"])
    if st.button("הכן שיעור"):
        st.session_state.lesson_count += 1
        st.session_state.current_topic = topic
        pb = st.progress(0)
        try:
            pb.progress(30)
            res = model.generate_content(f"כתוב שיעור על {topic} למבחן המתווכים.")
            st.session_state.lesson_data = res.text
            pb.progress(70)
            q_res = model.generate_content(f"צור 3 שאלות על {topic}. פורמט: [START_Q] [QUESTION] שאלה [OPTIONS] 1) א 2) ב 3) ג 4) ד [ANSWER] מספר [LAW] סעיף [END_Q]")
            st.session_state.quiz_data = parse_quiz(q_res.text)
            pb.progress(100)
            if topic not in [h.split(". ", 1)[-1] for h in st.session_state.history]:
                st.session_state.history.append(f"{st.session_state.lesson_count}. {topic}")
            st.session_state.view_mode = "lesson"; st.rerun()
        except Exception as e: st.error(f"שגיאה: {e}")

elif mode == "lesson":
    st.title(f"שיעור: {st.session_state.current_topic}")
    st.markdown(st.session_state.lesson_data)
    if st.button("למבחן 📝"):
        st.session_state.view_mode = "quiz"; st.rerun()

elif mode == "quiz":
    st.title(f"תרגול: {st.session_state.current_topic}")
    for i, q in enumerate(st.session_state.quiz_data):
        with st.container():
            st.markdown(f'<div class="quiz-card">', unsafe_allow_html=True)
            st.write(f"**{i+1}. {q['q']}**")
            ans = st.radio("בחר:", q['options'], key=f"q{i}", index=None, label_visibility="collapsed")
            if st.button(f"בדוק {i+1}", key=f"b{i}"):
                if ans:
                    is_correct = q['options'].index(ans) == q['correct']
                    st.session_state.user_answers[i] = is_correct
                    st.success("נכון!") if is_correct else st.error(f"טעות. הנכונה: {q['options'][q['correct']]}")
                    st.info(f"⚖️ {q['ref']}")
            st.markdown('</div>', unsafe_allow_html=True)
