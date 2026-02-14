import streamlit as st
import google.generativeai as genai
import re

# 1. עיצוב RTL ויישור (מותאם לנייד)
st.set_page_config(page_title="מתווך בקליק", layout="wide")

st.markdown("""
<style>
    html, body, [data-testid="stAppViewContainer"], .main, .block-container, [data-testid="stMarkdownContainer"], p, li, label, h1, h2, h3 {
        direction: rtl !important;
        text-align: right !important;
    }
    [data-testid="stSidebar"] { direction: rtl !important; text-align: right !important; border-left: 1px solid #e0e0e0; }
    [data-testid="stSidebarCollapsedControl"] { left: 10px !important; right: auto !important; }
    .stButton button { width: 100%; text-align: right !important; }
    .sidebar-logo { font-size: 24px; font-weight: bold; color: #1E88E5; text-align: center !important; padding: 10px; border-bottom: 1px solid #ddd; }
    .main-header { font-size: 28px; font-weight: bold; text-align: center !important; color: #2c3e50; border-bottom: 2px solid #1E88E5; margin-bottom: 20px; }
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
            opts_text = re.search(r"\[OPTIONS\](.*?)\[ANSWER\]", b, re.DOTALL).group(1).strip()
            opts = [o.strip() for o in opts_text.split('\n') if o.strip()]
            ans_match = re.search(r"\[ANSWER\]\s*(\d)", b)
            ans = int(ans_match.group(1)) if ans_match else 1
            if q and len(opts) >= 2:
                qs.append({"q": q, "options": opts[:4], "correct": ans-1})
        except: continue
    return qs

# 3. סרגל צידי
if st.session_state.user_name:
    with st.sidebar:
        st.markdown('<div class="sidebar-logo">🎓 מתווך בקליק</div>', unsafe_allow_html=True)
        st.write(f"שלום, **{st.session_state.user_name}**")
        
        if st.button("📚 תפריט שיעורים"):
            st.session_state.view_mode = "setup"; st.rerun()
            
        if st.session_state.current_topic:
            st.markdown("---")
            if st.button("📖 קרא שיעור"):
                st.session_state.view_mode = "lesson_view"; st.rerun()
            if st.session_state.lesson_quiz_ready:
                if st.button("✍️ שאלון תרגול"):
                    st.session_state.view_mode = "lesson_quiz"; st.rerun()

        st.markdown("---")
        # בדיקה כפולה: גם דאטה קיים וגם הדגל ready דלוק
        is_exam_actually_ready = len(st.session_state.full_exam_data) > 0
        if st.button("📝 מבחן מלא (25 שאלות)", type="primary", disabled=not is_exam_actually_ready):
            st.session_state.view_mode = "full_exam"; st.rerun()

# 4. דפים
if st.session_state.view_mode == "login":
    st.markdown('<div class="main-header">כניסה למערכת</div>', unsafe_allow_html=True)
    name = st.text_input("שם משתמש:")
    if st.button("התחבר"):
        if name:
            st.session_state.user_name = name
            st.session_state.view_mode = "setup"
            # ייצור המבחן רק כאן כדי שלא יתקע את ה-Login
            st.rerun()

elif st.session_state.view_mode == "setup":
    st.markdown('<div class="main-header">מה נלמד היום?</div>', unsafe_allow_html=True)
    t = st.selectbox("בחר נושא:", ["חוק המתווכים", "חוק המקרקעין", "דיני חוזים", "מיסוי מקרקעין"])
    
    # טעינת המבחן הגדול ברקע בזמן שהמשתמש בוחר שיעור
    if not st.session_state.full_exam_ready:
        with st.status("מכין את מבחן הסימולציה ברקע...", expanded=False):
            res_ex = model.generate_content("צור 25 שאלות אמריקאיות למבחן תיווך בפורמט [START_Q] [QUESTION] [OPTIONS] [ANSWER]")
            st.session_state.full_exam_data = parse_quiz(res_ex.text)
            st.session_state.full_exam_ready = True
            st.rerun()

    if st.button("התחל שיעור"):
        st.session_state.current_topic = t
        st.session_state.lesson_data = ""
        st.session_state.lesson_quiz_ready = False
        st.session_state.view_mode = "lesson_view"; st.rerun()

elif st.session_state.view_mode == "full_exam":
    st.markdown('<div class="main-header">מבחן סימולציה מלא</div>', unsafe_allow_html=True)
    if not st.session_state.full_exam_data:
        st.warning("המבחן עדיין לא נוצר. חוזר לדף הבית...")
        st.session_state.view_mode = "setup"; st.rerun()
    else:
        for i, q in enumerate(st.session_state.full_exam_data):
            st.write(f"**{i+1}. {q['q']}**")
            st.radio(f"בחר תשובה {i+1}:", q['options'], key=f"ex_q_{i}", index=None)
            st.markdown("---")

# לוגיקת lesson_view נשארת כפי שהייתה (עם הזרמה מידית)
elif st.session_state.view_mode == "lesson_view":
    st.markdown(f'<div class="main-header">{st.session_state.current_topic}</div>', unsafe_allow_html=True)
    lesson_placeholder = st.empty()
    if not st.session_state.lesson_data:
        full_text = ""
        response = model.generate_content(f"כתוב שיעור מפורט למבחן המתווכים על {st.session_state.current_topic}", stream=True)
        for chunk in response:
            full_text += chunk.text
            lesson_placeholder.markdown(full_text)
        st.session_state.lesson_data = full_text
        res_q = model.generate_content(f"צור 5 שאלות על {st.session_state.current_topic} בפורמט [START_Q]")
        st.session_state.lesson_quiz_data = parse_quiz(res_q.text)
        st.session_state.lesson_quiz_ready = True
        st.rerun()
    else:
        lesson_placeholder.markdown(st.session_state.lesson_data)
