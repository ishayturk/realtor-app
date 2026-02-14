import streamlit as st
import google.generativeai as genai
import time

# --- הגדרות ליבה ---
st.set_page_config(page_title="מתווך בקליק", layout="centered")

# עיצוב RTL מקצועי - הכל מיושר לימין, כותרות במרכז
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"], .main, .block-container { 
        direction: rtl !important; 
        text-align: right !important; 
    }
    h1, h2, h3, .centered-text { 
        text-align: center !important; 
        width: 100%; 
        display: block; 
        color: #1E88E5;
    }
    .stButton > button { 
        width: 100%; 
        border-radius: 8px; 
        font-weight: bold; 
        margin-top: 10px; 
    }
    input { 
        direction: rtl !important; 
        text-align: right !important; 
    }
    .lesson-content { 
        background: white; 
        padding: 20px; 
        border-radius: 12px; 
        border-right: 5px solid #1E88E5; 
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        line-height: 1.8; 
        color: #333;
        direction: rtl;
    }
    /* תיקון ליישור טקסט בתוך רדיו וצ'קבוקס */
    [data-testid="stMarkdownContainer"] p {
        text-align: right !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- ניהול זיכרון (Session State) ---
if "step" not in st.session_state:
    st.session_state.update({
        "step": "login", 
        "user": "", 
        "topic": "", 
        "lessons": {}, 
        "exam_idx": 0, 
        "answers": {}
    })

# --- פונקציות AI (Gemini 2.0 Flash) ---
def get_ai_lesson(topic):
    if topic in st.session_state.lessons:
        return st.session_state.lessons[topic]
    
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-2.0-flash')
        prompt = f"כתוב שיעור הכנה למבחן המתווכים על {topic} בעברית. כלול סעיפי חוק רלוונטיים והסברים פשוטים."
        response = model.generate_content(prompt)
        st.session_state.lessons[topic] = response.text
        return response.text
    except Exception as e:
        return f"שגיאה בתקשורת עם השרת: {str(e)}"

# --- כותרת קבועה ---
st.markdown("<h1>🏠 מתווך בקליק</h1>", unsafe_allow_html=True)
st.write("---")

# --- ניהול הצעדים באפליקציה ---

# 1. דף כניסה
if st.session_state.step == "login":
    st.markdown("<h3 class='centered-text'>ברוכים הבאים</h3>", unsafe_allow_html=True)
    name = st.text_input("הכנס שם מלא לכניסה:", placeholder="ישראל ישראלי")
    if st.button("התחבר 🔓"):
        if name:
            st.session_state.user = name
            st.session_state.step = "menu"
            st.rerun()

# 2. תפריט ראשי
elif st.session_state.step == "menu":
    # תיקון יישור השם - שימוש ב-HTML למניעת בריחה שמאלה
    st.markdown(f"<div style='direction: rtl; text-align: right;'><h3>שלום, {st.session_state.user} 👋</h3></div>", unsafe_allow_html=True)
    st.markdown("<p class='centered-text'>מה תרצה לעשות היום?</p>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📚 לימוד עיוני"):
            st.session_state.step = "select_topic"
            st.rerun()
    with col2:
        if st.button("📝 מבחן תרגול"):
            st.session_state.step = "exam"
            st.rerun()

# 3. בחירת נושא
elif st.session_state.step == "select_topic":
    st.markdown("<h3>בחר נושא ללימוד</h3>", unsafe_allow_html=True)
    topics = ["חוק המתווכים", "חוק המקרקעין", "חוק הגנת הצרכן", "חוק החוזים", "מושגי יסוד בנדל\"ן"]
    selected = st.selectbox("נושאים זמינים:", topics)
    
    if st.button("פתח שיעור 📖"):
        st.session_state.topic = selected
        st.session_state.step = "view_lesson"
        st.rerun()
    
    if st.button("🏠 חזרה לתפריט"):
        st.session_state.step = "menu"
        st.rerun()

# 4. הצגת שיעור
elif st.session_state.step == "view_lesson":
    st.markdown(f"<h2>{st.session_state.topic}</h2>", unsafe_allow_html=True)
    
    with st.spinner("מטעין תוכן מקצועי מ-Gemini 2.0..."):
        content = get_ai_lesson(st.session_state.topic)
    
    st.markdown(f"<div class='lesson-content'>{content}</div>", unsafe_allow_html=True)
    
    if st.button("⬅️ חזרה לבחירת נושא"):
        st.session_state.step = "select_topic"
        st.rerun()

# 5. מבחן תרגול
elif st.session_state.step == "exam":
    st.markdown("<h2>מבחן תרגול</h2>", unsafe_allow_html=True)
    st.info("שאלה 1 מתוך 25 (דוגמה)")
    
    st.markdown("<p style='text-align: right; font-weight: bold;'>מי מהבאים רשאי לעסוק בתיווך מקרקעין בישראל?</p>", unsafe_allow_html=True)
    st.radio("בחר תשובה:", [
        "כל אזרח מעל גיל 18", 
        "רק מי שיש לו תואר במשפטים", 
        "רק בעל רישיון תיווך בתוקף ממשרד המשפטים", 
        "מי שעוסק במכירת דירות מעל 5 שנים"
    ], index=None)
    
    if st.button("🏠 חזרה לתפריט"):
        st.session_state.step = "menu"
        st.rerun()
