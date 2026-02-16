# ==========================================
# Project: מתווך בקליק
# File: app.py
# Version: 1127 (Full Integrated)
# Last Updated: 2026-02-16 | 18:50
# ==========================================

import streamlit as st
import google.generativeai as genai
import json, re

# --- הגדרות דף ו-UI ---
st.set_page_config(page_title="מתווך בקליק", layout="wide")

st.markdown("""
<style>
    * { direction: rtl; text-align: right; }
    .user-strip { background-color: rgba(0,0,0,0.05); padding: 8px 15px; border-radius: 8px; margin-bottom: 20px; font-weight: bold; text-align: left; }
    .stButton>button { width: 100%; border-radius: 8px; }
    [data-testid="stSidebar"] { direction: rtl; }
</style>
""", unsafe_allow_html=True)

# --- ניהול זיכרון (Session State) ---
if "step" not in st.session_state:
    st.session_state.update({
        "step": "login", "user": None, "selected_topic": None,
        "lesson_titles": [], "lesson_contents": {}, "current_sub_idx": None,
        "show_topic_exam": False, "topic_exam_questions": [],
        "current_exam_q_idx": 0
    })

# --- מנוע ה-AI (מופרד לוגית) ---
def ask_ai(prompt):
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        if "429" in str(e): st.warning("⚠️ מכסת ה-AI הסתיימה זמנית. נסה שוב בעוד דקה.")
        return None

# --- בלוק לוגיקת שיעורים (Study Logic) ---
def fetch_titles(topic):
    p = f"צור 3 כותרות מקצועיות לשיעור על {topic} עבור מתווכים. החזר JSON בלבד: ['title1', 'title2', 'title3']"
    res = ask_ai(p)
    try:
        match = re.search(r'\[.*\]', res, re.DOTALL)
        return json.loads(match.group())
    except: return ["מבוא", "עיקרי החוק", "היבטים מעשיים"]

def fetch_content(main_topic, sub_title):
    p = f"כתוב שיעור מפורט בפורמט Markdown על '{sub_title}' בתוך '{main_topic}'. כלול סעיפי חוק ודוגמאות."
    return ask_ai(p)

# --- בלוק לוגיקת מבחנים (Exam Logic) ---
def fetch_questions(topic, count=10):
    p = f"צור {count} שאלות אמריקאיות על {topic}. לכל שאלה: q, options, correct. החזר JSON בלבד."
    res = ask_ai(p)
    try:
        match = re.search(r'\[.*\]', res, re.DOTALL)
        return json.loads(match.group())
    except: return []

# --- ממשק משתמש (UI) ---

if st.session_state.user:
    st.markdown(f'<div class="user-strip">👤 שלום, {st.session_state.user}</div>', unsafe_allow_html=True)

st.title("🏠 מתווך בקליק")

if st.session_state.step == 'login':
    u_name = st.text_input("שם מלא:")
    if st.button("כניסה"):
        if u_name: st.session_state.user = u_name; st.session_state.step = 'menu'; st.rerun()

elif st.session_state.step == 'menu':
    c1, c2 = st.columns(2)
    if c1.button("📚 לימוד לפי נושאים"): st.session_state.step = 'study'; st.rerun()
    if c2.button("⏱️ סימולציית בחינה"): st.session_state.step = 'exam_init'; st.rerun()

elif st.session_state.step == 'study':
    all_topics = [
        "חוק המתווכים במקרקעין", "תקנות המתווכים (פרטי הזמנה)", "תקנות המתווכים (פעולות שיווק)",
        "חוק המקרקעין", "חוק הגנת הדייר", "חוק המכר (דירות)", "חוק החוזים (חלק כללי)",
        "חוק החוזים (תרופות)", "חוק הגנת הצרכן", "חוק עבירות עונשין", "חוק שמאי מקרקעין",
        "חוק התכנון והבנייה", "חוק מיסוי מקרקעין", "חוק הירושה", "חוק הוצאה לפועל", "פקודת הנזיקין"
    ]
    sel = st.selectbox("בחר נושא:", all_topics)
    if st.button("התחל שיעור"):
        with st.spinner("מכין ראשי פרקים..."):
            st.session_state.selected_topic = sel
            st.session_state.lesson_titles = fetch_titles(sel)
            st.session_state.current_sub_idx = None
            st.session_state.lesson_contents = {}
            st.session_state.step = 'lesson_run'; st.rerun()

elif st.session_state.step == 'lesson_run':
    st.header(f"📖 {st.session_state.selected_topic}")
    
    # 3 כפתורי תתי-נושאים (Disabled לנבחר)
    cols = st.columns(3)
    for i, title in enumerate(st.session_state.lesson_titles):
        is_curr = (st.session_state.current_sub_idx == i)
        if cols[i].button(title, disabled=is_curr):
            st.session_state.current_sub_idx = i
            if title not in st.session_state.lesson_contents:
                with st.spinner(f"מייצר תוכן על {title}..."):
                    st.session_state.lesson_contents[title] = fetch_content(st.session_state.selected_topic, title)
            st.rerun()

    # תצוגת חומר הלימוד
    idx = st.session_state.current_sub_idx
    if idx is not None:
        title = st.session_state.lesson_titles[idx]
        st.markdown(f"### {title}")
        st.markdown(st.session_state.lesson_contents.get(title, ""))
        
        st.write("---")
        b1, b2, b3 = st.columns(3)
        with b1:
            if st.button("📝 שאלון 10 שאלות"):
                st.session_state.topic_exam_questions = fetch_questions(st.session_state.selected_topic)
                st.session_state.show_topic_exam = True; st.rerun()
        with b2:
            if st.button("🏠 תפריט ראשי"): st.session_state.step = 'menu'; st.rerun()
        with b3:
            if st.button("🔝 לראש העמוד"): st.rerun()

    if st.session_state.show_topic_exam:
        st.divider()
        st.subheader(f"שאלון תרגול: {st.session_state.selected_topic}")
        for q_idx, q in enumerate(st.session_state.topic_exam_questions):
            st.radio(f"{q_idx+1}. {q['q']}", q['options'], index=None, key=f"q_{q_idx}")
        if st.button("סגור שאלון"): st.session_state.show_topic_exam = False; st.rerun()

elif st.session_state.step == 'exam_init':
    st.session_state.current_exam_q_idx = 0
    st.session_state.step = 'exam_run'; st.rerun()

elif st.session_state.step == 'exam_run':
    # לוח ניווט בחינה (Sidebar)
    with st.sidebar:
        st.header("📌 ניווט שאלות")
        for r in range(5):
            c_row = st.columns(5)
            for i in range(5):
                n = r * 5 + i
                if c_row[i].button(f"{n+1}", key=f"nav_{n}"):
                    st.session_state.current_exam_q_idx = n; st.rerun()
        if st.button("🏁 סיום"): st.session_state.step = 'menu'; st.rerun()
    
    st.subheader(f"שאלה {st.session_state.current_exam_q_idx + 1}")
    st.radio("בחר תשובה:", ["אפשרות 1", "אפשרות 2", "אפשרות 3", "אפשרות 4"], index=None)
