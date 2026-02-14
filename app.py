import streamlit as st
import google.generativeai as genai
import re

# הגדרות עיצוב בסיסיות לימין
st.set_page_config(page_title="מתווך בקליק", layout="wide")
st.markdown("""<style> .main { direction: rtl; text-align: right; } div.stButton > button { width: 100%; background-color: #1E88E5; color: white; } </style>""", unsafe_allow_html=True)

if "view_mode" not in st.session_state: st.session_state.view_mode = "login"

# חיבור ל-AI
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("חסר API Key ב-Secrets")

# פונקציה למציאת מודל עובד
def find_working_model():
    try:
        # פקודה שבודקת מה גוגל מרשה לנו לראות
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                return genai.GenerativeModel(m.name)
    except Exception as e:
        st.error(f"שגיאה בסריקת מודלים: {e}")
    return None

model = find_working_model()

# --- דף כניסה ---
if st.session_state.view_mode == "login":
    st.title("🎓 מתווך בקליק")
    name = st.text_input("הזן שם:")
    if st.button("כניסה"):
        st.session_state.user_name = name
        st.session_state.view_mode = "setup"
        st.rerun()

# --- דף בחירת נושא ---
elif st.session_state.view_mode == "setup":
    st.title(f"מה נלמד היום, {st.session_state.get('user_name', '')}?")
    topic = st.selectbox("בחר נושא:", ["חוק המתווכים", "חוק המקרקעין", "דיני חוזים"])
    
    if st.button("התחל ללמוד"):
        if not model:
            st.error("לא נמצא מודל תקין. וודא שעדכנת את requirements.txt")
        else:
            try:
                with st.spinner("מייצר תוכן..."):
                    res = model.generate_content(f"כתוב שיעור קצר על {topic} למבחן המתווכים.")
                    st.session_state.lesson_data = res.text
                    st.session_state.view_mode = "lesson"
                    st.rerun()
            except Exception as e:
                st.error(f"שגיאה: {e}")

# --- דף שיעור ---
elif st.session_state.view_mode == "lesson":
    st.title("חומר לימוד")
    st.write(st.session_state.get("lesson_data", ""))
    if st.button("חזרה להתחלה"):
        st.session_state.view_mode = "setup"
        st.rerun()
