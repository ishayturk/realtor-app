import streamlit as st
import google.generativeai as genai
import re

# 1. הגדרות ועיצוב RTL ממוקד
st.set_page_config(page_title="מתווך בקליק", layout="wide")

def scroll_to_top():
    st.components.v1.html(
        """<script>window.parent.document.querySelector('.main').scrollTo(0,0);</script>""",
        height=0,
    )

st.markdown("""
<style>
/* יישור כללי לימין */
html, body, [data-testid="stAppViewContainer"], .main, .block-container {
    direction: rtl !important;
    text-align: right !important;
}

/* תיקון ספציפי לרכיבי בחירה (Radio) שלא יברחו שמאלה */
[data-testid="stWidgetLabel"], [data-testid="stMarkdownContainer"] p {
    text-align: right !important;
    direction: rtl !important;
}

/* יישור כפתורי הרדיו עצמם */
div[data-testid="stRadio"] > label {
    display: flex;
    flex-direction: row-reverse;
    justify-content: flex-end;
    gap: 10px;
}

div[role="radiogroup"] {
    text-align: right !important;
    direction: rtl !important;
}

/* עיצוב כרטיסיית שאלה */
.quiz-card { 
    background-color: #f9f9f9; 
    padding: 25px; 
    border-radius: 12px; 
    border-right: 6px solid #1E88E5; 
    margin-bottom: 20px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.score-box {
    background-color: #E3F2FD; 
    padding: 20px; 
    border-radius: 12px;
    text-align: center !important; 
    border: 2px solid #1E88E5; 
    margin-bottom: 25px;
}
</style>
""", unsafe_allow_html=True)

# 2. אתחול משתנים
TOPICS = ["בחר נושא...", "חוק המתווכים במקרקעין", "חוק המקרקעין", "חוק המכר (דירות)", "חוק החוזים", "חוק הגנת הצרכן"]

for k, v in {
    "user_name": "", "view_mode": "login", "lesson_data": "", 
    "quiz_data": [], "current_topic": "", "quiz_ready": False, 
    "user_answers": {}
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
            law = b.split("[LAW]")[1].split("[END_Q]")[0].strip() if "[LAW]" in b else "סעיף חוק רלוונטי"
            options = [re.sub(r"^\d+[\s\).\-]+", "", o.strip()) for o in opts_raw.split('\n') if len(o.strip()) > 1]
            qs.append({"q": q, "options": options[:4], "correct": int(ans)-1, "ref": law})
        except: continue
    return qs

# 3. סרגל צידי
if st.session_state.user_name:
    with st.sidebar:
        st.markdown(f"### שלום, {st.session_state.user_name}")
        if st.button("➕ נושא חדש"):
            st.session_state.view_mode = "setup"; st.rerun()
        if st.session_state.current_topic and st.session_state.quiz_ready:
            label = "📖 חזרה לשיעור" if st.session_state.view_mode == "quiz" else "📝 מעבר למבחן"
            if st.button(label):
                st.session_state.view_mode = "quiz" if st.session_state.view_mode == "lesson" else "lesson"
                if st.session_state.view_mode == "quiz": scroll_to_top()
                st.rerun()

# 4. ניהול דפים
m = st.session_state.view_mode

if m == "login":
    st.title("🎓 מתווך בקליק")
    name = st.text_input("שם משתמש:")
    if st.button("כניסה"):
        if name:
            st.session_state.user_name = name
            st.session_state.view_mode = "setup"; st.rerun()

elif m == "setup":
    st.title("מה נלמד היום?")
    t = st.selectbox("בחר נושא:", TOPICS)
    if t != "בחר נושא...":
        st.session_state.current_topic = t
        st.session_state.quiz_ready = False
        st.session_state.user_answers = {}
        st.session_state.view_mode = "streaming_lesson"; st.rerun()

elif m == "streaming_lesson":
    st.title(st.session_state.current_topic)
    placeholder = st.empty()
    full_txt = ""
    res = model.generate_content(f"כתוב שיעור מפורט למבחן המתווכים על {st.session_state.current_topic}", stream=True)
    for chunk in res:
        full_txt += chunk.text
        placeholder.markdown(full_txt)
    st.session_state.lesson_data = full_txt
    with st.status("מכין שאלות תרגול..."):
        q_res = model.generate_content(f"צור 3 שאלות על {st.session_state.current_topic} בפורמט: [START_Q] [QUESTION] שאלה [OPTIONS] 1) א 2) ב 3) ג 4) ד [ANSWER] מספר [LAW] סעיף [END_Q]")
        st.session_state.quiz_data = parse_quiz_robust(q_res.text)
        st.session_state.quiz_ready = True
    st.session_state.view_mode = "lesson"; st.rerun()

elif m == "lesson":
    st.title(st.session_state.current_topic)
    st.markdown(st.session_state.lesson_data)
    if st.button("📝 סיימתי ללמוד - למבחן"):
        scroll_to_top()
        st.session_state.view_mode = "quiz"; st.rerun()

elif m == "quiz":
    st.title(f"מבחן: {st.session_state.current_topic}")
    
    # הצגת ציון
    if st.session_state.user_answers:
        correct = sum(1 for v in st.session_state.user_answers.values() if v is True)
        total = len(st.session_state.quiz_data)
        st.markdown(f'<div class="score-box">הציון שלך: {int((correct/total)*100)}%</div>', unsafe_allow_html=True)

    for i, q in enumerate(st.session_state.quiz_data):
        st.markdown('<div class="quiz-card">', unsafe_allow_html=True)
        st.write(f"**{i+1}. {q['q']}**")
        
        # בחירת תשובה
        ans = st.radio(f"בחר תשובה נכונה:", q['options'], key=f"r_{i}", index=None)
        
        if st.button(f"בדוק תשובה {i+1}", key=f"b_{i}"):
            if ans:
                is_correct = q['options'].index(ans) == q['correct']
                st.session_state.user_answers[i] = is_correct
                if is_correct: st.success("נכון מאוד! 🟢")
                else: st.error(f"טעות. התשובה הנכונה היא: {
