import streamlit as st
import google.generativeai as genai
import json
import re

# 1. הגדרות RTL ותפריט המבורגר מעוצב
st.set_page_config(page_title="מתווך בקליק", layout="wide")

st.markdown("""
<style>
    /* יישור RTL גלובלי */
    .stApp { direction: rtl !important; text-align: right !important; }
    
    /* עיצוב כפתורי הניווט העליונים שיראו כמו תפריט אתר */
    .nav-container {
        background-color: #ffffff;
        padding: 10px;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin-bottom: 20px;
        display: flex;
        justify-content: space-around;
        border-bottom: 3px solid #1E88E5;
    }
    
    /* הסתרת הסיידבר המקורי של Streamlit כדי שלא יפריע בנייד */
    [data-testid="stSidebar"] { display: none; }
    [data-testid="stSidebarCollapsedControl"] { display: none; }

    /* עיצוב כפתורי התפריט */
    .stButton button {
        border-radius: 20px;
        border: 1px solid #1E88E5;
        transition: 0.3s;
    }
    
    input { direction: rtl !important; text-align: right !important; }
</style>
""", unsafe_allow_html=True)

# 2. ניהול State
if "view_mode" not in st.session_state:
    st.session_state.update({
        "view_mode": "login", "user_name": "", "current_topic": "",
        "exam_questions": [], "user_answers": {}, "current_exam_idx": 0
    })

# 3. הזרקת תפריט "שורת ניווט" עליונה (תחליף ל-3 קווים)
def render_top_menu():
    if st.session_state.user_name:
        # יצירת שורת תפריט עליונה נקייה
        with st.container():
            cols = st.columns([1, 1, 1], gap="small")
            with cols[0]:
                if st.button("🏠 בית", use_container_width=True):
                    st.session_state.view_mode = "setup"; st.rerun()
            with cols[1]:
                if st.button("🏆 מבחן", use_container_width=True):
                    # כאן תבוא פונקציית טעינת המבחן (start_exam)
                    st.session_state.view_mode = "full_exam_mode"; st.rerun()
            with cols[2]:
                if st.button("🚪 יציאה", use_container_width=True):
                    st.session_state.clear(); st.rerun()
        st.markdown("---")

# 4. לוגיקת דפים
if st.session_state.view_mode == "login":
    st.markdown("<h1 style='text-align: center;'>🏠 מתווך בקליק</h1>", unsafe_allow_html=True)
    with st.container():
        u_name = st.text_input("שם מלא:")
        if st.button("התחל ללמוד", use_container_width=True):
            if u_name:
                st.session_state.user_name = u_name
                st.session_state.view_mode = "setup"; st.rerun()

else:
    # הצגת התפריט העליון בכל דף חוץ ממסך הכניסה
    render_top_menu()

    if st.session_state.view_mode == "setup":
        st.header("סילבוס הלימודים")
        # רשימת ה-16 נושאים ככפתורים גדולים ונוחים לנייד
        topics = ["חוק המתווכים", "חוק המקרקעין", "חוק המכר", "חוק הגנת הצרכן"]
        for t in topics:
            if st.button(f"📖 {t}", use_container_width=True):
                st.session_state.current_topic = t
                st.session_state.view_mode = "lesson_view"; st.rerun()

    elif st.session_state.view_mode == "lesson_view":
        st.header(st.session_state.current_topic)
        st.info("כאן מופיע השיעור המפורט...")
        if st.button("✍️ התחל תרגול על הנושא", use_container_width=True):
             st.session_state.view_mode = "quiz_mode"; st.rerun()

    elif st.session_state.view_mode == "full_exam_mode":
        st.header("🏆 מבחן סימולציה מלא")
        # לוגיקת שאלה-שאלה עם כפתורי "הבא/הקודם"
        st.write("שאלה 1 מתוך 25")
