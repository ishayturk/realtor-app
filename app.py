# Project: מתווך בקליק | Version: 1213-Final-Anchor | File: app.py
import streamlit as st
import google.generativeai as genai
import json
import re
import streamlit.components.v1 as components

# הגדרת דף - layout="wide" הכרחי אך נטפל במירכוז דרך CSS
st.set_page_config(page_title="מתווך בקליק", layout="wide")

# בדיקת ניווט חזרה דרך URL (למניעת שימוש בכפתורי Streamlit בסטריפ)
if st.query_params.get("nav") == "menu":
    st.query_params.clear()
    st.session_state.step = "menu"
    st.rerun()

# --- CSS אגרסיבי לאיפוס רווחים ועיצוב סטריפ דק וממורכז ---
st.markdown("""
<style>
    /* הסתרת כפתורי התפריט המובנים של Streamlit */
    header { visibility: hidden; }
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }

    /* איפוס מוחלט של הרווחים ש-Streamlit יוצרת סביב התוכן */
    .main .block-container {
        padding-top: 0 !important;
        padding-bottom: 0 !important;
        padding-left: 0 !important;
        padding-right: 0 !important;
        max-width: 100% !important;
    }

    /* הסטריפ הדק - שורה אחת מתחת לקצה, רוחב 1200px וממורכז */
    .exam-strip-container {
        width: 100%;
        display: flex;
        justify-content: center;
        background-color: transparent;
        margin-top: 15px; /* שורה אחת מהקצה העליון */
        margin-bottom: 5px; /* רווח מינימלי מהפריים */
    }

    .exam-strip-content {
        width: 100%;
        max-width: 1200px; /* הגבלת רוחב כדי שלא ימרח */
        display: flex;
        justify-content: space-between;
        align-items: center;
        height: 30px;
        padding: 0 20px;
        direction: rtl;
    }

    .strip-logo { font-weight: bold; font-size: 1rem; color: black; flex: 1; text-align: right; }
    .strip-user { font-weight: bold; font-size: 1rem; color: black; flex: 1; text-align: center; }
    .strip-nav { flex: 1; text-align: left; }

    .nav-link-pure {
        color: black !important;
        text-decoration: none !important;
        font-weight: bold !important;
        font-size: 1rem;
    }
    .nav-link-pure:hover { text-decoration: underline !important; }

    /* פריסת ה-Iframe - צמוד לסטריפ */
    iframe {
        border: none !important;
        margin: 0 !important;
        padding: 0 !important;
    }
</style>
""", unsafe_allow_html=True)

# --- לוגיקה וניהול מצב ---
if "step" not in st.session_state:
    st.session_state.update({"user": None, "step": "login"})

def show_main_header():
    """הדר רגיל לתפריטים הראשיים (לא למבחן)"""
    st.markdown(f"""
        <div style="display:flex; align-items:center; gap:45px; margin: 20px auto; max-width:1200px; direction: rtl;">
            <div style="font-size:2.5rem; font-weight:bold;">🏠 מתווך בקליק</div>
            <div style="font-size:1.2rem; font-weight:900;">👤 <b>{st.session_state.user}</b></div>
        </div>
    """, unsafe_allow_html=True)

# --- ניתוב דפים ---

if st.session_state.step == "login":
    st.title("🏠 מתווך בקליק")
    u_in = st.text_input("שם מלא:")
    if st.button("כניסה") and u_in:
        st.session_state.user = u_in
        st.session_state.step = "menu"
        st.rerun()

elif st.session_state.step == "menu":
    show_main_header()
    c1, c2, _ = st.columns([1.5, 1.5, 3])
    with c1:
        if st.button("📚 לימוד לפי נושאים"):
            st.session_state.step = "study"
            st.rerun()
    with c2:
        if st.button("⏱️ גש/י למבחן"):
            st.session_state.step = "exam_frame"
            st.rerun()

elif st.session_state.step == "exam_frame":
    # הזרקת הסטריפ כ-HTML טהור - דק, ממורכז וצמוד
    st.markdown(f"""
        <div class="exam-strip-container">
            <div class="exam-strip-content">
                <div class="strip-logo">🏠 מתווך בקליק</div>
                <div class="strip-user">👤 {st.session_state.user}</div>
                <div class="strip-nav">
                    <a href="/?nav=menu" target="_self" class="nav-link-pure">לתפריט הראשי</a>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # הצגת הפריים של המבחן - צמוד לסטריפ ובפריסה מלאה
    exam_url = "https://fullrealestatebroker-yevuzewxde4obgrpgacrpc.streamlit.app/?embed=true"
    components.iframe(exam_url, height=1200, scrolling=True)

elif st.session_state.step == "study":
    show_main_header()
    if st.button("חזרה לתפריט הראשי"):
        st.session_state.step = "menu"
        st.rerun()

# --- סוף קובץ ---
