import streamlit as st
import google.generativeai as genai
import re

# 1. הגדרות עיצוב RTL ונעילת כותרות
st.set_page_config(page_title="מתווך בקליק", layout="wide")

st.markdown("""
    <style>
    html, body, [data-testid="stAppViewContainer"], .main, .block-container, h1, h2, h3, p, li, span, label {
        direction: rtl !important;
        text-align: right !important;
    }
    .sidebar-logo {
        font-size: 34px !important; font-weight: bold; text-align: center !important;
        margin-top: -50px !important; color: #1E88E5; display: block; width: 100%;
    }
    [data-testid="stSidebar"] button { width: 100% !important; margin-bottom: 10px; }
    .quiz-card { 
        background-color: #f9f9f9; padding: 20px; border-radius: 12px; 
        border-right: 6px solid #1E88E5; margin-bottom: 20px;
    }
    </style>
    <script>
        var mainSection = window.parent.document.querySelector('section.main');
        if (mainSection) { mainSection.scrollTo(0, 0); }
    </script>
    """, unsafe_allow_html=True)

# 2. ניהול משתנים
for key, default in [
    ("user_name", ""), ("view_mode", "login"), ("lesson_data", ""), 
    ("quiz_data", []), ("history", []), ("lesson_count", 0), 
    ("user_answers", {}), ("current_topic", "")
]:
    if key not in st.session_state: st.session_state[key] = default

if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-2.0-flash')

# פונקציית חילוץ שאלות משופרת
def parse_quiz(text):
    questions = []
    # חיפוש גמיש יותר של בלוקים
    blocks = re.findall(r"\[START_Q\](.*?)\[END_Q\]", text, re.DOTALL)
    for b in blocks:
        try:
            # חילוץ שאלה
            q_match = re.search(r"\[QUESTION\](.*?)\[OPTIONS\]", b, re.DOTALL)
            q = q_match.group(1).strip() if q_match else "שאלה חסרה"
            
            # חילוץ אופציות
            opts_match = re.search(r"\[OPTIONS\](.*?)\[ANSWER\]", b, re.DOTALL)
            opts_raw = opts_match.group(1).strip() if opts_match else ""
            options = [re.sub(r"^\d+[\s\).\-]+", "", o.strip()) for o in opts_raw.split('\n') if o.strip()]
            
            # חילוץ תשובה ובסיס חוקי
            ans_match = re.search(r"\[ANSWER\](.*?)(?:\[LAW\]|$)", b, re.DOTALL)
            law_match = re.search(r"\[LAW\](.*?)$", b, re.DOTALL)
            
            ans_val = ans_match.group(1).strip() if ans_match else "1"
            law_val = law_match.group(1).strip() if law_match else "לא צוין מקור חוקי"
            
            # ניקוי מספר התשובה
            correct_idx = int(re.search(r'\d', ans_val).group()) - 1
            
            questions.append({
                "q": q, 
                "options": options[:4], 
                "correct": correct_idx if 0 <= correct_idx < 4 else 0, 
                "ref": law_val
            })
        except: continue
    return questions

# 3. סרגל צידי
if st.session_state.user_name:
    with st.sidebar:
        st.markdown('<div class="sidebar-logo">🎓 מתווך בקליק</div>', unsafe_allow_html=True)
        st.write(f"שלום, **{st.session_state.user_name}**")
        st.markdown("---")
        if st.button("➕ נושא חדש"):
            st.session_state.update({"lesson_data": "", "quiz_data": [], "user_answers": {}, "view_mode": "setup"})
            st.rerun()
        if st.session_state.current_topic:
            if st.button("📖 חזרה לשיעור"):
                st.session_state.view_mode = "lesson"; st.rerun()
            if st.button("📝 מעבר למבחן"):
                st.session_state.view_mode = "quiz"; st.rerun()
        st.markdown("---")
        for h in st.session_state.history: st.caption(f"• {h}")

# 4. תוכן ראשי
if st.session_state.view_mode == "login":
    st.title("🎓 מתווך בקליק")
    name = st.text_input("הזן שם:")
    if st.button("כניסה"):
        if name: st.session_state.user_name = name; st.session_state.view_mode = "setup"; st.rerun()

elif st.session_state.view_mode == "setup":
    st.title(f"מה נלמד, {st.session_state.user_name}?")
    topic = st.selectbox("בחר נושא:", ["חוק המתווכים", "חוק המקרקעין", "דיני חוזים", "דיני תכנון ובנייה"])
    if st.button("הכן שיעור"):
        st.session_state.lesson_count += 1
        st.session_state.current_topic = topic
        st.session_state.user_answers = {}
        pb = st.progress(0); stext = st.empty()
        try:
            stext.text("📖 כותב שיעור..."); pb.progress(30)
            res = model.generate_content(f"כתוב שיעור מפורט על {topic} למבחן המתווכים.")
            st.session_state.lesson_data = res.text
            
            stext.text("📝 מייצר שאלות..."); pb.progress(70)
            q_prompt = f"צור 3 שאלות אמריקאיות על {topic}. חובה להשתמש בפורמט הזה בדיוק:\n[START_Q]\n[QUESTION] הטקסט\n[OPTIONS]\n1) א\n2) ב\n3) ג\n4) ד\n[ANSWER] מספר התשובה\n[LAW] סעיף החוק והסבר\n[END_Q]"
            q_res = model.generate_content(q_prompt)
            st.session_state.quiz_data = parse_quiz(q_res.text)
            
            pb.progress(100); stext.empty()
            if topic not in [h.split(". ", 1)[-1] for h in st.session_state.history]:
                st.session_state.history.append(f"{st.session_state.lesson_count}. {topic}")
            st.session_state.view_mode = "lesson"; st.rerun()
        except Exception as e: st.error(f"שגיאה: {e}")

elif st.session_state.view_mode == "lesson":
    st.title(f"שיעור: {st.session_state.current_topic}")
    st.markdown(st.session_state.lesson_data)
    if st.button("למבחן 📝"):
        st.session_state.view_mode = "quiz"; st.rerun()

elif st.session_state.view_mode == "quiz":
    st.title(f"תרגול: {st.session_state.current_topic}")
    if not st.session_state.quiz_data:
        st.error("ה-AI לא הצליח לייצר שאלות הפעם. נסה ללחוץ על 'נושא חדש' ולבחור שוב.")
    else:
        for i, q in enumerate(st.session_state.quiz_data):
            st.markdown('<div class="quiz-card">', unsafe_allow_html=True)
            st.write(f"**{i+1}. {q['q']}**")
            ans = st.radio("בחר:", q['options'], key=f"q{i}", index=None, label_visibility="collapsed")
            if st.button(f"בדוק תשובה {i+1}", key=f"b{i}"):
                if ans:
                    is_correct = q['options'].index(ans) == q['correct']
                    st.session_state.user_answers[i] = is_correct
                    if is_correct: st.success("נכון מאוד!")
                    else: st.error(f"לא נכון. התשובה הנכונה היא: {q['options'][q['correct']]}")
                    st.info(f"⚖️ **הסבר:** {q['ref']}")
            st.markdown('</div>', unsafe_allow_html=True)
