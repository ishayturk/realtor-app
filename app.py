import streamlit as st
import streamlit.components.v1 as components
import google.generativeai as genai

# הגדרות דף - עוגן 1213
st.set_page_config(
    page_title="מתווך בקליק",
    layout="wide"
)

# CSS לניהול שני הפריימים וביטול קווים
# פיצול מחרוזות ארוכות לטובת Git
css = """
<style>
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 0rem !important;
    }
    .stApp header {
        visibility: hidden;
    }
    .slim-strip {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 10px 20px;
        background-color: white;
    }
    hr {
        display: none !important;
    }
    div[data-testid="stVerticalBlock"] > div {
        border: none !important;
    }
    * {
        direction: rtl;
        text-align: right;
    }
</style>
"""
st.markdown(css, unsafe_allow_html=True)

# אתחול Session State
if "step" not in st.session_state:
    st.session_state.update({
        "user": None,
        "step": "login",
        "selected_topic": None
    })

# --- ניווט ---

if st.session_state.step == "login":
    st.title("🏠 מתווך בקליק")
    u = st.text_input("שם מלא:")
    if st.button("כניסה") and u:
        st.session_state.user = u
        st.session_state.step = "menu"
        st.rerun()

elif st.session_state.step == "menu":
    st.title("🏠 מתווך בקליק")
    st.subheader(f"👤 שלום, {st.session_state.user}")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("📚 לימוד לפי נושאים"):
            st.session_state.step = "study"
            st.rerun()
    with c2:
        if st.button("⏱️ גש/י למבחן"):
            st.session_state.step = "exam_frame"
            st.rerun()

# --- מצב המבחן: שני פריימים ---
elif st.session_state.step == "exam_frame":
