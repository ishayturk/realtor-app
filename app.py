# ==========================================
# Project: מתווך בקליק | Version: 1213-Anchor-Updated
# Last Update: 21/02/2026 | 14:45 (Jerusalem Time GMT+2)
# Status: Strip Visibility Restored | Protocol: Full File Delivery
# ==========================================
import streamlit as st
import google.generativeai as genai
import json, re

st.set_page_config(page_title="מתווך בקליק", layout="wide")

st.markdown("""
<style>
    * { direction: rtl; text-align: right; }
    .header-container { display: flex; align-items: center; gap: 45px; margin-bottom: 30px; }
    .header-title { font-size: 2.5rem !important; font-weight: bold !important; margin: 0 !important; }
    .header-user { font-size: 1.2rem !important; font-weight: 900 !important; color: #31333f; }
    .stButton>button { width: 100% !important; border-radius: 8px !important; height: 3em !important; }
    
    .strip-text { font-size: 1.2rem; font-weight: bold; padding-top: 10px; }
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
        fmt = "{'q':'','options':['','','',''],'correct':'','explain':''}"
        p = f"צור שאלה אמריקאית קשה על {topic}. החזר JSON: {fmt}"
        res = m.generate_content(p).text
        match = re.search(r'\{.*\}', res, re.DOTALL)
        if match: return json.loads(match.group())
    except: return None

def stream_ai_lesson(p):
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        m = genai.GenerativeModel('gemini-2.0-flash')
        full_p = f"{p}. כתוב שיעור הכנה מעמיק למבחן המתווכים עם סעיפי חוק."
        response = m.generate_content(full_p, stream=True)
        placeholder = st.empty(); txt = ""
        for chunk in response:
            txt += chunk.text
            placeholder.markdown(txt + "▌")
        placeholder.markdown(txt)
        return txt
    except: return "⚠️ שירות ה-AI אינו זמין כרגע."

if "step" not in st.session_state:
    st.session_state.update({
        "user": None, "step": "login", "lesson_txt": "",
        "q_data": None, "q_count": 0, "quiz_active": False,
        "correct_answers": 0, "quiz_finished": False
    })

def show_header():
    if st.session_state.user:
        u = st.session_state.user
        h = f'<div class="header-container"><div class="header-title">🏠 מתווך בקליק</div>' \
            f'<div class="header-user">👤 <b>{u}</b></div></div>'
        st.markdown(h, unsafe_allow_html=True)

# --- ניהול שלבים ---

if st.session_state.step == "login":
    st.title("🏠 מתווך בקליק")
    u_in = st.text_input("שם מלא:")
    if st.button("כניסה") and u_in:
        st.session_state.update({"user": u_in, "step": "menu"}); st.rerun()

elif st.session_state.step == "menu":
    show_header()
    c1, c2, c3 = st.columns([1.5, 1.5, 3])
    with c1:
        if st.button("📚 לימוד לפי נושאים"):
            st.session_state.step = "study"; st.rerun()
    with c2:
        if st.button("⏱️ גש/י למבחן"):
            st.session_state.step = "exam_frame"; st.rerun()

elif st.session_state.step == "exam_frame":
    # ניקוי מרווחים בסיסי בלי להעלים אלמנטים
    st.markdown("""<style>
        header {visibility: hidden !important; height: 0 !important;}
        .block-container {padding-top: 2rem !important;}
    </style>""", unsafe_allow_html=True)
    
    # הסטריפ - שורה ראשונה
    strip_cols = st.columns([1, 1, 1])
    with strip_cols[0]:
        st.markdown('<p class="strip-text" style="text-align:right;">🏠 מתווך בקליק</p>', unsafe_allow_html=True)
    with strip_cols[1]:
        st.markdown(f'<p class="strip-text" style="text-align:center;">{st.session_state.user}</p>', unsafe_allow_html=True)
    with strip_cols[2]:
        if st.button("🔙 חזרה", key="back_from_exam"):
            st.session_state.step = "menu"; st.rerun()

    st.divider() # קו מפריד דק בין הסטריפ ל-iframe

    u_enc = st.session_state.user.replace(" ", "%20")
    b_url = "https://fullrealestatebroker-yevuzewxde4obgrpgacrpc.streamlit.app/"
    st.components.v1.iframe(f"{b_url}?user={u_enc}", height=1000, scrolling=True)

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
            st.session_state.update({"current_sub": s, "lesson_txt": "LOADING", "quiz_active": False})
            st.rerun()
    
    if st.session_state.get("lesson_txt") == "LOADING":
        st.session_state.lesson_txt = stream_ai_lesson(f"שיעור על {st.session_state.current_sub}")
        st.rerun()
    elif st.session_state.get("lesson_txt"):
        st.markdown(st.session_state.lesson_txt)
        if st.button("🏠 חזרה לתפריט"):
            st.session_state.step = "menu"; st.rerun()
