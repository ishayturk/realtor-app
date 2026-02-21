# Project: מתווך בקליק | Version: 1213-Ultra-Slim-Strip | File: app.py
import streamlit as st
import google.generativeai as genai
import json
import re
import streamlit.components.v1 as components

# הגדרת דף
st.set_page_config(page_title="מתווך בקליק", layout="wide")

# עיצוב RTL בסיסי
st.markdown("""
<style>
    * { direction: rtl; text-align: right; }
    .header-container { 
        display: flex; 
        align-items: center; 
        gap: 45px; 
        margin-bottom: 30px; 
    }
    .header-title { 
        font-size: 2.5rem !important; 
        font-weight: bold !important; 
        margin: 0 !important; 
    }
    .header-user { 
        font-size: 1.2rem !important; 
        font-weight: 900 !important; 
        color: #31333f; 
    }
    .stButton>button { 
        width: 100% !important; 
        border-radius: 8px !important; 
        font-weight: bold !important; 
        height: 3em !important; 
    }
    
    /* סטריפ דק מאוד (עובי 2 שורות גג) */
    .ultra-slim-strip {
        max-width: 1200px;
        margin: 1rem auto 0 auto; /* שורה אחת מהלמעלה */
        height: 40px; /* גובה מינימלי */
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: None; /* ללא קו מפריד לפי הבקשה */
        padding: 0 10px;
    }
</style>
""", unsafe_allow_html=True)

# סילבוס
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

# פונקציות
def reset_quiz_state():
    st.session_state.update({
        "quiz_active": False, "q_data": None, "q_count": 0,
        "checked": False, "quiz_finished": False, "correct_answers": 0
    })
    for key in list(st.session_state.keys()):
        if key.startswith("sc_"):
            del st.session_state[key]

def fetch_q_ai(topic):
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-2.0-flash')
        json_fmt = "{'q': '','options': ['','','',''], 'correct': '', 'explain': ''}"
        prompt = (f"צור שאלה אמריקאית אחת קשה על {topic} למבחן המתווכים. "
                  f"החזר אך ורק בפורמט JSON: {json_fmt}")
        response = model.generate_content(prompt)
        match = re.search(r'\{.*\}', response.text, re.DOTALL)
        return json.loads(match.group()) if match else None
    except: return None

def stream_ai_lesson(prompt_text):
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-2.0-flash')
        full_p = f"{prompt_text}. כתוב שיעור הכנה מעמיק למבחן המתווכים."
        response = model.generate_content(full_p, stream=True)
        placeholder = st.empty()
        full_text = ""
        for chunk in response:
            full_text += chunk.text
            placeholder.markdown(full_text + "▌")
        placeholder.markdown(full_text)
        return full_text
    except: return "⚠️ תקלה בטעינה."

# Init State
if "step" not in st.session_state:
    st.session_state.update({
        "user": None, "step": "login", "lesson_txt": "",
        "selected_topic": None, "current_sub": None,
        "quiz_active": False, "quiz_finished": False,
        "checked": False, "correct_answers": 0, "q_count": 0, "q_data": None
    })

def show_header():
    if st.session_state.get("user"):
        st.markdown(f"""<div class="header-container">
            <div class="header-title">🏠 מתווך בקליק</div>
            <div class="header-user">👤 <b>{st.session_state.user}</b></div>
        </div>""", unsafe_allow_html=True)

# --- Routing ---

if st.session_state.step == "login":
    st.title("🏠 מתווך בקליק")
    u_in = st.text_input("שם מלא:")
    if st.button("כניסה") and u_in:
        st.session_state.user = u_in
        st.session_state.step = "menu"
        st.rerun()

elif st.session_state.step == "menu":
    show_header()
    c1, c2, _ = st.columns([1.5, 1.5, 3])
    if c1.button("📚 לימוד לפי נושאים"):
        st.session_state.step = "study"
        st.rerun()
    if c2.button("⏱️ גש/י למבחן"):
        st.session_state.step = "exam_frame"
        st.rerun()

elif st.session_state.step == "exam_frame":
    # CSS לביטול שוליים והסתרת הדר (כדי שהפריים יצמד למעלה)
    st.markdown("""
        <style>
            header {visibility: hidden;}
            .main .block-container {
                padding-top: 0 !important;
                padding-left: 0 !important;
                padding-right: 0 !important;
                max-width: 100% !important;
            }
        </style>
    """, unsafe_allow_html=True)
    
    # בניית הסטריפ הדק
    st.markdown(f"""
        <div class="ultra-slim-strip">
            <div style="font-weight: bold;">🏠 מתווך בקליק</div>
            <div style="font-weight: bold;">👤 {st.session_state.user}</div>
            <div id="back-link"></div>
        </div>
    """, unsafe_allow_html=True)
    
    # כפתור חזרה שמוצמד לסטריפ בצד (שימוש ב-columns מצומצמות מאוד ליישור)
    _, strip_box, _ = st.columns([1, 4, 1])
    with strip_box:
        sc1, sc2, sc3 = st.columns([1, 2, 1])
        with sc3:
            if st.button("לתפריט הראשי", key="exam_back_btn"):
                st.session_state.step = "menu"
                st.rerun()
    
    # Iframe בפריסה מלאה ללא רווח
    exam_url = "https://fullrealestatebroker-yevuzewxde4obgrpgacrpc.streamlit.app/?embed=true"
    components.iframe(exam_url, height=1000, scrolling=True)

elif st.session_state.step == "study":
    show_header()
    sel = st.selectbox("בחר נושא לימוד:", ["בחר..."] + list(SYLLABUS.keys()))
    col_a, col_b = st.columns([1, 1])
    if col_a.button("טען נושא") and sel != "בחר...":
        reset_quiz_state()
        st.session_state.update({"selected_topic": sel, "step": "lesson_run", "lesson_txt": "", "current_sub": None})
        st.rerun()
    if col_b.button("לתפריט הראשי"):
        reset_quiz_state()
        st.session_state.step = "menu"
        st.rerun()

elif st.session_state.step == "lesson_run":
    show_header()
    if not st.session_state.get("selected_topic"):
        st.session_state.step = "study"
        st.rerun()
    st.header(f"📖 {st.session_state.selected_topic}")
    subs = SYLLABUS.get(st.session_state.selected_topic, [])
    cols = st.columns(len(subs))
    for i, s in enumerate(subs):
        if cols[i].button(s, key=f"s_{i}"):
            reset_quiz_state()
            st.session_state.update({"current_sub": s, "lesson_txt": "LOADING"})
            st.rerun()
    if not st.session_state.get("current_sub"):
        st.write("")
        if st.button("לתפריט הראשי", key
