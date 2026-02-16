# ==========================================
# Project: מתווך בקליק | Version: 1193
# ==========================================

import streamlit as st
import google.generativeai as genai
import json, re

# הגדרות דף ועוגן עליון
st.set_page_config(page_title="מתווך בקליק", layout="wide")
st.markdown('<div id="top"></div>', unsafe_allow_html=True)

# עיצוב RTL נקי
st.markdown("""
<style>
    * { direction: rtl; text-align: right; }
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; }
    .top-btn { border: 1px solid #ccc; padding: 10px; border-radius: 8px; 
               text-align: center; text-decoration: none; display: block; 
               color: black; background: #f0f2f6; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# סילבוס מלא ומסודר
SYLLABUS = {
    "חוק המתווכים במקרקעין": ["רישוי והגבלות עיסוק", "חובת הגינות וזהירות", "הזמנת תיווך ובלעדיות", "פעולות שאינן תיווך"],
    "תקנות המתווכים": ["פרטי הזמנה", "פעולות שיווק", "דמי תיווך"],
    "חוק המקרקעין": ["בעלות וזכויות", "בתים משותפים", "עסקאות נוגדות", "הערות אזהרה", "שכירות ושאילה"],
    "חוק המכר (דירות)": ["מפרט וחובת גילוי", "בדק ואחריות", "איחור במסירה", "הבטחת השקעות"],
    "חוק החוזים": ["כריתת חוזה", "פגמים בחוזה", "תרופות בשל הפרה", "ביטול והשבה"],
    "חוק התכנון והבנייה": ["היתרי בנייה", "היטל השבחה", "תוכניות מתאר", "שימוש חורג"],
    "חוק מיסוי מקרקעין": ["מס שבח", "מס רכישה", "פטורים והקלות", "שווי שוק"],
    "חוק הגנת הצרכן": ["ביטול עסקה", "הטעיה בפרסום"],
    "דיני ירושה": ["צוואות וירושות"],
    "חוק העונשין": ["עבירות מרמה"]
}

def ask_ai(p, is_lesson=True):
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        m = genai.GenerativeModel('gemini-2.0-flash')
        # הוראה ברורה לניקוי קשקושים בכותרות
        suffix = " תן רק את תוכן השיעור ללא כותרות פתיחה." if is_lesson else ""
        r = m.generate_content(p + suffix)
        return r.text if r else None
    except: return None

def fetch_q(topic):
    # בקשה ממוקדת ל-JSON כדי להאיץ את התגובה
    p = f"שאלה אמריקאית על {topic}. JSON: {{'q':'','options':['','','',''],'correct':'','explain':''}}"
    res = ask_ai(p, is_lesson=False)
    try:
        match = re.search(r'\{.*\}', res, re.DOTALL)
        return json.loads(match.group()) if match else None
    except: return None

# אתחול Session State
if "user" not in st.session_state: st.session_state.user = None
if "step" not in st.session_state: st.session_state.step = "login"
if "q_count" not in st.session_state: st.session_state.q_count = 0

st.title("🏠 מתווך בקליק")

# --- שלבי האפליקציה ---
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
    if st.button("⏱️ גש/י למבחן"):
        st.info("סימולציית מבחן מלאה - בקרוב")

elif st.session_state.step == "study":
    st.write(f"👤 משתמש: {st.session_state.user}")
    sel = st.selectbox("בחר נושא:", list(SYLLABUS.keys()))
    if st.button("טען נושא"):
        st.session_state.update({"selected_topic": sel, "step": "lesson_run", 
                                 "quiz_active": False, "lesson_txt": "", "q_count": 0})
        st.rerun()

elif st.session_state.step == "lesson_run":
    topic = st.session_state.selected_topic
    st.write(f"👤 תלמיד: {st.session_state.user}")
    
    subs = SYLLABUS.get(topic, [])
    t_cols = st.columns(len(subs))
    for i, s in enumerate(subs):
        if t_cols[i].button(s, key=f"s_{i}"):
            st.session_state.current_sub = s
            with st.spinner(f"טוען..."):
                st.session_state.lesson_txt = ask_ai(f"כתוב שיעור מפורט על {s} בחוק {topic}")
            st.rerun()
            
    if st.session_state.get("lesson_txt"):
        st.header(st.session_state.get("current_sub", ""))
        st.markdown(st.session_state.lesson_txt)

    # --- חלק השאלון ---
    if st.session_state.get("quiz_active"):
        st.divider()
        st.subheader(f"📝 שאלון: {topic}")
        st.write(f"**שאלה מספר: {st.session_state.q_count}**")
        
        q = st.session_state.get("q_data")
        if q:
            ans = st.radio(q['q'], q['options'], index=None)
            if st.button("בדוק תשובה"):
                if ans == q['correct']: st.success("נכון!")
                else: st.error(f"טעות. התשובה היא: {q['correct']}")
                st.info(f"הסבר: {q['explain']}")
        
        if st.button("שאלה הבאה ➡️"):
            st.session_state.q_count += 1
            st.session_state.q_data = fetch_q(topic)
            st.rerun()

    # --- תפריט תחתון ---
    st.write("---")
    b_cols = st.columns([2.5, 1.5, 1.5, 4])
    with b_cols[0]:
        if not st.session_state.get("quiz_active"):
            if st.button(f"📝 שאלון: {topic}"):
                st.session_state.update({"quiz_active": True, "q_count": 1, 
                                         "q_data": fetch_q(topic)})
                st.rerun()
    with b_cols[1]:
        if st.button("🏠 תפריט"):
            st.session_state.step = "menu"
            st.rerun()
    with b_cols[2]:
        st.markdown('<a href="#top" class="top-btn">🔝 למעלה</a>', unsafe_allow_html=True)
