# ==========================================
# Project: מתווך בקליק | Version: 1180
# ==========================================

import streamlit as st
import google.generativeai as genai
import json, re

# הגדרות דף בשורות נפרדות
st.set_page_config(
    page_title="מתווך בקליק",
    layout="wide"
)

# CSS במבנה מקוצר מאוד
st.markdown(
    """
    <style>
        * { direction: rtl; text-align: right; }
        .stButton>button { 
            min-width: 150px; 
            border-radius: 8px; 
            font-weight: bold; 
        }
        .nav-btn { 
            border: 1px solid #888; 
            padding: 8px 16px; 
            text-decoration: none; 
            border-radius: 8px; 
            font-weight: bold; 
            display: inline-block; 
            color: #333;
        }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown('<div id="top"></div>', unsafe_allow_html=True)

SYLLABUS = {
    "חוק המתווכים": ["רישוי", "הגינות", "בלעדיות"],
    "תקנות המתווכים": ["פרטי הזמנה", "שיווק"],
    "חוק המקרקעין": ["בעלות", "בתים", "אזהרה"],
    "חוק המכר": ["מפרט", "בדק", "איחור"],
    "חוק החוזים": ["כריתה", "פגמים", "תרופות"],
    "תכנון ובנייה": ["היתרים", "השבחה"],
    "מיסוי מקרקעין": ["שבח", "רכישה"]
}

def ask_ai(p):
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        m = genai.GenerativeModel('gemini-2.0-flash')
        r = m.generate_content(p)
        return r.text if r else None
    except:
        return None

def fetch_content(topic, sub):
    p = f"כתוב שיעור על {sub} בתוך {topic}."
    res = ask_ai(p)
    return res if res else "⚠️ שגיאה."

def fetch_q(topic):
    p = f"צור שאלה אמריקאית על {topic}. JSON."
    res = ask_ai(p)
    try:
        m = re.search(r'\{.*\}', res, re.DOTALL)
        return json.loads(m.group()) if m else None
    except:
        return None

# אתחול
if "step" not in st.session_state:
    st.session_state.update({
        "step": "login", "user": None,
        "selected_topic": None, "lesson_contents": {},
        "current_sub_idx": None, "quiz_active": False,
        "q_counter": 0, "current_q_data": None,
        "next_q_data": None, "show_feedback": False
    })

st.title("🏠 מתווך בקליק")

# לוגיקת שלבים
step = st.session_state.step

if step == 'login':
    u = st.text_input("הזן שם מלא:")
    if st.button("כניסה") and u:
        st.session_state.user = u
        st.session_state.step = 'menu'
        st.rerun()

elif step == 'menu':
    st.write(f"👤 שלום, {st.session_state.user}")
    c1, c2 = st.columns(2)
    if c1.button("📚 לימוד לפי נושאים"):
        st.session_state.step = 'study'
        st.rerun()
    if c2.button("⏱️ סימולציה"):
        st.info("בקרוב")

elif step == 'study':
    opts = ["בחר..."] + list(SYLLABUS.keys())
    sel = st.selectbox("נושא:", opts)
    if sel != "בחר..." and st.button("טען"):
        st.session_state.update({
            "selected_topic": sel, "lesson_contents": {},
            "current_sub_idx": None, "quiz_active": False,
            "step": "lesson_run", "q_counter": 0
        })
        st.rerun()

elif step == 'lesson_run':
    cur_topic = st.session_state.selected_topic
    st.header(f"📖 {cur_topic}")
    subs = SYLLABUS.get(cur_topic, [])
    
    if subs:
        t_cols = st.columns(len(
