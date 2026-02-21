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

    st.divider()
    f1, f2, f3 = st.columns([2, 2, 4])
    with f1:
        if st.button("🏠 חזרה לתפריט"):
            st.session_state.step = "menu"; st.rerun()
    with f2:
        if st.session_state.get("lesson_txt") and st.session_state.lesson_txt != "LOADING":
            if not st.session_state.quiz_active:
                if st.button("📝 שאלון תרגול"):
                    with st.spinner("מכין שאלה 1..."):
                        res = fetch_q_ai(st.session_state.current_sub)
                        if res:
                            st.session_state.update({"q_data": res, "quiz_active": True, "q_count": 1, "correct_answers": 0, "quiz_finished": False, "ans_checked": False})
                            st.rerun()
            elif not st.session_state.quiz_finished:
                # כפתור בדוק תשובה - דיסאבל עד שבוחרים תשובה
                check_disabled = (user_choice is None or st.session_state.ans_checked)
                if st.button("✅ בדוק תשובה", disabled=check_disabled):
                    st.session_state.ans_checked = True
                    st.session_state.last_result = "correct" if user_choice == q['correct'] else "wrong"
                    if user_choice == q['correct']: st.session_state.correct_answers += 1
                    st.rerun()
                
                # כפתור שאלה הבאה - אקטיבי רק לאחר לחיצה על בדוק תשובה
                if st.session_state.q_count < 10:
                    next_disabled = not st.session_state.ans_checked
                    if st.button("➡️ שאלה הבאה", disabled=next_disabled):
                        with st.spinner(f"מכין שאלה {st.session_state.q_count + 1}..."):
                            res = fetch_q_ai(st.session_state.current_sub)
                            if res:
                                st.session_state.update({"q_data": res, "q_count": st.session_state.q_count + 1, "ans_checked": False})
                                st.rerun()
                else:
                    if st.button("🏁 סיכום שאלון", disabled=not st.session_state.ans_checked):
                        st.session_state.quiz_finished = True; st.rerun()
