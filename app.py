import streamlit as st
import google.generativeai as genai
import re

# 1. הגדרות RTL ועיצוב
st.set_page_config(page_title="מתווך בקליק - הכנה למבחן", layout="wide")

st.markdown("""
<style>
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stMarkdownContainer"] {
        direction: rtl !important;
        text-align: right !important;
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
state_keys = {"view_mode": "login", "user_name": "", "current_topic": "", "lesson_data": "", "lesson_quiz_data": [], "history": []}
for key, value in state_keys.items():
    if key not in st.session_state:
        st.session_state[key] = value

if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-2.0-flash')

# 3. רשימת הנושאים המלאה למבחן
TOPICS_LIST = [
    "חוק המתווכים במקרקעין",
    "תקנות המתווכים (פרטי הזמנה בכתב)",
    "חוק המקרקעין (עסקאות, רישום, בתים משותפים)",
    "חוק המכר (דירות) (הבטחת השקעות)",
    "חוק הגנת הצרכן",
    "חוק החוזים (חלק כללי וחרופות)",
    "חוק הגנת הדייר",
    "חוק התכנון והבנייה (נושאים נבחרים)",
    "חוק מיסוי מקרקעין (שבח ורכישה)",
    "חוק העונשין (עבירות מרמה וזיוף)",
    "חוק שמאי מקרקעין",
    "דיני ירושה (בהקשר למקרקעין)"
]

def parse_quiz(text):
    qs = []
    blocks = re.split(r"\[START_Q\]", text)[1:]
    for b in blocks:
        try:
            q_m = re.search(r"\[QUESTION\](.*?)\[OPTIONS\]", b, re.DOTALL)
            o_m = re.search(r"\[OPTIONS\](.*?)\[ANSWER\]", b, re.DOTALL)
            a_m = re.search(r"\[ANSWER\]\s*(\d)", b)
            if q_m and o_m and a_m:
                opts = [o.strip() for o in o_m.group(1).strip().split('\n') if o.strip()]
                qs.append({"q": q_m.group(1).strip(), "options": opts[:4], "correct": int(a_m.group(1))-1})
        except: continue
    return qs[:5]

# --- Sidebar ---
if st.session_state.user_name:
    with st.sidebar:
        st.markdown(f"### שלום, {st.session_state.user_name}")
        if st.button("📚 בחירת נושא חדש"):
            st.session_state.view_mode = "setup"; st.rerun()
        if st.session_state.current_topic:
            st.markdown("---")
            st.write(f"📖 **נושא:** {st.session_state.current_topic}")
            if st.button("📖 קרא שיעור"):
                st.session_state.view_mode = "lesson_view"; st.rerun()
            if st.button("✍️ שאלון תרגול"):
                st.session_state.view_mode = "lesson_quiz"; st.rerun()

# --- ניווט ---
if st.session_state.view_mode == "login":
    st.markdown('<div class="main-header">🎓 הכנה למבחן המתווכים</div>', unsafe_allow_html=True)
    name = st.text_input("שם משתמש:")
    if st.button("התחבר"):
        if name: st.session_state.user_name = name; st.session_state.view_mode = "setup"; st.rerun()

elif st.session_state.view_mode == "setup":
    st.markdown('<div class="main-header">בחר נושא לימוד מהסילבוס</div>', unsafe_allow_html=True)
    t = st.selectbox("רשימת החוקים והנושאים:", TOPICS_LIST)
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
    st.button("🎯 עבור לשאלון תרגול", on_click=lambda: st.session_state.update({"view_mode": "lesson_quiz"}), type="primary")

elif st.session_state.view_mode == "lesson_quiz":
    st.markdown(f'<div class="main-header">תרגול: {st.session_state.current_topic}</div>', unsafe_allow_html=True)
    if not st.session_state.lesson_quiz_data:
        with st.spinner("מייצר שאלות..."):
            res = model.generate_content(f"צור 5 שאלות על {st.session_state.current_topic} בפורמט [START_Q] [QUESTION] [OPTIONS] [ANSWER]")
            st.session_state.lesson_quiz_data = parse_quiz(res.text); st.rerun()
    with st.form("quiz"):
        choices = []
        for i, q in enumerate(st.session_state.lesson_quiz_data):
            st.write(f"**{i+1}. {q['q']}**")
            choices.append(st.radio(f"בחירה {i+1}:", q['options'], key=f"q_{i}", index=None))
        if st.form_submit_button("בדוק ציון"):
            score = sum(1 for i, q in enumerate(st.session_state.lesson_quiz_data) if choices[i] and q['options'].index(choices[i]) == q['correct'])
            st.success(f"הציון שלך: {score} מתוך 5")
            st.session_state.history.append({"topic": st.session_state.current_topic, "score": score})
