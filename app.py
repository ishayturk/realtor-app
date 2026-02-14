import streamlit as st
import google.generativeai as genai
import re
import time

# 1. הגדרות ועיצוב RTL
st.set_page_config(page_title="מתווך בקליק - סימולטור", layout="wide")

def scroll_to_top():
    st.components.v1.html(
        """<script>window.parent.document.querySelector('.main').scrollTo(0,0);</script>""",
        height=0,
    )

st.markdown("""
<style>
html, body, [data-testid="stAppViewContainer"], .main, .block-container {
    direction: rtl !important; text-align: right !important;
}
h1, h2, h3, h4, h5, p, span, label, div {
    text-align: right !important;
}
.timer-display {
    font-size: 28px; font-weight: bold; color: #e63946;
    text-align: center !important; padding: 15px;
    border: 3px solid #e63946; border-radius: 12px;
    margin-bottom: 20px; background-color: #fff1f2;
}
.nav-container {
    background-color: #f8f9fa; padding: 10px;
    border-radius: 10px; border: 1px solid #dee2e6;
}
</style>
""", unsafe_allow_html=True)

# 2. ניהול Session State
for k, v in {
    "view_mode": "login", "current_q_idx": 0, "user_answers": {},
    "start_time": None, "quiz_finished": False, "user_name": "",
    "lesson_data": "", "quiz_data": [], "current_topic": "", "quiz_ready": False
}.items():
    if k not in st.session_state: st.session_state[k] = v

if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-2.0-flash')

def parse_quiz_robust(text):
    qs = []
    blocks = re.split(r"\[START_Q\]", text)[1:]
    for b in blocks:
        try:
            q = re.search(r"\[QUESTION\](.*?)\[OPTIONS\]", b, re.DOTALL).group(1).strip()
            opts_raw = re.search(r"\[OPTIONS\](.*?)\[ANSWER\]", b, re.DOTALL).group(1).strip()
            ans = re.search(r"\[ANSWER\]\s*(\d)", b).group(1)
            law = b.split("[LAW]")[1].split("[END_Q]")[0].strip() if "[LAW]" in b else ""
            options = [re.sub(r"^\d+[\s\).\-]+", "", o.strip()) for o in opts_raw.split('\n') if len(o.strip()) > 1]
            qs.append({"q": q, "options": options[:4], "correct": int(ans)-1, "ref": law})
        except: continue
    return qs

# 3. ניהול דפים
m = st.session_state.view_mode

if m == "login":
    st.title("🎓 מתווך בקליק - כניסה")
    name = st.text_input("שם המשתמש שלך:")
    if st.button("כניסה למערכת"):
        st.session_state.user_name = name
        st.session_state.view_mode = "setup"; st.rerun()

elif m == "setup":
    st.title(f"שלום {st.session_state.user_name}")
    t = st.selectbox("בחר נושא:", ["חוק המתווכים", "חוק המקרקעין", "דיני חוזים", "מיסוי מקרקעין"])
    if st.button("התחל שיעור"):
        st.session_state.current_topic = t
        st.session_state.view_mode = "streaming_lesson"; st.rerun()

elif m == "streaming_lesson":
    st.title(f"שיעור: {st.session_state.current_topic}")
    placeholder = st.empty()
    full_txt = ""
    res = model.generate_content(f"כתוב שיעור מפורט למבחן המתווכים על {st.session_state.current_topic}", stream=True)
    for chunk in res:
        full_txt += chunk.text
        placeholder.markdown(full_txt)
    st.session_state.lesson_data = full_txt
    with st.status("מייצר מבחן..."):
        q_res = model.generate_content(f"צור 15 שאלות על {st.session_state.current_topic} בפורמט: [START_Q] [QUESTION] שאלה [OPTIONS] 1) א 2) ב 3) ג 4) ד [ANSWER] מספר [LAW] סעיף [END_Q]")
        st.session_state.quiz_data = parse_quiz_robust(q_res.text)
        st.session_state.quiz_ready = True
    st.session_state.view_mode = "lesson"; st.rerun()

elif m == "lesson":
    st.title(st.session_state.current_topic)
    st.markdown(st.session_state.lesson_data)
    if st.button("📝 עבור למבחן סימולציה (90 דקות)"):
        st.session_state.start_time = time.time()
        st.session_state.current_q_idx = 0
        st.session_state.user_answers = {}
        st.session_state.quiz_finished = False
        st.session_state.view_mode = "quiz"
        scroll_to_top(); st.rerun()

elif m == "quiz":
    # טיימר 90 דקות
    elapsed = time.time() - st.session_state.start_time
    remaining = max(0, 5400 - int(elapsed))
    if remaining <= 0: st.session_state.quiz_finished = True

    col_main, col_nav = st.columns([3, 1])

    with col_nav:
        st.markdown(f'<div class="timer-display">{remaining//60:02d}:{remaining%60:02d}</div>', unsafe_allow_html=True)
        st.write("### מפת שאלות")
        for i in range(len(st.session_state.quiz_data)):
            label = f"שאלה {i+1}"
            if i in st.session_state.user_answers: label += " ✅"
            if i == st.session_state.current_q_idx: label += " 📍"
            if st.button(label, key=f"n_{i}", use_container_width=True):
                st.session_state.current_q_idx = i; st.rerun()
        if st.button("🏁 סיום מבחן", type="primary", use_container_width=True):
            st
