# ==========================================
# Project: מתווך בקליק | Version: 1191
# ==========================================

import streamlit as st
import google.generativeai as genai
import json, re
import streamlit.components.v1 as components

st.set_page_config(page_title="מתווך בקליק", layout="wide")

def scroll_to_top():
    components.html(
        "<script>window.parent.document.querySelector('section.main').scrollTo(0, 0);</script>",
        height=0
    )

st.markdown("""
<style>
    * { direction: rtl; text-align: right; }
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# סילבוס מקצועי ומלא - מבנה מופרד למניעת חיתוך
SYLLABUS = {
    "חוק המתווכים במקרקעין": [
        "רישוי והגבלות עיסוק", "חובת הגינות וזהירות", 
        "הזמנת תיווך ובלעדיות", "פעולות שאינן תיווך"
    ],
    "תקנות המתווכים": [
        "פרטי הזמנה (תקנות 1997)", "פעולות שיווק (תקנות 2004)", 
        "דמי תיווך וזכאות"
    ],
    "חוק המקרקעין": [
        "בעלות וזכויות במקרקעין", "בתים משותפים וניהולם", 
        "עסקאות נוגדות", "הערות אזהרה", "שכירות, שאילה וזיקת הנאה"
    ],
    "חוק המכר (דירות)": [
        "מפרט וחובת גילוי", "תקופת בדק ואחריות", 
        "פיצוי בשל איחור במסירה", "חוק המכר (הבטחת השקעות)"
    ],
    "חוק החוזים": [
        "כריתת חוזה (הצעה וקיבול)", "פגמים בחוזה (טעות, הטעיה, עושק)", 
        "תרופות בשל הפרת חוזה", "ביטול, השבה ופיצויים"
    ],
    "חוק התכנון והבנייה": [
        "היתרי בנייה ושימוש חורג", "היטל השבחה", 
        "תוכניות מתאר (ארצית, מחוזית, מקומית)", "מוסדות התכנון"
    ],
    "חוק מיסוי מקרקעין": [
        "מס שבח", "מס רכישה", "פטורים והקלות לדירת מגורים", "חישוב שווי השוק"
    ],
    "חוק הגנת הצרכן": [
        "ביטול עסקת מכר מרחוק", "הטעיה בפרסום וניצול מצוקה"
    ],
    "חוק הירושה": [
        "סדר הירושה על פי דין", "סוגי צוואות ותוקפן"
    ],
    "חוק העונשין": [
        "עבירות מרמה וזיוף", "קבלת דבר במרמה בנסיבות מחמירות"
    ]
}

def ask_ai(p):
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        m = genai.GenerativeModel('gemini-2.0-flash')
        # דרישה לתוכן מקצועי ומפורט להצלחה בבחינה
        r = m.generate_content(p + " כתוב שיעור מעמיק, מקצועי ומפורט מאוד שיכין את התלמיד למבחן המתווכים בצורה הטובה ביותר.")
        return r.text if r else None
    except Exception as e:
        return f"⚠️ שגיאה: {str(e)}"

def fetch_q(topic):
    p = f"צור שאלה אמריקאית מאתגרת ברמת מבחן המתווכים על {topic}. JSON format: {{'q':'','options':[],'correct':'','explain':''}}"
    res = ask_ai(p)
    try:
        match = re.search(r'\{.*\}', res, re.DOTALL)
        return json.loads(match.group()) if match else None
    except: return None

# ניהול מצב
if "user" not in st.session_state: st.session_state.user = None
if "step" not in st.session_state: st.session_state.step = "login"
if "quiz_active" not in st.session_state: st.session_state.quiz_active = False

st.title("🏠 מתווך בקליק")

if st.session_state.step == "login":
    u = st.text_input("הזן שם מלא:")
    if st.button("כניסה") and u:
        st.session_state.user = u
        st.session_state.step = "menu"
        st.rerun()

elif st.session_state.step == "menu":
    st.subheader(f"👤 שלום, {st.session_state.user}")
    if st.button("📚 לימוד לפי נושאים"):
        st.session_state.step = "study"
        st.rerun()

elif st.session_state.step == "study":
    st.write(f"👤 משתמש: {st.session_state.user}")
    sel = st.selectbox("בחר נושא לימוד:", list(SYLLABUS.keys()))
    if st.button("טען נושא"):
        st.session_state.update({"selected_topic": sel, "step": "lesson_run", "quiz_active": False, "lesson_txt": ""})
        st.rerun()

elif st.session_state.step == "lesson_run":
    topic = st.session_state.selected_topic
    st.header(f"📖 {topic}")
    st.write(f"👤 תלמיד: {st.session_state.user}")
    
    subs = SYLLABUS.get(topic, [])
    t_cols = st.columns(len(subs))
    for i, s in enumerate(subs):
        if t_cols[i].button(s, key=f"s_{i}"):
            with st.spinner(f"טוען חומר מפורט על {s}..."):
                st.session_state.lesson_txt = ask_ai(f"שיעור מלא על {s} בתוך {topic}")
            st.rerun()
            
    if st.session_state.get("lesson_txt"):
        st.markdown(st.session_state.lesson_txt)

    # שאלון דינמי
    if st.session_state.quiz_active:
        st.divider()
        st.subheader(f"📝 שאלון: {topic}")
        if "q_data" not in st.session_state or st.session_state.q_data is None:
            st.session_state.q_data = fetch_q(topic)
            st.rerun()
        
        q = st.session_state.q_data
        if q:
            ans = st.radio(q['q'], q['options'], index=None)
            if st.button("בדוק תשובה"):
                if ans == q['correct']: st.success("נכון!")
                else: st.error(f"טעות. התשובה הנכונה היא: {q['correct']}")
                st.info(f"הסבר מקצועי: {q['explain']}")

    st.write("---")
    b_cols = st.columns([2.5, 1.5, 1.5, 4])
    
    with b_cols[0]:
        if not st.session_state.quiz_active:
            if st.button(f"📝 שאלון: {topic}"):
                st.session_state.quiz_active = True
                st.session_state.q_data = fetch_q(topic)
                st.rerun()
        else:
            if st.button("➡️ שאלה הבאה"):
                st.session_state.q_data = fetch_q(topic)
                st.rerun()

    with b_cols[1]:
        if st.button("🏠 תפריט"):
            st.session_state.step = "menu"
            st.rerun()
            
    with b_cols[2]:
        if st.button("🔝 למעלה"): scroll_to_top()
