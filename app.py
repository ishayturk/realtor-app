# ==========================================
# Project: מתווך בקליק | Version: 1194 (PART 1)
# ==========================================
import streamlit as st
import google.generativeai as genai
import json, re

st.set_page_config(page_title="מתווך בקליק", layout="wide")
st.markdown('<div id="top"></div>', unsafe_allow_html=True)

st.markdown("""
<style>
    * { direction: rtl; text-align: right; }
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; }
    .top-btn { border: 1px solid #ccc; padding: 10px; border-radius: 8px; text-align: center; 
               text-decoration: none; display: block; color: black; background: #f0f2f6; }
</style>
""", unsafe_allow_html=True)

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
        suffix = " תן רק את תוכן השיעור ללא כותרות פתיחה." if is_lesson else ""
        r = m.generate_content(p + suffix)
        return r.text if r else None
    except: return "⚠️ שגיאה בתקשורת עם השרת."

def fetch_q(topic):
    p = f"שאלה אמריקאית על {topic}. JSON: {{'q':'','options':['','','',''],'correct':'','explain':''}}"
    res = ask_ai(p, is_lesson=False)
    try:
        match = re.search(r'\{.*\}', res, re.DOTALL)
        return json.loads(match.group()) if match else None
    except: return None

if "user" not in st.session_state: st.session_state.user = None
if "step" not in st.session_state: st.session_state.step = "login"
if "q_count" not in st.session_state: st.session_state.q_count = 0
# --- לוגיקה ממשק PART 2 ---
st.title("🏠 מתווך בקליק")

if st.session_state.step == "login":
    u = st.text_input("הזן שם מלא:")
    if st.button("כניסה") and u:
        st.session_state.user, st.session_state.step = u, "menu"
        st.rerun()

elif st.session_state.step == "menu":
    st.subheader(f"👤 שלום, {st.session_state.user}")
    mc1, mc2 = st.columns(2)
    if mc1.button("📚 לימוד לפי נושאים"):
        st.session_state.step = "study"
        st.rerun()
    if mc2.button("⏱️ גש/י למבחן"):
        st.info("סימולציה מלאה בקרוב")

elif st.session_state.step == "study":
    st.write(f"👤 משתמש: {st.session_state.user}")
    s_opts = ["בחר נושא..."] + list(SYLLABUS.keys())
    sel = st.selectbox("בחר נושא לימוד:", s_opts)
    if sel != "בחר נושא..." and st.button("טען נושא"):
        st.session_state.update({"selected_topic": sel, "step": "lesson_run", "quiz_active": False, "lesson_txt": "", "q_count": 0})
        st.rerun()

elif st.session_state.step == "lesson_run":
    topic = st.session_state.selected_topic
    st.header(f"📖 {topic}")
    st.write(f"👤 תלמיד: {st.session_state.user}")
    
    subs = SYLLABUS.get(topic, [])
    t_cols = st.columns(len(subs))
    for i, s in enumerate(subs):
        if t_cols[i].button(s, key=f"sub_btn_{i}"):
            st.session_state.current_sub = s
            with st.spinner("טוען..."):
                st.session_state.lesson_txt = ask_ai(f"שיעור על {s} בחוק {topic}")
            st.rerun()
            
    if st.session_state.get("lesson_txt"):
        st.subheader(st.session_state.get("current_sub", ""))
        st.markdown(st.session_state.lesson_txt)

    if st.session_state.get("quiz_active"):
        st.divider()
        st.subheader(f"📝 שאלון: {topic}")
        st.write(f"**שאלה מספר: {st.session_state.q_count}**")
        q = st.session_state.get("q_data")
        if q:
            ans = st.radio(q['q'], q['options'], index=None, key=f"q_radio_{st.session_state.q_count}")
            if st.button("בדיקת תשובה"):
                if ans == q['correct']: st.success("נכון!")
                else: st.error(f"טעות. הנכון: {q['correct']}")
                st.info(f"הסבר: {q['explain']}")
        
        if st.button("שאלה הבאה ➡️"):
            st.session_state.q_count += 1
            st.session_state.q_data = fetch_q(topic)
            st.rerun()

    st.write("---")
    b_cols = st.columns([2.5, 1.5, 1.5, 4])
    with b_cols[0]:
        if not st.session_state.get("quiz_active"):
            if st.button(f"📝 שאלון: {topic}"):
                st.session_state.update({"quiz_active": True, "q_count": 1, "q_data": fetch_q(topic)})
                st.rerun()
    with b_cols[1]:
        if st.button("🏠 תפריט"):
            st.session_state.step = "menu"
            st.rerun()
    with b_cols[2]:
        st.markdown('<a href="#top" class="top-btn">🔝 למעלה</a>', unsafe_allow_html=True)
