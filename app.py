import streamlit as st
import google.generativeai as genai
import re
import time

# 1. הגדרות ועיצוב RTL מקיף
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
    direction: rtl !important; text-align: right !important;
}
/* כפיית יישור לימין לכל סוגי הכותרות והטקסט */
h1, h2, h3, h4, h5, p, span, label, div, [data-testid="stMarkdownContainer"] h1 {
    text-align: right !important; direction: rtl !important; width: 100%;
}
/* הגדרות לסרגל הצידי */
[data-testid="stSidebar"] {
    direction: rtl !important; text-align: right !important;
}
.timer-display {
    font-size: 24px; font-weight: bold; color: #e63946;
    text-align: center !important; padding: 10px;
    border: 2px solid #e63946; border-radius: 10px;
    background-color: #fff1f2; margin-bottom: 15px;
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

# 3. סרגל צידי קבוע - מוצג תמיד לאחר התחברות
if st.session_state.user_name:
    with st.sidebar:
        st.markdown("### 🎓 מתווך בקליק")
        st.write(f"משתמש: **{st.session_state.user_name}**")
        st.markdown("---")
        
        if st.button("➕ החלף נושא למידה"):
            st.session_state.view_mode = "setup"
            st.session_state.current_topic = ""
            st.session_state.quiz_ready = False
            st.rerun()
            
        if st.session_state.current_topic:
            st.write(f"📖 **{st.session_state.current_topic}**")
            if st.session_state.quiz_ready:
                if st.session_state.view_mode == "quiz":
                    if st.button("📖 חזור לשיעור"):
                        st.session_state.view_mode = "lesson"; st.rerun()
                else:
                    if st.button("📝 עבור למבחן"):
                        if st.session_state.start_time is None:
                            st.session_state.start_time = time.time()
                        st.session_state.view_mode = "quiz"
                        scroll_to_top(); st.rerun()

# 4. לוגיקת דפים
m = st.session_state.view_mode

if m == "login":
    st.title("🎓 ברוכים הבאים למתווך בקליק")
    name = st.text_input("הכנס שם משתמש:")
    if st.button("כניסה"):
        if name:
            st.session_state.user_name = name
            st.session_state.view_mode = "setup"; st.rerun()

elif m == "setup":
    st.title("מה נלמד היום?")
    t = st.selectbox("בחר נושא:", ["חוק המתווכים", "חוק המקרקעין", "דיני חוזים", "מיסוי מקרקעין", "חוק המכר (דירות)"])
    if st.button("התחל למידה"):
        st.session_state.current_topic = t
        st.session_state.quiz_ready = False
        st.session_state.user_answers = {}
        st.session_state.start_time = None
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
    with st.status("מכין שאלות סימולציה..."):
        q_res = model.generate_content(f"צור 15 שאלות על {st.session_state.current_topic} בפורמט: [START_Q] [QUESTION] שאלה [OPTIONS] 1) א 2) ב 3) ג 4) ד [ANSWER] מספר [LAW] סעיף [END_Q]")
        st.session_state.quiz_data = parse_quiz_robust(q_res.text)
        st.session_state.quiz_ready = True
    st.session_state.view_mode = "lesson"; st.rerun()

elif m == "lesson":
    st.title(st.session_state.current_topic)
    st.markdown(st.session_state.lesson_data)
    if st.session_state.quiz_ready:
        st.write("---")
        if st.button("📝 סיימתי ללמוד - התחל מבחן (90 דקות)"):
            st.session_state.start_time = time.time()
            st.session_state.view_mode = "quiz"
            scroll_to_top(); st.rerun()

elif m == "quiz":
    # טיימר
    elapsed = time.time() - st.session_state.start_time
    remaining = max(0, 5400 - int(elapsed))
    
    # פריסת מבחן: מרכז המבחן וצד ימין לניווט
    col_main, col_nav = st.columns([3, 1])

    with col_nav:
        st.markdown(f'<div class="timer-display">⌛ {remaining//60:02d}:{remaining%60:02d}</div>', unsafe_allow_html=True)
        st.write("### מפת שאלות")
        for i in range(len(st.session_state.quiz_data)):
            lbl = f"שאלה {i+1}"
            if i in st.session_state.user_answers: lbl += " ✅"
            if i == st.session_state.current_q_idx: lbl += " 📍"
            if st.button(lbl, key=f"nav_{i}", use_container_width=True):
                st.session_state.current_q_idx = i; st.rerun()
        if st.button("🏁 סיים והגש", type="primary", use_container_width=True):
            st.session_state.quiz_finished = True; st.rerun()

    with col_main:
        if st.session_state.quiz_finished:
            st.header("תוצאות המבחן")
            correct = sum(1 for i, a in st.session_state.user_answers.items() if a == st.session_state.quiz_data[i]['correct'])
            score = int((correct/len(st.session_state.quiz_data))*100)
            st.success(f"הציון שלך: {score}%")
            if st.button("חזרה לשיעור"):
                st.session_state.quiz_finished = False
                st.session_state.view_mode = "lesson"; st.rerun()
        else:
            curr = st.session_state.current_q_idx
            q = st.session_state.quiz_data[curr]
            st.subheader(f"שאלה {curr + 1}")
            st.write(q['q'])
            
            ans_idx = st.session_state.user_answers.get(curr, None)
            choice = st.radio("בחר תשובה:", q['options'], index=ans_idx, key=f"r_{curr}")
            if choice: st.session_state.user_answers[curr] = q['options'].index(choice)
            
            st.write("---")
            c1, c2 = st.columns(2)
            with c1:
                if curr > 0:
                    if st.button("⬅️ שאלה קודמת"):
                        st.session_state.current_q_idx -= 1; st.rerun()
            with c2:
                if curr < len(st.session_state.quiz_data) - 1:
                    if st.button("שאלה הבאה ➡️"):
                        st.session_state.current_q_idx += 1; st.rerun()
