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
    .explanation-box { padding: 15px; border-radius: 10px; margin-top: 10px; border-right: 5px solid; font-size: 0.95em; text-align: right; }
    .success { background-color: #e8f5e9; border-color: #4caf50; color: #2e7d32; }
    .error { background-color: #ffebee; border-color: #f44336; color: #c62828; }
    .source-tag { font-weight: bold; color: #1565c0; }
    div[role="radiogroup"] { direction: rtl !important; text-align: right !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. אתחול משתנים ---
if "step" not in st.session_state:
    st.session_state.update({
        "step": "login", "user": "", "lesson_text": "",
        "quiz_active": False, "quiz_idx": 0, "quiz_answers": {}, "quiz_questions": [], "quiz_done": False,
        "checked_questions": set() # מעקב אחרי שאלות שנבדקו
    })

# --- 3. לוגיקה ---
st.markdown("<h1>🏠 מתווך בקליק</h1>", unsafe_allow_html=True)

if st.session_state.step == "login":
    name = st.text_input("הכנס שם מלא:")
    if st.button("כניסה"):
        if name:
            st.session_state.user = name
            st.session_state.step = "menu"
            st.rerun()

elif st.session_state.step == "menu":
    st.markdown(f"### שלום, {st.session_state.user} 👋")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📚 לימוד עיוני + שאלון"):
            st.session_state.step = "study"
            st.rerun()
    with col2:
        if st.button("📝 סימולציית בחינה (25 שאלות)"):
             st.info("סימולציה מלאה עם הסברים מופעלת כאן")

elif st.session_state.step == "study":
    topic = st.selectbox("בחר נושא:", ["חוק המתווכים", "חוק המקרקעין", "חוק החוזים"])
    
    if not st.session_state.lesson_text:
        if st.button("📖 התחל שיעור"):
            try:
                genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                model = genai.GenerativeModel('gemini-2.0-flash')
                response = model.generate_content(f"כתוב שיעור מפורט על {topic} למבחן המתווכים", stream=True)
                placeholder = st.empty()
                full_text = ""
                for chunk in response:
                    full_text += chunk.text
                    placeholder.markdown(f"<div class='lesson-box'>{full_text}</div>", unsafe_allow_html=True)
                st.session_state.lesson_text = full_text
                st.rerun()
            except Exception as e:
                st.error(f"שגיאה בחיבור ל-AI: {str(e)}")

    if st.session_state.lesson_text:
        st.markdown(f"<div class='lesson-box'>{st.session_state.lesson_text}</div>", unsafe_allow_html=True)
        
        if not st.session_state.quiz_active and not st.session_state.quiz_done:
            if st.button("✍️ סיימתי לקרוא, עבור לתרגול"):
                st.session_state.quiz_questions = [
                    {
                        "q": f"שאלה {i+1} על {topic}:", 
                        "options": ["אופציה א'", "אופציה ב'", "אופציה ג'", "אופציה ד'"], 
                        "correct": "אופציה א'", 
                        "reason": "זהו ההסבר המפורט מדוע התשובה נכונה.",
                        "source": "ניתן למצוא זאת בחומר תחת הכותרת הרלוונטית או בסעיף חוק מתאים."
                    } for i in range(10)
                ]
                st.session_state.quiz_active = True
                st.rerun()

    if st.session_state.quiz_active:
        idx = st.session_state.quiz_idx
        q = st.session_state.quiz_questions[idx]
        st.markdown(f"#### שאלון תרגול: {idx+1}/10")
        
        ans = st.radio(q['q'], q['options'], key=f"sq_{idx}", index=None)
        
        # כפתור בדיקה
        if ans and idx not in st.session_state.checked_questions:
            if st.button("🔍 בדוק תשובה"):
                st.session_state.quiz_answers[idx] = ans
                st.session_state.checked_questions.add(idx)
                st.rerun()

        # הצגת הסבר רק אם נבדק
        if idx in st.session_state.checked_questions:
            user_ans = st.session_state.quiz_answers.get(idx)
            is_correct = (user_ans == q['correct'])
            style = "success" if is_correct else "error"
            icon = "✅ נכון!" if is_correct else f"❌ טעות. התשובה הנכונה: {q['correct']}"
            
            st.markdown(f"""
                <div class='explanation-box {style}'>
                    <b>{icon}</b><br>
                    {q['reason']}<br><br>
                    <span class='source-tag'>📍 היכן זה מופיע?</span> {q['source']}
                </div>
            """, unsafe_allow_html=True)
        
        # ניווט
        c1, c2 = st.columns(2)
        if c1.button("⬅️ הקודם") and idx > 0:
            st.session_state.quiz_idx -= 1
            st.rerun()
        if idx < 9:
            if c2.button("הבא ➡️"):
                st.session_state.quiz_idx += 1
                st.rerun()
        else:
            if st.button("🏁 סיום כל השאלון"):
                st.session_state.quiz_active = False
                st.session_state.quiz_done = True
                st.rerun()

    if st.session_state.quiz_done:
        score = sum(1 for i, q in enumerate(st.session_state.quiz_questions) if st.session_state.quiz_answers.get(i) == q['correct'])
        st.markdown(f"<div class='score-box'><h3>ציון סופי: {score*10}</h3><p>{score}/10 נכונות</p></div>", unsafe_allow_html=True)
        if st.button("חזרה לתפריט"):
            st.session_state.update({"lesson_text":"", "quiz_active":False, "quiz_done":False, "quiz_idx":0, "quiz_answers":{}, "checked_questions": set()})
            st.session_state.step = "menu"
            st.rerun()
