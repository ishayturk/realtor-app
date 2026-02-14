import streamlit as st
import google.generativeai as genai
import re

# 1. הגדרות דף ועיצוב RTL יציב (ללא קונפליקטים)
st.set_page_config(page_title="מתווך בקליק", layout="wide")

st.markdown("""
<style>
    html, body, [data-testid="stAppViewContainer"], .main {
        direction: rtl;
        text-align: right;
    }
    [data-testid="stSidebar"] {
        position: fixed;
        right: 0;
        left: auto;
        direction: rtl;
        background-color: #f8f9fa;
        border-left: 1px solid #e0e0e0;
    }
    [data-testid="stSidebar"] section { direction: rtl; }
    .sidebar-logo {
        font-size: 26px;
        font-weight: bold;
        color: #1E88E5;
        text-align: center;
        padding: 15px 0;
        border-bottom: 2px solid #e9ecef;
        margin-bottom: 20px;
    }
    .main-header {
        font-size: 38px;
        font-weight: bold;
        color: #2c3e50;
        text-align: center;
        margin-bottom: 30px;
        border-bottom: 3px solid #1E88E5;
        width: 100%;
    }
    .stButton button { width: 100%; text-align: right; }
    .summary-card { 
        border: 1px solid #dee2e6; 
        padding: 20px; 
        border-radius: 12px; 
        margin-bottom: 15px; 
        background-color: #ffffff;
    }
</style>
""", unsafe_allow_html=True)

# 2. ניהול Session State - אתחול משתנים
state_vars = {
    "view_mode": "login", 
    "user_name": "", 
    "current_topic": "",
    "full_exam_data": [], 
    "full_exam_ready": False,
    "lesson_data": "", 
    "lesson_quiz_data": [], 
    "lesson_quiz_ready": False,
    "current_exam_idx": 0, 
    "exam_answers": {}, 
    "exam_finished": False
}

for key, value in state_vars.items():
    if key not in st.session_state:
        st.session_state[key] = value

# הגדרת ה-AI
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-2.0-flash')
else:
    st.error("חסר מפתח API ב-Secrets")

def parse_quiz(text):
    qs = []
    blocks = re.split(r"\[START_Q\]", text)[1:]
    for b in blocks:
        try:
            q = re.search(r"\[QUESTION\](.*?)\[OPTIONS\]", b, re.DOTALL).group(1).strip()
            opts = re.search(r"\[OPTIONS\](.*?)\[ANSWER\]", b, re.DOTALL).group(1).strip().split('\n')
            ans = re.search(r"\[ANSWER\]\s*(\d)", b).group(1)
            qs.append({"q": q, "options": [o.strip() for o in opts if o.strip()][:4], "correct": int(ans)-1})
        except: continue
    return qs

# 3. סרגל צידי קבוע (Sidebar) - יוצג רק אם המשתמש מחובר
if st.session_state.user_name:
    with st.sidebar:
        st.markdown('<div class="sidebar-logo">🎓 מתווך בקליק</div>', unsafe_allow_html=True)
        st.write(f"שלום, **{st.session_state.user_name}**")
        st.markdown("---")
        
        if st.button("📚 שיעורי הלימוד", use_container_width=True):
            st.session_state.view_mode = "setup"
            st.rerun()
            
        if st.session_state.current_topic:
            st.write(f"📖 נושא: {st.session_state.current_topic}")
            if st.button("קרא שיעור", use_container_width=True):
                st.session_state.view_mode = "lesson_view"
                st.rerun()
            
            # כפתור שאלון נושא
            if st.button("✍️ שאלון תרגול", use_container_width=True, disabled=not st.session_state.lesson_quiz_ready):
                st.session_state.view_mode = "lesson_quiz"
                st.rerun()

        st.markdown("---")
        # כפתור מבחן 25 שאלות
        if st.button("📝 בחינה (25 שאלות)", use_container_width=True, type="primary", disabled=not st.session_state.full_exam_ready):
            st.session_state.view_mode = "full_exam"
            st.session_state.exam_answers = {}
            st.session_state.current_exam_idx = 0
            st.session_state.exam_finished = False
            st.rerun()

# 4. לוגיקת דפים
if st.session_state.view_mode == "login":
    st.markdown('<div class="main-header">🎓 מתווך בקליק</div>', unsafe_allow_html=True)
    name = st.text_input("הכנס שם משתמש:")
    if st.button("התחבר"):
        if name:
            st.session_state.user_name = name
            st.session_state.view_mode = "setup"
            # יצירת המבחן הראשוני ברקע
            try:
                res = model.generate_content("צור 25 שאלות למבחן תיווך בפורמט [START_Q]")
                st.session_state.full_exam_data = parse_quiz(res.text)
                st.session_state.full_exam_ready = True
            except:
                pass
            st.rerun()
        else:
            st.warning("אנא הכנס שם משתמש")

elif st.session_state.view_mode == "setup":
    st.markdown('<div class="main-header">בחירת נושא לימוד</div>', unsafe_allow_html=True)
    t = st.selectbox("בחר נושא:", ["חוק המתווכים", "חוק המקרקעין", "דיני חוזים", "מיסוי מקרקעין", "חוק המכר"])
    if st.button("טען שיעור"):
        st.session_state.current_topic = t
        st.session_state.lesson_data = ""
        st.session_state.lesson_quiz_ready = False
        st.session_state.view_mode = "lesson_view"
        st.rerun()

elif st.session_state.view_mode == "lesson_view":
    st.markdown(f'<div class="main-header">{st.session_state.current_topic}</div>', unsafe_allow_html=True)
    if not st.session_state.lesson_data:
        with st.spinner("טוען..."):
            res_l = model.generate_content(f"כתוב שיעור על {st.session_state.current_topic}")
            st.session_state.lesson_data = res_l.text
            res_q = model.generate_content(f"צור 5 שאלות על {st.session_state.current_topic} בפורמט [START_Q]")
            st.session_state.lesson_quiz_data = parse_quiz(res_q.text)
            st.session_state.lesson_quiz_ready = True
            st.rerun()
    st.markdown(st.session_state.lesson_data)

elif st.session_state.view_mode == "lesson_quiz":
    st.markdown(f'<div class="main-header">תרגול: {st.session_state.current_topic}</div>', unsafe_allow_html=True)
    for i, q in enumerate(st.session_state.lesson_quiz_data):
        with st.container():
            st.markdown('<div class="summary-card">', unsafe_allow_html=True)
            st.write(f"**{i+1}. {q['q']}**")
            ans = st.radio(f"בחירה {i}", q['options'], key=f"lq_{i}", index=None)
            if st.button(f"בדוק {i+1}", key=f"lb_{i}"):
                if ans and q['options'].index(ans) == q['correct']: st.success("נכון")
                else: st.error("טעות")
            st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.view_mode == "full_exam":
    if not st.session_state.exam_finished:
        st.markdown('<div class="main-header">בחינה (25 שאלות)</div>', unsafe_allow_html=True)
        col_main, col_nav = st.columns([4, 1])
        with col_nav:
            for i in range(25):
                lbl = f"{i+1}" + (" ✅" if i in st.session_state.exam_answers else "")
                if st.button(lbl, key=f"n_{i}", use_container_width=True):
                    st.session_state.current_exam_idx = i
                    st.rerun()
            if st.button("🏁 סיום", type="primary", use_container_width=True):
                st.session_state.exam_finished = True
                st.rerun()
        with col_main:
            idx = st.session_state.current_exam_idx
            if idx < len(st.session_state.full_exam_data):
                q = st.session_state.full_exam_data[idx]
                st.subheader(f"שאלה {idx+1}")
                st.write(q['q'])
                ch = st.radio("תשובה:", q['options'], index=st.session_state.exam_answers.get(idx), key=f"eq_{idx}")
                if ch: st.session_state.exam_answers[idx] = q['options'].index(ch)
    else:
        st.markdown('<div class="main-header">תוצאות המבחן</div>', unsafe_allow_html=True)
        # חישוב והצגת תוצאות...
        correct = sum(1 for i, a in st.session_state.exam_answers.items() if a == st.session_state.full_exam_data[i]['correct'])
        st.metric("ציון", f"{int((correct/25)*100)}%")
        if st.button("חזרה לשיעורים"):
            st.session_state.view_mode = "setup"
            st.rerun()
