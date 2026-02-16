# ==========================================
# Project: מתווך בקליק
# File: app.py
# Version: 1149
# Last Updated: 2026-02-16 | 23:55
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
        if response and response.text:
            return response.text
        return None
    except:
        return None

# --- לוגיקה ---
def fetch_titles(topic):
    p = f"צור 3 כותרות לתתי-נושאים בתוך {topic}. JSON: ['א','ב','ג']"
    res = ask_ai(p)
    try:
        match = re.search(r'\[.*\]', res, re.DOTALL)
        return json.loads(match.group())
    except:
        return ["הוראות חוק", "חובות המתווך", "פסיקה"]

def fetch_content(main_topic, sub_title):
    p = f"כתוב שיעור Markdown על '{sub_title}' בתוך '{main_topic}'."
    content = ask_ai(p)
    return content if content else "⚠️ שגיאה בטעינה."

def fetch_question(topic):
    p = f"צור שאלה אמריקאית על {topic}. JSON: {{'q':'..','options':['..'],'correct':'..','explain':'..'}}"
    res = ask_ai(p)
    try:
        match = re.search(r'\{.*\}', res, re.DOTALL)
        return json.loads(match.group())
    except:
        return None

# --- Session State ---
if "step" not in st.session_state:
    st.session_state.update({
        "step": "login", "user": None, "selected_topic": None,
        "lesson_titles": [], "lesson_contents": {}, "current_sub_idx": None,
        "quiz_active": False, "q_counter": 0, "score": 0,
        "current_q_data": None, "show_feedback": False
    })

# --- CSS ---
st.markdown("""
<style>
    * { direction: rtl; text-align: right; }
    .user-strip { margin-top: -15px; margin-bottom: 20px; font-weight: bold; }
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; }
    .nav-box { margin-top: 40px; border-top: 1px solid #eee; padding-top: 10px; }
</style>
""", unsafe_allow_html=True)

# --- כותרות ---
st.title("🏠 מתווך בקליק")
if st.session_state.user:
    st.markdown(f'<div class="user-strip">👤 שלום, {st.session_state.user}</div>', unsafe_allow_html=True)

# --- ניתוב ---
if st.session_state.step == 'login':
    u_name = st.text_input("הזן שם מלא:")
    if st.button("כניסה"):
        if u_name:
            st.session_state.user = u_name
            st.session_state.step = 'menu'
            st.rerun()

elif st.session_state.step == 'menu':
    c1, c2 = st.columns(2)
    if c1.button("📚 לימוד לפי נושאים"):
        st.session_state.step = 'study'
        st.rerun()
    if c2.button("⏱️ סימולציית בחינה"):
        st.info("בפיתוח...")

elif st.session_state.step == 'study':
    # שבירת רשימה למניעת חיתוך מחרוזת
    topics = ["בחר נושא..."]
    topics += ["חוק המתווכים במקרקעין"]
    topics += ["תקנות המתווכים (פרטי הזמנה)"]
    topics += ["תקנות המתווכים (פעולות שיווק)"]
    topics += ["חוק המקרקעין"]
    topics += ["חוק הגנת הדייר"]
    topics += ["חוק המכר (דירות)"]
    topics += ["חוק החוזים (חלק כללי)"]
    topics += ["חוק החוזים (תרופות)"]
    topics += ["חוק הגנת הצרכן"]
    topics += ["חוק עבירות עונשין"]
    topics += ["חוק שמאי מקרקעין"]
    topics += ["חוק התכנון והבנייה"]
    topics += ["חוק מיסוי מקרקעין"]
    topics += ["חוק הירושה"]
    topics += ["חוק הוצאה לפועל"]
    topics += ["פקודת הנזיקין"]
    
    sel = st.selectbox("נושא לימוד:", topics)
    if sel != "בחר נושא..." and st.button("טען שיעור"):
        st.session_state.update({
            "selected_topic": sel, "lesson_titles": fetch_titles(sel),
            "lesson_contents": {}, "current_sub_idx": None,
            "quiz_active": False, "step": "lesson_run"
        })
        st.rerun()

elif st.session_state.step == 'lesson_run':
    st.header(f"📖 {st.session_state.selected_topic}")
    cols = st.columns(3)
    for i, title in enumerate(st.session_state.lesson_titles):
        if cols[i].button(title, disabled=(st.session_state.current_sub_idx == i)):
            st.session_state.current_sub_idx = i
            with st.spinner("טוען..."):
                content = fetch_content(st.session_state.selected_topic, title)
                st.session_state.lesson_contents[title] = content
            st.rerun()

    if st.session_state.current_sub_idx is not None:
        key = st.session_state.lesson_titles[st.session_state.current_sub_idx]
        st.markdown(st.session_state.lesson_contents.get(key, "⚠️ שגיאה"))
        st.divider()

        if not st.session_state.quiz_active:
            if st.button(f"📝 התחל שאלון - {st.session_state.selected_topic}"):
                with st.spinner("מכין שאלה..."):
                    q_data = fetch_question(st.session_state.selected_topic)
                    st.session_state.update({
                        "quiz_active": True, "q_counter": 1, "score": 0,
                        "show_feedback": False, "current_q_data": q_data
                    })
                st.rerun()

        if st.session_state.quiz_active and st.session_state.current_q_data:
            q = st.session_state.current_q_data
            st.subheader(f"שאלה {st.session_state.q_counter} מתוך 10")
            ans = st.radio(q['q'], q['options'], index=None, key=f"q_{st.session_state.q_counter}")
            
            if not st.session_state.show_feedback:
                if st.button("בדיקת תשובה"):
                    if ans:
                        st.session_state.show_feedback = True
                        if ans == q['correct']: st.session_state.score += 1
                        st.rerun()
            else:
                if ans == q['correct']: st.success("✅ נכון!")
                else: st.error(f"❌ טעות. הנכונה: {q['correct']}")
                st.info(f"**הסבר:** {q['explain']}")
                
                if st.session_state.q_counter < 10:
                    if st.button("שאלה הבאה ➡️"):
                        st.session_state.current_q_data = fetch_question(st.session_state.selected_topic)
                        st.session_state.q_counter += 1
                        st.session_state.show_feedback = False
                        st.rerun()
                else:
                    st.success(f"🏁 ציון סופי: {st.session_state.score * 10}")
                    if st.button("סגור שאלון"):
                        st.session_state.quiz_active = False
                        st.rerun()

        st.markdown('<div class="nav-box"></div>', unsafe_allow_html=True)
        n_cols = st.columns(2)
        if n_cols[0].button("🏠 תפריט ראשי"):
            st.session_state.step = 'menu'; st.rerun()
        if n_cols[1].button("🔝 לראש הדף"):
            st.rerun()
