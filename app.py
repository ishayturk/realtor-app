import streamlit as st
import google.generativeai as genai
import time

# הגדרות דף
st.set_page_config(page_title="מתווך בקליק", layout="centered")

# CSS מקצועי - יישור לימין ועיצוב נקי ללא סיידבר
st.markdown("""
    <style>
    [data-testid="stSidebar"] { display: none; } /* ביטול הסיידבר שנדחף לשמאל */
    .main, .block-container { direction: rtl; text-align: right; }
    .stMarkdown, p, li, h1, h2, h3, span, label { direction: rtl !important; text-align: right !important; }
    div.stButton > button { width: 100%; border-radius: 10px; height: 3em; font-weight: bold; }
    .history-link { color: #1E88E5; cursor: pointer; text-decoration: underline; }
    .quiz-container { background-color: #f9f9f9; padding: 20px; border-radius: 15px; border: 1px solid #ddd; margin-top: 20px; }
    </style>
    """, unsafe_allow_html=True)

# אתחול משתני מערכת
if "user_name" not in st.session_state: st.session_state.user_name = ""
if "history" not in st.session_state: st.session_state.history = []
if "lesson_data" not in st.session_state: st.session_state.lesson_data = ""
if "quiz_ready" not in st.session_state: st.session_state.quiz_ready = False
if "show_history" not in st.session_state: st.session_state.show_history = False

# הגדרת AI
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

    # תפריט נושאים
    topic = st.selectbox("בחר נושא ללימוד:", ["חוק המתווכים", "חוק המקרקעין", "דיני חוזים"])

    # כפתור התחל שיעור - הופך ללא פעיל בזמן עבודה
    if st.button("התחל שיעור", disabled=st.session_state.lesson_data != "" and not st.session_state.quiz_ready):
        st.session_state.quiz_ready = False
        st.session_state.lesson_data = ""
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        status_text.write("מתחבר למרצה הדיגיטלי...")
        
        try:
            # שלב 1: יצירת השיעור
            progress_bar.progress(30)
            status_text.write("מכין את חומר הלימוד...")
            lesson_prompt = f"כתוב שיעור ממוקד על {topic} למבחן המתווכים. ללא שאלות בסוף."
            lesson = model.generate_content(lesson_prompt)
            st.session_state.lesson_data = lesson.text
            
            # שלב 2: הכנת המבחן ברקע (מוסתר מהמשתמש)
            progress_bar.progress(70)
            status_text.write("בונה מבחן מותאם עבורך...")
            quiz_prompt = f"צור 3 שאלות אמריקאיות על {topic}. פורמט: שאלה|אופציה1|אופציה2|אופציה3|אופציה4|מספר תשובה נכונה(1-4)"
            quiz = model.generate_content(quiz_prompt)
            st.session_state.quiz_raw = quiz.text
            
            progress_bar.progress(100)
            status_text.empty()
            progress_bar.empty()
            
            if topic not in st.session_state.history:
                st.session_state.history.append(topic)
            st.session_state.quiz_ready = True
            st.rerun()
            
        except Exception as e:
            st.error(f"תקלה: {e}")

    # הצגת השיעור
    if st.session_state.lesson_data:
        st.markdown("### 📖 חומר הלימוד")
        st.markdown(f'<div dir="rtl">{st.session_state.lesson_data}</div>', unsafe_allow_html=True)
        st.markdown("---")

    # הצגת המבחן האינטראקטיבי
    if st.session_state.quiz_ready:
        st.markdown("### ✍️ מבחן בדיקה")
        st.write("ענה על השאלות כדי לוודא הבנה:")
        
        # כאן אפשר להוסיף לוגיקה של שאלות אמריקאיות (פירוס ה-quiz_raw)
        # לצורך הפשטות כרגע, נציג כפתור שחושף את המבחן המלא
        if st.button("הצג שאלות תרגול"):
            st.markdown(f'<div class="quiz-container" dir="rtl">{st.session_state.quiz_raw}</div>', unsafe_allow_html=True)

    # הצגת היסטוריה כלינק בתחתית
    st.markdown("---")
    if st.button("🔗 לחץ כאן לצפייה בהיסטוריית הלמידה שלך"):
        st.session_state.show_history = not st.session_state.show_history
    
    if st.session_state.show_history:
        st.info(f"נושאים שלמדת: {', '.join(st.session_state.history) if st.session_state.history else 'טרם למדת נושאים'}")

    # כפתור איפוס (לשיעור חדש)
    if st.session_state.lesson_data and st.button("חזרה לתפריט ראשי / נושא חדש"):
        st.session_state.lesson_data = ""
        st.session_state.quiz_ready = False
        st.rerun()
