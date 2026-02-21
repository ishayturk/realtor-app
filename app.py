# Project: מתווך בקליק | File: app.py | Version: 1218-G8-Final-Fix
import streamlit as st
import google.generativeai as genai
import json
import re

# הגדרת דף
st.set_page_config(page_title="מתווך בקליק", layout="wide", initial_sidebar_state="collapsed")

# --- CSS CORE (עוגן 1213) ---
st.markdown("""
<style>
    * { direction: rtl; text-align: right; }
    .header-container { display: flex; align-items: center; gap: 45px; margin-bottom: 30px; }
    .header-title { font-size: 2.5rem !important; font-weight: bold !important; margin: 0 !important; }
    .header-user { font-size: 1.2rem !important; font-weight: 900 !important; color: #31333f; }
    .stButton>button { width: 100% !important; border-radius: 8px !important; font-weight: bold !important; height: 3em !important; }
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

# --- לוגיקת AI ---
def stream_ai_lesson(prompt_text):
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content(f"כתוב שיעור הכנה למבחן המתווכים על: {prompt_text}", stream=True)
        placeholder = st.empty()
        full_text = ""
        for chunk in response:
            full_text += chunk.text
            placeholder.markdown(full_text + "▌")
        placeholder.markdown(full_text)
        return full_text
    except: return "⚠️ תקלה בטעינה."

def fetch_q_ai(topic):
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-2.0-flash')
        prompt = f"צור שאלה אמריקאית על {topic}. החזר JSON בלבד: {{'q': '','options': ['','','',''], 'correct': '', 'explain': ''}}"
        response = model.generate_content(prompt)
        match = re.search(r'\{.*\}', response.text, re.DOTALL)
        return json.loads(match.group()) if match else None
    except: return None

# אתחול
if "step" not in st.session_state:
    st.session_state.update({"user": None, "step": "login", "selected_topic": None, "current_sub": None, "lesson_txt": ""})

def show_header():
    if st.session_state.user:
        st.markdown(f'<div class="header-container"><div class="header-title">🏠 מתווך בקליק</div><div class="header-user">👤 <b>{st.session_state.user}</b></div></div>', unsafe_allow_html=True)

# --- ניתוב ---
if st.session_state.step == "login":
    st.title("🏠 מתווך בקליק")
    u_in = st.text_input("שם מלא:")
    if st.button("כניסה") and u_in:
        st.session_state.user = u_in
        st.session_state.step = "menu"
        st.rerun()

elif st.session_state.step == "menu":
    show_header()
    c1, c2, _ = st.columns([1.5, 1.5, 3])
    if c1.button("📚 לימוד לפי נושאים"): st.session_state.step = "study"; st.rerun()
    if c2.button("⏱️ גש/י למבחן"): st.session_state.step = "exam_frame"; st.rerun()

elif st.session_state.step == "exam_frame":
    col_back, col_user, col_logo = st.columns([1.5, 2, 1.5])
    with col_back:
        if st.button("🏠 לתפריט הראשי"): st.session_state.step = "menu"; st.rerun()
    with col_user: st.markdown(f"<p style='text-align:center; font-weight:bold; padding-top:10px;'>{st.session_state.user}</p>", unsafe_allow_html=True)
    with col_logo: st.markdown("<p style='text-align:right; font-weight:bold; padding-top:10px;'>🏠 מתווך בקליק</p>", unsafe_allow_html=True)
    st.markdown("<style>header { visibility: hidden !important; } .block-container { padding-top: 0 !important; }</style>", unsafe_allow_html=True)
    exam_url = f"https://fullrealestatebroker-yevuzewxde4obgrpgacrpc.streamlit.app/?user={st.session_state.user}&embed=true"
    st.markdown(f'<iframe src="{exam_url}" style="width:100%; height:92vh; border:none;"></iframe>', unsafe_allow_html=True)

elif st.session_state.step == "study":
    show_header()
    sel = st.selectbox("בחר נושא:", ["בחר..."] + list(SYLLABUS.keys()))
    if st.button("טען נושא") and sel != "בחר...":
        st.session_state.update({"selected_topic": sel, "step": "lesson_run", "lesson_txt": "", "current_sub": None})
        st.rerun()
    if st.button("🏠 לתפריט הראשי"): st.session_state.step = "menu"; st.rerun()

elif st.session_state.step == "lesson_run":
    show_header()
    st.header(f"📖 {st.session_state.selected_topic}")
    subs = SYLLABUS.get(st.session_state.selected_topic, [])
    cols = st.columns(len(subs))
    for i, s in enumerate(subs):
        if cols[i].button(s, key=f"s_{i}"):
            st.session_state.update({"current_sub": s, "lesson_txt": "LOADING"})
            st.rerun()
    
    if st.session_state.current_sub:
        st.divider()
        if st.session_state.lesson_txt == "LOADING":
            st.session_state.lesson_txt = stream_ai_lesson(st.session_state.current_sub)
            st.rerun()
        else:
            st.markdown(st.session_state.lesson_txt)
            if st.button("📝 שאלת תרגול"):
                res = fetch_q_ai(st.session_state.current_sub)
                if res: st.session_state.q_data = res; st.session_state.quiz_active = True; st.rerun()
            if st.session_state.get("quiz_active"):
                q = st.session_state.q_data
                choice = st.radio(q['q'], q['options'])
                if st.button("בדוק"):
                    if choice == q['correct']: st.success("נכון!")
                    else: st.error(f"טעות. הנכון: {q['correct']}")

    if st.button("🏠 לתפריט הראשי", key="final_back"): st.session_state.step = "menu"; st.rerun()
