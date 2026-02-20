# ==========================================
# Project: מתווך בקליק | Version: 1213-Fixed-V3
# ==========================================
import streamlit as st
import streamlit.components.v1 as components
import google.generativeai as genai
import json, re

st.set_page_config(page_title="מתווך בקליק", layout="wide")

# CSS לדיוק הסטריפ והצמדה לתקרה
st.markdown("""
<style>
    * { direction: rtl; text-align: right; }
    .stApp header { visibility: hidden; }
    .block-container { padding-top: 0px !important; }
    
    /* עיצוב הסטריפ - שורה אחת מתחת לקצה */
    .exam-strip {
        background-color: #ffffff;
        padding: 5px 20px;
        margin-top: 10px;
        border-bottom: 1px solid #f0f2f6;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; }
    .v-footer { text-align: center; color: rgba(255, 255, 255, 0.1); font-size: 0.7em; }
</style>
""", unsafe_allow_html=True)

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

# --- פונקציות AI ---
def stream_ai_lesson(p):
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        m = genai.GenerativeModel('gemini-2.0-flash')
        response = m.generate_content(p + " ללא כותרות.", stream=True)
        ph = st.empty()
        txt = ""
        for chunk in response:
            txt += chunk.text
            ph.markdown(txt + "▌")
        ph.markdown(txt)
        return txt
    except: return "⚠️ תקלה בטעינה."

# אתחול
if "step" not in st.session_state:
    st.session_state.update({
        "user": None, "step": "login", "lesson_txt": "", 
        "current_sub": None, "selected_topic": None
    })

# --- ניהול דפים ---

if st.session_state.step == "login":
    st.title("🏠 מתווך בקליק")
    u = st.text_input("שם מלא:")
    if st.button("כניסה") and u:
        st.session_state.update({"user": u, "step": "menu"})
        st.rerun()

elif st.session_state.step == "menu":
    st.title("🏠 מתווך בקליק")
    st.subheader(f"👤 שלום, {st.session_state.user}")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("📚 לימוד לפי נושאים"):
            st.session_state.step = "study"; st.rerun()
    with c2:
        if st.button("⏱️ גש/י למבחן"):
            st.session_state.step = "exam_mode"; st.rerun()

elif st.session_state.step == "study":
    st.title("🏠 מתווך בקליק")
    st.subheader(f"👤 שלום, {st.session_state.user}")
    sel = st.selectbox("בחר נושא:", ["בחר..."] + list(SYLLABUS.keys()))
    if sel != "בחר..." and st.button("טען נושא"):
        st.session_state.selected_topic = sel
        st.session_state.step = "lesson_run"
        st.rerun()
    if st.button("🏠 חזרה"):
        st.session_state.step = "menu"; st.rerun()

elif st.session_state.step == "lesson_run":
    st.title("🏠 מתווך בקליק")
    st.subheader(f"👤 שלום, {st.session_state.user}")
    topic = st.session_state.selected_topic
    st.header(f"📖 {topic}")
    
    subs = SYLLABUS.get(topic, [])
    cols = st.columns(len(subs))
    for i, s in enumerate(subs):
        if cols[i].button(s, key=f"s_{i}"):
            st.session_state.current_sub = s
            st.session_state.lesson_txt = "LOADING"
            st.rerun()

    if st.session_state.get("lesson_txt") == "LOADING":
        st.session_state.lesson_txt = stream_ai_lesson(f"שיעור על {st.session_state.current_sub}")
        st.rerun()
    elif st.session_state.lesson_txt:
        st.markdown(st.session_state.lesson_txt)
    
    if st.button("↩️ חזרה לבחירת נושא"):
        st.session_state.lesson_txt = ""; st.session_state.step = "study"; st.rerun()

elif st.session_state.step == "exam_mode":
    # סטריפ צמוד ודק (פריים 1)
    with st.container():
        c1, c2, c3 = st.columns([1, 2, 1])
        with c1: st.write(f"### מתווך בקליק 🏠")
        with c2: st.write(f"### <center>👤 {st.session_state.user}</center>", unsafe_allow_html=True)
        with c3: 
            if st.button("↩️ לתפריט הראשי", key="back_btn"):
                st.session_state.step = "menu"; st.rerun()
    
    st.markdown("---")
    # הצמדה מקסימלית (פריים 2)
    ex_url = "https://fullrealestatebroker-yevuzewxde4obgrpgacrpc.streamlit.app/?embedded=true"
    components.iframe(ex_url, height=1000, scrolling=True)

st.markdown(f'<div class="v-footer">Version: 1213</div>', unsafe_allow_html=True)
