import streamlit as st
import google.generativeai as genai
import json
import re
import time
import random

# 1. הגדרות בסיסיות ביותר (בלי CSS מורכב בינתיים)
st.set_page_config(page_title="מתווך בקליק", layout="centered")

# פונקציית עזר ליישור לימין (פשוטה)
def rtl_text(text, tag="p"):
    st.markdown(f'<{tag} style="direction: rtl; text-align: right;">{text}</{tag}>', unsafe_allow_html=True)

# 2. אתחול משתני מערכת
if "view" not in st.session_state:
    st.session_state.view = "login"
    st.session_state.user = ""
    st.session_state.topic = ""
    st.session_state.lesson = ""
    st.session_state.questions = []
    st.session_state.idx = 0
    st.session_state.correct_answers = 0
    st.session_state.user_answers = {}

# 3. מנוע AI
def init_gemini():
    try:
        if "GEMINI_API_KEY" in st.secrets:
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            return genai.GenerativeModel('gemini-1.5-flash')
    except:
        return None
    return None

model = init_gemini()

# 4. מבנה האפליקציה
st.markdown('<h1 style="text-align: center;">🏠 מתווך בקליק</h1>', unsafe_allow_html=True)

# --- דף כניסה ---
if st.session_state.view == "login":
    rtl_text("ברוכים הבאים! אנא הכנס שם כדי להתחיל.", "h3")
    name = st.text_input("שם מלא:", key="name_input")
    if st.button("כניסה"):
        if name:
            st.session_state.user = name
            st.session_state.view = "menu"
            st.rerun()
        else:
            st.error("חובה להזין שם")

# --- תפריט ראשי ---
elif st.session_state.view == "menu":
    rtl_text(f"שלום {st.session_state.user}, מה תרצה לעשות היום?")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📚 לימוד לפי נושאים"):
            st.session_state.view = "select_topic"
            st.rerun()
    with col2:
        if st.button("🚀 סימולציית מבחן"):
            st.session_state.view = "exam"
            st.session_state.idx = 0
            st.session_state.start_time = time.time()
            st.rerun()

# --- בחירת נושא ---
elif st.session_state.view == "select_topic":
    rtl_text("בחר נושא ללימוד:")
    topic = st.selectbox("נושאים:", ["חוק המתווכים", "חוק המקרקעין", "חוק החוזים"])
    if st.button("התחל שיעור"):
        st.session_state.topic = topic
        st.session_state.lesson = ""
        st.session_state.view = "lesson"
        st.rerun()
    if st.button("חזרה"):
        st.session_state.view = "menu"
        st.rerun()

# --- דף שיעור ---
elif st.session_state.view == "lesson":
    rtl_text(f"שיעור בנושא: {st.session_state.topic}", "h2")
    
    if not st.session_state.lesson:
        with st.spinner("ה-AI כותב..."):
            if model:
                resp = model.generate_content(f"כתוב שיעור קצר על {st.session_state.topic}")
                st.session_state.lesson = resp.text
            else:
                st.session_state.lesson = "אין חיבור ל-AI. בדוק את ה-API Key."
    
    st.markdown(f'<div style="direction: rtl; text-align: right; border: 1px solid #ccc; padding: 15px;">{st.session_state.lesson}</div>', unsafe_allow_html=True)
    
    if st.button("חזרה לתפריט"):
        st.session_state.view = "menu"
        st.rerun()

# --- דף מבחן (שלד בסיסי) ---
elif st.session_state.view == "exam":
    rtl_text("סימולציית מבחן (בהקמה)", "h2")
    rtl_text("כאן יופיעו השאלות מהמאגר הרשמי.")
    if st.button("חזרה לתפריט"):
        st.session_state.view = "menu"
        st.rerun()
