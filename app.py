import streamlit as st
import google.generativeai as genai
import re
import time

# 1. הגדרות ועיצוב RTL מורחב
st.set_page_config(page_title="מתווך בקליק - סימולטור", layout="wide")

def scroll_to_top():
    st.components.v1.html(
        """<script>window.parent.document.querySelector('.main').scrollTo(0,0);</script>""",
        height=0,
    )

st.markdown("""
<style>
/* הגדרות RTL ויישור לימין */
html, body, [data-testid="stAppViewContainer"], .main, .block-container {
    direction: rtl !important; text-align: right !important;
}
h1, h2, h3, h4, h5, h6, p, span, label, div {
    text-align: right !important;
}
/* פריים ניווט שאלות בצד ימין */
.nav-container {
    background-color: #f8f9fa;
    padding: 15px;
    border-radius: 10px;
    border: 1px solid #dee2e6;
}
/* כפתור מספר שאלה */
.q-link {
    display: inline-block;
    width: 40px;
    height: 40px;
    line-height: 40px;
    text-align: center;
    margin: 4px;
    border-radius: 5px;
    background-color: #ffffff;
    border: 1px solid #1E88E5;
    color: #1E88E5;
    font-weight: bold;
    text-decoration: none;
}
.q-answered {
    background-color: #4CAF50 !important;
    color: white !important;
    border-color: #4CAF50 !important;
}
.q-current {
    background-color: #1E88E5 !important;
    color: white !important;
    box-shadow: 0 0 8px rgba(30,136,229,0.5);
}
/* טיימר */
.timer-display {
    font-size: 28px;
    font-weight: bold;
    color: #e63946;
    text-align: center !important;
    padding: 15px;
    border: 3px solid #e63946;
    border-radius: 12px;
    margin-bottom: 20px;
    background-color: #fff1f2;
}
</style>
""", unsafe_allow_html=True)

# 2. ניהול Session State
if "view_mode" not in st.session_state: st.session_state.view_mode = "login"
if "current_q_idx" not in st.session_state: st.session_state.current_q_idx = 0
if "user_answers" not in st.session_state: st.session_state.user_answers = {}
if "start_time" not in st.session_state: st.session_state.start_time = None
if "quiz_finished" not in st.session_state: st.session_state.quiz_finished = False

for k, v in {
    "user_name": "", "lesson_data": "", "quiz_data": [], 
    "current_topic": "", "quiz_ready": False
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
    t = st.selectbox("בחר נושא ללימוד ומבחן:", ["חוק המתווכים", "חוק המקרקעין", "דיני חוזים", "מיסוי מקרקעין", "חוק המכר (דירות)"])
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
    with st.status("מייצר מבחן סימולציה..."):
        q_res = model.generate_content(f"צור 15 שאלות למבחן המתווכים על {st.session_state.current_topic}. פורמט: [START_Q] [QUESTION] שאלה [OPTIONS] 1) א 2) ב 3) ג 4) ד [ANSWER] מספר [LAW] סעיף [END_Q]")
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
    # --- חישוב טיימר ---
    time_limit = 90 * 60  # 90 דקות
    elapsed = time.time() - st.session_state.start_time
    remaining = max(0, time_limit - int(elapsed))
    
    if remaining <= 0:
        st.session_state.quiz_finished = True

    # פריסה: ניווט בימין (Sidebar), שאלה במרכז
    col_main, col_nav = st.columns([3, 1])

    with col_nav:
        st.markdown(f'<div class="timer-display">{remaining // 60:02d}:{remaining % 60:02d}</div>', unsafe_allow_html=True)
        st.write("### מפת שאלות")
        
        # יצירת גריד של כפתורי ניווט
        num_questions = len(st.session_state.quiz_data)
        for i in range(num_questions):
            # עיצוב מותנה
            status_class = ""
            if i == st.session_state.current_q_idx: status_class = " (נוכחית)"
            elif i in st.session_state.user_answers: status_class = " ✅"
            
            if st.button(f"שאלה {i+1}{status_class}", key=f"nav_btn_{i}", use_container_width=True):
                st.session_state.current_q_idx = i; st.rerun()
        
        st.markdown("---")
        if st.button("🏁 סיום והגשת מבחן", type="primary", use_container_width=True):
            st.session_state.quiz_finished = True; st.rerun()

    with col_main:
        if st.session_state.quiz_finished:
            st.header("סיכום מבחן")
            correct = sum(1 for i, a in st.session_state.user_answers.items() if a == st.session_state.quiz_data[i]['correct'])
            total = len(st.session_state.quiz_data)
            score = int((correct/total)*100)
            
            st.success(f"השלמת את המבחן! הציון שלך הוא: {score}")
            st.write(f"ענית נכון על {correct} מתוך {total} שאלות.")
            if st.button("חזרה לשיעור"):
                st.session_state.view_mode = "lesson"; st.rerun()
        else:
            idx = st.session_state.current_q_idx
            q = st.session_state.quiz_data[idx]
            
            st.subheader(f"שאלה {idx +
