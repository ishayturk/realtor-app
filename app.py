# ==========================================
# Project: מתווך בקליק
# File: app.py
# Version: 1154
# Last Updated: 2026-02-16 | 23:59
# ==========================================

import streamlit as st
import google.generativeai as genai
import json, re

# --- הגדרות דף ---
st.set_page_config(page_title="מתווך בקליק", layout="wide")

# אנקור לראש הדף
st.markdown('<div id="top"></div>', unsafe_allow_html=True)

def ask_ai(prompt):
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content(prompt)
        return response.text if (response and response.text) else None
    except: return None

# --- לוגיקה ---
def fetch_titles(topic):
    p = f"צור 3 כותרות לתתי-נושאים בתוך {topic}. JSON: ['א','ב','ג']"
    res = ask_ai(p)
    try:
        match = re.search(r'\[.*\]', res, re.DOTALL)
        titles = json.loads(match.group())
        return [str(t) for t in titles if t]
    except: return ["הוראות חוק", "חובות המתווך", "פסיקה"]

def fetch_content(main_topic, sub_title):
    p = (f"כתוב שיעור Markdown על '{sub_title}' בתוך '{main_topic}'. "
         "בלי הסברים על המבנה. רק תוכן מקצועי.")
    content = ask_ai(p)
    return content if content else "⚠️ שגיאה בטעינה."

def fetch_question(topic):
    p = (f"צור שאלה אמריקאית על {topic}. "
         "JSON: {{'q':'..','options':['..'],'correct':'..','explain':'..'}}")
    res = ask_ai(p)
    try:
        match = re.search(r'\{.*\}', res, re.DOTALL)
        return json.loads(match.group())
    except: return None

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
    .user-strip { margin-top: 40px; margin-bottom: 30px; font-weight: bold; color: #444; }
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# --- כותרות ---
st.title("🏠 מתווך בקליק")
if st.session_state.user:
    st.markdown(f'<div class="user-strip">👤 שלום, {st.session_state.user}</div>', 
                unsafe_allow_html=True)

# --- ניתוב ---
if st.session_state.step == 'login':
    u_name = st.text_input("הזן שם מלא:")
    if st.button("כניסה"):
        if u_name:
            st.session_state.user = u_name
            st.session_state.step = 'menu'; st.rerun()

elif st.session_state.step == 'menu':
    c1, c2 = st.columns(2)
    if c1.button("📚 לימוד לפי נושאים"):
        st.session_state.step = 'study'; st.rerun()
    if c2.button("⏱️ סימולציית בחינה"): st.info("בפיתוח...")

elif st.session_state.step == 'study':
    # רשימה מלאה ומחולקת למניעת חיתוך
    topics = ["בחר נושא...", "חוק המתווכים במקרקעין", "תקנות המתווכים (פרטי הזמנה)"]
    topics += ["תקנות המתווכים (פעולות שיווק)", "חוק המקרקעין", "חוק הגנת הדייר"]
    topics += ["חוק המכר (דירות)", "חוק החוזים (חלק כללי)", "חוק החוזים (תרופות)"]
    topics += ["חוק הגנת הצרכן", "חוק עבירות עונשין", "חוק שמאי מקרקעין"]
    topics += ["חוק התכנון והבנייה", "חוק מיסוי מקרקעין", "חוק הירושה"]
    topics += ["חוק הוצאה לפועל", "פקודת הנזיקין"]
    
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
    
    titles = st.session_state.lesson_titles
    if titles:
        cols = st.columns(len(titles))
        for i, title in enumerate(titles):
            label = str(title) if title else "שיעור"
            if cols[i].button(label, key=f"btn_{i}", 
                             disabled=(st.session_state.current_sub_idx == i)):
                st.session_state.current_sub_idx = i
                st.session_state.quiz_active = False 
                with st.spinner("טוען..."):
                    st.session_state.lesson_contents[title] = fetch_content(
                        st.session_state.selected_topic, title)
                st.rerun()

    if st.session_state.current_sub_idx is not None:
        key = st.session_state.lesson_titles[st.session_state.current_sub_idx]
        st.markdown(st.session_state.lesson_contents.get(key, "⚠️ שגיאה"))
        st.divider()

        b_cols = st.columns(3)
        if not st.session_state.quiz_active:
            if b_cols[0].button(f"📝 התחל שאלון"):
                st.session_state.update({
                    "quiz_active": True, "q_counter": 1, "score": 0,
                    "show_feedback": False, "current_q_data": fetch_question(
                        st.session_state.selected_topic)
                })
                st.rerun()
        
        if b_cols[1].button("🏠 לתפריט"):
            st.session_state.step = 'menu'; st.rerun()
            
        b_cols[2].markdown('<a href="#top" target="_self"><button style="width:100%; height:38px; border-radius:8px; font-weight:bold; cursor:pointer; background-color:#f0f2f6; border:1px solid #ccc;">🔝 לראש הדף</button></a>', unsafe_allow_html=True)

        if st.session_state.quiz_active and st.session_state.current_q_data:
            st.divider()
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
                        st.session_state.q_counter += 1; st.session_state.show_feedback = False; st.rerun()
                else:
                    score_val = st.session_state.score * 10
                    st.success(f"🏁 ציון סופי: {score_val}")
                    if st.button("סגור שאלון"):
                        st.session_state.quiz_active = False; st.rerun()
