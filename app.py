import streamlit as st
import google.generativeai as genai

# --- 1. הגדרות ליבה ---
st.set_page_config(page_title="מתווך בקליק", layout="centered")

# CSS ליישור ימין, מרכוז כותרות וניקוי עיצובי
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"], .main, .block-container { direction: rtl !important; text-align: right !important; }
    h1, h2, h3 { text-align: center !important; color: #1E88E5; width: 100%; }
    .stButton > button { width: 100%; border-radius: 8px; font-weight: bold; height: 3em; }
    .lesson-content { background: white; padding: 20px; border-radius: 12px; border-right: 5px solid #1E88E5; line-height: 1.8; color: #333; direction: rtl; }
    div[data-testid="stExpander"] { direction: rtl !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. אתחול משתני מערכת (מניעת AttributeError) ---
if "step" not in st.session_state:
    st.session_state.step = "login"
if "user" not in st.session_state:
    st.session_state.user = ""
if "topic" not in st.session_state:
    st.session_state.topic = ""
if "current_lesson" not in st.session_state:
    st.session_state.current_lesson = ""

# --- 3. פונקציית AI (שימוש ב-Gemini 2.0 בלבד) ---
def fetch_lesson(topic):
    try:
        if "GEMINI_API_KEY" not in st.secrets:
            return "שגיאה: מפתח API חסר בהגדרות ה-Secrets."
        
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        # שימוש במודל 2.0 בלבד כפי שדרשת
        model = genai.GenerativeModel('gemini-2.0-flash')
        resp = model.generate_content(f"כתוב שיעור מפורט למבחן המתווכים על {topic} בעברית. כלול סעיפי חוק רלוונטיים.")
        return resp.text
    except Exception as e:
        return f"שגיאה בתקשורת עם Gemini 2.0: {str(e)}"

# כותרת קבועה
st.markdown("<h1>🏠 מתווך בקליק</h1>", unsafe_allow_html=True)

# --- 4. ניווט וניהול דפים ---

# דף כניסה
if st.session_state.step == "login":
    name = st.text_input("הכנס שם מלא לכניסה:")
    if st.button("התחבר"):
        if name:
            st.session_state.user = name
            st.session_state.step = "menu"
            st.rerun()

# תפריט ראשי
elif st.session_state.step == "menu":
    st.markdown(f"<div style='text-align: right;'><h3>שלום, {st.session_state.user} 👋</h3></div>", unsafe_allow_html=True)
    if st.button("📚 לימוד עיוני"):
        st.session_state.step = "select_topic"
        st.rerun()
    if st.button("📝 מבחן תרגול"):
        st.session_state.step = "exam"
        st.rerun()

# בחירת נושא
elif st.session_state.step == "select_topic":
    st.markdown("<h3>בחר נושא ללימוד</h3>", unsafe_allow_html=True)
    topic = st.selectbox("נושאים:", ["חוק המתווכים", "חוק המקרקעין", "חוק המכר (דירות)", "חוק החוזים"])
    
    if st.button("📖 פתח שיעור"):
        st.session_state.topic = topic
        st.session_state.current_lesson = "" # איפוס שיעור קודם
        st.session_state.step = "view_lesson"
        st.rerun()
    
    if st.button("🏠 חזרה"):
        st.session_state.step = "menu"
        st.rerun()

# הצגת שיעור
elif st.session_state.step == "view_lesson":
    st.markdown(f"<h2>{st.session_state.topic}</h2>", unsafe_allow_html=True)
    
    # טעינה אוטומטית ללא לחיצה נוספת
    if not st.session_state.current_lesson:
        with st.spinner("Gemini 2.0 מייצר עבורך תוכן מקצועי..."):
            st.session_state.current_lesson = fetch_lesson(st.session_state.topic)
            st.rerun() 
    
    st.markdown(f"<div class='lesson-content'>{st.session_state.current_lesson}</div>", unsafe_allow_html=True)
    
    if st.button("⬅️ חזרה לבחירת נושא"):
        st.session_state.step = "select_topic"
        st.rerun()

# מבחן
elif st.session_state.step == "exam":
    st.markdown("<h2>מבחן תרגול</h2>", unsafe_allow_html=True)
    st.info("כאן נטמיע את המאגר הרשמי.")
    if st.button("🏠 חזרה לתפריט"):
        st.session_state.step = "menu"
        st.rerun()
