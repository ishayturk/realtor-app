# ==========================================
# Project: מתווך בקליק | Version: 1157
# Last Updated: 2026-02-17 | 00:40
# ==========================================

import streamlit as st
import google.generativeai as genai
import json, re

st.set_page_config(page_title="מתווך בקליק", layout="wide")
st.markdown('<div id="top"></div>', unsafe_allow_html=True)

def ask_ai(prompt):
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-2.0-flash')
        res = model.generate_content(prompt)
        return res.text if (res and res.text) else None
    except: return None

def clean_txt(t):
    return re.sub(r"[\[\]{}'\"]", "", str(t)).strip() if t else ""

def fetch_titles(topic):
    p = f"צור 3 כותרות לתתי-נושאים בתוך {topic}. JSON: ['א','ב','ג']"
    res = ask_ai(p)
    try:
        m = re.search(r'\[.*\]', res, re.DOTALL)
        return [clean_txt(t) for t in json.loads(m.group())]
    except: return ["שיעור 1", "שיעור 2", "שיעור 3"]

def fetch_content(topic, sub):
    p = f"כתוב שיעור Markdown על '{sub}' בתוך '{topic}'. בלי הקדמות."
    return ask_ai(p) or "⚠️ שגיאה."

def fetch_q(topic):
    p = f"צור שאלה אמריקאית על {topic}. JSON: {{'q':'..','options':['..'],'correct':'..','explain':'..'}}"
    res = ask_ai(p)
    try:
        m = re.search(r'\{.*\}', res, re.DOTALL)
        return json.loads(m.group())
    except: return None

if "step" not in st.session_state:
    st.session_state.update({
        "step": "login", "user": None, "selected_topic": None,
        "lesson_titles": [], "lesson_contents": {}, "current_sub_idx": None,
        "quiz_active": False, "q_counter": 0, "score": 0,
        "current_q_data": None, "show_feedback": False
    })

st.markdown("""
<style>
    * { direction: rtl; text-align: right; }
    .user-strip { margin-top: 40px; margin-bottom: 30px; font-weight: bold; color: #444; }
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; }
    .nav-btn { background-color: #f0f2f6 !important; border: 1px solid #ccc !important; font-weight: normal !important; color: black !important; }
</style>
""", unsafe_allow_html=True)

st.title("🏠 מתווך בקליק")
if st.session_state.user:
    st.markdown(f'<div class="user-strip">👤 שלום, {st.session_state.user}</div>', unsafe_allow_html=True)

if st.session_state.step == 'login':
    u = st.text_input("הזן שם מלא:")
    if st.button("כניסה"):
        if u:
            st.session_state.user = u
            st.session_state.step = 'menu'; st.rerun()

elif st.session_state.step == 'menu':
    c1, c2 = st.columns(2)
    if c1.button("📚 לימוד לפי נושאים"):
        st.session_state.step = 'study'; st.rerun()
    if c2.button("⏱️ סימולציית בחינה"): st.info("בפיתוח...")

elif st.session_state.step == 'study':
    ts = ["בחר נושא...", "חוק המתווכים במקרקעין", "תקנות המתווכים (פרטי הזמנה)", 
          "תקנות המתווכים (פעולות שיווק)", "חוק המקרקעין", "חוק הגנת הדייר", 
          "חוק המכר (דירות)", "חוק החוזים", "חוק הגנת הצרכן", "חוק עבירות עונשין", 
          "חוק שמאי מקרקעין", "חוק התכנון והבנייה", "חוק מיסוי מקרקעין", "חוק הירושה"]
    sel = st.selectbox("נושא לימוד:", ts)
    if sel != "בחר נושא..." and st.button("טען שיעור"):
        st.session_state.update({
            "selected_topic": sel, "lesson_titles": fetch_titles(sel),
            "lesson_contents": {}, "current_sub_idx": None,
            "quiz_active": False, "step": "lesson_run"
        })
        st.rerun()

elif st.session_state.step == 'lesson_run':
    st.header(f"📖 {st.session_state.selected_topic}")
    tls = st.session_state.lesson_titles
    if tls:
        cols = st.columns(len(tls))
        for i, t in enumerate(tls):
            if cols[i].button(t, key=f"b{i}", disabled=(st.session_state.current_sub_idx == i)):
                st.session_state.current_sub_idx = i
                st.session_state.quiz_active = False 
                with st.spinner("מכין שיעור..."):
                    st.session_state.lesson_contents[t] = fetch_content(st.session_state.selected_topic, t)
                st.rerun()

    if st.session_state.current_sub_idx is not None:
        curr_t = st.session_state.lesson_titles[st.session_state.current_sub_idx]
        st.markdown(st.session_state.lesson_contents.get(curr_t, "⚠️"))
        
        if st.session_state.quiz_active and st.session_state.current_q_data:
            st.divider()
            q = st.session_state.current_q_data
