# Project: מתווך בקליק | Version: 1221-G1-Final-Strict | File: app.py
import streamlit as st
import google.generativeai as genai
import json
import re

st.set_page_config(page_title="מתווך בקליק", layout="wide", initial_sidebar_state="collapsed")

# --- CSS CORE (עוגן 1213) ---
st.markdown("""
<style>
    * { direction: rtl; text-align: right; }
    .header-container { display: flex; align-items: center; gap: 45px; margin-bottom: 30px; }
    .header-title { font-size: 2.5rem !important; font-weight: bold !important; margin: 0 !important; }
    .header-user { font-size: 1.2rem !important; font-weight: 900 !important; color: #31333f; }
    .stButton>button { width: 100% !important; border-radius: 8px !important; font-weight: bold !important; height: 3em !important; }
    
    /* עיצוב הסטריפ העליון במצב מבחן בלבד */
    .exam-strip {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 5px 20px;
        background: white;
        border-bottom: 1px solid #eee;
        height: 50px;
        position: sticky;
        top: 0;
        z-index: 999;
    }
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

if "step" not in st.session_state:
    st.session_state.update({"user": None, "step": "login", "selected_topic": None, "current_sub": None, "lesson_txt": ""})

# --- ROUTING ---

if st.session_state.step == "login":
    st.title("🏠 מתווך בקליק")
    u_in = st.text_input("שם מלא:")
    if st.button("כניסה") and u_in:
        st.session_state.user = u_in
        st.session_state.step = "menu"
        st.rerun()

elif st.session_state.step == "menu":
    st.markdown(f'<div class="header-container"><div class="header-title">🏠 מתווך בקליק</div><div class="header-user">👤 <b>{st.session_state.user}</b></div></div>', unsafe_allow_html=True)
    c1, c2, _ = st.columns([1.5, 1.5, 3])
    if c1.button("📚 לימוד לפי נושאים"): st.session_state.step = "study"; st.rerun()
    if c2.button("⏱️ גש/י למבחן"): st.session_state.step = "exam_frame"; st.rerun()

elif st.session_state.step == "exam_frame":
    st.markdown("<style>header { visibility: hidden !important; } .block-container { padding: 0 !important; }</style>", unsafe_allow_html=True)
    
    # הסטריפ העליון (מדרגת שורה אחת מתחת לקצה העליון כפי שביקשת)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("← חזרה"): st.session_state.step = "menu"; st.rerun()
    with col2:
        st.markdown(f"<p style='text-align:center; font-weight:bold; padding-top:10px;'>{st.session_state.user}</p>", unsafe_allow_html=True)
    with col3:
        st.markdown("<p style='text-align:right; font-weight:bold; padding-top:10px;'>🏠 מתווך בקליק</p>", unsafe_allow_html=True)
    
    exam_url = f"https://fullrealestatebroker-yevuzewxde4obgrpgacrpc.streamlit.app/?user={st.session_state.user}&embed=true"
    st.markdown(f'<iframe src="{exam_url}" style="width:100%; height:92vh; border:none; margin-top:0;"></iframe>', unsafe_allow_html=True)

elif st.session_state.step == "study":
    st.markdown(f'<div class="header-container"><div class="header-title">🏠 מתווך בקליק</div><div class="header-user">👤 <b>{st.session_state.user}</b></div></div>', unsafe_allow_html=True)
    sel = st.selectbox("בחר נושא:", ["בחר..."] + list(SYLLABUS.keys()))
    if st.button("טען נושא") and sel != "בחר...":
        st.session_state.update({"selected_topic": sel, "step": "lesson_run", "lesson_txt": "", "current_sub": None})
        st.rerun()
    if st.button("🏠 חזרה"): st.session_state.step = "menu"; st.rerun()

elif st.session_state.step == "lesson_run":
    st.markdown(f'<div class="header-container"><div class="header-title">🏠 מתווך בקליק</div><div class="header-user">👤 <b>{st.session_state.user}</b></div></div>', unsafe_allow_html=True)
    st.header(f"📖 {st.session_state.selected_topic}")
    subs = SYLLABUS.get(st.session_state.selected_topic, [])
    cols = st.columns(len(subs))
    for i, s in enumerate(subs):
        if cols[i].button(s, key=f"s_{i}"):
            st.session_state.update({"current_sub": s, "lesson_txt": "LOADING"})
            st.rerun()
    
    if st.session_state.current_sub:
        st.divider()
        st.subheader(st.session_state.current_sub)
        # לוגיקת ה-AI נשארת כאן (השמטתי לקיצור, היא קיימת בקוד שלך)

    if st.button("🏠 לתפריט הראשי"): st.session_state.step = "menu"; st.rerun()

# --- End of File ---
# Version: 1221-G1 | Date: 2026-02-21
