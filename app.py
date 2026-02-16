# ==========================================
# Project: מתווך בקליק | Version: 1177
# Last Updated: 2026-02-16 | 19:30
# ==========================================

import streamlit as st
import google.generativeai as genai
import json, re

# הגדרה ראשונה לרוחב מלא
st.set_page_config(page_title="מתווך בקליק", layout="wide")

# CSS לידידותיות למשתמש ויישור לימין
st.markdown("""
<style>
    * { direction: rtl; text-align: right; }
    .stButton>button { width: auto; min-width: 140px; border-radius: 8px; font-weight: bold; background-color: transparent !important; border: 1px solid #888 !important; color: #333 !important; }
    .nav-btn { background: transparent; border: 1px solid #888; color: #333; padding: 7px 15px; text-decoration: none; border-radius: 8px; font-size: 14px; font-weight: bold; display: inline-block; }
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
    except: return None

def fetch_content(topic, sub):
    p = f"כתוב שיעור מקצועי על '{sub}' בתוך '{topic}'. בלי הקדמות."
    return ask_ai(p) or "⚠️ שגיאה בטעינה."

def fetch_q(topic):
    p = f"צור שאלה אמריקאית על {topic}. JSON: {{'q':'..','options':['..'],'correct':'..','explain':'..'}}"
    res = ask_ai(p)
    try:
        m = re.search(r'\{.*\}', res, re.DOTALL)
        return json.loads(m.group())
    except: return None

# ניהול מצב
if "step" not in st.session_state:
    st.session_state.update({
        "step": "login", "user": None, "selected_topic": None,
        "lesson_contents": {}, "current_sub_idx": None,
        "quiz_active": False, "q_counter": 0, "score": 0,
        "current_q_data": None, "next_q_data": None, "show_feedback": False
    })

st.title("🏠 מתווך בקליק")

# --- מסך כניסה ---
if st.session_state.step == 'login':
    u = st.text_input("הזן שם מלא:")
    if st.button("כניסה"):
        if u: 
            st.session_state.update({"user": u, "step": "menu"})
            st.rerun()

# --- תפריט ראשי ---
elif st.session_state.step == 'menu':
    st.write(f"👤 שלום, {st.session_state.user}")
    c1, c2 = st.columns(2)
    if c1.button("📚 לימוד לפי נושאים"):
        st.session_state.update({"step": "study", "selected_topic": None, "current_sub_idx": None, "quiz_active": False})
        st.rerun()
    if c2.button("⏱️ סימולציית בחינה"): 
        st.info("סימולציית בחינה מלאה תתווסף בקרוב.")

# --- בחירת נושא ---
elif st.session_state.step == 'study':
    ts = ["בחר נושא לימוד מתוך הרשימה..."] + list(SYLLABUS.keys())
    sel = st.selectbox("בחר נושא:", ts)
    if sel != "בחר נושא לימוד מתוך הרשימה..." and st.button("טען נושא נבחר"):
        st.session_state.update({
            "selected_topic": sel, "lesson_contents": {}, "current_sub_idx": None, 
            "quiz_active": False, "step": "lesson_run", "current_q_data": None, "q_counter": 0
        })
        st.rerun()

# --- הרצת שיעור ---
elif st.session_state.step == 'lesson_run':
    st.header(f"📖 {st.session_state.selected_topic}")
    subs = SYLLABUS.get(st.session_state.selected_topic, [])
    
    if subs:
        t_cols = st.columns(len(subs))
        for i, t in enumerate(subs):
            if t_cols[i].button(t, key=f"sub_{i}", disabled=(st.session_state.current_sub_idx == i)):
                st.session_state.update({"current_sub_idx": i, "quiz_active": False, "current_q_data": None})
                with st.spinner(f"מכין תוכן עבור: {t}..."):
                    st.session_state.lesson_contents[t] = fetch_content(st.session_state.selected_topic, t)
                st.rerun()

    if st.session_state.current_sub_idx is not None:
        idx = st.session_state.current_sub_idx
        st.markdown(st.session_state.lesson_contents.get(subs[idx], ""))

    if st.session_state.quiz_active:
        st.divider()
        st.subheader(f"📝 שאלון תרגול: {st.session_state.selected_topic}")
        if not st.session_state.current_q_data:
            with st.spinner("מייצר שאלה חדשה..."):
                st.session_state.current_q_data = fetch_q(st.session_state.selected_topic)
            st.rerun()
        
        q = st.session_state.current_q_data
        st.write(f"**שאלה {st.session_state.q_counter} מתוך 10**")
        ans = st.radio(q['q'], q['options'], index=None, key=f"q_radio_{st.session_state.q_counter}")
        
        if st.session_state.show_feedback:
            if ans == q['correct']: st.success("✅ תשובה נכונה!")
            else: st.error(f"❌ טעות. התשובה הנכונה היא: {q['correct']}")
            st.info(f"הסבר מקצועי: {q['explain']}")

    # --- תפריט תחתון ידידותי ---
    st.write("") 
    b1, b2, b3, _ = st.columns([2, 1.2, 1.2, 4])

    # לוגיקת כפתור הפעולה
    if not st.session_state.quiz_active: btn_txt = "📝 התחל שאלון"
    elif not st.session_state.show_feedback: btn_txt = "✅ בדיקת תשובה"
    elif st.session_state.q_counter < 10: btn_txt = "➡️ שאלה הבאה"
    else: btn_txt = "🔄 התחל מחדש"

    with b1:
        if st.button(btn_txt):
            if btn_txt in ["📝 התחל שאלון", "🔄 התחל מחדש"]:
                st.session_state.update({"quiz_active": True, "q_counter": 1, "score": 0, "show_feedback": False, "current_q_data": None})
            elif btn_txt == "✅ בדיקת תשובה" and ans:
                st.session_state.show_feedback = True
                if st.session_state.q_counter < 10:
                    st.session_state.next_q_data = fetch_q(st.session_state.selected_topic)
            elif btn_txt == "➡️ שאלה הבאה":
                st.session_state.current_q_data = st.session_state.next_q_data
                st.session_state.update({"next_q_data": None, "q_counter": st.session_state.q_counter + 1, "show_feedback": False})
            st.rerun()

    with b2:
        if st.button("🏠 תפריט ראשי"):
            st.session_state.update({"step": "menu", "selected_topic": None, "quiz_active": False})
            st.rerun()
    
    with b3:
        st.markdown(f'<a href="#top" class="nav-btn">🔝 למעלה</a>', unsafe_allow_
