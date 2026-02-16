# ==========================================
# Project: מתווך בקליק
# File: app.py
# Version: 1121
# ==========================================

import streamlit as st
import time
from exam_manager import init_exam_state, load_exam_chunk, generate_lesson_content, get_remaining_time

st.set_page_config(page_title="מתווך בקליק", layout="centered")

# CSS - כולל יישור לימין
st.markdown("<style>* { direction: rtl; text-align: right; } .stButton>button { width: 100%; }</style>", unsafe_allow_html=True)

init_exam_state()

st.title("🏠 מתווך בקליק")

# --- דף לימוד (שחזור 1118) ---
if st.session_state.step == 'study':
    st.subheader("📚 בחירת נושא ללימוד")
    topics = ["חוק המתווכים", "חוק המקרקעין", "חוק הגנת הצרכן", "חוק החוזים"]
    cols = st.columns(2)
    for i, t in enumerate(topics):
        if cols[i%2].button(t):
            st.session_state.selected_topic = t
            st.session_state.step = 'lesson_run'
            st.session_state.lesson_data = None # איפוס לטעינה חדשה
            st.rerun()
    
    if st.button("🔙 חזרה לתפריט"):
        st.session_state.step = 'menu'; st.rerun()

elif st.session_state.step == 'lesson_run':
    if not st.session_state.lesson_data:
        with st.spinner("מכין את השיעור..."):
            st.session_state.lesson_data = generate_lesson_content(st.session_state.selected_topic)
            st.session_state.current_sub_idx = 0
            st.rerun()

    data = st.session_state.lesson_data["sub_topics"]
    curr_idx = st.session_state.current_sub_idx
    curr_sub = data[curr_idx]

    st.header(f"📖 {st.session_state.selected_topic}: {curr_sub['title']}")
    st.write(curr_sub['content'])
    
    st.write("---")
    st.subheader("❓ תרגול מהיר")
    q = curr_sub['question']
    ans = st.radio(q['q'], q['options'], key=f"lesson_q_{curr_idx}")
    
    if st.button("בדוק תשובה"):
        if ans == q['correct']: st.success("נכון מאוד!")
        else: st.error(f"לא מדויק. התשובה הנכונה היא: {q['correct']}")

    st.write("---")
    c1, c2, c3 = st.columns(3)
    with c1:
        if curr_idx > 0 and st.button("⬅️ חלק קודם"):
            st.session_state.current_sub_idx -= 1; st.rerun()
    with c2:
        if st.button("🔝 לראש הדף"): st.rerun()
    with c3:
        if curr_idx < 2:
            if st.button("חלק הבא ➡️"):
                st.session_state.current_sub_idx += 1; st.rerun()
        else:
            if st.button("🏁 סיום שיעור"):
                st.session_state.step = 'menu'; st.rerun()

# --- לוגיקת המבחן והתפריטים (בקיצור, כפי שהיה קודם) ---
elif st.session_state.step == 'menu':
    st.subheader(f"שלום, {st.session_state.get('user', 'אורח')}")
    if st.button("📚 לימוד"): st.session_state.step = 'study'; st.rerun()
    if st.button("⏱️ מבחן"): st.session_state.step = 'exam_info'; st.rerun()

# (שאר הקוד של המבחן נשאר זהה ל-1120)
