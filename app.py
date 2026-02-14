import streamlit as st
import google.generativeai as genai
import re
import time
import streamlit.components.v1 as components

# 1. הגדרות עיצוב RTL ואיפוס גלילה
st.set_page_config(page_title="מתווך בקליק", layout="wide")

# סקריפט לאיפוס גלילה לראש הדף במעבר בין מצבים
components.html(
    f"""
    <script>
        window.parent.document.querySelector('section.main').scrollTo(0, 0);
    </script>
    """,
    height=0
)

st.markdown("""
    <style>
    /* יישור גלובלי אגרסיבי לימין */
    html, body, [data-testid="stAppViewContainer"], .main, .block-container {
        direction: rtl !important;
        text-align: right !important;
    }
    
    /* וידוא שכל אלמנט טקסט בתוך המרחב המרכזי מיושר לימין */
    .stMarkdown, .stMarkdown p, .stMarkdown li, .stMarkdown div, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        direction: rtl !important;
        text-align: right !important;
        unicode-bidi: bidi-override !important;
    }

    /* תיקון רשימות (Bullet points) שבורחות לשמאל */
    .stMarkdown ul, .stMarkdown ol {
        padding-right: 2rem !important;
        padding-left: 0 !important;
        text-align: right !important;
    }

    [data-testid="stSidebar"], [data-testid="stSidebar"] * {
        direction: rtl !important;
        text-align: right !important;
    }
    
    div.stButton > button { 
        width: 100%; border-radius: 8px; font-weight: bold;
        background-color: #1E88E5; color: white;
    }
    
    .quiz-card { 
        background-color: #ffffff; padding: 20px; border-radius: 12px; 
        border-right: 6px solid #1E88E5; box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. ניהול משתני מערכת
if "user_name" not in st.session_state: st.session_state.user_name = ""
if "view_mode" not in st.session_state: st.session_state.view_mode = "login"
if "lesson_data" not in st.session_state: st.session_state.lesson_data = ""
if "quiz_data" not in st.session_state: st.session_state.quiz_data = []
if "history" not in st.session_state: st.session_state.history = []
if "lesson_count" not in st.session_state: st.session_state.lesson_count = 0
if "user_answers" not in st.session_state: st.session_state.user_answers = {}
if "current_topic" not in st.session_state: st.session_state.current_topic = ""

# 3. אתחול AI
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-2.0-flash')

def parse_quiz(quiz_text):
    questions = []
    raw_questions = re.findall(r"\[START_Q\](.*?)\[END_Q\]", quiz_text, re.DOTALL)
    for q_block in raw_questions:
        try:
            q_text = re.search(r"\[QUESTION\](.*?)\[OPTIONS\]", q_block, re.DOTALL).group(1).strip()
            opts_text = re.search(r"\[OPTIONS\](.*?)\[ANSWER\]", q_block, re.DOTALL).group(1).strip()
            ans_val = re.search(r"\[ANSWER\](.*?)\[LAW\]", q_block, re.DOTALL).group(1).strip()
            law_val = re.search(r"\[LAW\](.*?)$", q_block, re.DOTALL).group(1).strip()
            
            options = [opt.strip() for opt in opts_text.split('\n') if opt.strip()]
            clean_options = [re.sub(r"^\d+[\s\).\-]+", "", opt) for opt in options[:4]]
            
            questions.append({
                "q": q_text,
                "options": clean_options,
                "correct": int(re.search(r'\d', ans_val).group()) - 1,
                "ref": law_val
            })
        except:
            continue
    return questions

# --- סרגל צידי ---
if st.session_state.user_name:
    with st.sidebar:
        st.markdown("<h2 style='text-align: center;'>🎓 מתווך בקליק</h2>", unsafe_allow_html=True)
        st.markdown("---")
        if st.button("➕ בחירת נושא חדש"):
            st.session_state.view_mode = "setup"; st.rerun()
        if st.session_state.view_mode == "lesson" and st.session_state.quiz_data:
            if st.button(f"📝 מעבר למבחן: {st.session_state.current_topic}"):
                st.session_state.view_mode = "quiz"; st.rerun()
        if st.session_state.view_mode == "quiz":
            if st.button(f"📖 חזרה לשיעור: {st.session_state.current_topic}"):
                st.session_state.view_mode = "lesson"; st.rerun()
        st.markdown("---")
        for item in st.session_state.history: st.caption(f"• {item}")

# --- ניהול דפים ---
if st.session_state.view_mode == "login":
    st.markdown("<h1>🎓 מתווך בקליק</h1>", unsafe_allow_html=True)
    name = st.text_input("הזן שם כדי להתחיל:")
    if st.button("כניסה למערכת"):
        if name: st.session_state.user_name = name; st.session_state.view_mode = "setup"; st.rerun()

elif st.session_state.view_mode == "setup":
    st.markdown(f"<h1>מה נלמד היום, {st.session_state.user_name}?</h1>", unsafe_allow_html=True)
    topic = st.selectbox("בחר נושא:", ["חוק המתווכים", "חוק המקרקעין", "דיני חוזים", "דיני תכנון ובנייה"])
    if st.button("הכן שיעור"):
        st.session_state.lesson_count += 1
        st.session_state.current_topic = topic
        st.session_state.user_answers = {}
        bar = st.progress(0)
        try:
            bar.progress(30)
            res = model.generate_content(f"כתוב שיעור מפורט על {topic} למבחן המתווכים. השתמש בכותרות ונקודות.")
            st.session_state.lesson_data = res.text
            bar.progress(70)
            q_prompt = f"""צור 3 שאלות אמריקאיות על {topic}. פורמט:
            [START_Q]
            [QUESTION] טקסט השאלה [OPTIONS]
            1) אופציה
            2) אופציה
            3) אופציה
            4) אופציה
            [ANSWER] מספר [LAW] סעיף חוק והסבר
            [END_Q]
            """
            quiz_res = model.generate_content(q_prompt)
            st.session_state.quiz_data = parse_quiz(quiz_res.text)
            if topic not in [h.split(". ", 1)[-1] for h in st.session_state.history]:
                st.session_state.history.append(f"{st.session_state.lesson_count}. {topic}")
            bar.progress(100); st.session_state.view_mode = "lesson"; st.rerun()
        except Exception as e: st.error(f"שגיאה: {e}")

elif st.session_state.view_mode == "lesson":
    st.markdown(f"<h1>שיעור {st.session_state.lesson_count}: {st.session_state.current_topic}</h1>", unsafe_allow_html=True)
    st.markdown(f'<div style="direction: rtl; text-align: right;">{st.session_state.lesson_data}</div>', unsafe_allow_html=True)
    if st.button(f"סיימתי ללמוד! למבחן על {st.session_state.current_topic} 📝"):
        st.session_state.view_mode = "quiz"; st.rerun()

elif st.session_state.view_mode == "quiz":
    st.markdown(f"<h1>תרגול: {st.session_state.current_topic}</h1>", unsafe_allow_html=True)
    for i, q in enumerate(st.session_state.quiz_data):
        st.markdown('<div class="quiz-card">', unsafe_allow_html=True)
        st.write(f"**שאלה {i+1}:** {q['q']}")
        ans = st.radio(f"בחירה {i}:", q['options'], key=f"q{i}", index=None, label_visibility="collapsed")
        if st.button(f"בדוק שאלה {i+1}", key=f"b{i}"):
            if ans:
                idx = q['options'].index(ans)
                st.session_state.user_answers[i] = (idx == q['correct'])
                if idx == q['correct']: st.success("✅ נכון!")
                else: st.error(f"❌ טעות. התשובה הנכונה היא: {q['options'][q['correct']]}")
                st.info(f"⚖️ **ביסוס משפטי:** {q['ref']}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    if len(st.session_state.user_answers) == len(st.session_state.quiz_data):
        correct = sum(st.session_state.user_answers.values())
        st.markdown(f'<div class="score-box">סיכום: ענית נכון על {correct} מתוך {len(st.session_state.quiz_data)}<br>ציון: {int(correct/len(st.session_state.quiz_data)*100)}</div>', unsafe_allow_html=True)
