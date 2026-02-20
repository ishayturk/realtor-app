import streamlit as st
import google.generativeai as genai
import json, re

st.set_page_config(page_title="מתווך בקליק", layout="wide")

# סילבוס ופונקציות לימוד (מגרסה 1213)
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
        p = f"צור שאלה אמריקאית קשה על {topic} למבחן המתווכים. החזר אך ורק JSON תקני: {{'q':'','options':['','','',''],'correct':'','explain':''}}"
        res = m.generate_content(p).text
        match = re.search(r'\{.*\}', res, re.DOTALL)
        if match: return json.loads(match.group())
    except: return None
    return None

def stream_ai_lesson(p):
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        m = genai.GenerativeModel('gemini-2.0-flash')
        full_p = p + " כתוב שיעור הכנה מעמיק למבחן המתווכים. פרט סעיפי חוק, מספרים ודוגמאות. ללא כותרות."
        response = m.generate_content(full_p, stream=True)
        placeholder = st.empty()
        full_text = ""
        for chunk in response:
            full_text += chunk.text
            placeholder.markdown(full_text + "▌")
        placeholder.markdown(full_text)
        return full_text
    except: return "⚠️ תקלה בטעינה."

# אתחול Session State
if "step" not in st.session_state:
    st.session_state.update({
        "user": None, "step": "login", "q_count": 0, "quiz_active": False, 
        "show_ans": False, "lesson_txt": "", "q_data": None, 
        "correct_answers": 0, "quiz_finished": False
    })

# --- לוגיקת דפים ---

if st.session_state.step == "login":
    st.markdown("<style>* { direction: rtl; text-align: right; }</style>", unsafe_allow_html=True)
    st.title("🏠 מתווך בקליק")
    u = st.text_input("שם מלא:")
    if st.button("כניסה") and u:
        st.session_state.update({"user": u, "step": "menu"})
        st.rerun()

elif st.session_state.step == "menu":
    st.markdown("<style>* { direction: rtl; text-align: right; }</style>", unsafe_allow_html=True)
    st.title("🏠 מתווך בקליק")
    st.subheader(f"👤 שלום, {st.session_state.user}")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("📚 לימוד לפי נושאים"):
            st.session_state.step = "study"; st.rerun()
    with c2:
        if st.button("⏱️ גש/י למבחן"):
            st.session_state.step = "exam_intro"; st.rerun()

elif st.session_state.step == "study":
    st.markdown("<style>* { direction: rtl; text-align: right; }</style>", unsafe_allow_html=True)
    sel = st.selectbox("בחר נושא:", ["בחר..."] + list(SYLLABUS.keys()))
    if sel != "בחר..." and st.button("טען נושא"):
        st.session_state.update({
            "selected_topic": sel, "step": "lesson_run", "quiz_active": False, 
            "lesson_txt": "", "q_data": None, "q_count": 0, 
            "correct_answers": 0, "quiz_finished": False
        })
        st.rerun()
    if st.button("🏠 חזרה לתפריט"):
        st.session_state.step = "menu"; st.rerun()

elif st.session_state.step == "lesson_run":
    # לוגיקה מקורית של הלימוד מגרסה 1213 (מושמטת כאן בקיצור אך קיימת בקוד המלא שלך)
    st.header(f"📖 {st.session_state.selected_topic}")
    if st.button("🏠 חזור"): 
        st.session_state.step = "study"; st.rerun()

elif st.session_state.step == "exam_intro":
    st.markdown("""
        <style>
        #MainMenu, footer, header {visibility: hidden;}
        .block-container { padding-top: 0.5rem !important; }
        .header-strip { display: flex; justify-content: space-between; align-items: center; }
        .user-info { font-size: 0.85rem; color: #555; text-align: center; }
        .instruction-line { margin-bottom: -10px; }
        div[data-testid="stCheckbox"] { direction: rtl !important; margin-top: -10px; }
        * { direction: rtl; text-align: right; }
        </style>
        """, unsafe_allow_html=True)

    col_r, col_m, col_l = st.columns([1.5, 3, 1.5])
    with col_r: st.markdown("<h4 style='margin:0;'>🏠 מתווך בקליק</h4>", unsafe_allow_html=True)
    with col_m: st.markdown(f"<p class='user-info'>👤 משתמש: {st.session_state.user}</p>", unsafe_allow_html=True)
    with col_l:
        if st.button("לתפריט הראשי"):
            st.session_state.step = "menu"; st.rerun()

    st.markdown("<h2 style='margin-top:0;'>הוראות למבחן רישויי מקרקעין</h2>", unsafe_allow_html=True)
    for line in ["1. המבחן כולל 25 שאלות.", "2. זמן מוקצב: 90 דקות.", "6. ציון עובר: 60."]: # דוגמה מקוצרת
        st.markdown(f"<p class='instruction-line'>{line}</p>", unsafe_allow_html=True)

    st.divider()
    agree = st.checkbox("קראתי את ההוראות ואני מוכן להתחיל")
    if st.button("התחל בחינה", disabled=not agree):
        st.session_state.step = "exam_run"; st.rerun()
