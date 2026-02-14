import streamlit as st
import google.generativeai as genai

# --- הגדרות ליבה ---
st.set_page_config(page_title="מתווך בקליק", layout="centered")

# CSS ליישור לימין ומרכוז כותרות
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"], .main, .block-container { direction: rtl !important; text-align: right !important; }
    h1, h2, h3 { text-align: center !important; color: #1E88E5; width: 100%; }
    .stButton > button { width: 100%; border-radius: 8px; font-weight: bold; }
    .lesson-content { background: white; padding: 20px; border-radius: 12px; border-right: 5px solid #1E88E5; line-height: 1.8; color: #333; direction: rtl; }
    </style>
    """, unsafe_allow_html=True)

# --- ניהול State ---
if "step" not in st.session_state:
    st.session_state.update({"step": "login", "user": "", "topic": "", "current_lesson": ""})

# --- פונקציית AI ---
def fetch_lesson(topic):
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-2.0-flash')
        resp = model.generate_content(f"כתוב שיעור מפורט למבחן המתווכים על {topic} בעברית")
        return resp.text
    except Exception as e:
        return f"שגיאה: {str(e)}"

# כותרת קבועה
st.markdown("<h1>🏠 מתווך בקליק</h1>", unsafe_allow_html=True)

# --- ניווט ---
if st.session_state.step == "login":
    name = st.text_input("הכנס שם מלא:")
    if st.button("כניסה"):
        if name:
            st.session_state.user = name
            st.session_state.step = "menu"
            st.rerun()

elif st.session_state.step == "menu":
    st.markdown(f"<div style='text-align: right;'><h3>שלום, {st.session_state.user}</h3></div>", unsafe_allow_html=True)
    if st.button("📚 לימוד עיוני"):
        st.session_state.step = "select_topic"
        st.rerun()
    if st.button("📝 מבחן תרגול"):
        st.session_state.step = "exam"
        st.rerun()

elif st.session_state.step == "select_topic":
    topic = st.selectbox("בחר נושא:", ["חוק המתווכים", "חוק המקרקעין", "חוק החוזים"])
    if st.button("פתח שיעור"):
        st.session_state.topic = topic
        # מנקה שיעור קודם ומכין את הקרקע לטעינה אוטומטית
        st.session_state.current_lesson = "" 
        st.session_state.step = "view_lesson"
        st.rerun()
    if st.button("חזרה"):
        st.session_state.step = "menu"
        st.rerun()

elif st.session_state.step == "view_lesson":
    st.markdown(f"<h2>{st.session_state.topic}</h2>", unsafe_allow_html=True)
    
    # טעינה אוטומטית מיד עם הכניסה לדף
    if not st.session_state.current_lesson:
        with st.spinner("מייצר שיעור..."):
            st.session_state.current_lesson = fetch_lesson(st.session_state.topic)
            st.rerun() # מרענן פעם אחת להצגת התוכן מיד
    
    st.markdown(f"<div class='lesson-content'>{st.session_state.current_lesson}</div>", unsafe_allow_html=True)
    
    if st.button("חזרה לבחירת נושא"):
        st.session_state.step = "select_topic"
        st.rerun()

elif st.session_state.step == "exam":
    st.markdown("<h2>מבחן תרגול</h2>", unsafe_allow_html=True)
    if st.button("חזרה"):
        st.session_state.step = "menu"
        st.rerun()
