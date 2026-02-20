import streamlit as st
import google.generativeai as genai
import json, re

st.set_page_config(page_title="מתווך בקליק", layout="wide")

# אתחול Session State
if "step" not in st.session_state:
    st.session_state.update({
        "user": None, "step": "login"
    })

# --- מסך כניסה: מקורי ונקי מגרסה 1213 ---
if st.session_state.step == "login":
    st.markdown("<style>* { direction: rtl; text-align: right; }</style>", unsafe_allow_html=True)
    st.title("🏠 מתווך בקליק")
    u = st.text_input("שם מלא:")
    if st.button("כניסה") and u:
        st.session_state.update({"user": u, "step": "menu"})
        st.rerun()

# --- תפריט ראשי ---
elif st.session_state.step == "menu":
    st.markdown("<style>* { direction: rtl; text-align: right; }</style>", unsafe_allow_html=True)
    st.title("🏠 מתווך בקליק")
    st.subheader(f"👤 שלום, {st.session_state.user}")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("📚 לימוד לפי נושאים"):
            st.session_state.step = "study"; st.rerun()
    with c2:
        if st.button("⏱️ גש/י למבחן"):
            st.session_state.step = "exam_intro"; st.rerun()

# --- עמוד הוראות המבחן: עם הסטריפ העליון שביקשת ---
elif st.session_state.step == "exam_intro":
    # הזרקת עיצוב ספציפי לעמוד זה בלבד
    st.markdown("""
        <style>
        header { visibility: hidden; }
        .user-name-small { font-size: 0.9rem; color: gray; text-align: center; width: 100%; }
        div[data-testid="stCheckbox"] { direction: rtl !important; }
        div[data-testid="stCheckbox"] > label {
            display: flex !important;
            flex-direction: row !important;
            align-items: center !important;
            gap: 10px !important;
        }
        * { direction: rtl; text-align: right; }
        </style>
        """, unsafe_allow_html=True)

    # סטריפ עליון: לוגו | שם משתמש | כפתור חזרה
    col_r, col_m, col_l = st.columns([2, 2, 1])
    
    with col_r:
        st.markdown("### 🏠 מתווך בקליק")
    
    with col_m:
        st.markdown(f"<p class='user-name-small'>👤 {st.session_state.user}</p>", 
                    unsafe_allow_html=True)
    
    with col_l:
        if st.button("לתפריט הראשי"):
            st.session_state.step = "menu"; st.rerun()

    st.header("הוראות למבחן רישויי מקרקעין")
    st.write("1. המבחן כולל 25 שאלות.")
    st.write("2. זמן מוקצב: 90 דקות.")
    st.write("3. מעבר לשאלה הבאה רק לאחר סימון תשובה.")
    st.write("4. ניתן לחזור אחורה רק לשאלות שנענו.")
    st.write("5. בסיום 90 דקות המבחן יינעל.")
    st.write("6. ציון עובר: 60.")
    st.write("7. חל איסור על שימוש בחומר עזר.")

    st.divider()

    agree = st.checkbox("קראתי את ההוראות ואני מוכן להתחיל בבחינה")

    if st.button("התחל בחינה", disabled=not agree):
        st.session_state.step = "exam_run"; st.rerun()
