# ==========================================
# Project: מתווך בקליק | Version: 1213-Final-Verified
# ==========================================
import streamlit as st
import google.generativeai as genai
import json, re

# ... (SYLLABUS, fetch_q_ai, stream_ai_lesson ללא שינוי)

if st.session_state.step == "lesson_run":
    show_header()
    
    # 1. כותרת הנושא נשארת תמיד
    st.header(f"📖 {st.session_state.selected_topic}")
    
    subs = SYLLABUS.get(st.session_state.selected_topic, [])
    cols = st.columns(len(subs))
    for i, s in enumerate(subs):
        if cols[i].button(s, key=f"sub_{i}"):
            st.session_state.update({"current_sub": s, "lesson_txt": "LOADING", "quiz_active": False, "q_count": 0, "ans_checked": False})
            st.rerun()

    if st.session_state.get("lesson_txt") == "LOADING":
        st.session_state.lesson_txt = stream_ai_lesson(f"שיעור על {st.session_state.current_sub}")
        st.rerun()
    elif st.session_state.get("lesson_txt"):
        st.markdown(st.session_state.lesson_txt)

    # שאלון
    user_choice = None
    if st.session_state.quiz_active and st.session_state.q_data and not st.session_state.quiz_finished:
        st.divider()
        q = st.session_state.q_data
        st.subheader(f"📝 שאלה {st.session_state.q_count} מתוך 10")
        
        # בחירת תשובה
        user_choice = st.radio(q['q'], q['options'], index=None, key=f"q_{st.session_state.q_count}")
        
        if st.session_state.ans_checked:
            if st.session_state.last_result == "correct": st.success("נכון!")
            else: st.error(f"טעות. התשובה היא: {q['correct']}")
            st.info(f"הסבר: {q['explain']}")

    if st.session_state.quiz_finished:
        st.divider(); st.balloons()
        st.success(f"🏆 סיימת! ענית נכון על {st.session_state.correct_answers} מתוך 10.")

    # שורת כפתורים אחת
    st.divider()
    # placeholder למניעת כפל תפריטים
    menu_placeholder = st.empty()
    
    with menu_placeholder.container():
        f1, f2, f3, f4 = st.columns([1.2, 1.2, 1.2, 4])
        
        with f1: # כפתור בדוק תשובה
            # 2. לא ניתן לבדוק תשובה אם user_choice הוא None
            can_check = (st.session_state.quiz_active and 
                         not st.session_state.ans_checked and 
                         user_choice is not None and
                         not st.session_state.quiz_finished)
            
            if st.button("✅ בדוק תשובה", disabled=not can_check):
                st.session_state.ans_checked = True
                st.session_state.last_result = "correct" if user_choice == q['correct'] else "wrong"
                if user_choice == q['correct']: st.session_state.correct_answers += 1
                st.rerun()

        with f2: # כפתור שאלה הבאה
            if not st.session_state.quiz_active:
                if st.button("📝 שאלון תרגול", disabled=(st.session_state.lesson_txt == "")):
                    menu_placeholder.empty()
                    with st.spinner("מכין..."):
                        res = fetch_q_ai(st.session_state.current_sub)
                        if res:
                            st.session_state.update({"q_data": res, "quiz_active": True, "q_count": 1, "correct_answers": 0, "quiz_finished": False, "ans_checked": False})
                            st.rerun()
            else:
                # 3. מופיע תמיד, אקטיבי רק לאחר בדיקה
                btn_txt = "➡️ לשאלה הבאה" if st.session_state.q_count < 10 else "🏁 סיכום שאלון"
                can_next = st.session_state.ans_checked and not st.session_state.quiz_finished
                
                if st.button(btn_txt, disabled=not can_next):
                    menu_placeholder.empty() # ניקוי לפני הספינר למניעת כפל
                    if st.session_state.q_count < 10:
                        with st.spinner("מכין..."):
                            res = fetch_q_ai(st.session_state.current_sub)
                            if res:
                                st.session_state.update({"q_data": res, "q_count": st.session_state.q_count + 1, "ans_checked": False})
                                st.rerun()
                    else:
                        st.session_state.quiz_finished = True
                        st.rerun()

        with f3: # תפריט ראשי
            if st.button("🏠 לתפריט הראשי"):
                st.session_state.step = "menu"
                st.rerun()
