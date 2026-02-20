# ==========================================
# Project: מתווך בקליק | Version: 1213-Exam
# ==========================================
import streamlit as st
import streamlit.components.v1 as components
import google.generativeai as genai
import json, re

st.set_page_config(page_title="מתווך בקליק", layout="wide")
st.markdown('<div id="top"></div>', unsafe_allow_html=True)

# CSS לשמירה על המבנה המקורי + הסטריפ בתוך האפליקציה הראשית
st.markdown("""
<style>
    * { direction: rtl; text-align: right; }
    .stApp header { visibility: hidden; }
    .stButton>button { 
        width: 100%; border-radius: 8px; 
        font-weight: bold; height: 3em; 
    }
    .slim-strip {
        display: flex; justify-content: space-between;
        align-items: center; padding: 5px 20px;
        background-color: white; border-bottom: none;
    }
    .top-link { 
        display: inline-block; width: 100%; text-align: center; 
        border-radius: 8px; text-decoration: none; border: 1px solid #d1d5db;
        font-weight: bold; height: 2.8em; line-height: 2.8em;
        background-color: transparent; color: inherit;
    }
    .v-footer {
        text-align: center; color: rgba(255, 255, 255, 0.1);
        font-size: 0.7em; margin-top: 50px; width: 100%;
    }
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

def fetch_q_ai(topic):
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        m = genai.GenerativeModel('gemini-2.0-flash')
        p = f"צור שאלה אמריקאית קשה על {topic} למבחן המתווכים. החזר אך ורק JSON תקני."
        res = m.generate_content(p).text
        match = re.search(r'\{.*\}', res, re.DOTALL)
        if match: return json.loads(match.group())
    except: return None

def stream_ai_lesson(p):
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        m = genai.GenerativeModel('gemini-2.0-flash')
        full_p = p + " כתוב שיעור הכנה מעמיק. ללא כותרות."
        response = m.generate_content(full_p, stream=True)
        placeholder = st.empty()
        full_text = ""
        for chunk in response:
            full_text += chunk.text
            placeholder.markdown(full_text + "▌")
        placeholder.markdown(full_text)
        return full_text
    except: return "⚠️ תקלה בטעינה."

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

elif st.session_state.step == "menu":
    st.title("🏠 מתווך בקליק")
    st.subheader(f"👤 שלום, {st.session_state.user}")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("📚 לימוד לפי נושאים"):
            st.session_state.step = "study"; st.rerun()
    with c2:
        if st.button("⏱️ גש/י למבחן"):
            st.session_state.step = "exam_mode"; st.rerun()

elif st.session_state.step == "exam_mode":
    # הסטריפ העליון בתוך האפליקציה הראשית
    st.markdown('<div class="slim-strip">', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 1])
    with c1: st.markdown("**מתווך בקליק**")
    with c2: st.markdown(f"<center>👤 {st.session_state.user}</center>", 
                         unsafe_allow_html=True)
    with c3:
        if st.button("↩️ לתפריט הראשי"):
            st.session_state.step = "menu"; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # הפריים התחתון שמושך את האפליקציה השנייה
    exam_url = "https://ishayturk-realtor-app-app-kk1gme.streamlit.app/?embedded=true"
    components.iframe(exam_url, height=1000, scrolling=True)

elif st.session_state.step == "study":
    # לוגיקת לימוד מקורית ללא שינוי
    st.title("📚 בחירת נושא")
    sel = st.selectbox("בחר נושא:", ["בחר..."] + list(SYLLABUS.keys()))
    if sel != "בחר..." and st.button("טען נושא"):
        st.session_state.update({
            "selected_topic": sel, "step": "lesson_run", "quiz_active": False, 
            "lesson_txt": "", "q_data": None, "q_count": 0, 
            "correct_answers": 0, "quiz_finished": False
        })
        st.rerun()

elif st.session_state.step == "lesson_run":
    # כאן נכנס כל המשך הקוד המקורי של 1213 (Subs, Lessons, Quizzes)
    topic = st.session_state.selected_topic
    st.header(f"📖 {topic}")
    
    # ... שאר לוגיקת ה-lesson_run כפי שהופיעה במקור ...
    if st.button("🏠 חזרה לתפריט"):
        st.session_state.step = "menu"; st.rerun()

st.markdown(f'<div class="v-footer">Version: 1213-Exam-Ready</div>', 
            unsafe_allow_html=True)
