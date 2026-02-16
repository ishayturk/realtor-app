# ==========================================
# Project: מתווך בקליק | Version: 1174
# Last Updated: 2026-02-16 | 19:25
# ==========================================

import streamlit as st
import google.generativeai as genai
import json, re

st.set_page_config(page_title="מתווך בקליק", layout="wide")

st.markdown("""
<style>
    * { direction: rtl; text-align: right; }
    .stButton>button { width: auto; min-width: 110px; border-radius: 8px; font-weight: bold; background-color: transparent !important; border: 1px solid #888 !important; color: #333 !important; }
    .nav-link { background: transparent; border: 1px solid #888; color: #333; padding: 6px 12px; text-decoration: none; border-radius: 8px; font-size: 14px; font-weight: bold; display: inline-block; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div id="top"></div>', unsafe_allow_html=True)

SYLLABUS = {
    "חוק המתווכים במקרקעין": ["רישוי והגבלות עיסוק", "חובת הגינות וזהירות", "הזמנת תיווך ובלעדיות"],
    "תקנות המתווכים (פרטי הזמנה)": ["דרישות חובה בטופס", "זיהוי נכס וצדדים", "פירוט דמי התיווך"],
    "תקנות המתווכים (פעולות שיווק)": ["פעולות שיווק", "הרחבות לבלעדיות", "חובת הוכחת פעילות"],
    "חוק המקרקעין": ["בעלות וזכויות", "בתים משותפים", "עסקאות נוגדות והערות אזהרה"],
    "חוק המכר (דירות)": ["מפרט וחובת גילוי", "בדק ואחריות", "איחור במסירה"],
    "חוק החוזים": ["כריתת חוזה", "פגמים בחוזה", "תרופות בשל הפרה"],
    "חוק התכנון והבנייה": ["היתרי בנייה", "היטל השבחה", "תוכניות מתאר"],
    "חוק מיסוי מקרקעין": ["מס שבח", "מס רכישה", "פטורים והקלות"]
}

def ask_ai(prompt):
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-2.0-flash')
        res = model.generate_content(prompt)
        return res.text if (res and res.text) else None
    except:
        return None

def fetch_content(topic, sub):
    p = f"כתוב שיעור מקצועי על '{sub}' בתוך '{topic}'. בלי הקדמות ובלי המילים 'מבחן מתווכים'."
    res = ask_ai(p)
    return res if res else "⚠️ שגיאה בטעינה."

def fetch_q(topic):
    p = f"צור שאלה אמריקאית על {topic}. JSON: {{'q':'..','options':['..'],'correct':'..','explain':'..'}}"
    res = ask_ai(p)
    if not res: return None
    try:
        m = re.search(r'\{.*\}', res, re.DOTALL)
        if m:
            return json.loads(m.group())
        return None
    except:
        return None

if "step" not in st.session_state:
    st.session_state.update({
        "step": "login", "user": None, "selected_topic": None,
        "lesson_contents": {}, "current_sub_idx": None,
        "quiz_active": False, "q_counter": 0, "score": 0,
        "current_q_data": None, "next_q_data": None, "show_feedback": False
    })

st.title("🏠 מתווך בקליק")

if st.session_state.step == 'login':
    u = st.text_input("הזן שם מלא:")
    if st.button("כניסה"):
        if u:
            st.session_state.update({"user": u, "step": "menu"})
            st.rerun()

elif st.session_state.step == 'menu':
    st.write(f"👤 שלום, {st.session_state.user}")
    c1, c2 = st.columns(2)
    if c1.button("📚 לימוד לפי נושאים"):
        st.session_state.update({"step": "study", "selected_topic": None, "current_sub_idx": None, "quiz_active": False})
        st.rerun()
    if c2.button("⏱️ סימולציית בחינה"):
        st.info("בפיתוח...")

elif st.session_state.step == 'study':
    ts = ["בחר נושא..."] + list(SYLLABUS.keys())
    sel = st.selectbox("נושא לימוד:", ts)
    if sel != "בחר נושא..." and st.button("טען שיעור"):
        st.session_state.update({
            "selected_topic": sel, "lesson_contents": {}, "current_sub_idx": None, 
            "quiz_active": False, "step": "lesson_run", "current_q_data": None, "next_q_data": None, "q_counter": 0
        })
        st.rerun()

elif st.session_state.step == 'lesson_run':
    st.header(f"📖 {st.session_state.selected_topic}")
    subs = SYLLABUS.get(st.session_state.selected_topic, [])
    
    if subs:
        t_cols = st.columns(len(subs))
        for i, t in enumerate(subs):
            if t_cols[i].button(t, key=f"sub_{i}", disabled=(st.session_state.current_sub_idx == i)):
                st.session_state.update({"current_sub_idx": i, "quiz_active": False, "current_q_data": None, "next_q_data": None})
                with st.spinner("מכין תוכן..."):
                    st.session_state.lesson_contents[t] = fetch_content(st.session_state.selected_topic, t)
                st.rerun()

    if st.session_state.current_sub_idx is not None and st.session_state.current_sub_idx < len(subs):
        st.markdown(st.session_state.lesson_contents.get(subs[st.session_state.current_sub_idx], ""))

    if st.session_state.quiz_active:
        st.divider()
        st.subheader(f"📝 שאלון: {st.session_state.selected_topic}")
        if not st.session_state.current_q_data:
            with st.spinner("מייצר שאלה..."):
                st.session_state.current_q_data = fetch_q(st.session_state.selected_topic)
            st.rerun()
        
        q = st.session_state.current_q_data
        st.write(f"**שאלה {st.session_state.q_counter} מתוך 10**")
        ans = st.radio(q['q'], q['options'], index=None, key=f"q_{st.session_state.q_counter}")
        
        if st.session_state.show_feedback:
            if ans == q['correct']: st.success("✅ נכון!")
            else: st.error(f"❌ טעות. הנכונה: {q['correct']}")
            st.info(f"הסבר: {q['explain']}")

    st.write("") 
    b1, b2, b3, _ = st.columns([1.5, 1, 1, 5])

    btn_label = "📝 שאלון"
    if st.session_state.quiz_active:
        if not st.session_state.show_feedback: btn_label = "✅ בדיקה"
        elif st.session_state.q_counter < 10: btn_label = "➡️ הבאה"
        else: btn_label = "🔄 מחדש"

    with b1:
        if st.button(btn_label):
            if btn_label == "📝 שאלון" or btn_label == "🔄 מחדש":
                st.session_state.update({"quiz_active": True, "q_counter": 1, "score": 0, "show_feedback": False, "current_q_data": None})
            elif
