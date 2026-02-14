import streamlit as st
import google.generativeai as genai

# --- 1. הגדרות דף ויישור לימין ---
st.set_page_config(page_title="מתווך בקליק", layout="centered")

st.markdown("""
    <style>
    [data-testid="stAppViewContainer"], .main, .block-container { direction: rtl !important; text-align: right !important; }
    h1, h2, h3 { text-align: center !important; }
    .stButton > button { width: 100%; font-weight: bold; height: 3em; }
    .lesson-box { background: white; padding: 20px; border-radius: 10px; border: 1px solid #ddd; direction: rtl; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. אתחול משתנים (בצורה שלא יכולה להיכשל) ---
if "step" not in st.session_state: st.session_state.step = "login"
if "user" not in st.session_state: st.session_state.user = ""
if "topic" not in st.session_state: st.session_state.topic = ""
if "current_lesson" not in st.session_state: st.session_state.current_lesson = ""

# --- 3. פונקציית AI (Gemini 2.0 Flash) ---
def get_ai_response(topic):
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content(f"כתוב שיעור למבחן המתווכים על {topic} בעברית.")
        return response.text
    except Exception as e:
        return f"שגיאה: {str(e)}"

# --- 4. לוגיקת דפים ---

st.markdown("<h1>🏠 מתווך בקליק</h1>", unsafe_allow_html=True)

if st.session_state.step == "login":
    name = st.text_input("שם מלא:")
    if st.button("כניסה"):
        if name:
            st.session_state.user = name
            st.session_state.step = "menu"
            st.rerun()

elif st.session_state.step == "menu":
    st.markdown(f"<h3 style='text-align: right;'>שלום, {st.session_state.user}</h3>", unsafe_allow_html=True)
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
        st.session_state.current_lesson = "" # איפוס
        st.session_state.step = "view_lesson"
        st.rerun()
    if st.button("חזרה"):
        st.session_state.step = "menu"
        st.rerun()

elif st.session_state.step == "view_lesson":
    st.markdown(f"<h2>{st.session_state.topic}</h2>", unsafe_allow_html=True)
    
    # טעינה אוטומטית ללא לופים
    if not st.session_state.current_lesson:
        with st.spinner("טוען תוכן מ-Gemini 2.0..."):
            st.session_state.current_lesson = get_ai_response(st.session_state.topic)
            st.rerun()
    
    st.markdown(f"<div class='lesson-box'>{st.session_state.current_lesson}</div>", unsafe_allow_html=True)
    
    if st.button("חזרה"):
        st.session_state.step = "select_topic"
        st.rerun()

elif st.session_state.step == "exam":
    st.write("מבחן (בהקמה)")
    if st.button("חזרה"):
        st.session_state.step = "menu"
        st.rerun()
