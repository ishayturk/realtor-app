import streamlit as st
import google.generativeai as genai

# הגדרות עיצוב לימין
st.set_page_config(page_title="מתווך בקליק", layout="wide")
st.markdown("""
    <style>
    .stApp { direction: rtl; text-align: right; }
    h1, h2, h3, p, span, label { direction: rtl !important; text-align: right !important; }
    div.stButton > button { width: 100%; background-color: #1E88E5; color: white; border-radius: 8px; font-weight: bold; }
    [data-testid="stCodeBlock"] { direction: ltr !important; text-align: left !important; }
    </style>
    """, unsafe_allow_html=True)

# חיבור ל-API
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    # המודל הכי חדיש וזול (ללא צורך במנוי פרו)
    model = genai.GenerativeModel('gemini-2.0-flash')
else:
    st.error("חסר API Key ב-Secrets")

if "view_mode" not in st.session_state: st.session_state.view_mode = "login"

if st.session_state.view_mode == "login":
    st.title("🎓 מתווך בקליק")
    name = st.text_input("הזן שם:")
    if st.button("כניסה"):
        if name:
            st.session_state.user_name = name
            st.session_state.view_mode = "setup"
            st.rerun()

elif st.session_state.view_mode == "setup":
    st.title(f"מה נלמד היום, {st.session_state.user_name}?")
    topic = st.selectbox("בחר נושא:", ["חוק המתווכים", "חוק המקרקעין", "דיני חוזים", "דיני תכנון ובנייה"])
    
    if st.button("התחל ללמוד"):
        try:
            with st.spinner("מייצר שיעור ומבחן..."):
                prompt = f"כתוב שיעור מפורט בעברית על {topic} למבחן המתווכים. בסוף השיעור הוסף 3 שאלות אמריקאיות."
                res = model.generate_content(prompt)
                st.session_state.lesson_data = res.text
                st.session_state.view_mode = "lesson"
                st.rerun()
        except Exception as e:
            if "429" in str(e):
                st.warning("המערכת עדיין מעדכנת את חשבון התשלום שלך. נסה שוב בעוד כחצי שעה.")
            else:
                st.error(f"שגיאה: {e}")

elif st.session_state.view_mode == "lesson":
    st.title("חומר הלימוד")
    st.markdown(st.session_state.lesson_data)
    if st.button("חזרה לתפריט"):
        st.session_state.view_mode = "setup"
        st.rerun()
