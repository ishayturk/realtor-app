# ==========================================
# Project: מתווך בקליק | Version: 1213-Fixed
# ==========================================
import streamlit as st
import streamlit.components.v1 as components
import google.generativeai as genai
import json, re

st.set_page_config(page_title="מתווך בקליק", layout="wide")

# CSS לסטריפ עליון צמוד לתקרה ללא רווחים
st.markdown("""
<style>
    * { direction: rtl; text-align: right; }
    .stApp header { visibility: hidden; }
    /* ביטול פאדינג מובנה של סטרימליט כדי שהסטריפ יהיה למעלה */
    .block-container { 
        padding-top: 0px !important; 
        padding-bottom: 0px !important;
    }
    .slim-strip {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 10px 20px;
        background-color: #f8f9fa;
        border-bottom: 1px solid #ddd;
        margin-top: 10px; /* שורה אחת מתחת לקצה */
    }
    .stButton>button { 
        width: 100%; border-radius: 8px; 
        font-weight: bold; height: 3em; 
    }
    .v-footer {
        text-align: center; color: rgba(255, 255, 255, 0.1);
        font-size: 0.7em; margin-top: 50px; width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# ... (פונקציות AI וסילבוס מקוריות מ-1213 נשמרות כאן ללא שינוי) ...

# אתחול Session State
if "step" not in st.session_state:
    st.session_state.update({
        "user": None, "step": "login", "q_count": 0, 
        "quiz_active": False, "show_ans": False, 
        "lesson_txt": "", "q_data": None, 
        "correct_answers": 0, "quiz_finished": False
    })

# --- ניהול דפים ---

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
            st.session_state.step = "exam_mode"; st.rerun()

elif st.session_state.step == "exam_mode":
    # הסטריפ העליון (פריים 1)
    st.markdown(f"""
    <div class="slim-strip">
        <div style="font-weight:bold; font-size:1.2em;">🏠 מתווך בקליק</div>
        <div style="font-size:1.1em;">👤 {st.session_state.user}</div>
        <div></div>
    </div>
    """, unsafe_allow_html=True)
    
    # כפתור חזרה בנפרד (כדי שיהיה פונקציונלי בסטרימליט)
    c1, c2, c3 = st.columns([4, 4, 2])
    with c3:
        if st.button("↩️ לתפריט הראשי"):
            st.session_state.step = "menu"; st.rerun()

    # האפליקציה השנייה (פריים 2) - הלינק הנכון
    exam_url = "https://fullrealestatebroker-yevuzewxde4obgrpgacrpc.streamlit.app/?embedded=true"
    components.iframe(exam_url, height=1000, scrolling=True)

# ... (יתר הקוד המקורי של study ו-lesson_run מ-1213 ממשיך כאן) ...
