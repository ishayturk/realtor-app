# Project: מתווך בקליק | Version: 1213-Final-Restored | File: app.py
import streamlit as st
import google.generativeai as genai
import json
import re
import streamlit.components.v1 as components

# הגדרת דף
st.set_page_config(page_title="מתווך בקליק", layout="wide")

# בדיקת ניווט דרך URL
if st.query_params.get("nav") == "menu":
    st.query_params.clear()
    st.session_state.step = "menu"
    st.rerun()

# --- CSS בסיסי (חל על כל האפליקציה) ---
st.markdown("""
<style>
    * { direction: rtl; }
    header { visibility: hidden; }
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# סילבוס מלא
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

# --- פונקציות עזר ---
def reset_quiz_state():
    st.session_state.update({
        "quiz_active": False, "q_data": None, "q_count": 0,
        "checked": False, "quiz_finished": False, "correct_answers": 0
    })
    for key in list(st.session_state.keys()):
        if key.startswith("sc_"): del st.session_state[key]

def fetch_q_ai(topic):
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-2.0-flash')
        json_fmt = "{'q': '','options': ['','','',''], 'correct': '', 'explain': ''}"
        prompt = f"צור שאלה אמריקאית קשה על {topic} למבחן המתווכים. החזר אך ורק בפורמט JSON: {json_fmt}"
        response = model.generate_content(prompt)
        match = re.search(r'\{.*\}', response.text, re.DOTALL)
        return json.loads(match.group()) if match else None
    except: return None

def stream_ai_lesson(prompt_text):
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content(f"{prompt_text}. כתוב שיעור מעמיק.", stream=True)
        placeholder = st.empty()
        full_text = ""
        for chunk in response:
            full_text += chunk.text
            placeholder.markdown(full_text + "▌")
        placeholder.markdown(full_text)
        return full_text
    except: return "⚠️ תקלה בטעינה."

# --- ניהול מצב ---
if "step" not in st.session_state:
    st.session_state.update({
        "user": None, "step": "login", "lesson_txt": "", 
        "selected_topic": None, "current_sub": None,
        "quiz_active": False, "quiz_finished": False,
        "checked": False, "correct_answers": 0, "q_count": 0, "q_data": None
    })

def show_header():
    if st.session_state.user:
        st.markdown(f"""
            <div style="display:flex; align-items:center; gap:45px; margin-bottom:30px; max-width:1200px; margin-right:auto; margin-left:auto;">
                <div style="font-size:2.5rem; font-weight:bold;">🏠 מתווך בקליק</div>
                <div style="font-size:1.2rem; font-weight:900;">👤 <b>{st.session_state.user}</b></div>
            </div>
        """, unsafe_allow_html=True)

# --- ניתוב דפים ---

if st.session_state.step == "login":
    # מירכוז מסך כניסה
    _, col, _ = st.columns([1, 2, 1])
    with col:
        st.title("🏠 מתווך בקליק")
        u_in = st.text_input("שם מלא:")
        if st.button("כניסה") and u_in:
            st.session_state.user = u_in
            st.session_state.step = "menu"
            st.rerun()

elif st.session_state.step == "menu":
    show_header()
    _, col, _ = st.columns([1, 4, 1])
    with col:
        c1, c2 = st.columns(2)
        if c1.button("📚 לימוד לפי נושאים"):
            st.session_state.step = "study"
            st.rerun()
        if c2.button("⏱️ גש/י למבחן"):
            st.session_state.step = "exam_frame"
            st.rerun()

elif st.session_state.step == "exam_frame":
    # CSS ייעודי למבחן בלבד - ביטול Padding ואיפוס שוליים
    st.markdown("""
        <style>
            .main .block-container {
                padding: 0 !important;
                max-width: 100% !important;
            }
            .exam-strip-fixed {
                width: 100%;
                display: flex;
                justify-content: center;
                margin-top: 15px;
                margin-bottom: 5px;
            }
            .exam-strip-inner {
                width: 100%;
                max-width: 1200px;
                display: flex;
                justify-content: space-between;
                align-items: center;
                height: 30px;
                padding: 0 20px;
            }
        </style>
    """, unsafe_allow_html=True)
    
    # סטריפ דק וממורכז
    st.markdown(f"""
        <div class="exam-strip-fixed">
            <div class="exam-strip-inner">
                <div style="font-weight:bold; flex:1; text-align:right;">🏠 מתווך בקליק</div>
                <div style="font-weight:bold; flex:1; text-align:center;">👤 {st.session_state.user}</div>
                <div style="flex:1; text-align:left;">
                    <a href="/?nav=menu" target="_self" style="color:black; text-decoration:none; font-weight:bold;">לתפריט הראשי</a>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    exam_url = "https://fullrealestatebroker-yevuzewxde4obgrpgacrpc.streamlit.app/?embed=true"
    components.iframe(exam_url, height=1200, scrolling=True)

elif st.session_state.step == "study":
    show_header()
    _, col, _ = st.columns([1, 3, 1])
    with col:
        sel = st.selectbox("בחר נושא לימוד:", ["בחר..."] + list(SYLLABUS.keys()))
        ca, cb = st.columns(2)
        if ca.button("טען נושא") and sel != "בחר...":
            reset_quiz_state()
            st.session_state.update({"selected_topic": sel, "step": "lesson_run", "lesson_txt": "", "current_sub": None})
            st.rerun()
        if cb.button("חזרה לתפריט"):
            st.session_state.step = "menu"
            st.rerun()

elif st.session_state.step == "lesson_run":
    show_header()
    st.header(f"📖 {st.session_state.selected_topic}")
    subs = SYLLABUS.get(st.session_state.selected_topic, [])
    cols = st.columns(len(subs))
    for i, s in enumerate(subs):
        if cols[i].button(s, key=f"s_{i}"):
            reset_quiz_state()
            st.session_state.update({"current_sub": s, "lesson_txt": "LOADING"})
            st.rerun()
    
    if st.session_state.lesson_txt == "LOADING":
        st.session_state.lesson_txt = stream_ai_lesson(f"הסבר על {st.session_state.current_sub}")
        st.rerun()
    elif st.session_state.lesson_txt:
        st.markdown(st.session_state.lesson_txt)
        
        # לוגיקת שאלון (מקוצרת לצורך הדוגמה)
        if st.button("📝 שאלון תרגול (שאלה אחת)"):
            with st.spinner("מייצר..."):
                st.session_state.q_data = fetch_q_ai(st.session_state.current_sub)
                st.session_state.quiz_active = True
                st.rerun()
        
        if st.session_state.quiz_active and st.session_state.q_data:
            q = st.session_state.q_data
            ans = st.radio(q['q'], q['options'], index=None)
            if st.button("בדוק תשובה") and ans:
                if ans == q['correct']: st.success("נכון!")
                else: st.error(f"טעות. הנכון: {q['correct']}")
                st.info(q['explain'])

    if st.button("חזרה לבחירת נושא"):
        st.session_state.step = "study"
        st.rerun()

# --- סוף קובץ ---
