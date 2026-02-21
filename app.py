# Project: מתווך בקליק | Version: 1218-G2-Left-Nav-Final | File: app.py
import streamlit as st
import google.generativeai as genai
import json
import re

# הגדרת דף
st.set_page_config(page_title="מתווך בקליק", layout="wide", initial_sidebar_state="collapsed")

# עיצוב CSS - עוגן 1213 + תיקון מיקום לשמאל
st.markdown("""
<style>
    * { direction: rtl; text-align: right; }
    .header-container { display: flex; align-items: center; gap: 45px; margin-bottom: 30px; }
    .header-title { font-size: 2.5rem !important; font-weight: bold !important; margin: 0 !important; }
    .header-user { font-size: 1.2rem !important; font-weight: 900 !important; color: #31333f; }
    .stButton>button { width: 100% !important; border-radius: 8px !important; font-weight: bold !important; height: 3em !important; }
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

# --- לוגיקה ---
if "step" not in st.session_state:
    st.session_state.update({"user": None, "step": "login", "selected_topic": None, "current_sub": None, "lesson_txt": ""})

def show_header():
    if st.session_state.get("user"):
        st.markdown(f"""<div class="header-container">
            <div class="header-title">🏠 מתווך בקליק</div>
            <div class="header-user">👤 <b>{st.session_state.user}</b></div>
        </div>""", unsafe_allow_html=True)

# --- ניתוב דפים ---

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
    # CSS מבודד: כפתור חזרה לשמאל וביטול מרווחים
    st.markdown("""
    <style>
        header { visibility: hidden !important; }
        .block-container { padding: 0 !important; }
        .nav-left-box { 
            position: fixed; 
            top: 15px; 
            left: 20px; 
            z-index: 2000; 
        }
        .nav-link-simple { 
            text-decoration: none; 
            color: #1f77b4; 
            font-weight: bold; 
            font-size: 14px;
            background: rgba(255,255,255,0.9);
            padding: 5px 15px;
            border-radius: 20px;
            border: 1px solid #1f77b4;
        }
    </style>
    <div class="nav-left-box">
        <a href="/?step=menu" target="_self" class="nav-link-simple">← לתפריט הראשי</a>
    </div>
    """, unsafe_allow_html=True)
    
    if st.query_params.get("step") == "menu":
        st.session_state.step = "menu"
        st.query_params.clear()
        st.rerun()

    base_url = "https://fullrealestatebroker-yevuzewxde4obgrpgacrpc.streamlit.app/"
    exam_url = f"{base_url}?user={st.session_state.user}&embed=true"
    st.markdown(f'<iframe src="{exam_url}" style="width:100%; height:100vh; border:none; margin-top:-50px;"></iframe>', unsafe_allow_html=True)

elif st.session_state.step == "study":
    show_header()
    # (שארית הלוגיקה המקורית של הלמידה כאן...)
    if st.button("🏠 חזרה"):
        st.session_state.step = "menu"
        st.rerun()

# --- End of File ---
# Version: 1218-G2-Left-Nav-Final | Date: 2026-02-21
