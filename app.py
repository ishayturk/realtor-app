import streamlit as st
import google.generativeai as genai
import re

# 1. עיצוב CSS אגרסיבי ליישור לימין (RTL)
st.set_page_config(page_title="מתווך בקליק", layout="wide")

st.markdown("""
    <style>
    /* כפייה של כיוון ימין-לשמאל על כל העמוד */
    .stApp, div[data-testid="stAppViewContainer"], .main {
        direction: rtl !important;
        text-align: right !important;
    }

    /* יישור כל כותרת, פסקה ופריט רשימה לימין */
    h1, h2, h3, p, li, span, label, div {
        direction: rtl !important;
        text-align: right !important;
    }

    /* תיקון ספציפי לתיבות קלט (Input) ובחירה (Select) */
    .stTextInput input, .stSelectbox div {
        direction: rtl !important;
        text-align: right !important;
    }

    /* החרגה של תיבות קוד: הן חייבות להישאר משמאל לימין */
    [data-testid="stCodeBlock"], [data-testid="stCodeBlock"] * {
        direction: ltr !important;
        text-align: left !important;
    }

    /* עיצוב כפתורים */
    div.stButton > button {
        width: 100%;
        background-color: #1E88E5;
        color: white;
        border-radius: 8px;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. ניהול מצב האפליקציה
if "view_mode" not in st.session_state: st.session_state.view_mode = "login"

# 3. חיבור ל-AI ומציאת מודל זמין
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    
    # פונקציה למציאת המודל שהכי "רוצה" לעבוד
    def get_working_model():
        try:
            # אנחנו מנסים למצוא מודל שמאפשר ייצור תוכן
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    return genai.GenerativeModel(m.name)
        except:
            return genai.GenerativeModel('gemini-1.5-flash')
    model = get_working_model()
else:
    st.error("חסר API Key ב-Secrets")

# --- דף כניסה ---
if st.session_state.view_mode == "login":
    st.title("🎓 מתווך בקליק")
    name = st.text_input("הזן שם כדי להתחיל:")
    if st.button("כניסה"):
        if name:
            st.session_state.user_name = name
            st.session_state.view_mode = "setup"
            st.rerun()

# --- דף בחירת נושא ---
elif st.session_state.view_mode == "setup":
    st.title(f"מה נלמד היום, {st.session_state.get('user_name', '')}?")
    topic = st.selectbox("בחר נושא:", ["חוק המתווכים", "חוק המקרקעין", "דיני חוזים", "דיני תכנון ובנייה"])
    
    if st.button("התחל ללמוד"):
        try:
            with st.spinner("מייצר שיעור..."):
                res = model.generate_content(f"כתוב שיעור מפורט בעברית על {topic} למבחן המתווכים.")
                st.session_state.lesson_data = res.text
                st.session_state.view_mode = "lesson"
                st.rerun()
        except Exception as e:
            st.error(f"שגיאה בחיבור: {e}")

# --- דף שיעור ---
elif st.session_state.view_mode == "lesson":
    st.title("חומר הלימוד")
    st.markdown(st.session_state.get("lesson_data", ""))
    st.markdown("---")
    if st.button("חזרה לבחירת נושא"):
        st.session_state.view_mode = "setup"
        st.rerun()
