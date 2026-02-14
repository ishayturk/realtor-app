import streamlit as st
import google.generativeai as genai

# 1. הגדרות דף ועיצוב
st.set_page_config(page_title="מתווך בקליק", layout="centered")

st.markdown("""
    <style>
    [data-testid="stSidebar"] { display: none; }
    .main, .block-container { direction: rtl; text-align: right; }
    .stMarkdown, p, li, h1, h2, h3, span, label { direction: rtl !important; text-align: right !important; }
    
    .lesson-header {
        background-color: #e3f2fd;
        padding: 20px;
        border-radius: 10px;
        border-right: 8px solid #1E88E5;
        margin-bottom: 25px;
    }
    
    .quiz-box {
        background-color: #fff9c4;
        padding: 20px;
        border-radius: 10px;
        border: 1px dashed #fbc02d;
        margin-top: 20px;
    }
    
    div.stButton > button { width: 100%; border-radius: 10px; height: 3em; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# 2. אתחול משתנים
if "user_name" not in st.session_state: st.session_state.user_name = ""
if "history" not in st.session_state: st.session_state.history = []
if "lesson_data" not in st.session_state: st.session_state.lesson_data = ""
if "current_title" not in st.session_state: st.session_state.current_title = ""
if "ready_quiz" not in st.session_state: st.session_state.ready_quiz = ""

# 3. חיבור ל-AI
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-2.5-flash')

# מסך כניסה
if not st.session_state.user_name:
    st.title("🎓 ברוכים הבאים")
    name = st.text_input("איך קוראים לך?")
    if st.button("כניסה"):
        if name:
            st.session_state.user_name = name
            st.rerun()
else:
    st.title(f"שלום, {st.session_state.user_name}")

    topic = st.selectbox("בחר נושא ללימוד:", ["חוק המתווכים", "חוק המקרקעין", "דיני חוזים", "דיני תכנון ובנייה"])

    if st.button("התחל למידה"):
        # איפוס נתונים ישנים
        st.session_state.lesson_data = ""
        st.session_state.ready_quiz = ""
        
        # מספור השיעור
        num = len(st.session_state.history) + 1
        st.session_state.current_title = f"שיעור {num}: {topic}"
        
        progress = st.progress(0)
        status = st.empty()
        
        try:
            # ייצור שיעור
            status.write("מכין את השיעור...")
            progress.progress(40)
            lesson = model.generate_content(f"כתוב שיעור ממוקד על {topic} למבחן המתווכים. ללא שאלות.")
            st.session_state.lesson_data = lesson.text
            
            # ייצור מבחן ברקע
            status.write("מכין מבחן תרגול ברקע...")
            progress.progress(80)
            quiz = model.generate_content(f"צור 3 שאלות אמריקאיות על {topic} כולל פתרונות בסוף.")
            st.session_state.ready_quiz = quiz.text
            
            if topic not in st.session_state.history:
                st.session_state.history.append(topic)
                
            progress.progress(100)
            status.empty()
            progress.empty()
            st.rerun()
            
        except Exception as e:
            st.error(f"תקלה: {e}")

    # הצגת התוכן
    if st.session_state.lesson_data:
        st.markdown(f'<div class="lesson-header"><h1>{st.session_state.current_title}</h1></div>', unsafe_allow_html=True)
        st.markdown(f'<div dir="rtl">{st.session_state.lesson_data}</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        if st.button("אני מוכן למבחן על החומר"):
            st.markdown('<div class="quiz-box" dir="rtl"><h3>📝 מבחן תרגול:</h3>' + st.session_state.ready_quiz + '</div>', unsafe_allow_html=True)

    # היסטוריה בתחתית
    st.markdown("<br><br>", unsafe_allow_html=True)
    if st.session_state.history:
        if st.button("📚 לחץ כאן לצפייה בהיסטוריית הלמידה שלך"):
            st.info(f"הנושאים שלמדת עד כה: {', '.join(st.session_state.history)}")

    if st.session_state.lesson_data and st.button("חזרה לתפריט הראשי"):
        st.session_state.lesson_data = ""
        st.session_state.ready_quiz = ""
        st.rerun()
