import streamlit as st
import google.generativeai as genai
import json, re

BTN_STUDY = "📚 לימוד לפי נושאים"
BTN_EXAM = "⏱️ גש/י למבחן"
BTN_BACK = "🏠 חזרה"
BTN_MENU = "🏠 חזרה לתפריט"
BTN_QUIZ = "📝 שאלון תרגול"
BTN_CHECK = "✅ בדוק תשובה"
BTN_NEXT = "➡️ שאלה הבאה"
BTN_FINISH = "🏁 סיכום שאלון"

st.set_page_config(page_title="מתווך בקליק", layout="wide")

st.markdown("""
<style>
    * { direction: rtl; text-align: right; }
    .header-container { display: flex; align-items: center; gap: 45px; margin-bottom: 30px; }
    .header-title { font-size: 2.5rem !important; font-weight: bold !important; margin: 0 !important; }
    .header-user { font-size: 1.2rem !important; font-weight: 900 !important; color: #31333f; }
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

for key, val in {
    "step": "login", "user": None, "lesson_txt": "", 
    "quiz_active": False, "ans_checked": False, "q_count": 0,
    "q_data": None, "correct_answers": 0, "quiz_finished": False
}.items():
    if key not in st.session_state:
        st.session_state[key] = val

def fetch_q_ai(topic):
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        m = genai.GenerativeModel('gemini-2.0-flash')
        p = f"שאלה על {topic}. JSON: {{'q':'','options':['','','',''],'correct':'','explain':''}}"
        res = m.generate_content(p).text
        match = re.search(r'\{.*\}', res, re.DOTALL)
        if match: return json.loads(match.group())
    except: return None

def stream_ai_lesson(p):
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        m = genai.GenerativeModel('gemini-2.0-flash')
        full_p = f"{p}. שיעור מעמיק למבחן המתווכים עם סעיפי חוק."
        response = m.generate_content(full_p, stream=True)
        placeholder = st.empty()
        full_text = ""
        for chunk in response:
            full_text += chunk.text
            placeholder.markdown(full_text + "▌")
        placeholder.markdown(full_text)
        return full_text
    except: return "⚠️ תקלה בטעינה"

def show_header():
    if st.session_state.user:
        u = st.session_state.user
        h = f'<div class="header-container"><div class="header-title">🏠 מתווך בקליק</div><div class="header-user">👤 <b>{u}</b></div></div>'
        st.markdown(h, unsafe_allow_html=True)

if st.session_state.step == "login":
    st.title("🏠 מתווך בקליק")
    u_input = st.text_input("שם מלא:")
    if st.button("כניסה") and u_input:
        st.session_state.user = u_input
        st.session_state.step = "menu"
        st.rerun()

elif st.session_state.step == "menu":
    show_header()
    c1, c2, c3 = st.columns([1.5, 1.5, 3])
    if c1.button(BTN_STUDY):
        st.session_state.step = "study"
        st.rerun()
    if c2.button(BTN_EXAM):
        st.session_state.step = "exam_frame"
        st.rerun()

elif st.session_state.step == "exam_frame":
    if st.button(BTN_BACK):
        st.session_state.step = "menu"
        st.rerun()
    u_enc = st.session_state.user.replace(" ", "%20")
    b_url = "https://fullrealestatebroker-yevuzewxde4obgrpgacrpc.streamlit.app/"
    st.components.v1.iframe(f"{b_url}?user={u_enc}", height=900, scrolling=True)

elif st
