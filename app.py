# Project: מתווך בקליק | Training_full_V18 | 21/02/2026 | 18:45
import streamlit as st
import google.generativeai as genai
import json
import re

# הגדרת דף בסיסית - ללא CSS גלובלי שפוגע במרווחים
st.set_page_config(page_title="מתווך בקליק", layout="wide")

# עיצוב RTL בסיסי בלבד (לא נוגע במרווחים עליונים)
st.markdown("""<style>* { direction: rtl; text-align: right; }</style>""", unsafe_allow_html=True)

# סילבוס (לפי עוגן 1213)
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

# פונקציות עזר (ללא שינוי)
def reset_quiz_state():
    st.session_state.update({
        "quiz_active": False, "q_data": None, "q_count": 0,
        "checked": False, "quiz_finished": False, "correct_answers": 0
    })

if "step" not in st.session_state:
    st.session_state.update({"user": None, "step": "login"})

# --- Routing ---

if st.session_state.step == "login":
    st.title("🏠 מתווך בקליק")
    u_in = st.text_input("שם מלא:")
    if st.button("כניסה") and u_in:
        st.session_state.user = u_in
        st.session_state.step = "menu"
        st.rerun()

elif st.session_state.step == "menu":
    st.title("🏠 מתווך בקליק")
    st.write(f"שלום, **{st.session_state.user}**")
    c1, c2, _ = st.columns([1.5, 1.5, 3])
    if c1.button("📚 לימוד לפי נושאים"):
        st.session_state.step = "study"
        st.rerun()
    if c2.button("⏱️ גש/י למבחן"):
        st.session_state.step = "exam_frame"
        st.rerun()

elif st.session_state.step == "exam_frame":
    # הזרקת ה-CSS הקיצוני אך ורק כאן!
    st.markdown("""
        <style>
            /* העלמת ההדר רק למסך זה */
            header { visibility: hidden !important; }
            /* משיכת כל התוכן למעלה ב-100 פיקסלים */
            .main .block-container { 
                padding-top: 0px !important; 
                margin-top: -100px !important; 
            }
            /* עיצוב לינק החזרה בשמאל */
            .nav-link-box {
                text-align: left;
                direction: ltr;
                padding: 5px 20px;
                background-color: white;
            }
        </style>
    """, unsafe_allow_html=True)
    
    # הלינק כפי שהיה במקור (במראה טקסטואלי)
    st.markdown('<div class="nav-link-box">', unsafe_allow_html=True)
    if st.button("לתפריט הראשי", key="back_from_exam"):
        st.session_state.step = "menu"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    
    # הבחינה צמודה ללינק
    exam_url = f"https://fullrealestatebroker-yevuzewxde4obgrpgacrpc.streamlit.app/?user={st.session_state.user}&embed=true"
    st.markdown(f'<iframe src="{exam_url}" style="width:100%; height:100vh; border:none;"></iframe>', unsafe_allow_html=True)

elif st.session_state.step == "study":
    # כאן הכל רגיל - אין margin שלילי ואין הסתרת הדר
    st.title("📚 לימוד לפי נושאים")
    if st.button("חזרה לתפריט"):
        st.session_state.step = "menu"
        st.rerun()

# סוף קובץ
