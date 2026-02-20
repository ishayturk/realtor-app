import streamlit as st
import google.generativeai as genai
import json, re

st.set_page_config(page_title="מתווך בקליק", layout="wide")

# אתחול Session State
if "step" not in st.session_state:
    st.session_state.update({"user": None, "step": "login"})

# --- לוגיקה לעיצוב והצגת הדפים ---

if st.session_state.step == "login":
    st.markdown("<style>* { direction: rtl; text-align: right; }</style>", unsafe_allow_html=True)
    st.title("🏠 מתווך בקליק")
    u = st.text_input("שם מלא:")
    if st.button("כניסה") and u:
        st.session_state.update({"user": u, "step": "menu"})
        st.rerun()

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

elif st.session_state.step == "exam_intro":
    # CSS ממוקד לתיקון היישור והרווחים
    st.markdown("""
        <style>
        #MainMenu, footer, header {visibility: hidden;}
        .block-container { padding-top: 0.5rem !important; }
        
        /* עיצוב הסטריפ העליון */
        .header-container {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 5px 0;
            border-bottom: 1px solid #f0f0f0;
            margin-bottom: 10px;
        }
        .user-info { font-size: 0.85rem; color: #555; flex-grow: 1; text-align: center; }
        
        /* צמצום רווחים בין שורות הטקסט */
        .instruction-line { margin-bottom: -10px; }
        
        div[data-testid="stCheckbox"] { direction: rtl !important; margin-top: -10px; }
        * { direction: rtl; text-align: right; }
        </style>
        """, unsafe_allow_html=True)

    # סטריפ עליון מאוזן
    col_r, col_m, col_l = st.columns([1.5, 3, 1.5])
    
    with col_r:
        st.markdown("<h4 style='margin:0;'>🏠 מתווך בקליק</h4>", unsafe_allow_html=True)
    
    with col_m:
        st.markdown(f"<p class='user-info'>👤 משתמש: {st.session_state.user}</p>", 
                    unsafe_allow_html=True)
    
    with col_l:
        if st.button("לתפריט הראשי", key="back_btn"):
            st.session_state.step = "menu"; st.rerun()

    # תוכן הוראות המבחן בצורה מהודקת
