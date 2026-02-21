# Project: מתווך בקליק | Version: 1213-Safe-Exam-Final-Floating-Strict | File: app.py
import streamlit as st
import google.generativeai as genai
import json
import re

# הגדרת דף
st.set_page_config(page_title="מתווך בקליק", layout="wide")

# עיצוב CSS - תיקון הציפה כדי שלא יזיז את ה-iframe
st.markdown("""
<style>
    * { direction: rtl; text-align: right; }
    
    /* ביטול כל המרווחים של Streamlit במצב מבחן */
    .main .block-container {
        padding: 0 !important;
        max-width: 100% !important;
    }

    /* כפתור החזרה - ציפה מוחלטת שלא תופסת מקום בדף */
    .floating-back-btn {
        position: fixed;
        top: 15px;
        right: 15px;
        z-index: 999999;
        background-color: white !important;
        border: 2px solid #ff4b4b !important;
        border-radius: 10px;
        padding: 5px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }

    /* iframe שתופס 100% מהמסך ללא שוליים */
    .full-screen-iframe {
        border: none !important;
        width: 100vw;
        height: 100vh;
        display: block;
    }
</style>
""", unsafe_allow_html=True)

# סילבוס (עוגן 1213)
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

def reset_quiz_state():
    st.session_state.update({
        "quiz_active": False, "q_data": None, "q_count": 0,
        "checked": False, "quiz_finished": False, "correct_answers": 0
    })

if "step" not in st.session_state:
    st.session_state.update({"user": None, "step": "login"})

def show_header():
    if st.session_state.get("user"):
        st.markdown(f"""<div class="header-container">
            <div class="header-title">🏠 מתווך בקליק</div>
            <div class="header-user">👤 <b>{st.session_state.user}</b></div>
        </div>""", unsafe_allow_html=True)

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
    # הכפתור מוזרק כאלמנט HTML צף שלא דוחף שום דבר
    st.markdown(f"""
        <div class="floating-back-btn">
            <a href="/?step=menu" target="_self" style="text-decoration: none; color: #ff4b4b; font-weight: bold;">
                לתפריט הראשי →
            </a>
        </div>
    """, unsafe_allow_html=True)

    # ה-iframe מקבל את כל המסך
    base_url = "https://fullrealestatebroker-yevuzewxde4obgrpgacrpc.streamlit.app/"
    exam_url = f"{base_url}?user={st.session_state.user}&embed=true"
    st.markdown(f'<iframe src="{exam_url}" class="full-screen-iframe"></iframe>', unsafe_allow_html=True)

    # לוגיקה לחזרה (במקרה שהמשתמש לחץ על הלינק ב-HTML)
    query_params = st.query_params
    if query_params.get("step") == "menu":
        st.session_state.step = "menu"
        st.query_params.clear()
        st.rerun()

elif st.session_state.step == "study":
    show_header()
    if st.button("🏠 לתפריט הראשי"):
        st.session_state.step = "menu"
        st.rerun()
    # כאן שאר הלוגיקה של לימוד...
