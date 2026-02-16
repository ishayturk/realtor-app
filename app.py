# ==========================================
# Project: מתווך בקליק | Version: 1158
# Last Updated: 2026-02-17 | 01:10
# ==========================================

import streamlit as st
import google.generativeai as genai
import json, re

st.set_page_config(page_title="מתווך בקליק", layout="wide")
st.markdown('<div id="top"></div>', unsafe_allow_html=True)

# --- סילבוס קבוע (הטבלה) ---
SYLLABUS = {
    "חוק המתווכים במקרקעין": ["רישוי והגבלות עיסוק", "חובת הגינות וזהירות", "הזמנת תיווך ובלעדיות"],
    "תקנות המתווכים (פרטי הזמנה)": ["דרישות חובה בטופס", "זיהוי נכס וצדדים", "פירוט דמי התיווך"],
    "תקנות המתווכים (פעולות שיווק)": ["פעולות שיווק סטנדרטיות", "הרחבות לשיווק בבלעדיות", "חובת הוכחת פעילות"],
    "חוק המקרקעין": ["בעלות וזכויות במקרקעין", "בתים משותפים והצמדות", "עסקאות נוגדות והערות אזהרה"],
    "חוק הגנת הדייר": ["דיירות מוגנת ודמי מפתח", "עילות פינוי", "זכויות וחובות דייר מוגן"],
    "חוק המכר (דירות)": ["מפרט וחובת גילוי", "תקופות בדק ואחריות", "איחור במסירה ופיצויים"],
    "חוק החוזים": ["כריתת חוזה ותום לב", "פגמים בחוזה (טעות/הטעיה)", "תרופות בשל הפרת חוזה"],
    "חוק הגנת הצרכן": ["הטעיה בפרסום ושיווק", "ביטול עסקה והחזר כספי", "חובות גילוי כלפי צרכן"],
    "חוק עבירות עונשין": ["עבירות מרמה והונאה", "זיוף מסמכים במקרקעין", "אחריות פלילית של בעלי מקצוע"],
    "חוק שמאי מקרקעין": ["תפקיד השמאי והערכות", "סמכויות והגדרות", "בסיס השומה למכירה"],
    "חוק התכנון והבנייה": ["היתרי בנייה ושימוש חורג", "היטל השבחה", "תוכניות מתאר"],
    "חוק מיסוי מקרקעין": ["מס שבח", "מס רכישה", "פטורים והקלות במס"],
    "חוק הירושה": ["ירושה על פי דין מול צוואה", "ניהול עיזבון", "העברת מקרקעין בירושה"],
    "חוק הוצאה לפועל": ["עיקול מקרקעין", "מימוש משכנתאות", "פינוי נכסים"],
    "פקודת הנזיקין": ["רשלנות מקצועית", "מצג שווא", "חובת הזהירות כלפי צד ג'"]
}

def ask_ai(prompt):
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-2.0-flash')
        res = model.generate_content(prompt)
        return res.text if (res and res.text) else None
    except: return None

def fetch_content(topic, sub):
    p = f"כתוב שיעור Markdown מקצועי למבחן המתווכים על '{sub}' בתוך '{topic}'. בלי הקדמות."
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
        "current_q_data": None, "show_feedback": False
    })

st.markdown("""
<style>
    * { direction: rtl; text-align: right; }
    .user-strip { margin-top: 40px; margin-bottom: 30px; font-weight: bold; color: #444; }
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; }
    .nav-btn { background-color: #f0f2f6 !important; border: 1px solid #ccc !important; font-weight: normal !important; color: black !important; }
</style>
""", unsafe_allow_html=True)

st.title("🏠 מתווך בקליק")

if st.session_state.step == 'login':
    u = st.text_input("הזן שם מלא:")
    if st.button("כניסה"):
        if u: st.session_state.update({"user": u, "step": "menu"}); st.rerun()

elif st.session_state.step == 'menu':
    st.markdown(f'<div class="user-strip">👤 שלום, {st.session_state.user}</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    if c1.button("📚 לימוד לפי נושאים"):
        st.session_state.step = 'study'; st.rerun()
    if c2.button("⏱️ סימולציית בחינה"): st.info("בפיתוח...")

elif st.session_state.step == 'study':
    ts = ["בחר נושא..."] + list(SYLLABUS.keys())
    sel = st.selectbox("נושא לימוד:", ts)
    if sel != "בחר נושא..." and st.button("טען שיעור"):
        st.session_state.update({
            "selected_topic": sel, "lesson_contents": {}, 
            "current_sub_idx": None, "quiz_active": False, "step": "lesson_run"
        })
        st.rerun()

elif st.session_state.step == 'lesson_run':
    st.header(f"📖 {st.session_state.selected_topic}")
    subs = SYLLABUS.get(st.session_state.selected_topic, [])
    
    if subs:
        cols = st.columns(len(subs))
        for i, t in enumerate(subs):
            if cols[i].button(t, key=f"b{i}", disabled=(st.session_state.current_sub_idx == i)):
                st.session_state.current_sub_idx = i
                st.session_state.quiz_active = False 
                with st.spinner("מכין שיעור..."):
                    st.session_state.lesson_contents[t] = fetch_content(st.session_state.selected_topic, t)
                st.rerun()

    if st.session_state.current_sub_idx is not None:
        curr_t = subs[st.session_state.current_sub_idx]
        st.markdown(st.session_state.lesson_contents.get(curr_t, "⚠️"))
        
        # אזור השאלון
        if st.session_state.quiz_active and st.session_state.current_q_data:
            st.divider()
            q = st.session_state.current_q_data
            st.subheader(f"שאלה {st.session_state.q_counter} מתוך 10")
            ans = st.radio(q['q'], q['options'], index=None, key=f"q{st.session_state.q_counter}")
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
                        st.session_state.current_q_data = fetch_q(st.session_state.selected_topic)
                        st.session_state.q_counter += 1; st.session_state.show_feedback = False; st.rerun()
                else:
                    st.success(f"🏁 ציון סופי: {st.session_state.score * 10}")
                    if st.button("סגור שאלון"):
                        st.session_state.quiz_active = False; st.rerun()

        # תפריט ניווט תחתון קבוע - מחוץ לתנאי השאלון
        st.divider()
        b_cols = st.columns(3)
        lbl = f"📝 שאלון: {st.session_state.selected_topic}"
        if not st.session_state.quiz_active:
            if b_cols[0].button(lbl):
                st.session_state.update({
                    "quiz_active": True, "q_counter": 1, "score": 0, "show_feedback": False,
                    "current_q_data": fetch_q(st.session_state.selected_topic)
                })
                st.rerun()
        if b_cols[1].button("🏠 לתפריט"):
            st.session_state.step = 'menu'; st.rerun()
        b_cols[2].markdown('<a href="#top" target="_self"><button class="nav-btn" style="width:100%; height:38px; border-radius:8px; cursor:pointer;">🔝 לראש הדף</button></a>', unsafe_allow_html=True)
