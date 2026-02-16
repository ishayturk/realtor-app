# ==========================================
# Project: מתווך בקליק | Version: 1163
# Last Updated: 2026-02-16 | 18:05
# ==========================================

import streamlit as st
import google.generativeai as genai
import json, re

st.set_page_config(page_title="מתווך בקליק", layout="wide")
st.markdown('<div id="top"></div>', unsafe_allow_html=True)

# סילבוס מובנה - רשימה חלקית למניעת קטיעת קוד
SYLLABUS = {
    "חוק המתווכים במקרקעין": ["רישוי והגבלות עיסוק", "חובת הגינות וזהירות", "הזמנת תיווך ובלעדיות"],
    "חוק המקרקעין": ["בעלות וזכויות", "בתים משותפים", "עסקאות נוגדות והערות אזהרה"],
    "חוק המכר (דירות)": ["מפרט וחובת גילוי", "בדק ואחריות", "איחור במסירה"],
    "חוק החוזים": ["כריתת חוזה", "פגמים בחוזה", "תרופות בשל הפרה"],
    "חוק מיסוי מקרקעין": ["מס שבח", "מס רכישה", "פטורים והקלות"]
}

def ask_ai(prompt):
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-2.0-flash')
        res = model.generate_content(prompt)
        return res.text if (res and res.text) else None
    except: return None

def fetch_content(topic, sub):
    p = f"כתוב שיעור מקצועי על '{sub}' בתוך '{topic}'. בלי הקדמות ובלי המילים 'מבחן מתווכים'."
    res = ask_ai(p)
    return res if res else "⚠️ שגיאה בטעינה."

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
        "lesson_contents": {}, "current_sub_idx": None,
        "quiz_active": False, "q_counter": 0, "score": 0,
        "current_q_data": None, "show_feedback": False
    })

# CSS: כפתורים שקופים עם מסגרת אפורה כהה
st.markdown("""
<style>
    * { direction: rtl; text-align: right; }
    .stButton>button { width: auto; min-width: 100px; border-radius: 8px; font-weight: bold; background-color: transparent !important; border: 1px solid #888 !important; color: #333 !important; }
    .nav-btn { background: transparent; border: 1px solid #888; color: #333; padding: 6px 15px; text-decoration: none; border-radius: 8px; display: inline-block; font-size: 14px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

st.title("🏠 מתווך בקליק")

if st.session_state.step == 'login':
    u = st.text_input("הזן שם מלא:")
    if st.button("כניסה"):
        if u: st.session_state.update({"user": u, "step": "menu"}); st.rerun()

elif st.session_state.step == 'menu':
    st.write(f"👤 שלום, {st.session_state.user}")
    c1, c2 = st.columns(2)
    if c1.button("📚 לימוד לפי נושאים"):
        st.session_state.step = 'study'; st.rerun()
    if c2.button("⏱️ סימולציית בחינה"): st.info("בפיתוח...")

elif st.session_state.step == 'study':
