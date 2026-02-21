# Project: מתווך בקליק | Version: training_full_V10 | 21/02/2026 | 21:58
import streamlit as st
import google.generativeai as genai
import json
import re

# הגדרת דף
st.set_page_config(page_title="מתווך בקליק", layout="wide")

# עיצוב RTL בסיסי - עוגן 1213
st.markdown("""
<style>
    * { direction: rtl; text-align: right; }
    .header-container { display: flex; align-items: center; gap: 45px; margin-bottom: 30px; }
    .header-title { font-size: 2.5rem !important; font-weight: bold !important; margin: 0 !important; }
    .header-user { font-size: 1.2rem !important; font-weight: 900 !important; color: #31333f; }
    
    /* כפתורים כלליים בתפריט הראשי */
    .main-btn button { width: 100% !important; border-radius: 8px !important; font-weight: bold !important; height: 3em !important; }
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
    "חוק מיסוי מקרקעין": ["מס שבח (חישוב ופטורים)", "מס רכישה", "הקלות לדירת מגורים", "שווי שוק"],
    "חוק הגנת הצרכן": ["ביטול עסקה", "הטעיה בפרסום"],
    "דיני ירושה": ["סדר הירושה", "צוואות"],
    "חוק העונשין": ["עבירות מרמה וזיוף"]
}

# פונקציות AI (עוגן V01)
def stream_ai_lesson(prompt_text):
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content(prompt_text, stream=True)
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
    st.session_state.update({"user": None, "step": "login", "lesson_txt": "", "selected_topic": None, "current_sub": None})

def show_header():
    if st.session_state.get("user"):
        st.markdown(f"""<div class="header-container"><div class="header-title">🏠 מתווך בקליק</div><div class="header-user">👤 <b>{st.session_state.user}</b></div></div>""", unsafe_allow_html=True)

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
    st.markdown('<div class="main-btn">', unsafe_allow_html=True)
    c1, c2, _ = st.columns([1.5, 1.5, 3])
    if c1.button("📚 לימוד לפי נושאים"):
        st.session_state.step = "study"
        st.rerun()
    if c2.button("⏱️ גש/י למבחן"):
        st.session_state.step = "exam_frame"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.step == "exam_frame":
    st.markdown("""
    <style>
        header { visibility: hidden !important; }
        .main .block-container { padding: 0 !important; }
        div.stButton > button:first-child[key="zero_btn"] {
            position: fixed; top: 0; left: 0; z-index: 999999;
            width: auto !important; height: auto !important;
            padding: 2px 12px !important; background-color: #f8f9fb !important;
            border: 1px solid #d1d4d9 !important; border-top: none !important;
            border-left: none !important; border-radius: 0 0 5px 0 !important;
            font-size: 12px !important; color: #555 !important;
        }
    </style>
    """, unsafe_allow_html=True)

    if st.button("לתפריט הראשי", key="zero_btn"):
        st.session_state.step = "menu"
        st.rerun()

    base_url = "https://fullrealestatebroker-yevuzewxde4obgrpgacrpc.streamlit.app/"
    exam_url = f"{base_url}?user={st.session_state.user}&embed=true"
    st.markdown(f'<iframe src="{exam_url}" style="width:100%; height:100vh; border:none; margin-top:-45px;"></iframe>', unsafe_allow_html=True)

elif st.session_state.step == "study":
    show_header()
    sel = st.selectbox("בחר נושא לימוד:", ["בחר..."] + list(SYLLABUS.keys()))
    c_a, c_b = st.columns([1, 1])
    if c_a.button("טען נושא") and sel != "בחר...":
        st.session_state.update({"selected_topic": sel, "step": "lesson_run", "lesson_txt": "", "current_sub": None})
        st.rerun()
    if c_b.button("לתפריט הראשי"):
        st.session_state.step = "menu"
        st.rerun()

elif st.session_state.step == "lesson_run":
    show_header()
    st.header(f"📖 {st.session_state.selected_topic}")
    subs = SYLLABUS.get(st.session_state.selected_topic, [])
    # יצירת כפתורים שלא נמתחים ל-100%
    cols = st.columns(len(subs) if len(subs) > 0 else 1)
    for i, s in enumerate(subs):
        if cols[i].button(s, key=f"s_{i}"):
            st.session_state.update({"current_sub": s, "lesson_txt": "LOADING"})
            st.rerun()
    
    if st.session_state.current_sub:
        st.subheader(f"נושא: {st.session_state.current_sub}")
        if st.session_state.lesson_txt == "LOADING":
             st.session_state.lesson_txt = stream_ai_lesson(f"הסבר על {st.session_state.current_sub}")
             st.rerun()
        st.markdown(st.session_state.lesson_txt)
    
    if st.button("🏠 חזרה לתפריט", key="final_back"):
        st.session_state.step = "menu"
        st.rerun()

# סוף קובץ
