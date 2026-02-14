import streamlit as st
import google.generativeai as genai
import re

# 1. עיצוב CSS יציב - ללא קונפליקטים, יישור לימין מלא
st.set_page_config(page_title="מתווך בקליק", layout="wide")

st.markdown("""
<style>
    /* יישור כללי לימין */
    html, body, [data-testid="stAppViewContainer"], .main, [data-testid="stMarkdownContainer"] {
        direction: rtl;
        text-align: right;
    }
    
    /* סיידבר בצד ימין */
    [data-testid="stSidebar"] {
        position: fixed;
        right: 0;
        left: auto;
        direction: rtl;
        background-color: #f8f9fa;
        border-left: 1px solid #e0e0e0;
    }
    
    /* יישור טקסט בתוך הסיידבר (כולל שם משתמש) */
    section[data-testid="stSidebar"] .stMarkdown, 
    section[data-testid="stSidebar"] p, 
    section[data-testid="stSidebar"] span {
        text-align: right !important;
        direction: rtl !important;
    }

    .sidebar-logo {
        font-size: 24px;
        font-weight: bold;
        color: #1E88E5;
        text-align: center !important;
        padding-bottom: 20px;
        border-bottom: 1px solid #ddd;
        margin-bottom: 20px;
    }

    .main-header {
        font-size: 36px;
        font-weight: bold;
        text-align: center;
        color: #2c3e50;
        margin-bottom: 30px;
        border-bottom: 2px solid #1E88E5;
    }

    /* כפתורים מיושרים לימין */
    .stButton button {
        width: 100%;
        text-align: right;
    }
</style>
""", unsafe_allow_html=True)

# 2. אתחול Session State
for k, v in {
    "view_mode": "login", "user_name": "", "current_topic": "",
    "full_exam_data": [], "full_exam_ready": False,
    "lesson_data": "", "lesson_quiz_data": [], "lesson_quiz_ready": False
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-2.0-flash')

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

# 3. סרגל צידי (Sidebar)
if st.session_state.user_name:
    with st.sidebar:
        st.markdown('<div class="sidebar-logo">🎓 מתווך בקליק</div>', unsafe_allow_html=True)
        st.write(f"שלום, **{st.session_state.user_name}**")
        st.markdown("---")
        
        if st.button("📚 שיעורי הלימוד"):
            st.session_state.view_mode = "setup"
            st.rerun()
            
        if st.session_state.current_topic:
            st.write(f"📖 נושא: {st.session_state.current_topic}")
            if st.button("קרא שיעור"):
                st.session_state.view_mode = "lesson_view"
                st.rerun()
            
            if st.button("✍️ שאלון תרגול", disabled=not st.session_state.lesson_quiz_ready):
                st.session_state.view_mode = "lesson_quiz"
                st.rerun()

        st.markdown("---")
        if st.button("📝 בחינה (25 שאלות)", type="primary", disabled=not st.session_state.full_exam_ready):
            st.session_state.view_mode = "full_exam"
            st.rerun()

# 4. לוגיקת דפים
if st.session_state.view_mode == "login":
    st.markdown('<div class="main-header">🎓 מתווך בקליק</div>', unsafe_allow_html=True)
    name = st.text_input("שם משתמש:")
    if st.button("התחבר"):
        if name:
            st.session_state.user_name = name
            st.session_state.view_mode = "setup"
            try:
                res = model.generate_content("צור 25 שאלות למבחן תיווך בפורמט [START_Q]")
                st.session_state.full_exam_data = parse_quiz(res.text)
                st.session_state.full_exam_ready = True
            except: pass
            st.rerun()

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
        with st.spinner("טוען חומר לימוד..."):
            res_l = model.generate_content(f"כתוב שיעור מפורט על {st.session_state.current_topic}")
            st.session_state.lesson_data = res_l.text
            res_q = model.generate_content(f"צור 5 שאלות על {st.session_state.current_topic} בפורמט [START_Q]")
            st.session_state.lesson_quiz_data = parse_quiz(res_q.text)
            st.session_state.lesson_quiz_ready = True
            st.rerun()
    st.markdown(st.session_state.lesson_data)

elif st.session_state.view_mode == "lesson_quiz":
    st.markdown(f'<div class="main-header">שאלון: {st.session_state.current_topic}</div>', unsafe_allow_html=True)
    for i, q in enumerate(st.session_state.lesson_quiz_data):
        st.write(f"**{i+1}. {q['q']}**")
        st.radio("בחר תשובה:", q['options'], key=f"lq_{i}", index=None)
        st.markdown("---")

elif st.session_state.view_mode == "full_exam":
    st.markdown('<div class="main-header">בחינה כוללת</div>', unsafe_allow_html=True)
    st.write("כאן תוצג הבחינה של 25 השאלות.")
