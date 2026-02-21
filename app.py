# Project: מתווך בקליק | Version: 1218-G6-Final-Full | File: app.py
# Anchor: 1218-G6 | Complete logic: Study + AI Lesson + Exam Frame
import streamlit as st
import google.generativeai as genai
import json
import re

# הגדרת דף
st.set_page_config(page_title="מתווך בקליק", layout="wide", initial_sidebar_state="collapsed")

# --- CSS CORE (עוגן 1213) ---
st.markdown("""
<style>
    * { direction: rtl; text-align: right; }
    .header-container { display: flex; align-items: center; gap: 45px; margin-bottom: 30px; }
    .header-title { font-size: 2.5rem !important; font-weight: bold !important; margin: 0 !important; }
    .header-user { font-size: 1.2rem !important; font-weight: 900 !important; color: #31333f; }
    .stButton>button { width: 100% !important; border-radius: 8px !important; font-weight: bold !important; height: 3em !important; }
</style>
""", unsafe_allow_html=True)

SYLLABUS = {
    "חוק המתווכים": ["רישוי והגבלות", "הגינות וזהירות", "הזמנה ובלעדיות", "פעולות שאינן תיווך"],
    "תקנות המתווכים": ["פרטי הזמנה 1997", "פעולות שיווק 2004", "דמי תיווך"],
    "חוק המקרקעין": ["בעלות וזכויות", "בתים משותפים", "עסקאות נוגדות", "הערות אזהרה", "שכירות וזיקה"],
    "חוק המכר (דירות)": ["מפרט וגילוי", "בדק ואחריות", "איחור במסירה", "הבטחת השקעות"],
    "חוק החוזים": ["כריתת חוזה", "פגמים בחוזה", "תרופות והפרה", "ביטול והשבה"],
    "חוק התכנון והבנייה": ["היתרים ושימוש חורג", "היטל השבחה", "תוכניות מתאר", "מוסדות התכנון"],
    "חוק מיסוי מקרקעין": ["מס שבח (חישוב ופטורים)", "מס רכישה", "הקלות לדירת מגורים", "שווי שוק"],
    "חוק הגנת הצרכן": ["ביטול עסקה", "הטעיה בפרסום"],
    "דיני ירושה": ["סדר הירושה", "צוואות"],
    "חוק העונשין": ["עבירות מרמה וזיוף"]
}

# --- לוגיקת AI (עוגן 1213) ---
def stream_ai_lesson(prompt_text):
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content(f"כתוב שיעור הכנה מעמיק למבחן המתווכים על: {prompt_text}", stream=True)
        placeholder = st.empty()
        full_text = ""
        for chunk in response:
            full_text += chunk.text
            placeholder.markdown(full_text + "▌")
        placeholder.markdown(full_text)
        return full_text
    except:
        return "⚠️ תקלה בטעינת השיעור. וודא ש-API KEY מוגדר."

if "step" not in st.session_state:
    st.session_state.update({"user": None, "step": "login", "selected_topic": None, "current_sub": None, "lesson_txt": ""})

def show_header():
    if st.session_state.user:
        st.markdown(f'<div class="header-container"><div class="header-title">🏠 מתווך בקליק</div><div class="header-user">👤 <b>{st.session_state.user}</b></div></div>', unsafe_allow_html=True)

# --- ניתוב ---

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
    # סטריפ עליון במבחן
    col_back, col_user, col_logo = st.columns([1, 2, 1])
    with col_back:
        if st.button("← חזרה"):
            st.session_state.step = "menu"
            st.rerun()
    with col_user:
        st.markdown(f"<p style='text-align:center; font-weight:bold; padding-top:10px;'>{st.session_state.user}</p>", unsafe_allow_html=True)
    with col_logo:
        st.markdown("<p style='text-align:right; font-weight:bold; padding-top:10px;'>🏠 מתווך בקליק</p>", unsafe_allow_html=True)
    
    st.markdown("<style>header { visibility: hidden !important; } .block-container { padding-top: 0 !important; }</style>", unsafe_allow_html=True)
    exam_url = f"https://fullrealestatebroker-yevuzewxde4obgrpgacrpc.streamlit.app/?user={st.session_state.user}&embed=true"
    st.markdown(f'<iframe src="{exam_url}" style="width:100%; height:92vh; border:none;"></iframe>', unsafe_allow_html=True)

elif st.session_state.step == "study":
    show_header()
    sel = st.selectbox("בחר נושא לימוד:", ["בחר..."] + list(SYLLABUS.keys()))
    if st.button("טען נושא") and sel != "בחר...":
        st.session_state.update({"selected_topic": sel, "step": "lesson_run", "lesson_txt": "", "current_sub": None})
        st.rerun()
    if st.button("🏠 חזרה"):
        st.session_state.step = "menu"
        st.rerun()

elif st.session_state.step == "lesson_run":
    show_header()
    st.header(f"📖 {st.session_state.selected_topic}")
    
    # עימוד תתי-נושאים מקורי (Columns)
    subs = SYLLABUS.get(st.session_state.selected_topic, [])
    cols = st.columns(len(subs))
    for i, s in enumerate(subs):
        if cols[i].button(s, key=f"s_{i}"):
            st.session_state.update({"current_sub": s, "lesson_txt": "LOADING"})
            st.rerun()
    
    if st.session_state.current_sub:
        st.divider()
        st.subheader(f"נושא: {st.session_state.current_sub}")
        if st.session_state.lesson_txt == "LOADING":
            st.session_state.lesson_txt = stream_ai_lesson(st.session_state.current_sub)
            st.rerun()
        else:
            st.markdown(st.session_state.lesson_txt)

    if st.button("🏠 לתפריט הראשי"):
        st.session_state.step = "menu"
        st.rerun()

# --- End of File ---
# Version: 1218-G6-Final | Date: 2026-02-21
