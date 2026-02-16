# ==========================================
# Project: מתווך בקליק
# File: app.py
# Version: 1123
# Last Updated: 2026-02-16 | 17:40
# ==========================================

import streamlit as st
from exam_manager import *

st.set_page_config(page_title="מתווך בקליק", layout="wide")

# עיצוב UI מתקדם
st.markdown("""
<style>
    * { direction: rtl; text-align: right; }
    .stButton>button { width: 100%; border-radius: 8px; }
    .user-strip {
        background-color: rgba(255, 255, 255, 0.2);
        padding: 8px 15px; border-radius: 10px;
        margin-bottom: 25px; font-weight: bold; border: 1px solid #eee;
        text-align: left;
    }
    [data-testid="stSidebar"] { direction: rtl; }
    .stRadio > div { direction: rtl; }
</style>
""", unsafe_allow_html=True)

init_exam_state()

# הצגת שם משתמש בסטריפ קבוע (אחרי לוגין)
if st.session_state.user:
    st.markdown(f'<div class="user-strip">👤 שלום, {st.session_state.user}</div>', unsafe_allow_html=True)

st.title("🏠 מתווך בקליק")

# --- ניתוב דפים ---

if st.session_state.step == 'login':
    u_name = st.text_input("הזן שם מלא לכניסה:")
    if st.button("כניסה למערכת"):
        if u_name:
            st.session_state.user = u_name
            st.session_state.step = 'menu'; st.rerun()

elif st.session_state.step == 'menu':
    st.subheader("תפריט ראשי")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("📚 לימוד לפי נושאים"):
            st.session_state.step = 'study'; st.rerun()
    with c2:
        if st.button("⏱️ סימולציית בחינה"):
            st.session_state.step = 'exam_init'; st.rerun()

elif st.session_state.step == 'study':
    all_topics = [
        "חוק המתווכים במקרקעין", "תקנות המתווכים (פרטי הזמנה)", "חוק המקרקעין", 
        "חוק הגנת הדייר", "חוק המכר (דירות)", "חוק החוזים", "חוק הגנת הצרכן", 
        "חוק עבירות עונשין", "חוק התכנון והבנייה", "חוק מיסוי מקרקעין"
    ]
    selected = st.selectbox("בחר נושא ללימוד מהרשימה:", all_topics)
    if st.button("התחל שיעור"):
        with st.spinner("מחלץ ראשי פרקים מה-AI..."):
            st.session_state.selected_topic = selected
            st.session_state.lesson_titles = get_lesson_titles(selected)
            st.session_state.current_sub_idx = None
            st.session_state.lesson_contents = {}
            st.session_state.show_topic_exam = False
            st.session_state.step = 'lesson_run'; st.rerun()

elif st.session_state.step == 'lesson_run':
    st.header(f"📖 {st.session_state.selected_topic}")
    
    # 3 כפתורי תתי-נושאים עם לוגיקת Disabled
    cols = st.columns(3)
    for i, title in enumerate(st.session_state.lesson_titles):
        is_disabled = (st.session_state.current_sub_idx == i)
        if cols[i].button(title, disabled=is_disabled, key=f"t_{i}"):
            st.session_state.current_sub_idx = i
            if title not in st.session_state.lesson_contents:
                with st.spinner("מייצר תוכן עבורך..."):
                    st.session_state.lesson_contents[title] = get_sub_topic_content(st.session_state.selected_topic, title)
            st.rerun()

    # הצגת תוכן השיעור
    idx = st.session_state.current_sub_idx
    if idx is not None:
        curr_title = st.session_state.lesson_titles[idx]
        st.info(f"חלק {idx+1}: {curr_title}")
        st.markdown(st.session_state.lesson_contents[curr_title])
        
        st.write("---")
        # כפתורי תחתית השיעור
        b1, b2, b3 = st.columns(3)
        with b1:
            if st.button("📝 שאלון בנושא הכללי"):
                with st.spinner("מכין שאלות תרגול..."):
                    st.session_state.topic_exam_questions = get_topic_exam_questions(st.session_state.selected_topic)
                    st.session_state.show_topic_exam = True
                    st.rerun()
        with b2:
            if st.button("🏠 יציאה לתפריט"):
                st.session_state.step = 'menu'; st.rerun()
        with b3:
            if st.button("🔝 לראש העמוד"): st.rerun()

    # הצגת שאלון במידה ונבחר (10 שאלות, ללא בחירה מראש)
    if st.session_state.show_topic_exam:
        st.divider()
        st.subheader(f"📝 שאלון: {st.session_state.selected_topic}")
        for q_idx, q in enumerate(st.session_state.topic_exam_questions):
            st.radio(f"{q_idx+1}. {q['q']}", q['options'], index=None, key=f"q_{q_idx}")
        if st.button("סגור שאלון וחזור לשיעור"):
            st.session_state.show_topic_exam = False; st.rerun()

elif st.session_state.step == 'exam_init':
    # הכנה למבחן 25 שאלות
    st.session_state.exam_active = True
    st.session_state.current_exam_q_idx = 0
    st.session_state.step = 'exam_run'; st.rerun()

elif st.session_state.step == 'exam_run':
    # לוח ניווט בחינה ב-Sidebar (מותאם לנייד)
    with st.sidebar:
        st.header("📌 ניווט שאלות")
        # יצירת מטריצה של 5x5 למספרי השאלות
        for row in range(5):
            cols = st.columns(5)
            for col in range(5):
                q_num = row * 5 + col
                if cols[col].button(f"{q_num+1}", key=f"nav_{q_num}"):
                    st.session_state.current_exam_q_idx = q_num
                    st.rerun()
        st.write("---")
        if st.button("🏁 סיום והגשת בחינה"):
            st.session_state.step = 'menu'; st.rerun()
    
    # הצגת השאלה הנוכחית במבחן
    st.subheader(f"שאלה {st.session_state.current_exam_q_idx + 1} מתוך 25")
    st.write("כאן תופיע השאלה מהמאגר הממשלתי (יבוצע בשלב הבא עם טעינת הצ'אנקים)")
    st.radio("בחר את התשובה הנכונה:", ["אפשרות 1", "אפשרות 2", "אפשרות 3", "אפשרות 4"], index=None)
    
    # ניווט פנימי
    nb1, nb2 = st.columns(2)
    if st.session_state.current_exam_q_idx > 0:
        if nb1.button("⬅️ שאלה הקודמת"):
            st.session_state.current_exam_q_idx -= 1; st.rerun()
    if st.session_state.current_exam_q_idx < 24:
        if nb2.button("שאלה הבאה ➡️"):
            st.session_state.current_exam_q_idx += 1; st.rerun()
