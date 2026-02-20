import streamlit as st
import streamlit.components.v1 as components
import google.generativeai as genai
import json, re

# הגדרות דף - עוגן 1213
st.set_page_config(page_title="מתווך בקליק", layout="wide")

# CSS לניהול שני הפריימים והסטריפ
st.markdown("""
<style>
    /* הצמדה למעלה עם מרווח של שורה אחת */
    .block-container { padding-top: 1.5rem !important; padding-bottom: 0rem !important; }
    .stApp header { visibility: hidden; }
    
    /* הסטריפ העליון - הכי צר שאפשר */
    .slim-strip {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 5px 20px;
        background-color: white;
        border-bottom: none;
    }
    
    /* ביטול רווחים וקווים מפרידים בין הפריימים */
    hr { display: none !important; }
    .stIframe { margin-top: 0px !important; }
    
    * { direction: rtl; text-align: right; }
</style>
""", unsafe_allow_html=True)

# --- לוגיקת עוגן 1213 (ללא שינוי) ---
if "step" not in st.session_state:
    st.session_state.update({"user": None, "step": "login", "selected_topic": None})

SYLLABUS = {
    "חוק המתווכים": ["רישוי והגבלות", "הגינות וזהירות", "הזמנה ובלעדיות"],
    "חוק המקרקעין": ["בעלות וזכויות", "בתים משותפים", "הערות אזהרה"],
    "חוק החוזים": ["כריתת חוזה", "פגמים", "תרופות"]
}

# --- ניווט ---

if st.session_state.step == "login":
    st.title("🏠 מתווך בקליק")
    u = st.text_input("שם מלא:")
    if st.button("כניסה") and u:
        st.session_state.user = u
        st.session_state.step = "menu"
        st.rerun()

elif st.session_state.step == "menu":
    st.title("🏠 מתווך בקלי
