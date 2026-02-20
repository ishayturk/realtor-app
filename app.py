import streamlit as st
import google.generativeai as genai
import json, re

st.set_page_config(page_title="מתווך בקליק", layout="wide")

SYLLABUS = {
    "חוק המתווכים": ["רישוי", "הגינות", "בלעדיות"],
    "תקנות המתווכים": ["הזמנה 1997", "שיווק 2004"],
    "חוק המקרקעין": ["זכויות", "בתים משותפים", "אזהרה"],
    "חוק המכר": ["מפרט", "אחריות"],
    "חוק החוזים": ["כריתה", "תרופות"]
}

def fetch_q_ai(topic):
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        m = genai.GenerativeModel('gemini-2.0-flash')
        p = f"שאלה על {topic}. JSON: "
        p += "{'q':'','options':['','','',''],'correct':'','explain':''}"
        res = m.generate_content(p).text
        match = re.search(r'\{.*\}', res, re.DOTALL)
        if match: return json.loads(match.group())
    except: return None
    return None

def stream_ai_lesson(p):
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        m = genai.GenerativeModel('gemini-2.0-flash')
        full_p = p + " שיעור הכנה למבחן המתווכים."
        response = m.generate_content(full_p, stream=True)
        placeholder = st.empty()
        full_text = ""
        for chunk in response:
            full_text += chunk.text
            placeholder.markdown(full_text + "▌")
        placeholder.markdown(full_text)
        return full_text
    except: return "⚠️ תקלה."

if "step" not in st.session_state:
    st.session_state.update({
        "user": None, "step": "login", 
        "selected_topic": None, "lesson_txt": "", 
        "quiz_active": False, "q_data": None, "show_ans": False
    })

# --- ניווט ודפים ---

if st.session_state.step == "login":
    st.markdown("<style>* { direction: rtl; text-align: right; }</style>", 
                unsafe_allow_html=True)
    st.title("🏠 מתווך בקליק")
    u = st.text_input("שם מלא:")
    if st.button("כניסה") and u:
        st.session_state.update({"user": u, "step": "menu"})
        st.rerun()

elif st.session_state.step == "menu":
    st.markdown("<style>* { direction: rtl; text-align: right; }</style>", 
                unsafe_allow_html=True)
    st.title("🏠 מתווך בקליק")
    st.subheader(f"👤 שלום, {st.session_state.user}")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("📚 לימוד לפי נושאים", use_container_width=True):
            st.session_state.step = "study"; st.rerun()
    with c2:
        if st.button("⏱️ גש/י למבחן", use_container_width=True):
            st.session_state.step = "exam_intro"; st.rerun()

elif st.session_state.step == "study":
    st.markdown("<style>* { direction: rtl; text-align: right; }</style>", 
                unsafe_allow_html=True)
    st.title("🏠 מתווך בקליק")
    st.subheader(f"👤 שלום, {st.session_state.user}")
    sel = st.selectbox("בחר נושא:", ["בחר..."] + list(SYLLABUS.keys()))
    col1, col2 = st.columns(2)
    with col1:
        if st.button("התחל לימוד", use_container_width=True) and sel != "בחר...":
            st.session_state.update({
                "selected_topic": sel, "step": "lesson_run", 
                "lesson_txt": "", "quiz_active": False
            })
            st.rerun()
    with col2:
        if st.button("🏠 חזרה לתפריט", use_container_width=True):
            st.session_state.step = "menu"; st.rerun()

elif st.session_state.step == "lesson_run":
    st.markdown("<style>* { direction: rtl; text-align: right; }</style>", 
                unsafe_allow_html=True)
    st.title(f"📖 {st.session_state.selected_topic}")
    if not st.session_state.lesson_txt:
        st.session_state.lesson_txt = stream_ai_lesson(st.session_state.selected_topic)
    if st.button("❓ בחן אותי"):
        st.session_state.q_data = fetch_q_ai(st.session_state.selected_topic)
        st.session_state.quiz_active = True
        st.session_state.show_ans = False
    if st.session_state.quiz_active and st.session_state.q_data:
        q = st.session_state.q_data
        ans = st.radio(q['q'], q['options'], index=None)
        if st.button("בדוק"): st.session_state.show_ans
