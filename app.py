# Project: מתווך בקליק | Training_full_V19 | 21/02/2026 | 18:55
import streamlit as st
import google.generativeai as genai
import json
import re

# הגדרת דף בסיסית - ללא שום הגדרות CSS גלובליות שעלולות להרוס את הלמידה
st.set_page_config(page_title="מתווך בקליק", layout="wide")

# סילבוס (לפי עוגן 1213 - ללא שינוי)
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

# פונקציות עזר
def reset_quiz_state():
    st.session_state.update({
        "quiz_active": False, "q_data": None, "q_count": 0,
        "checked": False, "quiz_finished": False, "correct_answers": 0
    })

if "step" not in st.session_state:
    st.session_state.update({
        "user": None, "step": "login", "lesson_txt": "", 
        "selected_topic": None, "current_sub": None
    })

# --- Routing ---

if st.session_state.step == "login":
    st.markdown("<h1 style='text-align: right; direction: rtl;'>🏠 מתווך בקליק</h1>", unsafe_allow_html=True)
    u_in = st.text_input("שם מלא:", key="login_name")
    if st.button("כניסה") and u_in:
        st.session_state.user = u_in
        st.session_state.step = "menu"
        st.rerun()

elif st.session_state.step == "menu":
    st.markdown(f"<div style='text-align: right; direction: rtl;'><h1>🏠 מתווך בקליק</h1><p>שלום, {st.session_state.user}</p></div>", unsafe_allow_html=True)
    c1, c2, _ = st.columns([1.5, 1.5, 3])
    if c1.button("📚 לימוד לפי נושאים"):
        st.session_state.step = "study"
        st.rerun()
    if c2.button("⏱️ גש/י למבחן"):
        st.session_state.step = "exam_frame"
        st.rerun()

elif st.session_state.step == "exam_frame":
    # הזרקת CSS מבודדת אך ורק לדף הזה - כדי לא להרוס את שאר המערכת
    st.markdown("""
        <style>
            header { visibility: hidden !important; }
            .main .block-container { 
                padding-top: 0px !important; 
                margin-top: -80px !important; 
            }
            /* יישור הכפתור לשמאל */
            .stButton>button { float: left !important; width: auto !important; }
        </style>
    """, unsafe_allow_html=True)
    
    # שורה עליונה עם כפתור בשמאל
    col_empty, col_back = st.columns([5, 1])
    with col_back:
        if st.button("🏠 לתפריט הראשי"):
            st.session_state.step = "menu"
            st.rerun()
    
    # הבחינה
    exam_url = f"https://fullrealestatebroker-yevuzewxde4obgrpgacrpc.streamlit.app/?user={st.session_state.user}&embed=true"
    st.markdown(f'<iframe src="{exam_url}" style="width:100%; height:100vh; border:none;"></iframe>', unsafe_allow_html=True)

elif st.session_state.step == "study":
    # לוגיקת למידה נקייה (ללא margin שלילי)
    st.markdown(f"<div style='text-align: right; direction: rtl;'><h1>📚 לימוד: {st.session_state.user}</h1></div>", unsafe_allow_html=True)
    if st.button("חזרה לתפריט"):
        st.session_state.step = "menu"
        st.rerun()
    # (כאן יבוא המשך קוד הלמידה שלך כפי שהיה במקור)

# סוף קובץ
