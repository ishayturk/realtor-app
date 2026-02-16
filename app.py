# ==========================================
# Project: מתווך בקליק | Version: 1159
# Last Updated: 2026-02-17 | 01:25
# ==========================================

import streamlit as st
import google.generativeai as genai
import json, re

st.set_page_config(page_title="מתווך בקליק", layout="wide")
st.markdown('<div id="top"></div>', unsafe_allow_html=True)

# --- סילבוס קבוע ---
SYLLABUS = {
    "חוק המתווכים במקרקעין": ["רישוי והגבלות עיסוק", "חובת הגינות וזהירות", "הזמנת תיווך ובלעדיות"],
    "תקנות המתווכים (פרטי הזמנה)": ["דרישות חובה בטופס", "זיהוי נכס וצדדים", "פירוט דמי התיווך"],
    "תקנות המתווכים (פעולות שיווק)": ["פעולות שיווק סטנדרטיות", "הרחבות לשיווק בבלעדיות", "חובת הוכחת פעילות"],
    "חוק המקרקעין": ["בעלות וזכויות במקרקעין", "בתים משותפים והצמדות", "עסקאות נוגדות והערות אזהרה"],
    "חוק הגנת הדייר": ["דיירות מוגנת ודמי מפתח", "עילות פינוי", "זכויות וחובות דייר מוגן"],
    "חוק המכר (דירות)": ["מפרט וחובת גילוי", "תקופות בדק ואחריות", "איחור במסירה ופיצויים"],
    "חוק החוזים": ["כריתת חוזה ותום לב", "פגמים בחוזה (טעות/הטעיה)", "תרופות בשל הפרת חוזה"],
    "חוק הגנת הצרכן": ["הטעיה בפרסום ושיווק", "ביטול עסקה והחזר כספי", "חובות גילוי כלפי צרכן"],
    "חוק עבירות עונשין": ["עבירות מרמה והונאה", "זיוף מסמכים במקרקעין", "אחריות פלילית של בעלי מקצוע"],
    "חוק שמאי מקרקעין": ["תפקיד השמאי והערכות", "סמכויות והגדרות", "בסיס השומה למכירה"],
    "חוק התכנון והבנייה": ["היתרי בנייה ושימוש חורג", "היטל השבחה", "תוכניות מתאר"],
    "חוק מיסוי מקרקעין": ["מס שבח", "מס רכישה", "פטורים והקלות במס"],
    "חוק הירושה": ["ירושה על פי דין מול צוואה", "ניהול עיזבון", "העברת מקרקעין בירושה"],
    "חוק הוצאה לפועל": ["עיקול מקרקעין", "מימוש משכנתאות", "פינוי נכסים"],
    "פקודת הנזיקין": ["רשלנות מקצועית", "מצג שווא", "חובת הזהירות כלפי צד ג'"]
}

def ask_ai(prompt):
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-2.0-flash')
        res = model.generate_content(prompt)
        return res.text if (res and res.text) else None
    except: return None

def fetch_content(topic, sub):
    p = f"כתוב שיעור Markdown מקצועי על '{sub}' בתוך '{topic}'. בלי הקדמות ובלי לציין 'מבחן מתווכים'."
    return ask_ai(p) or "⚠️ שגיאה בטעינה."

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

# CSS מעודכן לכפתורים בגודל טבעי
st.markdown("""
<style>
    * { direction: rtl; text-align: right; }
    .user-strip { margin-top: 40px; margin-bottom: 30px; font-weight: bold; color: #444; }
    .stButton>button { width: auto; min-width: 120px; border-radius: 8px; font-weight: bold; padding: 5px 20px; }
    .nav-btn { 
        background-color: transparent !important; 
        border: 1px solid #ccc !important; 
        font-weight: normal !important; 
        color: #555 !important;
        padding: 6px 15px;
        display: inline-block;
        text-decoration: none;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

st.title("🏠 מתווך בקליק")

if st.session_state.step == 'login':
    u = st.text_input("הזן שם מלא:")
    if st.button("כניסה"):
        if u: st.session_state.update({"user": u, "step": "menu"}); st.rerun()

elif st.session_state.step == 'menu':
    st.markdown(f'<div class="user-strip">👤 שלום, {st.session_state.user}</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    if c1.button("📚 לימוד לפי נושאים"):
        st.session_state.step = 'study'; st.rerun()
    if c2.button("⏱️ סימולציית בחינה"): st.info("בפיתוח...")

elif st.session_state.step == 'study':
    ts = ["בחר נושא..."] + list(SYLLABUS.keys())
    sel = st.selectbox("נושא לימוד:", ts)
    if sel != "בחר נושא..." and st.button("טען שיעור"):
        st.session_state.update({
            "selected_topic": sel, "lesson_contents": {}, 
            "current_sub_idx": None, "quiz_active": False, "step": "lesson_run"
        })
        st.rerun()

elif st.session_state.step == 'lesson_run':
    st.header(f"📖 {st.session_state.selected_topic}")
    subs = SYLLABUS.get(st.session_state.selected_topic, [])
    
    # כפתורי תתי-נושאים בגודל דינמי
    if subs:
        cols = st.columns(len(subs))
        for i, t in enumerate(subs):
            if cols[i].button(t, key=f"b{
