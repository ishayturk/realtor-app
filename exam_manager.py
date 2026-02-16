# ==========================================
# Project: מתווך בקליק
# File: app.py
# Version: 1124
# Last Updated: 2026-02-16 | 18:25
# ==========================================

import streamlit as st
from exam_manager import *

st.set_page_config(page_title="מתווך בקליק", layout="wide")

st.markdown("""
<style>
    * { direction: rtl; text-align: right; }
    .user-strip {
        background-color: rgba(0, 0, 0, 0.05);
        padding: 10px; border-radius: 8px;
        margin-bottom: 20px; font-weight: bold; text-align: left;
    }
</style>
""", unsafe_allow_html=True)

init_exam_state()

if st.session_state.user:
    st.markdown(f'<div class="user-strip">👤 שלום, {st.session_state.user}</div>', unsafe_allow_html=True)

st.title("🏠 מתווך בקליק")

if st.session_state.step == 'login':
    u_name = st.text_input("הזן שם מלא:")
    if st.button("כניסה"):
        if u_name:
            st.session_state.user = u_name
            st.session_state.step = 'menu'; st.rerun()

elif st.session_state.step == 'menu':
    c1, c2 = st.columns(2)
    if c1.button("📚 לימוד לפי נושאים"):
        st.session_state.step = 'study'; st.rerun()
    if c2.button("⏱️ סימולציית בחינה"):
        st.session_state.step = 'exam_init'; st.rerun()

elif st.session_state.step == 'study':
    all_topics = ["חוק המתווכים", "חוק המקרקעין", "חוק החוזים", "חוק המכר (דירות)", "חוק הגנת הצרכן"]
    selected = st.selectbox("בחר נושא:", all_topics)
    if st.button("התחל ללמוד"):
        with st.spinner("מכין את ראשי הפרקים..."):
            st.session_state.selected_topic = selected
            st.session_state.lesson_titles = get_lesson_titles(selected)
            st.session_state.current_sub_idx = None
            st.session_state.lesson_contents = {}
            st.session_state.step = 'lesson_run'; st.rerun()

elif st.session_state.step == 'lesson_run':
    st.header(f"📖 {st.session_state.selected_topic}")
    
    # 3 כפתורי תתי-נושאים
    cols = st.columns(3)
    for i, title in enumerate(st.session_state.lesson_titles):
        is_active = (st.session_state.current_sub_idx == i)
        if cols[i].button(title, disabled=is_active, key=f"btn_{i}"):
            st.session_state.current_sub_idx = i
            if title not in st.session_state.lesson_contents:
                with st.spinner(f"מייצר עבורך תוכן מפורט על {title}..."):
                    st.session_state.lesson_contents[title] = get_sub_topic_content(st.session_state.selected_topic, title)
            st.rerun()

    # הצגת התוכן המפורט
    idx = st.session_state.current_sub_idx
    if idx is not None:
        curr_title = st.session_state.lesson_titles[idx]
        st.markdown(f"### {curr_title}")
        st.markdown(st.session_state.lesson_contents.get(curr_title, "טוען..."))
        
        st.write("---")
        b1, b2, b3 = st.columns(3)
        with b1:
            if st.button("📝 שאלון 10 שאלות"):
                with st.spinner("מייצר שאלון מקיף..."):
                    st.session_state.topic_exam_questions = get_topic_exam_questions(st.session_state.selected_topic)
                    st.session_state.show_topic_exam = True
                    st.rerun()
        with b2:
            if st.button("🏠 יציאה לתפריט"): st.session_state.step = 'menu'; st.rerun()
        with b3:
            if st.button("🔝 לראש העמוד"): st.rerun()

    if st.session_state.show_topic_exam:
        st.divider()
        st.subheader(f"שאלון תרגול: {st.session_state.selected_topic}")
        for q_idx, q in enumerate(st.session_state.topic_exam_questions):
            st.radio(f"{q_idx+1}. {q['q']}", q['options'], index=None, key=f"q_{q_idx}")
        if st.button("סגור שאלון"):
            st.session_state.show_topic_exam = False; st.rerun()

# לוגיקת המבחן (המבנה עם ה-Sidebar)
elif st.session_state.step == 'exam_init':
    st.session_state.exam_active = True
    st.session_state.step = 'exam_run'; st.rerun()

elif st.session_state.step == 'exam_run':
    with st.sidebar:
        st.header("📌 ניווט שאלות")
        for r in range(5):
            c_grid = st.columns(5)
            for c in range(5):
                num = r * 5 + c
                if c_grid[c].button(f"{num+1}", key=f"n_{num}"):
                    st.session_state.current_exam_q_idx = num; st.rerun()
        if st.button("🏁 סיים מבחן"): st.session_state.step = 'menu'; st.rerun()

    st.subheader(f"שאלה {st.session_state.current_exam_q_idx + 1}")
    st.write("בחר את התשובה הנכונה מבין האפשרויות:")
    st.radio("השאלה תופיע כאן:", ["תשובה 1", "תשובה 2", "תשובה 3", "תשובה 4"], index=None)
