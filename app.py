# ==========================================
# Project: מתווך בקליק | File: app.py
# Anchor: 1213 (Restored & Fixed)
# ==========================================
import streamlit as st
import google.generativeai as genai
import json, re

st.set_page_config(page_title="מתווך בקליק", layout="wide")

# CSS המקורי שלך - ללא נגיעה
st.markdown("""
<style>
    * { direction: rtl; text-align: right; }
    
    .header-container {
        display: flex;
        align-items: center;
        gap: 45px;
        margin-bottom: 30px;
    }
    
    .header-title { 
        font-size: 2.5rem !important; 
        font-weight: bold !important; 
        margin: 0 !important;
        white-space: nowrap;
    }
    
    .header-user { 
        font-size: 1.2rem !important; 
        font-weight: 900 !important; 
        color: #31333f; 
        white-space: nowrap;
        margin-top: 10px;
    }

    .stButton>button, .stLinkButton>a { 
        display: inline-flex !important;
        align-items: center;
        justify-content: center;
        width: 100% !important; 
        border-radius: 8px !important; 
        font-weight: bold !important; 
        height: 3em !important; 
        background-color: transparent !important;
        color: #31333f !important;
        border: 1px solid #d1d5db !important;
        text-decoration: none !important;
        transition: 0.2s;
    }
    .stButton>button:hover, .stLinkButton>a:hover {
        border-color: #ff4b4b !important;
        color: #ff4b4b !important;
    }
</style>
""", unsafe_allow_html=True)

# סילבוס מקורי ומלא מגרסה 1213 - ללא קיצורים
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
    st.session_state.update({"user": None, "step": "login", "lesson_txt": ""})

def show_header():
    if st.session_state.user:
        h_html = f"""
        <div class="header-container">
            <div class="header-title">🏠 מתווך בקליק</div>
            <div class="header-user">👤 <b>{st.session_state.user}</b></div>
        </div>
        """
        st.markdown(h_html, unsafe_allow_html=True)
    else:
        st.markdown('<div class="header-title">🏠 מתווך בקליק</div>', unsafe_allow_html=True)

# --- דפים ---

if st.session_state.step == "login":
    st.title("🏠 מתווך בקליק")
    u = st.text_input("שם מלא:")
    if st.button("כניסה") and u:
        st.session_state.update({"user": u, "step": "menu"})
        st.rerun()

elif st.session_state.step == "menu":
    show_header()
    c1, c2, c3 = st.columns([1.5, 1.5, 3])
    with c1:
        if st.button("📚 לימוד לפי נושאים"):
            st.session_state.step = "study"
            st.rerun()
    with c2:
        # פתיחת המבחן בתוך המסגרת
        if st.button("⏱️ גש/י למבחן"):
            st.session_state.step = "exam_frame"
            st.rerun()

elif st.session_state.step == "exam_frame":
    # הסטריפ העליון המבוקש
    st.markdown('<div style="margin-top: -30px;"></div>', unsafe_allow_html=True)
    c_back, c_name, c_logo, c_sp = st.columns([1, 1, 1, 5])
    with c_back:
        if st.button("🏠 חזרה"):
            st.session_state.step = "menu"
            st.rerun()
    with c_name:
        st.markdown(f"**👤 {st.session_state.user}**")
    with c_logo:
        st.markdown("**🏠 מתווך בקליק**")
    st.divider()
    
    u_enc = st.session_state.user.replace(" ", "%20")
    b_url = "https://fullrealestatebroker-yevuzewxde4obgrpgacrpc.streamlit.app/"
    t_url = f"{b_url}?user={u_enc}"
    
    st.markdown('<div style="margin-top: -20px;"></div>', unsafe_allow_html=True)
    st.components.v1.iframe(t_url, height=900, scrolling=True)

elif st.session_state.step == "study":
    show_header()
    sel = st.selectbox("בחר נושא:", ["בחר..."] + list(SYLLABUS.keys()))
    if sel != "בחר..." and st.button("טען נושא"):
        st.session_state.update({
            "selected_topic": sel, 
            "step": "lesson_run", 
            "lesson_txt": ""
        })
        st.rerun()
    if st.button("🏠 חזרה"):
        st.session_state.step = "menu"
        st.rerun()

elif st.session_state.step == "lesson_run":
    show_header()
    topic = st.session_state.selected_topic
    st.header(f"📖 {topic}")
    
    subs = SYLLABUS.get(topic, [])
    cols = st.columns(len(subs))
    for i, s in enumerate(subs):
        if cols[i].button(s, key=f"sub_{i}"):
            st.session_state.update({"current_sub": s, "lesson_txt": "LOADING"})
            st.rerun()
    
    if st.session_state.get("lesson_txt") == "LOADING":
        p = f"שיעור על {st.session_state.current_sub}"
        st.session_state.lesson_txt = stream_ai_lesson(p)
        st.rerun()
    elif st.session_state.get("lesson_txt"):
        st.markdown(st.session_state.lesson_txt)

    if st.button("🏠 לתפריט הראשי"):
        st.session_state.step = "menu"
        st.rerun()
