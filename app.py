# ==========================================
# Project: מתווך בקליק | Version: 1179
# ==========================================

import streamlit as st
import google.generativeai as genai
import json, re

# הגדרה רחבה עם שבירת שורות
st.set_page_config(
    page_title="מתווך בקליק", 
    layout="wide"
)

# CSS מחולק לשורות קצרות
st.markdown(
    """
    <style>
        * { direction: rtl; text-align: right; }
        .stButton>button { 
            width: auto; 
            min-width: 150px; 
            border-radius: 8px; 
            font-weight: bold; 
            border: 1px solid #888 !important; 
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
    "חוק המתווכים במקרקעין": ["רישוי", "הגינות", "בלעדיות"],
    "תקנות המתווכים": ["פרטי הזמנה", "פעולות שיווק"],
    "חוק המקרקעין": ["בעלות", "בתים משותפים", "הערות אזהרה"],
    "חוק המכר": ["מפרט", "בדק", "איחור במסירה"],
    "חוק החוזים": ["כריתה", "פגמים", "תרופות"],
    "תכנון ובנייה": ["היתרים", "היטל השבחה"],
    "מיסוי מקרקעין": ["מס שבח", "מס רכישה"]
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
    return res if res else "⚠️ שגיאה בטעינה."

def fetch_q(topic):
    p = f"צור שאלה אמריקאית על {topic}. JSON format: q, options, correct, explain."
    res = ask_ai(p)
    try:
        m = re.search(r'\{.*\}', res, re.DOTALL)
        return json.loads(m.group()) if m else None
    except:
        return None

# אתחול
if "step" not in st.session_state:
    st.session_state.update({
        "step": "login", "user": None, "selected_topic": None,
        "lesson_contents": {}, "current_sub_idx": None,
        "quiz_active": False, "q_counter": 0, "score": 0,
        "current_q_data": None, "next_q_data": None, "show_feedback": False
    })

st.title("🏠 מתווך בקליק")

if st.session_state.step == 'login':
    u = st.text_input("הזן שם מלא:")
    if st.button("כניסה לאפליקציה") and u:
        st.session_state.update({"user": u, "step": "menu"})
        st.rerun()

elif st.session_state.step == 'menu':
    st.write(f"👤 שלום, {st.session_state.user}")
    c1, c2 = st.columns(2)
    if c1.button("📚 לימוד לפי נושאים"):
        st.session_state.step = 'study'
        st.rerun()
    if c2.button("⏱️ סימולציית בחינה"):
        st.info("בקרוב...")

elif st.session_state.step == 'study':
    ts = ["בחר נושא..."] + list(SYLLABUS.keys())
    sel = st.selectbox("רשימת נושאים:", ts)
    if sel != "בחר נושא..." and st.button("טען נושא נבחר"):
        st.session_state.update({
            "selected_topic": sel, "lesson_contents": {}, 
            "current_sub_idx": None, "quiz_active": False, 
            "step": "lesson_run", "q_counter": 0
        })
        st.rerun()

elif st.session_state.step == 'lesson_run':
    topic = st.session_state.selected_topic
    st.header(f"📖 {topic}")
    subs = SYLLABUS.get(topic, [])
    
    if subs:
        t_cols = st.columns(len(subs))
        for i, t in enumerate(subs):
            if t_cols[i].button(t, key=f"s_{i}"):
                st.session_state.update({"current_sub_idx": i, "quiz_active": False})
                with st.spinner("טוען תוכן..."):
                    st.session_state.lesson_contents[t] = fetch_content(topic, t)
                st.rerun()

    if st.session_state.current_sub_idx is not None:
        idx = st.session_state.current_sub_idx
        st.markdown(st.session_state.lesson_contents.get(subs[idx], ""))

    if st.session_state.quiz_active:
        st.divider()
        if not st.session_state.current_q_data:
            st.session_state.current_q_data = fetch_q(topic)
            st.rerun()
        
        q = st.session_state.current_q_data
        st.write(f"**שאלה {st.session_state.q_counter} מתוך 10**")
        ans = st.radio(q['q'], q['options'], index=None, key="
