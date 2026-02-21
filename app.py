# ==========================================
# Project: מתווך בקליק | Version: 1213-Anchor-Updated
# Last Update: 21/02/2026 | 12:45 (Jerusalem Time GMT+2)
# Status: Syntax Integrity Guaranteed | Protocol: Full File Delivery
# ==========================================
import streamlit as st
import google.generativeai as genai
import json, re

st.set_page_config(page_title="מתווך בקליק", layout="wide")

# CSS בסיסי
css_main = """
<style>
    * { direction: rtl; text-align: right; }
    .header-container { display: flex; align-items: center; gap: 45px; margin-bottom: 30px; }
    .header-title { font-size: 2.5rem !important; font-weight: bold !important; margin: 0 !important; }
    .header-user { font-size: 1.2rem !important; font-weight: 900 !important; color: #31333f; }
    .stButton>button { width: 100% !important; border-radius: 8px !important; 
                       font-weight: bold !important; height: 3em !important; }
</style>
"""
st.markdown(css_main, unsafe_allow_html=True)

SYLLABUS = {
    "חוק המתווכים": ["רישוי והגבלות", "הגינות וזהירות", "הזמנה ובלעדיות", "פעולות שאינן תיווך"],
    "תקנות המתווכים": ["פרטי הזמנה 1997", "פעולות שיווק 2004", "דמי תיווך"],
    "חוק המקרקעין": ["בעלות וזכויות", "בתים משותפים", "עסקאות נוגדות", "הערות אזהרה", "שכירות וזיקה"],
    "חוק המכר (דירות)": ["מפרט וגילוי", "בדק ואחריות", "איחור במסירה", "הבטחת השקעות"],
    "חוק החוזים": ["כריתת חוזה", "פגמים בחוזה", "תרופות והפרה", "ביטול והשבה"],
    "חוק התכנון והבנייה": ["היתרים ושימוש חורג", "היטל השבחה", "תוכניות מתאר", "מוסדות התכנון"],
    "חוק מיסוי מקרקעין": ["מס שבח (חישוב ופפורים)", "מס רכישה", "הקלות לדירת מגורים", "שווי שוק"],
    "חוק הגנת הצרכן": ["ביטול עסקה", "הטעיה בפרסום"],
    "דיני ירושה": ["סדר הירושה", "צוואות"],
    "חוק העונשין": ["עבירות מרמה וזיוף"]
}

def fetch_q_ai(topic):
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        m = genai.GenerativeModel('gemini-2.0-flash')
        j_format = "{'q':'','options':['','','',''],'correct':'','explain':''}"
        p = f"צור שאלה אמריקאית קשה על {topic}. החזר JSON: {j_format}"
        res = m.generate_content(p).text
        match = re.search(r'\{.*\}', res, re.DOTALL)
        if match: return json.loads(match.group())
    except: return None

def stream_ai_lesson(p):
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        m = genai.GenerativeModel('gemini-2.0-flash')
        full_p = f"{p}. כתוב שיעור הכנה מעמיק למבחן המתווכים עם סעיפי חוק."
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
        "user": None, "step": "login", "lesson_txt": "",
        "q_data": None, "q_count": 0, "quiz_active": False,
        "correct_answers": 0, "quiz_finished": False
    })

def show_header():
    if st.session_state.user:
        u = st.session_state.user
        h_html = f'<div class="header-container">' \
                 f'<div class="header-title">🏠 מתווך בקליק</div>' \
                 f'<div class="header-user">👤 <b>{u}</b></div></div>'
        st.markdown(h_html, unsafe_allow_html=True)

# --- לוגיקה של שלבי האפליקציה ---

if st.session_state.step == "login":
    st.title("🏠 מתווך בקליק")
    u_in = st.text_input("שם מלא:")
    if st.button("כניסה") and u_in:
        st.session_state.update({"user": u_in, "step": "menu"})
        st.rerun()

elif st.session_state.step == "menu":
    show_header()
    c1, c2, c3 = st.columns([1.5, 1.5, 3])
    with c1:
        if st.button("📚 לימוד לפי נושאים"):
            st.session_state.step = "study"
            st.rerun()
    with c2:
        if st.button("⏱️ גש/י למבחן"):
            st.session_state.step = "exam_frame"
            st.rerun()

elif st.session_state.step == "exam_frame":
    st.markdown("""<style>
        header {visibility: hidden !important; height: 0 !important;}
        .block-container {padding-top: 1.5rem !important; padding-bottom: 0rem !important;}
        .stApp { margin-top: -30px; }
        .exam-txt { font-size: 1.1rem; font-weight: bold; margin: 0; }
    </style>""", unsafe_allow_html=True)
    
    cr, cm, cl = st.columns([2, 2, 2])
    with cr:
        st.markdown('<p class="exam-txt">🏠 מתווך בקליק</p>', unsafe_allow_html=True)
    with cm:
        st.markdown(f'<p class="exam-txt" style="text-align:center;">{st.session_state.user}</p>', 
                    unsafe_allow_html=True)
    with cl:
        if st.button("לתפריט הראשי", key="back_exam"):
            st.session_state.step = "menu"
            st.rerun()

    u_enc = st.session_state.user.replace(" ", "%20")
    b_url = "https://fullrealestatebroker-yevuzewxde4obgrpgacrpc.streamlit.app/"
    st.components.v1.iframe(f"{b_url}?user={u_enc}", height=1100, scrolling=True)

elif st.session_state.step == "study":
    show_header()
    sel = st.selectbox("בחר נושא:", ["בחר..."] + list(SYLLABUS.keys()))
    if sel != "בחר..." and st.button("טען נושא"):
        st.session_state.update({"selected_topic": sel, "step": "lesson_run", "lesson_txt": ""})
        st.rerun()

elif st.session_state.step == "lesson_run":
    show_header()
    st.header(f"📖 {st.session_state.selected_topic}")
    subs = SYLLABUS.get(st.session_state.selected_topic, [])
    cols = st.columns(len(subs))
    for i, s in enumerate(subs):
        if cols[i].button(s, key=f"sub_{i}"):
            st.session_state.update({"current_sub": s, "lesson_txt": "LOADING", 
                                   "quiz_active": False, "q_count": 0})
            st.rerun()
            
    if st.session_state.get("lesson_txt") == "LOADING":
        st.session_state.lesson_txt = stream_ai_lesson(f"שיעור על {st.session_state.current_sub}")
        st.rerun()
    elif st.session_state.get("lesson_txt"):
        st.markdown(st.session_state.lesson_txt)
    
    if st.session_state.quiz_active and st.session_state.q_data and not st.session_state.quiz_finished:
        st.divider()
        q = st.session_state.q_data
        st.subheader(f"📝 שאלה {st.session_state.q_count} מתוך 10")
        ans = st.radio(q['q'], q['options'], index=None, key=f"q_{st.session_state.q_count}")
        if st.button("✅ בדיקת תשובה"):
            if ans == q['correct']:
                st.success("נכון!")
                st.session_state.correct_answers += 1
            else:
                st.error(f"טעות. התשובה היא: {q['correct']}")
            st.info(f"הסבר: {q['explain']}")
    
    if st.session_state.quiz_finished:
        st.divider(); st.balloons()
        st.success(f"🏆 סיימת! ענית נכון על {st.session_state.correct_answers} מתוך 10.")
    
    st.divider()
    f1, f2, f3 = st.columns([2, 2, 4])
    with f1:
        if st.button("🏠 חזרה לתפריט"):
            st.session_state.step = "menu"
            st.rerun()
    with f2:
        if st.session_state.get("lesson_txt") and st.session_state.lesson_txt != "LOADING":
            if not st.session_state.quiz_active:
                if st.button("📝 שאלון תרגול"):
                    with st.spinner("מכין שאלה..."):
                        res = fetch_q_ai(st.session_state.current_sub)
                        if res: 
                            st.session_state.update({"q_data": res, "quiz_active": True, 
                                                   "q_count": 1, "correct_answers": 0, 
                                                   "quiz_finished": False})
                            st.rerun()
            elif not st.session_state.quiz_finished:
                if st.session_state.q_count < 10:
                    if st.button("➡️ שאלה הבאה"):
                        with st.spinner("מכין שאלה הבאה..."):
                            res = fetch_q_ai(st.session_state.current_sub)
                            if res: 
                                st.session_state.update({"q_data": res, 
                                                       "q_count": st.session_state.q_count + 1})
                                st.rerun()
                else:
                    if st.button("🏁 סיכום שאלון"):
                        st.session_state.update({"quiz_finished": True})
                        st.rerun()
