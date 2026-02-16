# ==========================================
# Project: מתווך בקליק
# File: app.py
# Version: 1122
# Last Updated: 2026-02-16 | 15:15
# ==========================================

import streamlit as st
import time
from exam_manager import init_exam_state, generate_lesson_content, load_exam_chunk, get_remaining_time

st.set_page_config(page_title="מתווך בקליק", layout="centered")
st.markdown("<style>* { direction: rtl; text-align: right; } .stButton>button { width: 100%; }</style>", unsafe_allow_html=True)

init_exam_state()

st.title("🏠 מתווך בקליק")

if st.session_state.step == 'login':
    u_name = st.text_input("הזן שם מלא:")
    if st.button("כניסה"):
        if u_name:
            st.session_state.user = u_name
            st.session_state.step = 'menu'; st.rerun()

elif st.session_state.step == 'menu':
    st.subheader(f"שלום, {st.session_state.user}")
    if st.button("📚 לימוד לפי נושאים"):
        st.session_state.step = 'study'; st.rerun()
    if st.button("⏱️ סימולציית בחינה"):
        st.session_state.step = 'exam_info'; st.rerun()

elif st.session_state.step == 'study':
    st.subheader("📚 בחר נושא ללימוד")
    
    all_topics = [
        "חוק המתווכים במקרקעין", "תקנות המתווכים (פרטי הזמנה)", "תקנות המתווכים (פעולות שיווק)",
        "חוק המקרקעין", "חוק הגנת הדייר", "חוק המכר (דירות)", "חוק החוזים (חלק כללי)",
        "חוק החוזים (תרופות)", "חוק הגנת הצרכן", "חוק עבירות עונשין", "חוק שמאי מקרקעין",
        "חוק התכנון והבנייה", "חוק מיסוי מקרקעין", "חוק הירושה", "חוק הוצאה לפועל", "פקודת הנזיקין"
    ]
    
    selected = st.selectbox("בחר נושא מהרשימה:", all_topics)
    
    if st.button("התחל ללמוד"):
        st.session_state.selected_topic = selected
        st.session_state.lesson_data = None
        st.session_state.step = 'lesson_run'; st.rerun()
    
    if st.button("🔙 חזרה לתפריט"):
        st.session_state.step = 'menu'; st.rerun()

elif st.session_state.step == 'lesson_run':
    if not st.session_state.lesson_data:
        with st.spinner("ה-AI מכין את השיעור..."):
            data = generate_lesson_content(st.session_state.selected_topic)
            if data:
                st.session_state.lesson_data = data
                st.session_state.current_sub_idx = 0
                st.rerun()
            else:
                st.stop()

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
        if ans == q['correct']: st.success("נכון מאוד!")
        else: st.error(f"לא מדויק. התשובה הנכונה היא: {q['correct']}")

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

# לוגיקת המבחן ממשיכה כרגיל...
