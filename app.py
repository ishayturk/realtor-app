# ==========================================
# Project: מתווך בקליק
# File: app.py
# Version: 1118
# ==========================================

import streamlit as st
import time
from exam_manager import (
    init_exam_state, 
    get_remaining_time, 
    load_exam_chunk,
    generate_lesson_content
)

st.set_page_config(page_title="מתווך בקליק", layout="centered")

# עיצוב UI
st.markdown("""
<style>
    * { direction: rtl; text-align: right; }
    .stButton>button { width: 100%; }
</style>
""", unsafe_allow_html=True)

init_exam_state()

st.title("🏠 מתווך בקליק")

# --- ניתוב דפים ---

if st.session_state.step == 'login':
    u_name = st.text_input("הזן שם מלא לכניסה:")
    if st.button("כניסה למערכת"):
        if u_name:
            st.session_state.user = u_name
            st.session_state.step = 'menu'
            st.rerun()

elif st.session_state.step == 'menu':
    st.subheader(f"שלום, {st.session_state.user}")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("📚 לימוד לפי נושאים"):
            st.session_state.step = 'study'; st.rerun()
    with c2:
        if st.button("⏱️ סימולציית בחינה"):
            st.session_state.step = 'exam_info'; st.rerun()

elif st.session_state.step == 'study':
    st.subheader("📚 בחר נושא ללימוד")
    topics = ["חוק המתווכים", "חוק המקרקעין", "חוק הגנת הצרכן", "חוק החוזים", "דיני עונשין"]
    for topic in topics:
        if st.button(topic):
            st.session_state.selected_topic = topic
            st.session_state.lesson_data = None
            st.session_state.step = 'lesson_run'
            st.rerun()
    if st.button("🔙 חזרה לתפריט"):
        st.session_state.step = 'menu'; st.rerun()

elif st.session_state.step == 'lesson_run':
    if not st.session_state.lesson_data:
        with st.spinner(f"טוען שיעור על {st.session_state.selected_topic}..."):
            st.session_state.lesson_data = generate_lesson_content(st.session_state.selected_topic)
            st.session_state.current_sub_idx = 0
            st.rerun()

    subs = st.session_state.lesson_data["sub_topics"]
    idx = st.session_state.current_sub_idx
    curr = subs[idx]

    st.header(f"📖 {st.session_state.selected_topic}")
    st.subheader(f"חלק {idx+1}: {curr['title']}")
    st.write(curr['content'])
    
    st.write("---")
    st.info("❓ שאלת תרגול")
    q = curr['question']
    ans = st.radio(q['q'], q['options'], key=f"l_q_{idx}")
    
    if st.button("בדוק תשובה"):
        if ans == q['correct']:
            st.success("תשובה נכונה!")
        else:
            st.error(f"לא נכון. התשובה הנכונה: {q['correct']}")

    st.write("---")
    b1, b2, b3 = st.columns(3)
    with b1:
        if idx > 0 and st.button("⬅️ חלק קודם"):
            st.session_state.current_sub_idx -= 1; st.rerun()
    with b2:
        if st.button("🔝 לראש הדף"): st.rerun()
    with b3:
        if idx < 2:
            if st.button("חלק הבא ➡️"):
                st.session_state.current_sub_idx += 1; st.rerun()
        else:
            if st.button("🏁 סיום שיעור"):
                st.session_state.step = 'menu'; st.rerun()

# (שאר חלקי המבחן ממשיכים מכאן...)
