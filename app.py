# ==========================================
# Project: מתווך בקליק | Version: 1213-Full-Fix
# ==========================================
import streamlit as st
import streamlit.components.v1 as components
import google.generativeai as genai
import json, re

st.set_page_config(page_title="מתווך בקליק", layout="wide")

st.markdown("""
<style>
    * { direction: rtl; text-align: right; }
    .stApp header { visibility: hidden; }
    .block-container { padding-top: 2rem !important; }
    .exam-strip {
        background-color: #f0f2f6;
        padding: 10px 20px;
        border-radius: 10px;
        margin-bottom: 10px;
    }
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; height: 3em; }
    .v-footer { text-align: center; color: rgba(255, 255, 255, 0.1); font-size: 0.7em; margin-top: 50px; }
</style>
""", unsafe_allow_html=True)

SYLLABUS = {
    "חוק המתווכים": ["רישוי והגבלות", "הגינות וזהירות", "הזמנה ובלעדיות", "פעולות שאינן תיווך"],
    "תקנות המתווכים": ["פרטי הזמנה 1997", "פעולות שיווק 2004", "דמי תיווך"],
    "חוק המקרקעין": ["בעלות וזכויות", "בתים משותפים", "עסקאות נוגדות", "הערות אזהרה", "שכירות וזיקה"],
    "חוק המכר (דירות)": ["מפרט וגילוי", "בדק ואחריות", "איחור במסירה", "הבטחת השקעות"],
    "חוק החוזים": ["כריתת חוזה", "פגמים בחוזה", "תרופות והפרה", "ביטול והשבה"],
    "חוק התכנון והבנייה": ["היתרים ושימוש חורג", "היטל השבחה", "תוכניות מתאר", "מוסדות התכנון"],
    "חוק מיסוי מקרקעין": ["מס שבח (חישוב ופפורים)", "מס רכישה", "הקלות לדירת מגורים", "שווי שוק"],
    "חוק הגנת הצרכן": ["ביטול עסקה", "הטעיה בפרסום"],
    "דיני ירושה": ["סדר הירושה", "צוואות"],
    "חוק העונשין": ["עבירות מרמה וזיוף"]
}

# --- פונקציות עזר (AI) ---
def fetch_q_ai(topic):
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        m = genai.GenerativeModel('gemini-2.0-flash')
        p = f"צור שאלה אמריקאית על {topic}. החזר JSON תקני בלבד."
        res = m.generate_content(p).text
        match = re.search(r'\{.*\}', res, re.DOTALL)
        if match: return json.loads(match.group())
    except: return None

def stream_ai_lesson(p):
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        m = genai.GenerativeModel('gemini-2.0-flash')
        response = m.generate_content(p + " ללא כותרות.", stream=True)
        ph = st.empty()
        txt = ""
        for chunk in response:
            txt += chunk.text
            ph.markdown(txt + "▌")
        ph.markdown(txt)
        return txt
    except: return "⚠️ תקלה בטעינה."

# אתחול
if "step" not in st.session_state:
    st.session_state.update({
        "user": None, "step": "login", "q_count": 0, "quiz_active": False, 
        "show_ans": False, "lesson_txt": "", "q_data": None, 
        "correct_answers": 0, "quiz_finished": False
    })

# --- ניהול דפים ---

if st.session_state.step == "login":
    st.title("🏠 מתווך בקליק")
    u = st.text_input("שם מלא:")
    if st.button("כניסה") and u:
        st.session_state.update({"user": u, "step": "menu"})
        st.rerun()

# מרגע זה המשתמש מחובר - הכותרת ושם המשתמש מופיעים כחלק מהמבנה הרגיל (למעט במבחן)
elif st.session_state.step != "exam_mode":
    st.title("🏠 מתווך בקליק")
    st.subheader(f"👤 שלום, {st.session_state.user}")

    if st.session_state.step == "menu":
        c1, c2 = st.columns(2)
        with c1:
            if st.button("📚 לימוד לפי נושאים"):
                st.session_state.step = "study"; st.rerun()
        with c2:
            if st.button("⏱️ גש/י למבחן"):
                st.session_state.step = "exam_mode"; st.rerun()

    elif st.session_state.step == "study":
        sel = st.selectbox("בחר נושא:", ["בחר..."] + list(SYLLABUS.keys()))
        if sel != "בחר..." and st.button("טען נושא"):
            st.session_state.update({
                "selected_topic": sel, "step": "lesson_run", "lesson_txt": "",
                "quiz_active": False, "q_count": 0, "quiz_finished": False
            })
            st.rerun()
        if st.button("🏠 חזרה לתפריט"):
            st.session_state.step = "menu"; st.rerun()

    elif st.session_state.step == "lesson_run":
        topic = st.session_state.selected_topic
        st.header(f"📖 {topic}")
        subs = SYLLABUS.get(topic, [])
        cols = st.columns(len(subs))
        for i, s in enumerate(subs):
            if cols[i].button(s, key=f"sub_{i}"):
                st.session_state.update({
                    "current_sub": s, "lesson_txt": "LOADING", "quiz_active": False
                })
                st.rerun()
        
        if st.session_state.get("lesson_txt") == "LOADING":
            st.session_state.lesson_txt = stream_ai_lesson(f"שיעור על {st.session_state.current_sub}")
            st.rerun()
        elif st.session_state.get("lesson_txt"):
            st.markdown(st.session_state.lesson_txt)
        
        if st.button("🏠 חזרה לבחירת נושא"):
            st.session_state.step = "study"; st.rerun()

# --- מצב מבחן (המבנה המיוחד של שני הפריימים) ---
elif st.session_state.step == "exam_mode":
    st.markdown('<div class="exam-strip">', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([2, 2, 1])
    with c1: st.markdown("### 🏠 מתווך בקליק")
    with c2: st.markdown(f"<center><h3>👤 {st.session_state.user}</h3></center>", unsafe_allow_html=True)
    with c3:
        if st.button("↩️ לתפריט הראשי"):
            st.session_state.step = "menu"; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    exam_url = "https://fullrealestatebroker-yevuzewxde4obgrpgacrpc.streamlit.app/?embedded=true"
    components.iframe(exam_url, height=850, scrolling=True)

st.markdown('<div class="v-footer">Version: 1213-Full-Fixed</div>', unsafe_allow_html=True)
