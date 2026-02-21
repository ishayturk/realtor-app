# Project: מתווך בקליק | Version: 1213-Original-Restored-Exam-Fix | File: app.py
import streamlit as st
import google.generativeai as genai
import json
import re

# הגדרת דף - שומר על המבנה המקורי
st.set_page_config(page_title="מתווך בקליק", layout="wide")

# עיצוב CSS המקורי של עוגן 1213 (ללא שינויים)
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
</style>
""", unsafe_allow_html=True)

# סילבוס (Anchor 1213)
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

# פונקציות (Anchor 1213)
def reset_quiz_state():
    st.session_state.update({"quiz_active": False, "quiz_finished": False, "checked": False, "q_count": 0})

def show_header():
    if st.session_state.get("user"):
        st.markdown(f"""<div class="header-container">
            <div class="header-title">🏠 מתווך בקליק</div>
            <div class="header-user">👤 <b>{st.session_state.user}</b></div>
        </div>""", unsafe_allow_html=True)

# אתחול State
if "step" not in st.session_state:
    st.session_state.update({"user": None, "step": "login"})

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
    # 1. הזרקת ה-CSS של המבחן באופן מבודד (רק כאן)
    st.markdown("""
    <style>
        header { visibility: hidden; }
        .block-container { padding-top: 0 !important; padding-bottom: 0 !important; }
        .nav-link-box { position: fixed; top: 10px; width: 100%; display: flex; justify-content: center; z-index: 1000; }
        .nav-link { text-decoration: none; color: #666; font-weight: bold; background: white; padding: 2px 10px; border-radius: 5px; border: 1px solid #ccc; }
        .right-barrier { position: fixed; right: 0; top: 0; width: 15px; height: 100vh; z-index: 999; background: transparent; }
    </style>
    <div class="right-barrier"></div>
    <div class="nav-link-box"><a href="/?step=menu" target="_self" class="nav-link">לתפריט הראשי</a></div>
    """, unsafe_allow_html=True)

    if st.query_params.get("step") == "menu":
        st.session_state.step = "menu"
        st.query_params.clear()
        st.rerun()

    # 2. ה-Iframe
    base_url = "https://fullrealestatebroker-yevuzewxde4obgrpgacrpc.streamlit.app/"
    exam_url = f"{base_url}?user={st.session_state.user}&embed=true"
    st.markdown(f'<iframe src="{exam_url}" style="width:100%; height:100vh; border:none; margin-top:-50px;"></iframe>', unsafe_allow_html=True)

elif st.session_state.step == "study":
    show_header()
    sel = st.selectbox("בחר נושא לימוד:", ["בחר..."] + list(SYLLABUS.keys()))
    if st.button("טען נושא") and sel != "בחר...":
        st.session_state.selected_topic = sel
        st.rerun()
    if st.button("🏠 לתפריט הראשי"):
        st.session_state.step = "menu"
        st.rerun()
