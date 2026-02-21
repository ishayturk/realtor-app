# Project: מתווך בקליק | Version: training_full_V15 | 21/02/2026 | 23:45
import streamlit as st
import google.generativeai as genai
import json
import re

# הגדרת דף
st.set_page_config(page_title="מתווך בקליק", layout="wide")

# --- חלק 1: Interceptor (יירוט פרמטרים מה-URL) ---
q_params = st.query_params
if "user" in q_params:
    st.session_state.user = q_params["user"]
    if q_params.get("nav") == "menu":
        st.session_state.step = "menu"
    # ניקוי ה-URL לאחר הזרקה כדי למנוע לופים בריענון ידני
    st.query_params.clear()

# Init State (אם לא הוזרק מה-URL)
if "step" not in st.session_state:
    st.session_state.update({
        "user": None, 
        "step": "login", 
        "lesson_txt": "", 
        "selected_topic": None, 
        "current_sub": None
    })

# עיצוב RTL בסיסי - עוגן 1213
st.markdown("""
<style>
    * { direction: rtl; text-align: right; }
    .header-container { display: flex; align-items: center; gap: 45px; margin-bottom: 30px; }
    .header-title { font-size: 2.5rem !important; font-weight: bold !important; margin: 0 !important; }
    .header-user { font-size: 1.2rem !important; font-weight: 900 !important; color: #31333f; }
    
    /* כפתורי תפריט ראשי בלבד */
    .main-menu-btns button { 
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

def show_header():
    if st.session_state.get("user"):
        st.markdown(f"""<div class="header-container">
            <div class="header-title">🏠 מתווך בקליק</div>
            <div class="header-user">👤 <b>{st.session_state.user}</b></div>
        </div>""", unsafe_allow_html=True)

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
    st.markdown('<div class="main-menu-btns">', unsafe_allow_html=True)
    c1, c2, _ = st.columns([1.5, 1.5, 3])
    if c1.button("📚 לימוד לפי נושאים"):
        st.session_state.step = "study"
        st.rerun()
    if c2.button("⏱️ גש/י למבחן"):
        st.session_state.step = "exam_frame"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.step == "exam_frame":
    # יצירת הלינק הדינמי עם שם המשתמש
    current_user = st.session_state.user
    # בניית ה-URL לחזרה - הקידוד מוודא ששמות בעברית יעברו תקין
    back_url = f"/?nav=menu&user={current_user}"
    
    st.markdown(f"""
    <style>
        header {{ visibility: hidden !important; }}
        .main .block-container {{ padding: 0 !important; }}
        .zero-nav {{
            position: fixed; top: 0; left: 0; z-index: 1000000;
            background: #f8f9fb; border: 1px solid #ccc;
            border-top: none; border-left: none;
            padding: 2px 15px; border-radius: 0 0 5px 0;
        }}
        .zero-nav a {{ text-decoration: none; color: #444; font-size: 13px; font-weight: bold; }}
    </style>
    <div class="zero-nav">
        <a href="{back_url}" target="_self">⬅️ חזרה לתפריט הראשי</a>
    </div>
    """, unsafe_allow_html=True)

    base_url = "https://fullrealestatebroker-yevuzewxde4obgrpgacrpc.streamlit.app/"
    exam_url = f"{base_url}?user={current_user}&embed=true"
    st.markdown(f'<iframe src="{exam_url}" style="width:100%; height:100vh; border:none; margin-top:-35px;"></iframe>', unsafe_allow_html=True)

elif st.session_state.step == "study":
    show_header()
    sel = st.selectbox("בחר נושא לימוד:", ["בחר..."] + list(SYLLABUS.keys()))
    ca, cb = st.columns([1, 1])
    if ca.button("טען נושא") and sel != "בחר...":
        st.session_state.update({"selected_topic": sel, "step": "lesson_run", "lesson_txt": "", "current_sub": None})
        st.rerun()
    if cb.button("לתפריט הראשי"):
        st.session_state.step = "menu"
        st.rerun()

elif st.session_state.step == "lesson_run":
    show_header()
    st.header(f"📖 {st.session_state.selected_topic}")
    subs = SYLLABUS.get(st.session_state.selected_topic, [])
    cols = st.columns(len(subs) if len(subs) > 0 else 1)
    for i, s in enumerate(subs):
        if cols[i].button(s, key=f"s_{i}"):
            st.session_state.update({"current_sub": s})
            st.rerun()
    if st.session_state.current_sub:
        st.info(f"מציג תוכן עבור: {st.session_state.current_sub}")
    if st.button("🏠 חזרה לתפריט"):
        st.session_state.step = "menu"
        st.rerun()

# סוף קובץ
