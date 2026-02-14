import streamlit as st
import time
import random

# פונקציה לבחירת שאלות אקראיות (כרגע דוגמה, בהמשך נטען מהלינק)
def get_random_exam():
    # כאן בעתיד נטען את השאלות האמיתיות מה-PDF/JSON של משרד המשפטים
    # כרגע אני שם שאלת דוגמה כדי לבדוק שהמנגנון עובד
    mock_questions = []
    for i in range(1, 26):
        mock_questions.append({
            "id": i,
            "q": f"שאלה מספר {i} מהבחינה הרשמית - נושא לדוגמה",
            "options": ["תשובה א'", "תשובה ב'", "תשובה ג'", "תשובה ד'"],
            "correct": random.randint(0, 3),
            "explanation": f"זהו הסבר משפטי לשאלה {i}"
        })
    return mock_questions

def init_exam_state():
    if "exam_active" not in st.session_state:
        st.session_state.exam_active = False
    if "exam_questions" not in st.session_state:
        st.session_state.exam_questions = []
    if "user_answers" not in st.session_state:
        st.session_state.user_answers = {}
    if "start_time" not in st.session_state:
        st.session_state.start_time = None

def render_exam_sidebar():
    st.sidebar.title("📌 ניווט בבחינה")
    cols = st.sidebar.columns(5)
    for i in range(1, 26):
        col_idx = (i - 1) % 5
        # צבע הכפתור משתנה אם ענו על השאלה
        button_type = "primary" if i in st.session_state.user_answers else "secondary"
        if cols[col_idx].button(f"{i}", key=f"nav_{i}", help=f"עבור לשאלה {i}"):
            st.session_state.exam_idx = i - 1
            st.rerun()

def get_remaining_time():
    if st.session_state.start_time is None:
        return "90:00"
    elapsed = time.time() - st.session_state.start_time
    remaining = max(0, 90 * 60 - elapsed)
    mins, secs = divmod(int(remaining), 60)
    return f"{mins:02d}:{secs:02d}"
