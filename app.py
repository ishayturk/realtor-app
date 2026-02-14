import streamlit as st
import google.generativeai as genai
import time

# --- הגדרות ליבה ---
st.set_page_config(page_title="מתווך בקליק", layout="centered")

# עיצוב RTL מקצועי עם יישור לימין וכותרות ממורכזות
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] { direction: rtl !important; text-align: right !important; }
    h1, h2, .stAlert { text-align: center !important; direction: rtl !important; }
    .stButton > button { width: 100%; border-radius: 8px; font-weight: bold; margin-top: 10px; }
    .lesson-content { 
        background: white; padding: 20px; border-radius: 12px; 
        border-right: 5px solid #1E88E5; box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        line-height: 1.8; color: #333;
    }
    div[data-testid="stExpander"] { direction: rtl !important; }
    </style>
    """, unsafe_allow_html=True)

# --- ניהול זיכרון (Session State) ---
if "step" not in st.session_state:
    st.session_state.update({
        "step": "login", "user": "", "topic": "", 
        "lessons": {}, "exam_idx": 0, "answers": {}
    })

# --- פונקציות AI ---
def get_ai_lesson(topic):
    if topic in st.session_state.lessons:
        return st.session_state.lessons[topic]
    
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-2.0-flash')
        prompt = f"כתוב שיעור הכנה למבחן המתווכים על {topic}. כלול סעיפי חוק רלוונטיים והסברים פשוטים."
        response = model.generate_content(prompt)
        st.session_state.lessons[topic] = response.text
        return response.text
    except Exception as e:
        return f"שגיאה בתקשורת: {str(e)}"

# --- מבנה האפליקציה ---

# כותרת קבועה בראש כל דף
st.markdown("<h1>🏠 מתווך בקליק</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>הכנה מקצועית למבחן רישוי מתווכים</p>", unsafe_allow_html=True)
st.write("---")

# 1. דף כניסה
if st.session_state.step == "login":
    name = st.text_input("הכנס שם מלא לכניסה:", placeholder="ישראל ישראלי")
    if st.button("התחבר"):
        if name:
            st.session_state.user = name
            st.session_state.step = "menu"
            st.rerun()

# 2. תפריט ראשי
elif st.session_state.step == "menu":
    st.markdown(f"### שלום, {st.session_state.user}")
    
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
    st.markdown("### בחר נושא ללימוד")
    topics = ["חוק המתווכים", "חוק המקרקעין", "חוק הגנת הצרכן", "חוק החוזים", "מושגי יסוד בנדל\"ן"]
    selected = st.selectbox("נושאים זמינים:", topics)
    
    if st.button("פתח שיעור 📖"):
        st.session_state.topic = selected
        st.session_state.step = "view_lesson"
        st.rerun()
    
    if st.button("חזרה לתפריט"):
        st.session_state.step = "menu"
        st.rerun()

# 4. הצגת שיעור
elif st.session_state.step == "view_lesson":
    st.markdown(f"## {st.session_state.topic}")
    
    # טעינה מהירה - אם קיים ב-Cache לא פונה ל-AI
    with st.spinner("מטעין תוכן מקצועי..."):
        content = get_ai_lesson(st.session_state.topic)
    
    st.markdown(f"<div class='lesson-content'>{content}</div>", unsafe_allow_html=True)
    
    if st.button("סיום וחזרה לבחירת נושא"):
        st.session_state.step = "select_topic"
        st.rerun()

# 5. מבחן (שלד מקצועי)
elif st.session_state.step == "exam":
    st.markdown("## מבחן תרגול")
    st.warning("בשלב זה המבחן כולל שאלות מהמאגר המובנה. האם תרצה לייבא שאלות מהרשת?")
    
    # דוגמה לשאלה
    st.info("שאלה 1: מהו התנאי היסודי לקבלת דמי תיווך?")
    st.radio("בחר תשובה:", ["רישיון בתוקף בלבד", "רישיון בתוקף, הזמנה בכתב והיות המתווך הגורם היעיל", "חתימה על בלעדיות", "הסכמה בעל פה"], index=None)
    
    if st.button("חזרה לתפריט"):
        st.session_state.step = "menu"
        st.rerun()
