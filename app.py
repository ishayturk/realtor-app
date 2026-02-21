# Project: מתווך בקליק | Version: 1213-Safe-Exam-Strict-Clean | File: app.py
import streamlit as st
import google.generativeai as genai
import json
import re

# הגדרת דף - סגירת סרגל צד כברירת מחדל למניעת עיוות
st.set_page_config(page_title="מתווך בקליק", layout="wide", initial_sidebar_state="collapsed")

# עיצוב CSS - ללא סטריפים חיצוניים, שימוש ב-Header קיים וקיר שקוף
st.markdown("""
<style>
    /* הגדרות RTL כלליות */
    * { direction: rtl; text-align: right; }
    
    /* ה-Header המקורי של הלמידה (Anchor 1213) */
    .header-container { 
        display: flex; 
        align-items: center; 
        gap: 45px; 
        margin-bottom: 30px; 
    }
    .header-title { font-size: 2.5rem !important; font-weight: bold !important; margin: 0 !important; }
    .header-user { font-size: 1.2rem !important; font-weight: 900 !important; color: #31333f; }

    /* --- הגדרות ייחודיות למצב מבחן --- */
    
    /* ביטול מוחלט של ה-Sidebar והכפתור המעוות >> */
    [data-testid="stSidebar"], [data-testid="stSidebarCollapseButton"] { display: none !important; }
    
    /* קיר שקוף מימין למניעת מריחה של ה-iframe */
    .invisible-barrier {
        position: fixed;
        top: 0;
        right: 0;
        width: 20px;
        height: 100vh;
        z-index: 999998;
        background: transparent;
    }

    /* הזרקת טקסט "לתפריט הראשי" לתוך ה-Header המובנה */
    .header-link-container {
        position: fixed;
        top: 10px;
        left: 0;
        width: 100%;
        display: flex;
        justify-content: center;
        z-index: 999999;
        pointer-events: none;
    }
    .header-link {
        pointer-events: auto;
        text-decoration: none;
        color: #555;
        font-size: 15px;
        font-weight: 500;
        background: rgba(255,255,255,0.7);
        padding: 2px 10px;
        border-radius: 5px;
    }

    /* iframe שתופס 100% מהגובה ומתחיל מהטופ */
    .full-iframe {
        border: none !important;
        width: 100%;
        height: 100vh;
        display: block;
        margin-top: -50px; /* קיזוז ה-Header המובנה של Streamlit */
    }

    /* הסרת רווחים של Streamlit */
    .block-container { padding: 0 !important; max-width: 100% !important; }
    header { visibility: hidden; } /* מסתיר את ה-Header המקורי כדי שלא יפריע לקישור שלנו */
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

# לוגיקה פנימית (Anchor 1213)
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
        st.rerun
