import streamlit as st
import google.generativeai as genai
import re

# 1. עיצוב RTL מלא (Desktop + Mobile)
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
state_defaults = {
    "view_mode": "login", "user_name": "", "current_topic": "",
    "full_exam_data": [], "full_exam_ready": False,
    "lesson_data": "", "lesson_quiz_data": [], "lesson_quiz_ready": False
}
for k, v in state_defaults.items():
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

# 3. סרגל צידי (Sidebar)
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
            
            # הצגת כפתור שאלון רק אם הוא מוכן
            if st.session_state.lesson_quiz_ready:
                if st.button("✍️ שאלון תרגול נושא"):
                    st.session_state.view_mode = "lesson_quiz"; st.rerun()
            elif st.session_state.lesson_data:
                st.caption("⌛ השאלון בטעינה...")

        st.markdown("---")
        if st.button("📝 מבחן סימולציה (25)", type="primary", disabled=not st.session_state.full_exam_ready):
            st.session_state.view_mode = "full_exam"; st.rerun()

# 4. לוגיקת דפים
if st.session_state.view_mode == "login":
    st.markdown('<div class="main-header">כניסה למערכת</div>', unsafe_allow_html=True)
    name = st.text_input("שם משתמש:")
    if st.button("התחבר"):
        if name:
            st.session_state.user_name = name
            st.session_state.view_mode = "setup"; st.rerun()

elif st.session_state.view_mode == "setup":
    st.markdown('<div class="main-header">בחירת נושא לימוד</div>', unsafe_allow_html=True)
    t = st.selectbox("בחר נושא:", ["חוק המתווכים", "חוק המקרקעין", "דיני חוזים", "מיסוי מקרקעין"])
    
    # טעינת מבחן מלא ברקע
    if not st.session_state.full_exam_ready:
        with st.status("מכין סימולציה מלאה...", expanded=False):
            res = model.generate_content("צור 25 שאלות למבחן תיווך בפורמט [START_Q] [QUESTION] [OPTIONS] [ANSWER]")
            st.session_state.full_exam_data = parse_quiz(res.text)
            st.session_state.full_exam_ready = True
            st.rerun()

    if st.button("התחל ללמוד"):
        st.session_state.current_topic = t
        st.session_state.lesson_data = ""
        st.session_state.lesson_quiz_ready = False
        st.session_state.view_mode = "lesson_view"; st.rerun()

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
        
        # יצירת השאלון בשקט
        res_q = model.generate_content(f"צור 5 שאלות על {st.session_state.current_topic} בפורמט [START_Q]")
        st.session_state.lesson_quiz_data = parse_quiz(res_q.text)
        st.session_state.lesson_quiz_ready = True
        st.rerun()
    else:
        lesson_placeholder.markdown(st.session_state.lesson_data)

elif st.session_state.view_mode == "lesson_quiz":
    st.markdown(f'<div class="main-header">תרגול: {st.session_state.current_topic}</div>', unsafe_allow_html=True)
    # הגנה מפני דף ריק: אם אין דאטה, ננסה לייצר שוב
    if not st.session_state.lesson_quiz_data:
        with st.spinner("מייצר שאלות תרגול..."):
            res_q = model.generate_content(f"צור 5 שאלות על {st.session_state.current_topic} בפורמט [START_Q]")
            st.session_state.lesson_quiz_data = parse_quiz(res_q.text)
            st.session_state.lesson_quiz_ready = True
            st.rerun()
    else:
        for i, q in enumerate(st.session_state.lesson_quiz_data):
            st.write(f"**{i+1}. {q['q']}**")
            st.radio(f"בחר תשובה {i+1}:", q['options'], key=f"q_l_{i}", index=None)
            st.markdown("---")

elif st.session_state.view_mode == "full_exam":
    st.markdown('<div class="main-header">מבחן סימולציה מלא</div>', unsafe_allow_html=True)
    if not st.session_state.full_exam_data:
        st.error("נתוני המבחן לא נטענו. חזור לדף הבית.")
    else:
        for i, q in enumerate(st.session_state.full_exam_data):
            st.write(f"**{i+1}. {q['q']}**")
            st.radio(f"תשובה לשאלה {i+1}:", q['options'], key=f"q_f_{i}", index=None)
            st.markdown("---")
