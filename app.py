# ==========================================
# Project: מתווך בקליק | Version: 1213
# ==========================================
import streamlit as st
import google.generativeai as genai
import json, re

st.set_page_config(page_title="מתווך בקליק", layout="wide")
st.markdown('<div id="top"></div>', unsafe_allow_html=True)

st.markdown("""
<style>
    * { direction: rtl; text-align: right; }
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; height: 3em; }
    .top-link { 
        display: inline-block; width: 100%; text-align: center; 
        border-radius: 8px; text-decoration: none; border: 1px solid #d1d5db;
        font-weight: bold; height: 2.8em; line-height: 2.8em;
        background-color: transparent; color: inherit;
    }
    .v-footer {
        text-align: center;
        color: rgba(255, 255, 255, 0.1);
        font-size: 0.7em;
        margin-top: 50px;
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# ... (SYLLABUS, fetch_q_ai, stream_ai_lesson נשארים ללא שינוי)

if "step" not in st.session_state:
    st.session_state.update({
        "user": None, "step": "login", "q_count": 0, "quiz_active": False, 
        "show_ans": False, "lesson_txt": "", "q_data": None, 
        "correct_answers": 0, "quiz_finished": False
    })

st.title("🏠 מתווך בקליק")

if st.session_state.step == "login":
    u = st.text_input("שם מלא:")
    if st.button("כניסה") and u:
        st.session_state.update({"user": u, "step": "menu"})
        st.rerun()

elif st.session_state.step == "menu":
    st.subheader(f"👤 שלום, {st.session_state.user}")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("📚 לימוד לפי נושאים"):
            st.session_state.step = "study"; st.rerun()
    with c2:
        # פתרון נקי: כפתור רגיל שמפעיל לינק דרך JS
        if st.button("⏱️ גש/י למבחן"):
            user_name = st.session_state.user.replace(" ", "%20")
            exam_url = f"https://fullrealestatebroker-yevuzewxde4obgrpgacrpc.streamlit.app/?user={user_name}"
            js = f"window.open('{exam_url}', '_self')"
            st.components.v1.html(f"<script>{js}</script>", height=0)

elif st.session_state.step == "study":
    # ... (שאר הקוד של study ו-lesson_run נשאר זהה לחלוטין למקור)
    sel = st.selectbox("בחר נושא:", ["בחר..."] + list(SYLLABUS.keys()))
    if sel != "בחר..." and st.button("טען נושא"):
        st.session_state.update({"selected_topic": sel, "step": "lesson_run", "lesson_txt": ""})
        st.rerun()

# ... (סוף הקוד נשאר ללא שינוי)
