import streamlit as st
import google.generativeai as genai
import re

# 1. הגדרות דף ועיצוב RTL מקיף (סיידבר + תוכן מרכזי)
st.set_page_config(page_title="מתווך בקליק", layout="wide")

st.markdown("""
<style>
    /* יישור גלובלי */
    html, body, [data-testid="stAppViewContainer"], .main { 
        direction: rtl; 
        text-align: right; 
    }
    
    /* יישור תוכן ה-Markdown והטקסט בתוך האפליקציה */
    .stMarkdown, .stText, [data-testid="stMarkdownContainer"] {
        direction: rtl;
        text-align: right;
    }

    /* יישור ספציפי לסיידבר */
    [data-testid="stSidebar"] { 
        position: fixed; 
        right: 0; 
        left: auto; 
        direction: rtl; 
        background-color: #f8f9fa; 
        border-left: 1px solid #e0e0e0; 
    }
    [data-testid="stSidebar"] div, [data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label {
        text-align: right !important; 
        direction: rtl !important;
    }

    /* עיצוב כותרות ולוגו */
    .sidebar-logo { 
        font-size: 26px; 
        font-weight: bold; 
        color: #1E88E5; 
        text-align: center !important; 
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
    
    /* יישור כפתורים */
    .stButton button { width: 100%; text-align: right; }
    
    /* תיבת תוכן השיעור */
    .lesson-container {
        direction: rtl;
        text-align: right;
        background-color: #ffffff;
        padding: 25px;
        border-radius: 10px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        line-height: 1.8;
    }
</style>
""", unsafe_allow_html=True)

# 2. ניהול Session State (ללא שינוי לוגי)
for k, v in {
    "view_mode": "login", "user_name": "", "current_topic": "",
    "full_exam_data": [], "full_exam_ready": False,
    "lesson_data": "", "lesson_quiz_data": [], "lesson_quiz_ready": False
}.items():
    if k not in st.session_state: st.session_state[k] = v

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
        
        if st.button("📚 שיעורי הלימוד", use_container_width=True):
            st.session_state.view_mode = "setup"; st.rerun()
            
        if st.session_state.current_topic:
            st.write(f"📖 **נושא:** {st.session_state.current_topic}")
            if st.button("קרא שיעור", use_container_width=True):
                st.session_state.view_mode = "lesson_view"; st.rerun()
            
            if st.button("✍️ שאלון תרגול", use_container_width=True, disabled=not st.session_state.lesson_quiz_ready):
                st.session_state.view_mode = "lesson_quiz"; st.rerun()

        st.markdown("---")
        if st.button("📝 בחינה (25 שאלות)", use_container_width=True, type="primary", disabled=not st.session_state.full_exam_ready):
            st.session_state.view_mode = "full_exam"; st.rerun()

# 4. דפים
if st.session_state.view_mode == "login":
    st.markdown('<div class="main-header">🎓 מתווך בקליק</div>', unsafe_allow_html=True)
    name = st.text_input("הכנס שם משתמש:")
    if st.button("התחבר"):
        if name:
            st.session_state.user_name = name
            st.session_state.view_mode = "setup"
            # יצירת המבחן הגדול
            try:
                res = model.generate_content("צור 25 שאלות למבחן תיווך בפורמט [START_Q]")
                st.session_state.full_exam_data = parse_quiz(res.text)
                st.session_state.full_exam_ready = True
            except: pass
            st.rerun()

elif st.session_state.view_mode == "setup":
    st.markdown('<div class="main-header">בחירת נושא לימוד</div>', unsafe_allow_html=True)
    t = st.selectbox("בחר נושא:", ["חוק המתווכים", "חוק המקרקעין", "דיני חוזים", "מיסוי מקרקעין", "חוק המכר"])
    if st.button("עבור לשיעור"):
        st.session_state.current_topic = t
        st.session_state.lesson_data = ""
        st.session_state.lesson_quiz_ready = False
        st.session_state.view_mode = "lesson_view"; st.rerun()

elif st.session_state.view_mode == "lesson_view":
    st.markdown(f'<div class="main-header">{st.session_state.current_topic}</div>', unsafe_allow_html=True)
    
    if not st.session_state.lesson_data:
        with st.spinner("מכין את חומרי הלימוד..."):
            res_l = model.
