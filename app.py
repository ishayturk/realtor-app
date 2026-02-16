# ==========================================
# Project: מתווך בקליק
# File: app.py
# Version: 1119
# Last Updated: 2026-02-16 | 14:50
# ==========================================

import streamlit as st
import time
from exam_manager import (
    init_exam_state, 
    render_exam_sidebar, 
    get_remaining_time, 
    load_exam_chunk
)

# הגדרות דף
st.set_page_config(page_title="מתווך בקליק", layout="centered")

# עיצוב UI
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
</style>
""", unsafe_allow_html=True)

# אתחול
init_exam_state()
if 'step' not in st.session_state:
    st.session_state.step = 'login'

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
    st.subheader(f"שלום, {st.session_state.get('user', 'אורח')}")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("📚 לימוד לפי נושאים"):
            st.session_state.step = 'study'; st.rerun()
    with c2:
        if st.button("⏱️ סימולציית בחינה"):
            st.session_state.step = 'exam_info'; st.rerun()

elif st.session_state.step == 'exam_info':
    st.subheader("📋 מידע על הסימולציה")
    st.info("""
    - המבחן כולל 25 שאלות ממבחני רשם המתווכים הרשמיים.
    - זמן מוקצב: 90 דקות (ספירה לאחור).
    - השאלות נטענות במנות של 5 כדי לשמור על יציבות המערכת.
    - הטיימר מתחיל ברגע שתלחץ על הכפתור למטה.
    """)
    if st.button("🚀 התחל בחינה"):
        st.session_state.start_time = time.time()
        st.session_state.exam_questions = []
        st.session_state.user_answers = {}
        st.session_state.exam_idx = 0
        st.session_state.step = 'load_questions'; st.rerun()

elif st.session_state.step == 'load_questions':
    q_len = len(st.session_state.exam_questions)
    with st.spinner(f"טוען שאלות {q_len + 1}-{q_len + 5} מהמאגר הממשלתי..."):
        new_q = load_exam_chunk(q_len + 1)
        if new_q:
            st.session_state.exam_questions.extend(new_q)
            st.session_state.step = 'exam_run'; st.rerun()
        else:
            st.error("תקלה בטעינת השאלות. וודא חיבור אינטרנט.")
            if st.button("נסה שוב"): st.rerun()

elif st.session_state.step == 'exam_run':
    render_exam_sidebar()
    
    # הצגת טיימר
    rem = get_remaining_time()
    if rem == "00:00":
        st.warning("תם הזמן המוקצב לבחינה!"); st.session_state.step = 'results'; st.rerun()
    
    st.markdown(f"<div class='timer-card'>⏳ זמן נותר: {rem}</div>", unsafe_allow_html=True)
    
    idx = st.session_state.exam_idx
    if idx < len(st.session_state.exam_questions):
        q = st.session_state.exam_questions[idx]
        
        st.markdown(f"<div class='question-container'><h3>שאלה {idx + 1}</h3><p>{q['q']}</p></div>", unsafe_allow_html=True)
        
        # שמירת תשובה ובחירה מחדש
        prev_ans = st.session_state.user_answers.get(idx, None)
        try:
            d_idx = q['options'].index(prev_ans) if prev_ans in q['options'] else None
        except:
            d_idx = None
            
        ans = st.radio("בחר את התשובה הנכונה:", q['options'], key=f"radio_{idx}", index=d_idx)
        if ans:
            st.session_state.user_answers[idx] = ans

        st.write("---")
        b1, b2, b3 = st.columns(3)
        with b1:
            if idx > 0 and st.button("⬅️ הקודמת"):
                st.session_state.exam_idx -= 1; st.rerun()
        with b2:
            if st.button("🏁 סיום ושליחה"):
                st.session_state.step = 'results'; st.rerun()
        with b3:
            if idx < 24:
                if st.button("הבאה ➡️"):
                    if (idx + 1) % 5 == 0 and len(st.session_state.exam_questions) <= idx + 1:
                        st.session_state.step = 'load_questions'
                    else:
                        st.session_state.exam_idx += 1
                    st.rerun()

elif st.session_state.step == 'results':
    st.balloons()
    st.header("🏁 תוצאות המבחן")
    
    score = sum(1 for i, q in enumerate(st.session_state.exam_questions) if st.session_state.user_answers.get(i) == q['correct'])
    st.metric("ציון סופי", f"{int((score/25)*100)}%", f"{score} מתוך 25")
    
    if st.button("🏠 חזרה לתפריט"):
        st.session_state.step = 'menu'; st.rerun()
