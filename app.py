import streamlit as st
import google.generativeai as genai
import re

# 1. עיצוב ויישור RTL
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
.score-box {
    background-color: #E3F2FD; padding: 20px; border-radius: 12px;
    text-align: center; border: 2px solid #1E88E5; margin-bottom: 25px;
}
</style>
""", unsafe_allow_html=True)

# 2. נושאים ומשתנים
TOPICS = [
    "בחר נושא...", "חוק המתווכים במקרקעין", "חוק המקרקעין", "חוק המכר (דירות)",
    "חוק הגנת הצרכן", "חוק החוזים", "דיני תכנון ובנייה",
    "מיסוי מקרקעין", "חוק העונשין", "חוק שמאי מקרקעין"
]

for k, v in {
    "user_name": "", "view_mode": "login", "lesson_data": "", 
    "quiz_data": [], "history": [], "current_topic": "", 
    "quiz_ready": False, "user_answers": {}
}.items():
    if k not in st.session_state: st.session_state[k] = v

if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-2.0-flash')

def parse_quiz_robust(text):
    qs = []
    blocks = re.split(r"\[START_Q\]|שאלה \d+:?", text)[1:]
    for b in blocks:
        try:
            b = b.replace("[END_Q]", "").strip()
            q_part = re.split(r"\[OPTIONS\]|\d\)", b)[0].replace("[QUESTION]", "").strip()
            opt_block = ""
            if "[OPTIONS]" in b:
                opt_block = re.split(r"\[OPTIONS\]", b)[1]
                opt_block = re.split(r"\[ANSWER\]", opt_block)[0]
            options = [re.sub(r"^\d+[\s\).\-]+", "", o.strip()) for o in opt_block.split('\n') if len(o.strip()) > 1]
            ans_match = re.search(r"\[ANSWER\]\s*(\d)", b)
            idx = int(ans_match.group(1)) - 1 if ans_match else 0
            law_part = b.split("[LAW]")[1].strip() if "[LAW]" in b else "מקור חוקי כללי"
            if q_part and len(options) >= 2:
                qs.append({"q": q_part, "options": options[:4], "correct": idx, "ref": law_part})
        except: continue
    return qs

# 3. סרגל צידי
if st.session_state.user_name:
    with st.sidebar:
        st.markdown('<div class="sidebar-logo">🎓 מתווך בקליק</div>', unsafe_allow_html=True)
        st.write(f"שלום, **{st.session_state.user_name}**")
        if st.button("➕ נושא חדש"):
            st.session_state.view_mode = "setup"
            st.session_state.current_topic = ""
            st.session_state.quiz_ready = False
            st.session_state.user_answers = {}
            st.rerun()
        if st.session_state.current_topic:
            if st.session_state.view_mode == "quiz":
                if st.button("📖 חזרה לשיעור"):
                    st.session_state.view_mode = "lesson"; st.rerun()
            if st.session_state.quiz_ready and st.session_state.view_mode != "quiz":
                if st.button("📝 מעבר למבחן"):
                    st.session_state.view_mode = "quiz"; st.rerun()
        st.markdown("---")
        for h in st.session_state.history: st.caption(f"• {h}")

# 4. ניהול דפים
m = st.session_state.view_mode

if m == "login":
    st.title("🎓 מתווך בקליק")
    name = st.text_input("הזן שם:")
    if st.button("כניסה"):
        if name:
            st.session_state.user_name = name
            st.session_state.view_mode = "setup"; st.rerun()

elif m == "setup":
    st.title(f"מה נלמד, {st.session_state.user_name}?")
    t = st.selectbox("בחר נושא להתחלת למידה:", TOPICS)
    if t != "בחר נושא...":
        st.session_state.current_topic = t
        st.session_state.quiz_ready = False
        st.session_state.user_answers = {}
        st.session_state.view_mode = "streaming_lesson"; st.rerun()

elif m == "streaming_lesson":
    st.title(f"שיעור: {st.session_state.current_topic}")
    placeholder = st.empty()
    full_txt = ""
    try:
        res = model.generate_content(f"כתוב שיעור מפורט על {st.session_state.current_topic} למבחן המתווכים.", stream=True)
        for chunk in res:
            full_txt += chunk.text
            placeholder.markdown(full_txt)
        st.session_state.lesson_data = full_txt
        with st.status("מכין שאלות תרגול..."):
            q_p = f"צור 3 שאלות על {st.session_state.current_topic}. פורמט: [START_Q] [QUESTION] שאלה [OPTIONS] 1) א 2) ב 3) ג 4) ד [ANSWER] מספר [LAW] סעיף חוק [END_Q]"
            q_res = model.generate_content(q_p)
            st.session_state.quiz_data = parse_quiz_robust(q_res.text)
            st.session_state.quiz_ready = len(st.session_state.quiz_data) > 0
        if st.session_state.current_topic not in st.session_state.history:
            st.session_state.history.append(st.session_state.current_topic)
        st.session_state.view_mode = "lesson"; st.rerun()
    except Exception as e:
        st.error(f"שגיאה: {e}")

elif m == "lesson":
    st.title(st.session_state.current_topic)
    st.markdown(st.session_state.lesson_data)
    st.info("השיעור מוכן. כפתור המבחן זמין כעת בתפריט הצד.")

elif m == "quiz":
    st.markdown('<div id="top"></div>', unsafe_allow_html=True)
    st.title(f"תרגול: {st.session_state.current_topic}")
    
    # הצגת ציון סופי אם ענו על הכל
    if len(st.session_state.user_answers) == len(st.session_state.quiz_data) and len(st.session_state.quiz_data) > 0:
        correct_count = sum(1 for i, val in st.session_state.user_answers.items() if val == True)
        score = int((correct_count / len(st.session_state.quiz_data)) * 100)
        st.markdown(f"""
        <div class="score-box">
            <h3>סיכום תוצאות</h3>
            <p style="font-size: 24px;">הציון שלך: <b>{score}</b></p>
            <p>ענית נכון על {correct_count} מתוך {len(st.session_state.quiz_data)} שאלות</p>
        </div>
        """, unsafe_allow_html=True)

    for i, q in enumerate(st.session_state.quiz_data):
        st.markdown('<div class="quiz-card">', unsafe_allow_html=True)
        st.write(f"**{i+1}. {q['q']}**")
        ans = st.radio(f"בחר תשובה:", q['options'], key=f"q{i}", index=None)
        
        if st.button(f"בדוק תשובה {i+1}", key=f"b{i}"):
            if ans:
                is_correct = q['options'].index(ans) == q['correct']
                st.session_state.user_answers[i] = is_correct
                if is_correct:
                    st.success("נכון! כל הכבוד.")
                else:
                    st.error(f"טעות. התשובה הנכונה: {q['options'][q['correct']]}")
                st.info(f"⚖️ {q['ref']}")
                st.rerun() # מרענן כדי לעדכן את הציון למעלה
        st.markdown('</div>', unsafe_allow_html=True)
