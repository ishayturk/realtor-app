# ==========================================
# Project: מתווך בקליק | Version: 1165
# Last Updated: 2026-02-16 | 18:35
# ==========================================

import streamlit as st
import google.generativeai as genai
import json, re

st.set_page_config(page_title="מתווך בקליק", layout="wide")
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
    p = f"כתוב שיעור מקצועי על '{sub}' בתוך '{topic}'. בלי הקדמות ובלי המילים 'מבחן מתווכים'."
    return ask_ai(p) or "⚠️ שגיאה בטעינה."

def fetch_q(topic):
    p = f"צור שאלה אמריקאית על {topic}. JSON: {{'q':'..','options':['..'],'correct':'..','explain':'..'}}"
    res = ask_ai(p)
    try:
        m = re.search(r'\{.*\}', res, re.DOTALL)
        return json.loads(m.group())
    except: return None

if "step" not in st.session_state:
    st.session_state.update({
        "step": "login", "user": None, "selected_topic": None,
        "lesson_contents": {}, "current_sub_idx": None,
        "quiz_active": False, "q_counter": 0, "score": 0,
        "current_q_data": None, "next_q_data": None, "show_feedback": False
    })

# CSS לשיפור המרווחים והצמדת תפריט לימין
st.markdown("""
<style>
    * { direction: rtl; text-align: right; }
    .stButton>button { width: auto; min-width: 100px; border-radius: 8px; font-weight: bold; background-color: transparent !important; border: 1px solid #888 !important; color: #333 !important; margin-left: 15px !important; }
    .nav-btn { background: transparent; border: 1px solid #888; color: #333; padding: 6px 15px; text-decoration: none; border-radius: 8px; display: inline-block; font-size: 14px; font-weight: bold; margin-left: 15px; }
    .bottom-nav { margin-top: -10px; display: flex; justify-content: flex-start; gap: 10px; }
</style>
""", unsafe_allow_html=True)

st.title("🏠 מתווך בקליק")

if st.session_state.step == 'login':
    u = st.text_input("הזן שם מלא:")
    if st.button("כניסה"):
        if u: st.session_state.update({"user": u, "step": "menu"}); st.rerun()

elif st.session_state.step == 'menu':
    st.write(f"👤 שלום, {st.session_state.user}")
    c1, c2 = st.columns(2)
    if c1.button("📚 לימוד לפי נושאים"):
        st.session_state.step = 'study'; st.rerun()
    if c2.button("⏱️ סימולציית בחינה"): st.info("בפיתוח...")

elif st.session_state.step == 'study':
    ts = ["בחר נושא..."] + list(SYLLABUS.keys())
    sel = st.selectbox("נושא לימוד:", ts)
    if sel != "בחר נושא..." and st.button("טען שיעור"):
        st.session_state.update({"selected_topic": sel, "lesson_contents": {}, "current_sub_idx": None, "quiz_active": False, "step": "lesson_run"})
        st.rerun()

elif st.session_state.step == 'lesson_run':
    st.header(f"📖 {st.session_state.selected_topic}")
    subs = SYLLABUS.get(st.session_state.selected_topic, [])
    
    if subs:
        cols = st.columns(len(subs))
        for i, t in enumerate(subs):
            if cols[i].button(t, key=f"sub_{i}", disabled=(st.session_state.current_sub_idx == i)):
                st.session_state.update({"current_sub_idx": i, "quiz_active": False, "current_q_data": None, "next_q_data": None})
                with st.spinner("מכין תוכן..."):
                    st.session_state.lesson_contents[t] = fetch_content(st.session_state.selected_topic, t)
                st.rerun()

    if st.session_state.current_sub_idx is not None:
        st.markdown(st.session_state.lesson_contents.get(subs[st.session_state.current_sub_idx], "⚠️"))

    if st.session_state.quiz_active:
        st.subheader(f"📝 שאלון: {st.session_state.selected_topic}")
        if not st.session_state.current_q_data:
            with st.spinner("טוען שאלה..."):
                st.session_state.current_q_data = fetch_q(st.session_state.selected_topic)
            st.rerun()
        
        q = st.session_state.current_q_data
        st.write(f"**שאלה {st.session_state.q_counter} מתוך 10**")
        ans = st.radio(q['q'], q['options'], index=None, key=f"q_{st.session_state.q_counter}")
        
        if st.session_state.show_feedback:
            if ans == q['correct']: st.success("✅ נכון!")
            else: st.error(f"❌ טעות. הנכונה: {q['correct']}")
            st.info(f"הסבר: {q['explain']}")
            if st.session_state.q_counter >= 10:
                st.success(f"🏁 ציון סופי: {st.session_state.score * 10}")

    # תפריט תחתון צמוד ימין
    st.write("") # רווח של שורה אחת
    cont = st.container()
    b_start, b_menu, b_up = cont.columns([6, 1, 1]) # יחס שמעדיף את הימין

    # לוגיקת כפתור פעולה דינמי
    btn_label = f"📝 שאלון: {st.session_state.selected_topic}"
    if st.session_state.quiz_active:
        if not st.session_state.show_feedback: btn_label = "✅ בדיקת תשובה"
        elif st.session_state.q_counter < 10: btn_label = "➡️ שאלה הבאה"
        else: btn_label = "🔄 שאלון מחדש"

    with b_start:
        if st.button(btn_label):
            if not st.session_state.quiz_active or btn_label.startswith("🔄"):
                st.session_state.update({"quiz_active": True, "q_counter": 1, "score": 0, "show_feedback": False, "current_q_data": None, "next_q_data": None})
            elif btn_label == "✅ בדיקת תשובה" and ans:
                st.session_state.show_feedback = True
                if ans == q['correct']: st.session_state.score += 1
                # טעינה מראש של השאלה הבאה ברקע
                if st.session_state.q_counter < 10:
                    st.session_state.next_q_data = fetch_q(st.session_state.selected_topic)
            elif btn_label == "➡️ שאלה הבאה":
                st.session_state.current_q_data = st.session_state.next_q_data
                st.session_state.update({"next_q_data": None, "q_counter": st.session_state.q_counter + 1, "show_feedback": False})
            st.rerun()

    with b_menu:
        if st.button("🏠 תפריט"):
            st.session_state.step = 'menu'; st.rerun()
    
    with b_up:
        st.markdown('<a href="#top" class="nav-btn">🔝 למעלה</a>', unsafe_allow_html=True)
