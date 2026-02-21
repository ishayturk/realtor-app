# Project: מתווך בקליק | Version: 1213-G2-Final-Safe | File: app.py
# Anchor: 1213 (Raw Content & Logic)
import streamlit as st
import google.generativeai as genai
import json
import re

# הגדרת דף
st.set_page_config(page_title="מתווך בקליק", layout="wide")

# עיצוב CSS - מבודד למבחן ושומר על למידה
st.markdown("""
<style>
    * { direction: rtl; text-align: right; }
    .header-container { display: flex; align-items: center; gap: 45px; margin-bottom: 30px; }
    .header-title { font-size: 2.5rem !important; font-weight: bold !important; margin: 0 !important; }
    .header-user { font-size: 1.2rem !important; font-weight: 900 !important; color: #31333f; }
    .stButton>button { width: 100% !important; border-radius: 8px !important; font-weight: bold !important; height: 3em !important; }
    
    /* עיצוב ייעודי למצב מבחן בלבד */
    .exam-mode header { visibility: hidden !important; }
    .exam-mode .block-container { padding: 0 !important; }
</style>
""", unsafe_allow_html=True)

# סילבוס (עוגן 1213)
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

# --- לוגיקה ופונקציות ---

def reset_quiz_state():
    st.session_state.update({
        "quiz_active": False, "q_data": None, "q_count": 0,
        "checked": False, "quiz_finished": False, "correct_answers": 0
    })

def fetch_q_ai(topic):
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-2.0-flash')
        json_fmt = "{'q': '','options': ['','','',''], 'correct': '', 'explain': ''}"
        prompt = f"צור שאלה אמריקאית אחת על {topic}. החזר רק JSON: {json_fmt}"
        response = model.generate_content(prompt)
        match = re.search(r'\{.*\}', response.text, re.DOTALL)
        return json.loads(match.group()) if match else None
    except: return None

def stream_ai_lesson(prompt_text):
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content(f"הסבר מעמיק על {prompt_text}", stream=True)
        placeholder = st.empty()
        full_text = ""
        for chunk in response:
            full_text += chunk.text
            placeholder.markdown(full_text + "▌")
        placeholder.markdown(full_text)
        return full_text
    except: return "⚠️ תקלה."

# אתחול Session
if "step" not in st.session_state:
    st.session_state.update({"user": None, "step": "login", "selected_topic": None, "current_sub": None, "lesson_txt": ""})
if "questions_memory" not in st.session_state:
    st.session_state.questions_memory = []

# --- ניתוב דפים ---

if st.session_state.step == "login":
    st.title("🏠 מתווך בקליק")
    u_in = st.text_input("שם מלא:")
    if st.button("כניסה") and u_in:
        st.session_state.user = u_in
        st.session_state.step = "menu"
        st.rerun()

elif st.session_state.step == "menu":
    st.markdown(f'<div class="header-container"><div class="header-title">🏠 מתווך בקליק</div><div class="header-user">👤 <b>{st.session_state.user}</b></div></div>', unsafe_allow_html=True)
    c1, c2, _ = st.columns([1.5, 1.5, 3])
    if c1.button("📚 לימוד לפי נושאים"):
        st.session_state.step = "study"
        st.rerun()
    if c2.button("⏱️ גש/י למבחן"):
        st.session_state.step = "exam_frame"
        st.rerun()

elif st.session_state.step == "exam_frame":
    st.markdown('<div style="position:fixed; top:10px; width:100%; display:flex; justify-content:center; z-index:1001;"><a href="/?step=menu" target="_self" style="text-decoration:none; color:#555; font-weight:bold; background:rgba(255,255,255,0.8); padding:2px 12px; border-radius:5px; border:1px solid #ddd;">לתפריט הראשי</a></div>', unsafe_allow_html=True)
    if st.query_params.get("step") == "menu":
        st.session_state.step = "menu"
        st.query_params.clear()
        st.rerun()
    base_url = "https://fullrealestatebroker-yevuzewxde4obgrpgacrpc.streamlit.app/"
    exam_url = f"{base_url}?user={st.session_state.user}&embed=true"
    st.markdown(f'<iframe src="{exam_url}" style="width:100%; height:100vh; border:none; margin-top:-50px;"></iframe>', unsafe_allow_html=True)

elif st.session_state.step == "study":
    sel = st.selectbox("בחר נושא לימוד:", ["בחר..."] + list(SYLLABUS.keys()))
    if st.button("טען נושא") and sel != "בחר...":
        st.session_state.update({"selected_topic": sel, "step": "lesson_run", "lesson_txt": "", "current_sub": None})
        st.rerun()
    if st.button("🏠 חזרה"):
        st.session_state.step = "menu"
        st.rerun()

elif st.session_state.step == "lesson_run":
    st.header(f"📖 {st.session_state.selected_topic}")
    subs = SYLLABUS.get(st.session_state.selected_topic, [])
    cols = st.columns(len(subs))
    for i, s in enumerate(subs):
        if cols[i].button(s, key=f"s_{i}"):
            reset_quiz_state()
            st.session_state.update({"current_sub": s, "lesson_txt": "LOADING"})
            st.rerun()
    
    if st.session_state.current_sub:
        if st.session_state.lesson_txt == "LOADING":
            st.session_state.lesson_txt = stream_ai_lesson(f"הסבר על {st.session_state.current_sub}")
            st.rerun()
        else:
            st.markdown(st.session_state.lesson_txt)
            
            # לוגיקת שאלון (השלמה חסרה)
            if st.button("📝 התחל שאלון תרגול") and not st.session_state.quiz_active:
                res = fetch_q_ai(st.session_state.current_sub)
                if res:
                    st.session_state.update({"q_data": res, "quiz_active": True, "q_count": 1})
                    st.rerun()
            
            if st.session_state.quiz_active and st.session_state.q_data:
                st.divider()
                q = st.session_state.q_data
                ans = st.radio(q['q'], q['options'], key=f"q_{st.session_state.q_count}")
                if st.button("בדוק תשובה"):
                    st.session_state.checked = True
                    if ans == q['correct']: st.success("נכון!")
                    else: st.error(f"טעות. הנכון: {q['correct']}")
                    st.info(q['explain'])
    
    if st.button("🏠 לתפריט הראשי", key="back_home"):
        st.session_state.step = "menu"
        st.rerun()

# --- End of File ---
# Version: 1213-G2-Final | Date: 2026-02-21
