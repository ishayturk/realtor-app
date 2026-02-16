# ==========================================
# Project: מתווך בקליק
# File: app.py
# Version: 1135
# Last Updated: 2026-02-16 | 21:00
# ==========================================

import streamlit as st
import google.generativeai as genai
import json, re

# --- הגדרות דף ---
st.set_page_config(page_title="מתווך בקליק", layout="wide")

def ask_ai(prompt):
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        if "429" in str(e): st.warning("⚠️ עומס במערכת. נסה שוב בעוד דקה.")
        return None

# --- לוגיקת תוכן ושאלות ---
def fetch_titles(topic):
    p = f"צור 3 כותרות קצרות (2-3 מילים) לתתי-נושאים בתוך {topic}. ללא המילים 'חלק' או 'פרק'. השתמש במושגים מקצועיים. החזר JSON בלבד: ['כותרת1', 'כותרת2', 'כותרת3']"
    res = ask_ai(p)
    try:
        match = re.search(r'\[.*\]', res, re.DOTALL)
        return json.loads(match.group())
    except: return ["יסודות החוק", "חובות וסמכויות", "הוראות מעשיות"]

def fetch_content(main_topic, sub_title):
    p = f"כתוב שיעור מפורט בפורמט Markdown על '{sub_title}' בתוך '{main_topic}'. כלול סעיפי חוק ודוגמאות."
    return ask_ai(p)

def fetch_single_question(topic):
    p = f"צור שאלה אמריקאית אחת קשה על {topic}. לכל שאלה: q (שאלה), options (רשימת 4 אפשרויות), correct (התשובה המדויקת). החזר JSON בלבד במבנה אובייקט {{}}."
    res = ask_ai(p)
    try:
        match = re.search(r'\{.*\}', res, re.DOTALL)
        return json.loads(match.group())
    except: return None

# --- ניהול Session State ---
if "step" not in st.session_state:
    st.session_state.update({
        "step": "login", "user": None, "selected_topic": None,
        "lesson_titles": [], "lesson_contents": {}, "current_sub_idx": None,
        "quiz_active": False, "current_q_data": None, "next_q_buffer": None,
        "q_counter": 0, "score": 0, "user_choice": None
    })

# --- CSS (Dark Mode Support & RTL) ---
st.markdown("""
<style>
    * { direction: rtl; text-align: right; }
    :root { --text-color: inherit; --bg-card: rgba(255,255,255,0.05); }
    .user-strip { 
        background-color: var(--bg-card); 
        padding: 10px; border-radius: 8px; margin-bottom: 20px; 
        font-weight: bold; text-align: left; border: 1px solid rgba(128,128,128,0.3);
    }
    .stButton>button { width: 100%; border-radius: 8px; height: 3.5em; font-weight: bold; }
    .question-box { 
        background-color: rgba(128,128,128,0.1); 
        padding: 20px; border-radius: 10px; border: 1px solid rgba(128,128,128,0.2); 
        margin-top: 20px; color: var(--text-color);
    }
    [data-testid="stSidebar"] { direction: rtl; }
</style>
""", unsafe_allow_html=True)

if st.session_state.user:
    st.markdown(f'<div class="user-strip">👤 שלום, {st.session_state.user}</div>', unsafe_allow_html=True)

st.title("🏠 מתווך בקליק")

# --- ניתוב דפים ---

if st.session_state.step == 'login':
    u_name = st.text_input("הזן שם מלא:")
    if st.button("כניסה"):
        if u_name: st.session_state.user = u_name; st.session_state.step = 'menu'; st.rerun()

elif st.session_state.step == 'menu':
    c1, c2 = st.columns(2)
    if c1.button("📚 לימוד לפי נושאים"): st.session_state.step = 'study'; st.rerun()
    if c2.button("⏱️ סימולציית בחינה"): st.session_state.step = 'exam_init'; st.rerun()

elif st.session_state.step == 'study':
    all_topics = [
        "בחר נושא מהרשימה...", "חוק המתווכים במקרקעין", "תקנות המתווכים (פרטי הזמנה)", 
        "תקנות המתווכים (פעולות שיווק)", "חוק המקרקעין", "חוק הגנת הדייר", 
        "חוק המכר (דירות)", "חוק החוזים (חלק כללי)", "חוק החוזים (תרופות)", 
        "חוק הגנת הצרכן", "חוק עבירות עונשין", "חוק שמאי מקרקעין", 
        "חוק התכנון והבנייה", "חוק מיסוי מקרקעין", "חוק הירושה", 
        "חוק הוצאה לפועל", "פקודת הנזיקין"
    ]
    sel = st.selectbox("נושא לימוד:", all_topics, index=0)
    if sel != "בחר נושא מהרשימה..." and st.button("טען שיעור"):
        with st.spinner("מכין ראשי פרקים..."):
            st.session_state.selected_topic = sel
            st.session_state.lesson_titles = fetch_titles(sel)
            st.session_state.current_sub_idx = None
            st.session_state.lesson_contents = {}
            st.session_state.quiz_active = False
            st.session_state.step = 'lesson_run'; st.rerun()

elif st.session_state.step == 'lesson_run':
    st.header(f"📖 {st.session_state.selected_topic}")
    cols = st.columns(3)
    for i, title in enumerate(st.session_state.lesson_titles):
        if cols[i].button(title, disabled=(st.session_state.current_sub_idx == i)):
            st.session_state.current_sub_idx = i
            if title not in st.session_state.lesson_contents:
                with st.spinner(f"טוען {title}..."):
                    st.session_state.lesson_contents[title] = fetch_content(st.session_state.selected_topic, title)
            st.rerun()

    if st.session_state.current_sub_idx is not None:
        curr_t = st.session_state.lesson_titles[st.session_state.current_sub_idx]
        st.markdown(st.session_state.lesson_contents.get(curr_t, ""))
        st.write("---")
        
        if not st.session_state.quiz_active:
            if st.button(f"📝 התחל שאלון תרגול - {st.session_state.selected_topic}"):
                with st.spinner("מייצר שאלה ראשונה..."):
                    st.session_state.current_q_data = fetch_single_question(st.session_state.selected_topic)
                    st.session_state.quiz_active = True
                    st.session_state.q_counter = 1
                    st.session_state.score = 0
                    st.session_state.next_q_buffer = fetch_single_question(st.session_state.selected_topic)
                    st.rerun()
        
        if st.session_state.quiz_active and st.session_state.current_q_data:
            st.markdown(f"### 📝 שאלון - {st.session_state.selected_topic}")
            st.info(f"שאלה {st.session_state.q_counter} מתוך 10")
            q = st.session_state.current_q_data
            st.session_state.user_choice = st.radio(q['q'], q['options'], index=None, key=f"q_{st.session_state.q_counter}")
            st.write("")
            b_cols = st.columns([2, 1, 1])
            label = "שאלה הבאה ➡️" if st.session_state.q_counter < 10 else "סיים ובדוק ציון 🏁"
            if b_cols[0].button(label):
                if st.session_state.user_choice == q['correct']:
                    st.session_state.score += 1
                if st.session_state.q_counter < 10:
                    st.session_state.current_q_data = st.session_state.next_q_buffer
                    st.session_state.q_counter += 1
                    if st.session_state.q_counter < 10:
                        st.session_state.next_q_buffer = fetch_single_question(st.session_state.selected_topic)
                    st.rerun()
                else:
                    st.success(f"השלמת את השאלון! ציון סופי: {st.session_state.score * 10}/100")
                    st.session_state.quiz_active = False
            if b_cols[1].button("🔝 לראש העמוד"): st.rerun()
            if b_cols[2].button("🏠 לתפריט"): st.session_state.step = 'menu'; st.rerun()

elif st.session_state.step == 'exam_init':
    st.session_state.step = 'menu'; st.rerun()
