# ==========================================
# Project: מתווך בקליק | Version: 1211
# ==========================================
import streamlit as st
import google.generativeai as genai
import json, re

st.set_page_config(page_title="מתווך בקליק", layout="wide")
st.markdown('<div id="top"></div>', unsafe_allow_html=True)

st.markdown("""
<style>
    * { direction: rtl; text-align: right; }
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; height: 3em; }
    .top-link { 
        display: inline-block; width: 100%; text-align: center; 
        border-radius: 8px; text-decoration: none; border: 1px solid #d1d5db;
        font-weight: bold; height: 2.8em; line-height: 2.8em;
        background-color: transparent; color: inherit;
    }
    .v-footer {
        text-align: center;
        color: rgba(255, 255, 255, 0.1);
        font-size: 0.7em;
        margin-top: 50px;
        width: 100%;
    }
    [data-testid="stSidebar"] { display: none; }
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

def fetch_q(topic):
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        m = genai.GenerativeModel('gemini-2.0-flash')
        p = f"צור שאלה אמריקאית קשה על {topic} למבחן המתווכים. החזר אך ורק JSON תקני: {{'q':'','options':['','','',''],'correct':'','explain':''}}"
        res = m.generate_content(p).text
        match = re.search(r'\{.*\}', res, re.DOTALL)
        if match: return json.loads(match.group())
    except: pass
    return None

def stream_ai_lesson(p):
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        m = genai.GenerativeModel('gemini-2.0-flash')
        full_p = p + " כתוב שיעור הכנה מעמיק למבחן המתווכים. פרט סעיפי חוק, מספרים ודוגמאות. ללא כותרות."
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
    st.session_state.update({"user": None, "step": "login", "q_count": 0, "quiz_active": False, "show_ans": False, "lesson_txt": "", "q_data": None})

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
            st.session_state.step = "study"; st.rerun()
    with c2:
        if st.button("⏱️ גש/י למבחן"): st.info("בקרוב!")

elif st.session_state.step == "study":
    sel = st.selectbox("בחר נושא:", ["בחר..."] + list(SYLLABUS.keys()))
    if sel != "בחר..." and st.button("טען נושא"):
        st.session_state.update({"selected_topic": sel, "step": "lesson_run", "quiz_active": False, "lesson_txt": "", "q_data": None, "q_count": 0})
        st.rerun()

elif st.session_state.step == "lesson_run":
    topic = st.session_state.selected_topic
    st.header(f"📖 {topic}")
    
    subs = SYLLABUS.get(topic, [])
    cols = st.columns(len(subs))
    for i, s in enumerate(subs):
        if cols[i].button(s, key=f"sub_btn_{i}"):
            st.session_state.update({"current_sub": s, "lesson_txt": "LOADING", "quiz_active": False, "q_data": None, "show_ans": False})
            st.rerun()

    if st.session_state.get("lesson_txt") == "LOADING":
        st.subheader(st.session_state.current_sub)
        st.session_state.lesson_txt = stream_ai_lesson(f"שיעור על {st.session_state.current_sub} בחוק {topic}")
        st.rerun()
    elif st.session_state.get("lesson_txt"):
        st.subheader(st.session_state.current_sub)
        st.markdown(st.session_state.lesson_txt)

    if st.session_state.quiz_active and st.session_state.q_data:
        st.markdown("---")
        q = st.session_state.q_data
        st.subheader(f"📝 שאלה {st.session_state.q_count} מתוך 10")
        
        # שימוש במפתח ייחודי שמשתנה בכל שאלה כדי למנוע תקיעה
        ans = st.radio(q['q'], q['options'], index=None, key=f"quiz_radio_{st.session_state.q_count}")
        
        if st.session_state.show_ans:
            if ans == q['correct']: st.success("נכון!")
            else: st.error(f"טעות. התשובה הנכונה: {q['correct']}")
            st.info(f"הסבר: {q['explain']}")

    st.write("")
    f_cols = st.columns([2.5, 2, 1.5, 3])
    with f_cols[0]:
        if st.session_state.lesson_txt not in ["", "LOADING"]:
            if not st.session_state.quiz_active:
                if st.button("📝 שאלון לבחינה עצמית"):
                    with st.spinner("מעלה שאלה..."):
                        data = fetch_q(topic)
                        if data:
                            st.session_state.update({"q_data": data, "quiz_active": True, "q_count": 1, "show_ans": False})
                            st.rerun()
            elif not st.session_state.show_ans:
                if st.button("✅ בדיקת תשובה"):
                    st.session_state.show_ans = True; st.rerun()
            else:
                if st.button("➡️ שאלה הבאה"):
                    with st.spinner("מעלה שאלה..."):
                        data = fetch_q(topic)
                        if data:
                            # עדכון ה-Session State לפני ה-rerun כדי לוודא יציבות
                            st.session_state.q_data = data
                            st.session_state.q_count += 1
                            st.session_state.show_ans = False
                            st.rerun()
    with f_cols[1]:
        if st.button("🏠 לתפריט הראשי"):
            st.session_state.step = "menu"; st.rerun()
    with f_cols[2]:
        st.markdown('<a href="#top" class="top-link">🔝 לראש הדף</a>', unsafe_allow_html=True)

    st.markdown('<div class="v-footer">Version: 1211</div>', unsafe_allow_html=True)
