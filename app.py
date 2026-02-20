# ==========================================
# Project: מתווך בקליק | File: app.py
# Anchor: 1213 (Raw Content)
# ==========================================
import streamlit as st
import google.generativeai as genai
import json, re

st.set_page_config(page_title="מתווך בקליק", layout="wide")
st.markdown('<div id="top"></div>', unsafe_allow_html=True)

# CSS לכפתורים שקופים ואחידים (ללא קו תחתי)
st.markdown("""
<style>
    * { direction: rtl; text-align: right; }
    
    .stButton>button, .stLinkButton>a { 
        display: inline-flex !important;
        align-items: center;
        justify-content: center;
        width: 100% !important; 
        padding: 0 25px !important;
        border-radius: 8px !important; 
        font-weight: bold !important; 
        height: 3em !important; 
        background-color: transparent !important;
        color: #31333f !important;
        border: 1px solid #d1d5db !important;
        text-decoration: none !important;
        box-sizing: border-box;
        transition: 0.2s;
        white-space: nowrap !important;
    }
    
    .stButton>button:hover, .stLinkButton>a:hover {
        border-color: #ff4b4b !important;
        color: #ff4b4b !important;
        background-color: transparent !important;
    }
</style>
""", unsafe_allow_html=True)

SYLLABUS = {
    "חוק המתווכים": ["רישוי והגבלות", "הגינות וזהירות", 
                     "הזמנה ובלעדיות", "פעולות שאינן תיווך"],
    "תקנות המתווכים": ["פרטי הזמנה 1997", "פעולות שיווק 2004", "דמי תיווך"],
    "חוק המקרקעין": ["בעלות וזכויות", "בתים משותפים", "עסקאות נוגדות", 
                     "הערות אזהרה", "שכירות וזיקה"],
    "חוק המכר (דירות)": ["מפרט וגילוי", "בדק ואחריות", 
                          "איחור במסירה", "הבטחת השקעות"],
    "חוק החוזים": ["כריתת חוזה", "פגמים בחוזה", 
                   "תרופות והפרה", "ביטול והשבה"],
    "חוק התכנון והבנייה": ["היתרים ושימוש חורג", "היטל השבחה", 
                           "תוכניות מתאר", "מוסדות התכנון"],
    "חוק מיסוי מקרקעין": ["מס שבח (חישוב ופפורים)", "מס רכישה", 
                          "הקלות לדירת מגורים", "שווי שוק"],
    "חוק הגנת הצרכן": ["ביטול עסקה", "הטעיה בפרסום"],
    "דיני ירושה": ["סדר הירושה", "צוואות"],
    "חוק העונשין": ["עבירות מרמה וזיוף"]
}

def stream_ai_lesson(p):
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        m = genai.GenerativeModel('gemini-2.0-flash')
        response = m.generate_content(p, stream=True)
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
        "user": None, "step": "login", "lesson_txt": ""
    })

st.title("🏠 מתווך בקליק")

if st.session_state.step == "login":
    u = st.text_input("שם מלא:")
    if st.button("כניסה") and u:
        st.session_state.update({"user": u, "step": "menu"})
        st.rerun()

elif st.session_state.step == "menu":
    st.subheader(f"👤 שלום, {st.session_state.user}")
    c1, c2, c3 = st.columns([1.5, 1.5, 3])
    with c1:
        if st.button("📚 לימוד לפי נושאים"):
            st.session_state.step = "study"
            st.rerun()
    with c2:
        u_name = st.session_state.user.replace(" ", "%20")
        t_url = f"https://fullrealestatebroker-yevuzewxde4obgrpgacrpc.streamlit.app/?user={u_name}"
        st.link_button("⏱️ גש/י למבחן", t_url)

elif st.session_state.step == "study":
    st.subheader(f"👤 שלום, {st.session_state.user}")
    sel = st.selectbox("בחר נושא:", ["בחר..."] + list(SYLLABUS.keys()))
    if sel != "בחר..." and st.button("טען נושא"):
        st.session_state.update({
            "selected_topic": sel, "step": "lesson_run", "lesson_txt": ""
        })
        st.rerun()

elif st.session_state.step == "lesson_run":
    topic = st.session_state.selected_topic
    st.header(f"📖 {topic}")
    # החזרת שם המשתמש בין הכותרת לתתי הנושאים
    st.subheader(f"👤 לומד/ת כעת: {st.session_state.user}")
    
    subs = SYLLABUS.get(topic, [])
    cols = st.columns(len(subs))
    for i, s in enumerate(subs):
        if cols[i].button(s, key=f"sub_{i}"):
            st.session_state.update({"current_sub": s, "lesson_txt": "LOADING"})
            st.rerun()
    
    if st.session_state.get("lesson_txt") == "LOADING":
        st.session_state.lesson_txt = stream_ai_lesson(f"שיעור על {st.session_state.current_sub}")
        st.rerun()
    elif st.session_state.get("lesson_txt"):
        st.markdown(st.session_state.lesson_txt)

    st.write("")
    f_cols = st.columns([2, 2, 4])
    with f_cols[0]:
        if st.button("🏠 לתפריט הראשי"):
            st.session_state.step = "menu"
            st.rerun()
    with f_cols[1]:
        if st.button("🔝 לראש הדף"):
            st.rerun()
