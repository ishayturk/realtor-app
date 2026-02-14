import streamlit as st
import google.generativeai as genai
import re

# 1. הגדרות RTL ועיצוב
st.set_page_config(page_title="מתווך בקליק", layout="wide")

st.markdown("""
<style>
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stMarkdownContainer"], p, li, h1, h2, h3, div {
        direction: rtl !important; text-align: right !important;
    }
    ul, ol { direction: rtl !important; text-align: right !important; padding-right: 1.5rem !important; list-style-position: inside !important; }
    .sidebar-top-branding { text-align: center; margin-top: -50px; margin-bottom: 20px; border-bottom: 1px solid #eee; }
    .sidebar-logo-icon { font-size: 45px; }
    .sidebar-app-name { color: #1E88E5; font-size: 24px; font-weight: 800; margin-top: -10px; }
</style>
""", unsafe_allow_html=True)

# 2. פונקציית הקסם - CACHE
# זה מבטיח שאם השיעור נוצר פעם אחת, הוא יישלף מהזיכרון תוך 0 שניות
@st.cache_resource(show_spinner=False)
def get_lesson_content(topic):
    model = genai.GenerativeModel('gemini-2.0-flash')
    prompt = f"כתוב שיעור מפורט למבחן המתווכים על {topic}. השתמש בבולטים וסעיפי חוק."
    response = model.generate_content(prompt)
    return response.text

# 3. ניהול Session State
if "view_mode" not in st.session_state:
    st.session_state.update({"view_mode": "login", "user_name": "", "current_topic": ""})

if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# 4. סיידבר
with st.sidebar:
    st.markdown('<div class="sidebar-top-branding"><div class="sidebar-logo-icon">🏠</div><div class="sidebar-app-name">מתווך בקליק</div></div>', unsafe_allow_html=True)
    if st.session_state.user_name:
        st.write(f"**שלום, {st.session_state.user_name}**")
        if st.button("📚 נושא חדש"):
            st.session_state.update({"view_mode": "setup", "current_topic": ""})
            st.rerun()

# 5. לוגיקה
if st.session_state.view_mode == "login":
    name = st.text_input("שם מלא:")
    if st.button("כניסה"):
        if name: st.session_state.user_name = name; st.session_state.view_mode = "setup"; st.rerun()

elif st.session_state.view_mode == "setup":
    topics = ["חוק המתווכים", "חוק המקרקעין", "חוק המכר (דירות)", "חוק הגנת הצרכן"]
    t = st.selectbox("בחר נושא:", topics)
    if st.button("טען שיעור"):
        st.session_state.current_topic = t
        st.session_state.view_mode = "lesson_view"
        st.rerun()

elif st.session_state.view_mode == "lesson_view":
    st.header(st.session_state.current_topic)
    
    # כאן קורה הקסם: אם השיעור בזיכרון, הוא עולה מיד. אם לא, Gemini יוצר אותו פעם אחת בלבד.
    with st.spinner("שולף שיעור מהמאגר..."):
        lesson_text = get_lesson_content(st.session_state.current_topic)
    
    st.markdown(lesson_text)
    
    if st.button("🎯 בוא נתרגל"):
        st.info("כאן יבוא השאלון...")
