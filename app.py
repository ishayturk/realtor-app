import streamlit as st
import google.generativeai as genai
import json, re

st.set_page_config(page_title="מתווך בקליק", layout="wide")

# CSS לעיצוב הסטריפ העליון והצ'קבוקס
st.markdown("""
    <style>
    * { direction: rtl; text-align: right; }
    header { visibility: hidden; }
    
    /* סטריפ עליון חסכוני */
    .header-strip {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.5rem 0;
        margin-bottom: 1rem;
    }
    .user-name { font-size: 0.9rem; color: gray; }
    
    /* יישור צ'קבוקס לימין */
    div[data-testid="stCheckbox"] { direction: rtl !important; }
    div[data-testid="stCheckbox"] > label {
        display: flex !important;
        flex-direction: row !important;
        align-items: center !important;
        gap: 10px !important;
    }
    
    .stButton>button { width: 100%; border-radius: 8px; }
    </style>
    """, unsafe_allow_html=True)

# אתחול
if "step" not in st.session_state:
    st.session_state.update({
        "user": None, "step": "login", "start_exam": False
    })

# --- לוגיקת דפים ---

if st.session_state.step == "login":
    st.title("🏠 מתווך בקליק")
    u = st.text_input("שם מלא:")
    if st.button("כניסה") and u:
        st.session_state.update({"user": u, "step": "menu"})
        st.rerun()

elif st.session_state.step == "menu":
    st.title("🏠 מתווך בקליק")
    st.subheader(f"👤 שלום, {st.session_state.user}")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("📚 לימוד לפי נושאים"):
            st.session_state.step = "study"; st.rerun()
    with c2:
        if st.button("⏱️ גש/י למבחן"):
            st.session_state.step = "exam_intro"; st.rerun()

elif st.session_state.step
