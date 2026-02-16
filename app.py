# ==========================================
# Project: מתווך בקליק | Version: 1184
# ==========================================

import streamlit as st
import google.generativeai as genai
import json, re

st.set_page_config(page_title="מתווך בקליק", layout="wide")

# CSS יציב
st.markdown("""
<style>
    * { direction: rtl; text-align: right; }
    .stButton>button { width: auto; min-width: 150px; border-radius: 8px; font-weight: bold; }
    .nav-btn { border: 1px solid #888; padding: 8px 16px; text-decoration: none; 
               border-radius: 8px; font-weight: bold; display: inline-block; color: #333; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div id="top"></div>', unsafe_allow_html=True)

# החזרת הסילבוס המפורט והמלא
SYLLABUS = {
    "חוק המתווכים במקרקעין": [
        "רישוי והגבלות עיסוק", "חובת הגינות וזהירות", 
        "הזמנת תיווך ובלעדיות", "פעולות שאינן תיווך"
    ],
    "תקנות המתווכים (פרטי הזמנה)": [
        "דרישות חובה בטופס", "זיהוי נכס וצדדים", "פירוט דמי התיווך"
    ],
    "תקנות המתווכים (פעולות שיווק)": [
        "פעולות שיווק", "הרחבות לבלעדיות", "חובת הוכחת פעילות"
    ],
    "חוק המקרקעין": [
        "בעלות וזכויות", "בתים משותפים", "עסקאות נוגדות", "הערות אזהרה"
    ],
    "חוק המכר (דירות)": [
        "מפרט וחובת גילוי", "בדק ואחריות", "איחור במסירה", "הבטחת השקעות"
    ],
    "חוק החוזים": [
        "כריתת חוזה", "פגמים בחוזה", "תרופות בשל הפרה", "ביטול והשבה"
    ],
    "חוק התכנון והבנייה": [
        "היתרי בנייה", "היטל השבחה", "תוכניות מתאר", "שימוש חורג"
    ],
    "חוק מיסוי מקרקעין": [
        "מס שבח", "מס רכישה", "פטורים והקלות", "שווי שוק"
    ]
}

def ask_ai(p):
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        m = genai.Generativeai('gemini-2.0-flash') # שים לב: שימוש במודל העדכני
        r = m.generate_content(p)
        return r.text if r else None
    except: return None

def fetch_content(topic, sub):
    p = f"כתוב שיעור מקצועי ומפורט על '{sub}' כחלק מנושא '{topic}' למבחן מתווכים."
    return ask_ai(p) or "⚠️ שגיאה בטעינת התוכן."

def fetch_q(topic):
    p = f"צור שאלה אמריקאית על {topic}. החזר JSON: q, options, correct, explain."
    res = ask_ai(p)
    try:
        m = re.search(r'\{.*\}', res, re.DOTALL)
        return json.loads(m.group()) if m else None
    except: return None

if "step" not in st.session_state:
    st.session_state.update({
        "step": "login", "user": None, "selected_topic": None,
        "lesson_contents": {}, "current_sub_idx": None,
        "quiz_active": False, "q_counter": 0, "current_q_data": None,
        "next_q_data": None, "show_feedback": False
    })

st.title("🏠 מתווך בקליק")

# ניהול שלבים
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
    if c2.button("⏱️ גש/י למבחן"):
        st.info("סימולציית מבחן מלאה תעלה בקרוב.")

elif st.session_state.step == 'study':
    opts = ["בחר נושא..."] + list(SYLLABUS.keys())
    sel = st.selectbox("בחר נושא לימוד:", opts)
    if sel != "בחר נושא..." and st.button("טען נושא"):
        st.session_state.update({
            "selected_topic": sel, "lesson_contents": {},
            "current_sub_idx": None, "quiz_active": False,
            "step": "lesson_run", "q_counter": 0
        })
        st.rerun()

elif st.session_state.step == 'lesson_run':
    cur_t = st.session_state.selected_topic
    st.header(f"📖 {cur_t}")
    subs = SYLLABUS.get(cur_t, [])
    
    if subs:
        t_cols = st.columns(len(subs))
        for i, t in enumerate(subs):
            if t_cols[i].button(t, key=f"s_{i}"):
                st.session_state.update({"current_sub_idx": i, "quiz_active": False})
                with st.spinner("טוען..."):
                    st.session_state.lesson_contents[t] = fetch_content(cur_t,
