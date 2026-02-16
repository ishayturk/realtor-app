# ==========================================
# Project: מתווך בקליק | Version: 1176
# ==========================================
import streamlit as st
import google.generativeai as genai
import json, re

st.set_page_config(page_title="מתווך בקליק", layout="wide")

st.markdown("""<style>
    * { direction: rtl; text-align: right; }
    .stButton>button { width: auto; min-width: 110px; border-radius: 8px; font-weight: bold; border: 1px solid #888 !important; }
    .nav-link { border: 1px solid #888; color: #333; padding: 6px 12px; text-decoration: none; border-radius: 8px; font-weight: bold; display: inline-block; }
</style>""", unsafe_allow_html=True)

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

def ask_ai(p):
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-2.0-flash')
        res = model.generate_content(p)
        return res.text if res else None
    except: return None

def fetch_content(topic, sub):
    res = ask_ai(f"כתוב שיעור על '{sub}' בתוך '{topic}'. בלי הקדמות.")
    return res if res else "⚠️ שגיאה."

def fetch_q(topic):
    res = ask_ai(f"צור שאלה אמריקאית על {topic}. JSON: {{'q':'..','options':['..'],'correct':'..','explain':'..'}}")
    try:
        m = re.search(r'\{.*\}', res, re.DOTALL)
        return json.loads(m.group()) if m else None
    except: return None

if "step" not in st.session_state:
    st.session_state.update({"step": "login", "user": None, "selected_topic": None, "lesson_contents": {}, "current_sub_idx": None, "quiz_active": False, "q_counter": 0, "score": 0, "current_q_data": None, "next_q_data": None, "show_feedback": False})

st.title("🏠 מתווך בקליק")

# --- מסך כניסה ---
if st.session_state.step == 'login':
    u = st.text_input("הזן שם:")
    if st.button("כניסה") and u:
        st.session_state.update({"user": u, "step": "menu"}); st.rerun()

# --- תפריט ראשי ---
elif st.session_state.step == 'menu':
    st.write(f"👤 שלום, {st.session_state.user}")
    c1, c2 = st.columns(2)
    if c1.button("📚 לימוד"):
        st.session_state.update({"step": "study", "selected_topic": None, "quiz_active": False}); st.rerun()
    if c2.button("⏱️ סימולציה"): st.info("בפיתוח...")

# --- בחירת נושא ---
elif st.session_state.step == 'study':
    ts = ["בחר נושא..."] + list(SYLLABUS.keys())
    sel = st.selectbox("נושא:", ts)
    if sel != "בחר נושא..." and st.button("טען"):
        st.session_state.update({"selected_topic": sel, "lesson_contents": {}, "current_sub_idx": None, "quiz_active": False, "step": "lesson_run", "current_q_data": None, "q_counter": 0})
        st.rerun()

# --- הרצת שיעור ושאלון ---
elif st.session_state.step == 'lesson_run':
    st.header(f"📖 {st.session_state.selected_topic}")
    subs = SYLLABUS.get(st.session_state.selected_topic, [])
    
    if subs:
        t_cols = st.columns(len(subs))
        for i, t in enumerate(subs):
            if t_cols[i].button(t, key=f"s_{i}", disabled=(st.session_state.current_sub_idx == i)):
                st.session_state.update({"current_sub_idx": i, "quiz_active": False})
                with st.spinner("טוען..."): st.session_state.lesson_contents[t] = fetch_content(st.session_state.selected_topic, t)
                st.rerun()

    if st.session_state.current_sub_idx is not None:
        idx = st.session_state.current_sub_idx
        st.markdown(st.session_state.lesson_contents.get(subs[idx], ""))

    if st.session_state.quiz_active:
        st.divider()
        if not st.session_state.current_q_data:
            with st.spinner("מייצר..."): st.session_state.current_q_data = fetch_q(st.session_state.selected_topic)
            st.rerun()
        q = st.session_state.current_q_data
        st.write(f"**שאלה {st.session_state.q_counter}**")
        ans = st.radio(q['q'], q['options'], index=None, key=f"q_{st.session_state.q_counter}")
        if st.session_state.show_feedback:
            if ans == q['correct']: st.success("✅ נכון!")
            else: st.error(f"❌ טעות. הנכונה: {q['correct']}")
            st.info(f"הסבר: {q['explain']}")

    # --- תפריט תחתון ---
    st.write("")
    b1, b2, b3, _ = st.columns([1.5, 1, 1, 5])
    
    # חישוב תווית כפתור
    if not st.session_state.quiz_active: label = "📝 שאלון"
    elif not st.session_state.show_feedback: label = "✅ בדיקה"
    elif st.session_state.q_counter < 10: label = "➡️ הבאה"
    else: label = "🔄 מחדש"

    with b1:
        if st.button(label):
            if label in ["📝 שאלון", "🔄 מחדש"]:
                st.session_state.update({"quiz_active": True, "q_counter": 1, "show_feedback": False, "current_q_data": None})
            elif label == "✅ בדיקה" and ans:
                st.session_state.show_feedback = True
                if st.session_state.q_counter < 10: st.session_state.next_q_data = fetch_q(st.session_state.selected_topic)
            elif label == "➡️ הבאה":
                st.session_state.current_q_data = st.session_state.next_q_data
                st.session_state.update({"next_q_data": None, "q_counter": st.session_state.q_counter + 1, "show_feedback": False})
            st.rerun()
            
    with b2:
        if st.button("🏠"):
            st.session_state.update({"step": "menu", "quiz_active": False}); st.rerun()
            
    with b3: st.markdown('<a href="#top" class="nav-link">🔝</a>', unsafe_allow_html=True)
