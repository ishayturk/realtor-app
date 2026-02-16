# ==========================================
# Project: מתווך בקליק | Version: 1197
# ==========================================
import streamlit as st
import google.generativeai as genai
import json, re

st.set_page_config(page_title="מתווך בקליק", layout="wide")
st.markdown('<div id="top"></div>', unsafe_allow_html=True)

# עיצוב CSS ממוקד לתפריט תחתון וישור ימין
st.markdown("""
<style>
    * { direction: rtl; text-align: right; }
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; height: 3em; }
    /* עיצוב כפתור למעלה ככפתור סטנדרטי */
    .top-link { 
        display: inline-block; width: 100%; background-color: #f0f2f6; 
        color: black; text-align: center; padding: 0.5em 0; 
        border-radius: 8px; text-decoration: none; border: 1px solid #d1d5db;
        font-weight: bold; height: 1.8em; line-height: 1.8em;
    }
</style>
""", unsafe_allow_html=True)

SYLLABUS = {
    "חוק המתווכים": ["רישוי והגבלות", "הגינות וזהירות", "הזמנה ובלעדיות", "פעולות שאינן תיווך"],
    "תקנות המתווכים": ["פרטי הזמנה 1997", "פעולות שיווק 2004", "דמי תיווך"],
    "חוק המקרקעין": ["בעלות וזכויות", "בתים משותפים", "עסקאות נוגדות", "הערות אזהרה", "שכירות וזיקה"],
    "חוק המכר (דירות)": ["מפרט וגילוי", "בדק ואחריות", "איחור במסירה", "הבטחת השקעות"],
    "חוק החוזים": ["כריתת חוזה", "פגמים בחוזה", "תרופות והפרה", "ביטול והשבה"],
    "חוק התכנון והבנייה": ["היתרים ושימוש חורג", "היטל השבחה", "תוכניות מתאר", "מוסדות התכנון"],
    "חוק מיסוי מקרקעין": ["מס שבח (חישוב ופטורים)", "מס רכישה", "הקלות לדירת מגורים", "שווי שוק"],
    "חוק הגנת הצרכן": ["ביטול עסקה", "הטעיה בפרסום"],
    "דיני ירושה": ["סדר הירושה", "צוואות"],
    "חוק העונשין": ["עבירות מרמה וזיוף"]
}

def ask_ai(p, is_lesson=True):
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        m = genai.GenerativeModel('gemini-2.0-flash')
        prompt = p + " כתוב שיעור ארוך מאוד, מעמיק, עם סעיפי חוק ומספרים. ללא כותרות." if is_lesson else p
        r = m.generate_content(prompt)
        return r.text if r else None
    except: return "⚠️ תקלה זמנית."

def fetch_q(topic):
    p = f"שאלה אמריקאית על {topic}. JSON: {{'q':'','options':['','','',''],'correct':'','explain':''}}"
    res = ask_ai(p, is_lesson=False)
    try:
        data = json.loads(re.search(r'\{.*\}', res, re.DOTALL).group())
        return data
    except: return None

if "step" not in st.session_state:
    st.session_state.update({"user": None, "step": "login", "q_count": 0, "quiz_active": False, "show_ans": False})

st.title("🏠 מתווך בקליק")

if st.session_state.step == "login":
    u = st.text_input("שם מלא:")
    if st.button("כניסה") and u:
        st.session_state.update({"user": u, "step": "menu"})
        st.rerun()

elif st.session_state.step == "menu":
    st.subheader(f"👤 שלום, {st.session_state.user}")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("📚 לימוד לפי נושאים"):
            st.session_state.step = "study"
            st.rerun()
    with c2:
        if st.button("⏱️ גש/י למבחן"): st.info("בקרוב")

elif st.session_state.step == "study":
    sel = st.selectbox("בחר נושא:", ["בחר..."] + list(SYLLABUS.keys()))
    if sel != "בחר..." and st.button("טען נושא"):
        st.session_state.update({"selected_topic": sel, "step": "lesson_run", "quiz_active": False, "lesson_txt": ""})
        st.rerun()

elif st.session_state.step == "lesson_run":
    topic = st.session_state.selected_topic
    st.header(f"📖 {topic}")
    subs = SYLLABUS.get(topic, [])
    cols = st.columns(len(subs))
    for i, s in enumerate(subs):
        if cols[i].button(s, key=f"btn_{i}"):
            st.session_state.current_sub = s
            with st.spinner("מייצר תוכן..."):
                st.session_state.lesson_txt = ask_ai(f"שיעור מפורט על {s} בחוק {topic}")
            st.rerun()

    if st.session_state.get("lesson_txt"):
        st.subheader(st.session_state.current_sub)
        st.markdown(st.session_state.lesson_txt)

    if st.session_state.quiz_active:
        st.divider()
        st.subheader(f"📝 שאלון: {topic} (שאלה {st.session_state.q_count})")
        q = st.session_state.get("q_data")
        if q:
            ans = st.radio(q['q'], q['options'], index=None, key=f"q_{st.session_state.q_count}")
            if st.session_state.show_ans:
                if ans == q['correct']: st.success("נכון!")
                else: st.error(f"טעות. התשובה: {q['correct']}")
                st.info(q['explain'])

    # תפריט תחתון מאוחד בשורה אחת
    st.write("---")
    foot_cols = st.columns([1.5, 1.5, 1.5, 1.5, 4]) # חלוקה ל-5 עמודות לישור ימין
    
    with foot_cols[0]: # כפתור שאלון דינמי
        if not st.session_state.quiz_active:
            if st.button(f"📝 שאלון"):
                st.session_state.update({"quiz_active": True, "q_count": 1, "q_data": fetch_q(topic), "show_ans": False})
                st.rerun()
        elif not st.session_state.show_ans:
            if st.button("✅ בדיקה"):
                st.session_state.show_ans = True
                st.rerun()
        else:
            if st.button("➡️ הבאה"):
                st.session_state.update({"q_count": st.session_state.q_count + 1, "q_data": fetch_q(topic), "show_ans": False})
                st.rerun()

    with foot_cols[1]:
        if st.button("🏠 תפריט"):
            st.session_state.step = "menu"
            st.rerun()

    with foot_cols[2]:
        st.markdown('<a href="#top" class="top-link">🔝 למעלה</a>', unsafe_allow_html=True)
    
    st.caption(f"Version: 1197 | User: {st.session_state.user}")
