# Project: מתווך בקליק | Version: training_full_V09 | 21/02/2026 | 21:55
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
    .stButton>button { width: 100% !important; border-radius: 8px !important; font-weight: bold !important; height: 3em !important; }
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
    c1, c2, _ = st.columns([1.5, 1.5, 3])
    if c1.button("📚 לימוד לפי נושאים"):
        st.session_state.step = "study"
        st.rerun()
    if c2.button("⏱️ גש/י למבחן"):
        st.session_state.step = "exam_frame"
        st.rerun()

elif st.session_state.step == "exam_frame":
    # הזרקת הכפתור לשורה 0 המוחלטת
    st.markdown("""
    <style>
        header { visibility: hidden !important; }
        .main .block-container { padding: 0 !important; }
        
        /* קיבוע הכפתור לקצה העליון - שורה 0 */
        div.stButton > button:first-child[key="zero_btn"] {
            position: fixed;
            top: 0;
            left: 0;
            z-index: 999999;
            width: auto !important;
            height: auto !important;
            padding: 2px 12px !important;
            background-color: #f8f9fb !important;
            border: 1px solid #d1d4d9 !important;
            border-top: none !important;
            border-left: none !important;
            border-radius: 0 0 5px 0 !important;
            font-size: 12px !important;
            color: #555 !important;
        }
    </style>
    """, unsafe_allow_html=True)

    if st.button("לתפריט הראשי", key="zero_btn"):
        st.session_state.step = "menu"
        st.rerun()

    # פריים המבחן צמוד למעלה
    base_url = "https://fullrealestatebroker-yevuzewxde4obgrpgacrpc.streamlit.app/"
    exam_url = f"{base_url}?user={st.session_state.user}&embed=true"
    st.markdown(f'<iframe src="{exam_url}" style="width:100%; height:100vh; border:none; margin-top:-45px;"></iframe>', unsafe_allow_html=True)

elif st.session_state.step == "study":
    show_header()
    sel = st.selectbox("בחר נושא לימוד:", ["בחר..."] + list(SYLLABUS.keys()))
    if st.button("טען נושא") and sel != "בחר...":
        st.session_state.update({"selected_topic": sel, "step": "lesson_run", "lesson_txt": ""})
        st.rerun()
    if st.button("לתפריט הראשי"):
        st.session_state.step = "menu"
        st.rerun()

# סוף קובץ
