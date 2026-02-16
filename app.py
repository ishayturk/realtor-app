# ==========================================
# Project: מתווך בקליק
# File: app.py
# Version: 1118
# Last Updated: 2026-02-16
# ==========================================

import streamlit as st
import time
from exam_manager import (
    init_exam_state, 
    render_exam_sidebar, 
    get_remaining_time, 
    load_exam_chunk,
    generate_lesson_content
)

# הגדרות דף
st.set_page_config(page_title="מתווך בקליק", layout="centered")

# עיצוב UI בסיסי
st.markdown("""
<style>
    * { direction: rtl; text-align: right; }
    .timer-card { 
        font-size: 1.8rem; color: #d32f2f; text-align: center; 
        font-weight: bold; padding: 15px; border: 3px solid #d32f2f; 
        border-radius: 15px; margin-bottom: 25px; background: #fff5f5;
    }
    .question-container { 
        background: #f8f9fa; padding: 25px; border-radius: 12px; 
        border-right: 6px solid #1e88e5; margin-bottom: 20px;
    }
    .stButton>button { width: 100%; }
</style>
""", unsafe_allow_html=True)

# אתחול מצב אפליקציה
init_exam_state()

st.title("🏠 מתווך בקליק")

# --- ניתוב דפים לפי ה-Step ב-Session State ---

# 1. מסך כניסה
if st.session_state.step == 'login':
    u_name = st.text_input("הזן שם מלא לכניסה:")
    if st.button("כניסה למערכת"):
        if u_name:
            st.session_state.user = u_name
            st.session_state.step = 'menu'
            st.rerun()

# 2. תפריט ראשי
elif st.session_state.step == 'menu':
    st.subheader(f"שלום, {st.session_state.user}")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("📚 לימוד לפי נושאים"):
            st.session_state.step = 'study'; st.rerun()
    with c2:
        if st.button("⏱️ סימולציית בחינה"):
            st.session_state.step = 'exam_info'; st.rerun()

# 3. דף בחירת נושא לימוד
elif st.session_state.step == 'study':
    st.subheader("📚 מרכז למידה - בחר נושא")
    topics = ["חוק המתווכים", "חוק המקרקעין", "חוק הגנת הצרכן", "חוק החוזים", "דיני עונשין", "מיסוי מקרקעין"]
    cols = st.columns(2)
    for i, topic in enumerate(topics):
        if cols[i % 2].button(topic):
            st.session_state.selected_topic = topic
            st.session_state.lesson_data = None
            st.session_state.step = 'lesson_run'
            st.rerun()
    
    if st.button("🔙 חזרה לתפריט"):
        st.session_state.step = 'menu'; st.rerun()

# 4. הרצת שיעור (מבנה 3 חלקים + שאלות)
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

# 5. מידע לפני בחינה
elif st.session_state.step == 'exam_info':
    st.subheader("📋 מידע על הסימולציה")
    st.info("25 שאלות | 90 דקות | מקור: רשם המתווכים")
    if st.button("🚀 התחל בחינה"):
        st.session_state.start_time = time.time()
        st.session_state.exam_questions = []
        st.session_state.user_answers = {}
        st.session_state.exam_idx = 0
        st.session_state.step = 'load_questions'; st.rerun()
    if st.button("🔙 חזרה"):
        st.session_state.step = 'menu'; st.rerun()

# 6. טעינת שאלות למבחן
elif st.session_state.step == 'load_questions':
    q_len = len(st.session_state.exam_questions)
    with st.spinner(f"טוען שאלות {q_len + 1}-{q_len + 5}..."):
        new_q = load_exam_chunk(q_len + 1)
        if new_q:
            st.session_state.exam_questions.extend(new_q)
            st.session_state.step = 'exam_run'; st.rerun()
        else:
            st.error("תקלה בטעינת השאלות."); st.button("נסה שוב")

# 7. הרצת המבחן
elif st.session_state.step == 'exam_run':
    render_exam_sidebar()
    rem = get_remaining_time()
    if rem == "00:00":
        st.session_state.step = 'results'; st.rerun()
    
    st.markdown(f"<div class='timer-card'>⏳ זמן נותר: {rem}</div>", unsafe_allow_html=True)
    
    idx = st.session_state.exam_idx
    if idx < len(st.session_state.exam_questions):
        q = st.session_state.exam_questions[idx]
        st.markdown(f"<div class='question-container'><h3>שאלה {idx + 1}</h3><p>{q['q']}</p></div>", unsafe_allow_html=True)
        
        prev_ans = st.session_state.user_answers.get(idx, None)
        try: d_idx = q['options'].index(prev_ans) if prev_ans in q['options'] else None
        except: d_idx = None
            
        ans = st.radio("בחר תשובה:", q['options'], key=f"radio_{idx}", index=d_idx)
        if ans: st.session_state.user_answers[idx] =
