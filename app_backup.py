# ==========================================
# Project: מתווך בקליק | Version: 1213-Fixed-Buttons
# Status: Fixed Buttons Row + Disabled Logic
# ==========================================
import streamlit as st
import google.generativeai as genai
import json, re

st.set_page_config(page_title="מתווך בקליק", layout="wide")

st.markdown("""
<style>
    * { direction: rtl; text-align: right; }
    .header-container { display: flex; align-items: center; gap: 45px; margin-bottom: 30px; }
    .header-title { font-size: 2.5rem !important; font-weight: bold !important; margin: 0 !important; }
    .header-user { font-size: 1.2rem !important; font-weight: 900 !important; color: #31333f; }
    .footer-buttons .stButton>button { width: auto !important; padding: 0 30px !important; }
</style>
""", unsafe_allow_html=True)

# ... (SYLLABUS, fetch_q_ai, stream_ai_lesson ללא שינוי)

if "step" not in st.session_state:
    st.session_state.update({
        "user": None, "step": "login", "lesson_txt": "",
        "q_data": None, "q_count": 0, "quiz_active": False,
        "correct_answers": 0, "quiz_finished": False, "ans_checked": False
    })

# --- ניווט דפים (קוד קיים) ---
# [כאן מופיע הקוד של Login, Menu, Exam Frame, Study כפי שהיה]

elif st.session_state.step == "lesson_run":
    show_header()
    st.header(f"📖 {st.session_state.selected_topic}")
    subs = SYLLABUS.get(st.session_state.selected_topic, [])
    cols = st.columns(len(subs))
    for i, s in enumerate(subs):
        if cols[i].button(s, key=f"sub_{i}"):
            st.session_state.update({
                "current_sub": s, "lesson_txt": "LOADING", 
                "quiz_active": False, "q_count": 0, "ans_checked": False
            })
            st.rerun()

    if st.session_state.get("lesson_txt") == "LOADING":
        st.session_state.lesson_txt = stream_ai_lesson(f"שיעור על {st.session_state.current_sub}")
        st.rerun()
    elif st.session_state.get("lesson_txt"):
        st.markdown(st.session_state.lesson_txt)

    # --- תצוגת שאלון ---
    if st.session_state.quiz_active and st.session_state.q_data and not st.session_state.quiz_finished:
        st.divider()
        q = st.session_state.q_data
        st.subheader(f"📝 שאלה {st.session_state.q_count} מתוך 10")
        ans = st.radio(q['q'], q['options'], index=None, key=f"q_{st.session_state.q_count}")
        
        if st.session_state.ans_checked:
            if st.session_state.last_result == "correct": st.success("נכון!")
            else: st.error(f"טעות. התשובה היא: {q['correct']}")
            st.info(f"הסבר: {q['explain']}")

    if st.session_state.quiz_finished:
        st.divider(); st.balloons()
        st.success(f"🏆 סיימת! ענית נכון על {st.session_state.correct_answers} מתוך 10.")

    # --- תפריט כפתורים תחתון (שורה אחת, מימין לשמאל) ---
    st.divider()
    st.markdown('<div class="footer-buttons">', unsafe_allow_html=True)
    f_cols = st.columns([1.2, 1.2, 1.2, 4]) 
    
    with f_cols[0]: # כפתור בדוק תשובה
        is_quiz = st.session_state.quiz_active and not st.session_state.quiz_finished
        can_check = is_quiz and not st.session_state.ans_checked
        if st.button("✅ בדוק תשובה", disabled=not can_check):
            if ans:
                st.session_state.ans_checked = True
                st.session_state.last_result = "correct" if ans == q['correct'] else "wrong"
                if ans == q['correct']: st.session_state.correct_answers += 1
                st.rerun()
            else: st.warning("אנא בחר תשובה")

    with f_cols[1]: # כפתור שאלה הבאה / התחלת שאלון
        if not st.session_state.quiz_active and st.session_state.lesson_txt != "LOADING":
            if st.button("📝 שאלון תרגול"):
                with st.spinner("מכין שאלה..."):
                    res = fetch_q_ai(st.session_state.current_sub)
                    if res:
                        st.session_state.update({
                            "q_data": res, "quiz_active": True, "q_count": 1, 
                            "correct_answers": 0, "quiz_finished": False, "ans_checked": False
                        })
                        st.rerun()
        else:
            # כפתור "שאלה הבאה" או "סיכום" - מופיע תמיד אך אקטיבי רק אחרי בדיקה
            btn_label = "➡️ לשאלה הבאה" if st.session_state.q_count < 10 else "🏁 סיכום שאלון"
            can_next = st.session_state.ans_checked and not st.session_state.quiz_finished
            
            if st.button(btn_label, disabled=not can_next):
                if st.session_state.q_count < 10:
                    with st.spinner("מכין שאלה הבאה..."):
                        res = fetch_q_ai(st.session_state.current_sub)
                        if res:
                            st.session_state.update({
                                "q_data": res, "q_count": st.session_state.q_count + 1, 
                                "ans_checked": False
                            })
                            st.rerun()
                else:
                    st.session_state.quiz_finished = True
                    st.rerun()

    with f_cols[2]: # כפתור חזרה
        if st.button("🏠 לתפריט הראשי"):
            st.session_state.step = "menu"
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
