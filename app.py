import streamlit as st
import google.generativeai as genai
import time

# --- 1. הגדרות תצוגה חסינות ---
st.set_page_config(page_title="מתווך בקליק", layout="centered")

st.markdown("""
    <style>
    [data-testid="stAppViewContainer"], .main, .block-container { direction: rtl !important; text-align: right !important; }
    h1, h2, h3 { text-align: center !important; color: #1E88E5; width: 100%; }
    .stButton > button { width: 100%; font-weight: bold; height: 3.5em; border-radius: 10px; }
    .stMarkdown div[data-testid="stMarkdownContainer"] { text-align: right !important; direction: rtl !important; }
    .score-box { text-align: center; padding: 20px; border-radius: 15px; background: #f0f7ff; border: 2px solid #1E88E5; }
    .timer-box { text-align: center; background: #fff3e0; padding: 10px; border-radius: 10px; font-weight: bold; border: 1px solid #ff9800; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. אתחול משתני מערכת (הגנה מפני היעלמות) ---
if "step" not in st.session_state:
    st.session_state.update({
        "step": "login", "user": "", 
        "quiz_mode": False, "quiz_idx": 0, "quiz_answers": {}, "quiz_questions": [], "quiz_finished": False,
        "exam_idx": 0, "exam_answers": {}, "exam_start_time": None
    })

# --- 3. פונקציות שרת ---
def get_10_questions(topic):
    return [{"q": f"שאלה {i+1} על {topic}", "options": ["תשובה א", "תשובה ב", "תשובה ג", "תשובה ד"], "correct": "תשובה א"} for i in range(10)]

def get_25_questions():
    return [{"q": f"שאלה {i+1} מתוך 25", "options": ["תשובה 1", "תשובה 2", "תשובה 3", "תשובה 4"], "correct": "תשובה 1"} for i in range(25)]

# --- 4. לוגיקה מרכזית ---
st.markdown("<h1>🏠 מתווך בקליק</h1>", unsafe_allow_html=True)

# דף כניסה
if st.session_state.step == "login":
    name = st.text_input("הכנס שם מלא:")
    if st.button("התחבר"):
        if name:
            st.session_state.user = name
            st.session_state.step = "menu"
            st.rerun()

# תפריט ראשי
elif st.session_state.step == "menu":
    st.markdown(f"### שלום, {st.session_state.user} 👋")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📚 לימוד עיוני"):
            st.session_state.step = "select_topic"
            st.rerun()
    with col2:
        if st.button("📝 מבחן סימולציה (25)"):
            st.session_state.exam_questions = get_25_questions()
            st.session_state.exam_idx = 0
            st.session_state.exam_answers = {}
            st.session_state.exam_start_time = time.time()
            st.session_state.step = "full_exam"
            st.rerun()

# בחירת נושא ושיעור
elif st.session_state.step == "select_topic":
    topic = st.selectbox("בחר נושא:", ["חוק המתווכים", "חוק המקרקעין", "חוק החוזים"])
    
    if not st.session_state.quiz_mode and not st.session_state.quiz_finished:
        if st.button("📖 התחל שיעור"):
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            model = genai.GenerativeModel('gemini-2.0-flash')
            response = model.generate_content(f"כתוב שיעור על {topic}", stream=True)
            
            placeholder = st.empty()
            full_text = ""
            for chunk in response:
                full_text += chunk.text
                placeholder.markdown(full_text)
            
            st.session_state.quiz_questions = get_10_questions(topic)
            st.session_state.quiz_mode = True
            st.rerun()

    if st.session_state.quiz_mode:
        st.write("---")
        idx = st.session_state.quiz_idx
        q = st.session_state.quiz_questions[idx]
        st.markdown(f"### תרגול: שאלה {idx+1}/10")
        ans = st.radio(q['q'], q['options'], key=f"quiz_{idx}", index=None)
        if ans: st.session_state.quiz_answers[idx] = ans
        
        c1, c2 = st.columns(2)
        if c1.button("⬅️ הקודם") and idx > 0:
            st.session_state.quiz_idx -= 1
            st.rerun()
        if idx < 9:
            if c2.button("הבא ➡️"):
                st.session_state.quiz_idx += 1
                st.rerun()
        elif c2.button("🏁 סיים ובדוק"):
            st.session_state.quiz_mode = False
            st.session_state.quiz_finished = True
            st.rerun()

    if st.session_state.quiz_finished:
        score = sum(1 for i, q in enumerate(st.session_state.quiz_questions) if st.session_state.quiz_answers.get(i) == q['correct'])
        st.markdown(f"<div class='score-box'><h2>ציון: {score*10}</h2><p>ענית על {score}/10</p></div>", unsafe_allow_html=True)
        if st.button("חזרה לתפריט"):
            st.session_state.quiz_finished = False
            st.session_state.step = "menu"
            st.rerun()

# מבחן מלא (25 שאלות)
elif st.session_state.step == "full_exam":
    elapsed = time.time() - st.session_state.exam_start_time
    st.markdown(f"<div class='timer-box'>זמן: {int(elapsed//60):02d}:{int(elapsed%60):02d}</div>", unsafe_allow_html=True)
    
    idx = st.session_state.exam_idx
    q = st.session_state.exam_questions[idx]
    st.markdown(f"### שאלה {idx+1}/25")
    ans = st.radio(q['q'], q['options'], key=f"ex_{idx}")
    
    c1, c2 = st.columns(2)
    if c1.button("⬅️") and idx > 0:
        st.session_state.exam_idx -= 1
        st.rerun()
    if idx < 24:
        if c2.button("➡️"):
            st.session_state.exam_idx += 1
            st.rerun()
    elif c2.button("סיום"):
        st.session_state.step = "menu"
        st.rerun()
