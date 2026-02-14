import streamlit as st
import google.generativeai as genai
import re

# 1. הגדרות RTL ועיצוב
st.set_page_config(page_title="מתווך בקליק", layout="wide")

st.markdown("""
<style>
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stMarkdownContainer"] {
        direction: rtl !important; text-align: right !important;
    }
    [data-testid="stSidebar"] { direction: rtl !important; text-align: right !important; }
    [data-testid="stSidebarCollapsedControl"] { right: 10px !important; left: auto !important; }
    ul, ol { direction: rtl !important; text-align: right !important; padding-right: 1.5rem !important; list-style-position: inside !important; }
    .stButton button { width: 100%; text-align: right !important; }
    div[role="radiogroup"] { direction: rtl !important; }
    .main-header { font-size: 26px; font-weight: bold; text-align: center !important; color: #1E88E5; border-bottom: 2px solid #1E88E5; padding-bottom: 10px; margin-bottom: 20px; }
</style>
""", unsafe_allow_html=True)

# 2. ניהול Session State
state_keys = {
    "view_mode": "login", "user_name": "", "current_topic": "", 
    "lesson_data": "", "lesson_quiz_data": [], "history": []
}
for k, v in state_keys.items():
    if k not in st.session_state:
        st.session_state[k] = v

# חיבור ל-Gemini 2.0 Flash
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    # שימוש במודל 2.0 כפי שסיכמנו
    model = genai.GenerativeModel('gemini-2.0-flash')

TOPICS_LIST = [
    "חוק המתווכים במקרקעין", "חוק המקרקעין", "חוק המכר (דירות)", 
    "חוק הגנת הצרכן", "חוק החוזים", "מיסוי מקרקעין"
]

def parse_quiz(text):
    """מפענח שאלות בצורה חכמה עבור Gemini 2.0"""
    qs = []
    # פיצול השאלות לפי תבנית מספרית או תגית
    blocks = re.split(r"\[START_Q\]|\n\d\.", text)[1:]
    for b in blocks:
        try:
            lines = [l.strip() for l in b.split('\n') if l.strip()]
            if len(lines) >= 5:
                q_text = lines[0].replace('QUESTION:', '').strip()
                opts = lines[1:5]
                # חילוץ התשובה הנכונה מהסוף
                ans_match = re.search(r"(\d)", b.split('ANSWER')[-1])
                ans_idx = int(ans_match.group(1)) - 1 if ans_match else 0
                if 0 <= ans_idx <= 3:
                    qs.append({"q": q_text, "options": opts, "correct": ans_idx})
        except: continue
    return qs[:5]

# --- Sidebar ---
if st.session_state.user_name:
    with st.sidebar:
        st.write(f"### שלום, {st.session_state.user_name}")
        if st.button("📚 בחירת נושא חדש"):
            st.session_state.view_mode = "setup"; st.rerun()
        if st.session_state.current_topic:
            st.markdown("---")
            if st.button("📖 קרא שיעור"):
                st.session_state.view_mode = "lesson_view"; st.rerun()
            if st.button("✍️ שאלון תרגול (Gemini 2.0)"):
                st.session_state.lesson_quiz_data = [] 
                st.session_state.view_mode = "lesson_quiz"; st.rerun()
        if st.session_state.history:
            st.markdown("---")
            st.write("📊 **היסטוריה:**")
            for h in st.session_state.history:
                st.write(f"• {h['topic']}: {h['score']}/5")

# --- לוגיקת דפים ---
if st.session_state.view_mode == "login":
    st.markdown('<div class="main-header">🎓 מתווך בקליק - Gemini 2.0</div>', unsafe_allow_html=True)
    name = st.text_input("שם משתמש:")
    if st.button("התחבר"):
        if name: st.session_state.user_name = name; st.session_state.view_mode = "setup"; st.rerun()

elif st.session_state.view_mode == "setup":
    st.markdown('<div class="main-header">מה נלמד היום?</div>', unsafe_allow_html=True)
    t = st.selectbox("בחר נושא:", TOPICS_LIST)
    if st.button("התחל ללמוד"):
        st.session_state.current_topic = t
        st.session_state.lesson_data = ""; st.session_state.lesson_quiz_data = []
        st.session_state.view_mode = "lesson_view"; st.rerun()

elif st.session_state.view_mode == "lesson_view":
    st.markdown(f'<div class="main-header">{st.session_state.current_topic}</div>', unsafe_allow_html=True)
    if not st.session_state.lesson_data:
        full_text = ""; placeholder = st.empty()
        resp = model.generate_content(f"כתוב שיעור מפורט למבחן המתווכים על {st.session_state.current_topic}. השתמש בבולטים.", stream=True)
        for chunk in resp:
            full_text += chunk.text; placeholder.markdown(full_text)
        st.session_state.lesson_data = full_text
    else: st.markdown(st.session_state.lesson_data)
    if st.button("🎯 עבור לשאלון תרגול", type="primary"):
        st.session_state.view_mode = "lesson_quiz"; st.rerun()

elif st.session_state.view_mode == "lesson_quiz":
    st.markdown(f'<div class="main-header">תרגול: {st.session_state.current_topic}</div>', unsafe_allow_html=True)
    
    if not st.session_state.lesson_quiz_data:
        with st.spinner("Gemini 2.0 מייצר עבורך 5 שאלות..."):
            prompt = f"צור 5 שאלות אמריקאיות על {st.session_state.current_topic}. פורמט: [START_Q] שאלה, 4 תשובות, [ANSWER] מספר."
            res = model.generate_content(prompt)
            st.session_state.lesson_quiz_data = parse_quiz(res.text)
            if not st.session_state.lesson_quiz_data:
                st.error("ה-AI לא הצליח לייצר שאלות. נסה שוב.")
            else: st.rerun()

    if st.session_state.lesson_quiz_data:
        with st.form("quiz_form"):
            choices = []
            for i, q in enumerate(st.session_state.lesson_quiz_data):
                st.write(f"**{i+1}. {q['q']}**")
                choices.append(st.radio(f"בחירה {i+1}:", q['options'], key=f"q_{i}", index=None))
            if st.form_submit_button("בדוק ציון"):
                score = sum(1 for i, q in enumerate(st.session_state.lesson_quiz_data) if choices[i] and choices[i] == q['options'][q['correct']])
                st.success(f"הציון שלך: {score} מתוך 5")
                st.session_state.history.append({"topic": st.session_state.current_topic, "score": score})
