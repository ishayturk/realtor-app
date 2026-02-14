import streamlit as st
import google.generativeai as genai
import time

# --- 1. הגדרות תצוגה RTL קשיחות ---
st.set_page_config(page_title="מתווך בקליק", layout="centered")

st.markdown("""
    <style>
    [data-testid="stAppViewContainer"], .main, .block-container { direction: rtl !important; text-align: right !important; }
    h1, h2, h3, h4 { text-align: center !important; color: #1E88E5; width: 100%; }
    .stButton > button { width: 100%; font-weight: bold; height: 3.5em; border-radius: 10px; }
    .lesson-box { 
        background: #ffffff; padding: 25px; border-radius: 15px; 
        border-right: 6px solid #1E88E5; box-shadow: 0 4px 12px rgba(0,0,0,0.1); 
        line-height: 1.8; color: #333; text-align: right; direction: rtl; margin-bottom: 25px;
    }
    .quiz-container { background: #f9f9f9; padding: 20px; border-radius: 12px; border: 1px solid #ddd; margin-top: 20px; }
    .score-box { text-align: center; padding: 20px; border-radius: 15px; background: #e3f2fd; border: 2px solid #1E88E5; font-size: 1.2em; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. אתחול משתנים ---
if "step" not in st.session_state:
    st.session_state.update({
        "step": "login", "user": "", "lesson_text": "",
        "quiz_active": False, "quiz_idx": 0, "quiz_answers": {}, "quiz_questions": [], "quiz_done": False
    })

# --- 3. לוגיקת דפים ---
st.markdown("<h1>🏠 מתווך בקליק</h1>", unsafe_allow_html=True)

# דף כניסה
if st.session_state.step == "login":
    name = st.text_input("שם מלא לכניסה:")
    if st.button("כניסה"):
        if name:
            st.session_state.user = name
            st.session_state.step = "menu"
            st.rerun()

# תפריט ולימוד
elif st.session_state.step == "menu":
    st.markdown(f"<div style='text-align: right;'><h3>שלום, {st.session_state.user}</h3></div>", unsafe_allow_html=True)
    
    topic = st.selectbox("בחר נושא ללימוד:", ["חוק המתווכים", "חוק המקרקעין", "חוק החוזים", "דיני מקרקעין"])
    
    # כפתור התחלה - מופיע רק אם לא התחלנו שיעור
    if not st.session_state.quiz_active and not st.session_state.quiz_done:
        if st.button("📖 התחל שיעור"):
            try:
                genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                model = genai.GenerativeModel('gemini-2.0-flash')
                response = model.generate_content(f"כתוב שיעור מפורט למבחן המתווכים על {topic} בעברית.", stream=True)
                
                placeholder = st.empty()
                full_text = ""
                for chunk in response:
                    full_text += chunk.text
                    placeholder.markdown(f"<div class='lesson-box'>{full_text}</div>", unsafe_allow_html=True)
                
                st.session_state.lesson_text = full_text
                # יצירת 10 שאלות
                st.session_state.quiz_questions = [{"q": f"שאלה {i+1} על {topic}: מהו הדין במקרה זה?", "options": ["אופציה 1", "אופציה 2", "אופציה 3", "אופציה 4"], "correct": "אופציה 1"} for i in range(10)]
                st.session_state.quiz_active = True
                st.rerun()
            except Exception as e:
                st.error(f"שגיאה: {str(e)}")

    # הצגת השיעור הקבוע (לא נעלם)
    if st.session_state.lesson_text:
        st.markdown(f"<div class='lesson-box'>{st.session_state.lesson_text}</div>", unsafe_allow_html=True)

    # הצגת השאלון מתחת לשיעור
    if st.session_state.quiz_active:
        st.markdown("<div class='quiz-container'>", unsafe_allow_html=True)
        idx = st.session_state.quiz_idx
        q = st.session_state.quiz_questions[idx]
        
        st.markdown(f"<h4>תרגול: שאלה {idx+1} מתוך 10</h4>", unsafe_allow_html=True)
        ans = st.radio(q['q'], q['options'], key=f"q_{idx}_{time.time()}", index=None)
        
        if ans: st.session_state.quiz_answers[idx] = ans
        
        col1, col2 = st.columns(2)
        with col1:
            if idx > 0 and st.button("⬅️ הקודם"):
                st.session_state.quiz_idx -= 1
                st.rerun()
        with col2:
            if idx < 9:
                if st.button("הבא ➡️"):
                    st.session_state.quiz_idx += 1
                    st.rerun()
            else:
                if st.button("🏁 סיום ובדיקה"):
                    st.session_state.quiz_active = False
                    st.session_state.quiz_done = True
                    st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    # מסך תוצאות
    if st.session_state.quiz_done:
        correct = sum(1 for i, q in enumerate(st.session_state.quiz_questions) if st.session_state.quiz_answers.get(i) == q['correct'])
        st.markdown(f"""
            <div class='score-box'>
                <h3>הציון שלך: {correct * 10}</h3>
                <p>ענית נכון על {correct} מתוך 10 שאלות</p>
            </div>
        """, unsafe_allow_html=True)
        
        if st.button("התחל נושא חדש"):
            st.session_state.update({
                "lesson_text": "", "quiz_active": False, "quiz_idx": 0, 
                "quiz_answers": {}, "quiz_questions": [], "quiz_done": False
            })
            st.rerun()
