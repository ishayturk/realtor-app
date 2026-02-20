import streamlit as st
import google.generativeai as genai
import json, re

st.set_page_config(page_title="מתווך בקליק", layout="wide")

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

def fetch_q_ai(topic):
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        m = genai.GenerativeModel('gemini-2.0-flash')
        p = f"צור שאלה אמריקאית קשה על {topic}. החזר JSON: {{'q':'','options':['','','',''],'correct':'','explain':''}}"
        res = m.generate_content(p).text
        match = re.search(r'\{.*\}', res, re.DOTALL)
        if match: return json.loads(match.group())
    except: return None
    return None

def stream_ai_lesson(p):
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        m = genai.GenerativeModel('gemini-2.0-flash')
        full_p = p + " כתוב שיעור הכנה למבחן המתווכים. ללא כותרות."
        response = m.generate_content(full_p, stream=True)
        placeholder = st.empty()
        full_text = ""
        for chunk in response:
            full_text += chunk.text
            placeholder.markdown(full_text + "▌")
        placeholder.markdown(full_text)
        return full_text
    except: return "⚠️ תקלה בטעינה."

if "step" not in st.session_state:
    st.session_state.update({
        "user": None, "step": "login", "selected_topic": None,
        "lesson_txt": "", "quiz_active": False, "q_data": None, "show_ans": False
    })

if st.session_state.step == "login":
    st.markdown("<style>* { direction: rtl; text-align: right; }</style>", unsafe_allow_html=True)
    st.title("🏠 מתווך בקליק")
    u = st.text_input("שם מלא:")
    if st.button("כניסה") and u:
        st.session_state.update({"user": u, "step": "menu"})
        st.rerun()

elif st.session_state.step == "menu":
    st.markdown("<style>* { direction: rtl; text-align: right; }</style>", unsafe_allow_html=True)
    st.title("🏠 מתווך בקליק")
    st.subheader(f"👤 שלום, {st.session_state.user}")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("📚 לימוד לפי נושאים"):
            st.session_state.step = "study"; st.rerun()
    with c2:
        if st.button("⏱️ גש/י למבחן"):
            st.session_state.step = "exam_intro"; st.rerun()

elif st.session_state.step == "study":
    st.markdown("<style>* { direction: rtl; text-align: right; }</style>", unsafe_allow_html=True)
    st.title("🏠 מתווך בקליק")
    st.subheader(f"👤 שלום, {st.session_state.user}")
    sel = st.selectbox("בחר נושא:", ["בחר..."] + list(SYLLABUS.keys()))
    col1, col2 = st.columns(2)
    with col1:
        if st.button("התחל לימוד") and sel != "בחר...":
            st.session_state.update({"selected_topic": sel, "step": "lesson_run", "lesson_txt": "", "quiz_active": False})
            st.rerun()
    with col2:
        if st.button("🏠 חזרה לתפריט"):
            st.session_state.step = "menu"; st.rerun()

elif st.session_state.step == "lesson_run":
    st.markdown("<style>* { direction: rtl; text-align: right; }</style>", unsafe_allow_html=True)
    st.title(f"📖 {st.session_state.selected_topic}")
    if not st.session_state.lesson_txt:
        st.session_state.lesson_txt = stream_ai_lesson(st.session_state.selected_topic)
    if st.button("❓ בחן אותי"):
        st.session_state.q_data = fetch_q_ai(st.session_state.selected_topic)
        st.session_state.quiz_active = True
        st.session_state.show_ans = False
    if st.session_state.quiz_active and st.session_state.q_data:
        q = st.session_state.q_data
        ans = st.radio(q['q'], q['options'], index=None)
        if st.button("בדוק"): st.session_state.show_ans = True
        if st.session_state.show_ans:
            if ans == q['correct']: st.success("נכון!")
            else: st.error(f"טעות. {q['correct']}")
            st.info(q['explain'])
    if st.button("🏠 חזור"):
        st.session_state.step = "study"; st.rerun()

elif st.session_state.step == "exam_intro":
    st.markdown("""<style>#MainMenu,footer,header{visibility:hidden;}.block-container{padding-top:0.8rem!important;}.user-info{font-size:0.9rem;color:gray;text-align:center;margin-top:10px;}.instruction-p{margin-bottom:-10px;}div[data-testid="stCheckbox"]{direction:rtl!important;margin-top:15px;}*{direction:rtl;text-align:right;}</style>""", unsafe_allow_html=True)
    cr, cm, cl = st.columns([1.5, 3, 1.5])
    with cr: st.markdown("<h4 style='margin:0;'>🏠 מתווך בקליק</h4>", unsafe_allow_html=True)
    with cm: st.markdown(f"<p class='user-info'>👤 {st.session_state.user}</p>", unsafe_allow_html=True)
    with cl:
        if st.button("לתפריט הראשי"): st.session_state.step = "menu"; st.rerun()
    st.header("הוראות למבחן")
    instr = ["1. המבחן כולל 25 שאלות.", "2. זמן מוקצב: 90 דקות.", "3. מעבר לשאלה הבאה רק לאחר סימון.", "4. ניתן לחזור אחורה לשאלות שנענו.", "5. בסיום הזמן המבחן
