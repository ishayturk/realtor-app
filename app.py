import streamlit as st
import streamlit.components.v1 as components

# הגדרות דף - עוגן 1213
st.set_page_config(
    page_title="מתווך בקליק",
    layout="wide"
)

# CSS לניהול שני הפריימים
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
    st.session_state.step = "login"
    st.session_state.user = None

# --- ניהול דפים ---

if st.session_state.step == "login":
    st.title("🏠 מתווך בקליק")
    u = st.text_input("שם מלא:")
    if st.button("כניסה") and u:
        st.session_state.user = u
        st.session_state.step = "menu"
        st.rerun()

elif st.session_state.step == "menu":
    st.title("🏠 מתווך בקליק")
    st.subheader(f"שלום, {st.session_state.user}")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("📚 לימוד לפי נושאים"):
            st.session_state.step = "study"
            st.rerun()
    with c2:
        if st.button("⏱️ גש/י למבחן"):
            st.session_state.step = "exam_frame"
            st.rerun()

elif st.session_state.step == "exam_frame":
    # פריים עליון: הסטריפ הצר
    st.markdown('<div class="slim-strip">', unsafe_allow_html=True)
    col_logo, col_name, col_back = st.columns([1, 2, 1])
    with col_logo:
        st.markdown("**🏠 מתווך בקליק**")
    with col_name:
        st.markdown(
            f"<p style='text-align:center;'>👤 נבחן: {st.session_state.user}</p>",
            unsafe_allow_html=True
        )
    with col_back:
        if st.button("↩️ חזרה לתפריט"):
            st.session_state.step = "menu"
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # פריים תחתון: האפליקציה השנייה
    u_base = "https://ishayturk-realtor-app-app-kk1gme"
    u_full = f"{u_base}.streamlit.app/?embedded=true"
    components.iframe(u_full, height=800, scrolling=True)

elif st.session_state.step == "study":
    st.title("📚 בחירת נושא")
    if st.button("חזרה"):
        st.session_state.step = "menu"
        st.rerun()

st.markdown(
    '<p style="text-align:center; color:grey; font-size:0.7rem;">'
    'Version 1213-Final-Fix</p>',
    unsafe_allow_html=True
)
