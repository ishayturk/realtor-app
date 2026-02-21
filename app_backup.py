import streamlit as st
import google.generativeai as genai
import json, re

# הגדרות תצוגה
st.set_page_config(page_title="מתווך בקליק", layout="wide")

st.markdown("""
<style>
    * { direction: rtl; text-align: right; }
    .header-container { display: flex; align-items: center; gap: 45px; margin-bottom: 30px; }
    .header-title { font-size: 2.5rem !important; font-weight: bold !important; margin: 0 !important; }
    .header-user { font-size: 1.2rem !important; font-weight: 900 !important; color: #31333f; }
    .footer-buttons .stButton>button { width: auto !important; padding: 0 30px !important; }
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
        p = f"צור שאלה אמריקאית קשה על {topic}. החזר JSON: {{'q':'','options':['','','',''],'correct':'','explain':''}}"
        res = m.generate_content(p).text
        match = re.search(r'\{.*\}', res, re.DOTALL)
        if match: return json.loads(match.group())
    except: return None

def stream_ai_lesson(p):
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        m = genai.GenerativeModel('gemini-2.0-flash')
        full_p = f"{p}. כתוב שיעור הכנה מעמיק ומפורט למבחן המתווכים עם סעיפי חוק ודוגמאות."
        response = m.generate_content(full_p, stream=True)
        placeholder = st.empty(); full_text = ""
        for chunk in response:
            full_text += chunk.text
            placeholder.markdown(full_text + "▌")
        placeholder.markdown(full_text)
        return full_text
    except: return "⚠️ תקלה בטעינה."

if "step" not in st.session_state:
    st.session_state.update({
        "user": None, "step": "login", "lesson_txt": "",
        "q_data": None, "q_count": 0, "quiz_active": False,
        "correct_answers": 0, "quiz_finished": False, "ans_checked": False
    })

def show_header():
    if st.session_state.user:
        h_html = f'<div class="header-container"><div class="header-title">🏠 מתווך בקליק</div><div class="header-user">👤 <b>{st.session_state.user}</b></div></div>'
        st.markdown(h_html, unsafe_allow_html=True)

if st.session_state.step == "login":
    st.title("🏠 מתווך בקליק")
    u = st.text_input("שם מלא:")
    if st.button("כניסה") and u:
        st.session_state.update({"user": u, "step": "menu"}); st.rerun()

elif st.session_state.step == "menu":
    show_header()
    c1, c2, c3 = st.columns([1.5, 1.5, 3])
    with c1:
        if st.button("📚 לימוד לפי נושאים"): st.session_state.step = "study"; st.rerun()
    with c2:
        if st.button("⏱️ גש/י למבחן"): st.session_state.step = "exam_frame"; st.rerun()

elif st.session_state.step == "exam_frame":
    c_back, c_name, c_logo = st.columns([1, 1, 6])
    with c_back:
        if st.button("🏠 חזרה"): st.session_state.step = "menu"; st.rerun()
    st.divider()
    u_enc = st.session_state.user.replace(" ", "%20")
    t_url = f"https://fullrealestatebroker-yevuzewxde4obgrpgacrpc.streamlit.app/?user={u_enc}"
    st.components.v1.iframe(t_url, height=900, scrolling=True)

elif st.session_state.step == "study":
    show_header()
    sel = st.selectbox("בחר נושא:", ["בחר..."] + list(SYLLABUS.keys()))
    if sel != "בחר..." and st.button("טען נושא"):
        st.session_state.update({"selected_topic": sel, "step": "lesson_run", "lesson_txt": ""})
        st.rerun()

elif st.session_state.step == "lesson_run":
    show_header()
    st.header(f"📖 {st.session_state.selected_topic}")
    
    subs = SYLLABUS.get(st.session_state.selected_topic, [])
    cols = st.columns(len(subs))
    for i, s in enumerate(subs):
        if cols[i].button(s, key=f"sub_{i}"):
            st.session_state.update({"current_sub": s, "lesson_txt": "LOADING", "quiz_active": False, "q_count": 0, "ans_checked": False})
            st.rerun()

    if st.session_state.get("lesson_txt") == "LOADING":
        st.session_state.lesson_txt = stream_ai_lesson(f"שיעור על {st.session_state.current_sub}")
        st.rerun()
    elif st.session_state.get("lesson_txt"):
        st.markdown(st.session_state.lesson_txt)

    user_choice = None
    if st.session_state.quiz_active and st.session_state.q_data and not st.session_state.quiz_finished:
        st.divider()
        q = st.session_state.q_data
        st.subheader(f"📝 שאלה {st.session_state.q_count} מתוך 10")
        user_choice = st.radio(q['q'], q['options'], index=None, key=f"radio_{st.session_state.q_count}")
