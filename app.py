# Project: מתווך בקליק | Version: 1218-G2-Full-Logic-Consistent | File: app.py
# Anchor: 1218-G2 | Logic: Study + Exam + Consistent Navigation
import streamlit as st
import google.generativeai as genai
import json
import re

# הגדרת דף
st.set_page_config(page_title="מתווך בקליק", layout="wide", initial_sidebar_state="collapsed")

# עיצוב CSS - עוגן 1213 מקורי
st.markdown("""
<style>
    * { direction: rtl; text-align: right; }
    .header-container { 
        display: flex; 
        align-items: center; 
        gap: 45px; 
        margin-bottom: 30px; 
    }
    .header-title { font-size: 2.5rem !important; font-weight: bold !important; margin: 0 !important; }
    .header-user { font-size: 1.2rem !important; font-weight: 900 !important; color: #31333f; }
    .stButton>button { width: 100% !important; border-radius: 8px !important; font-weight: bold !important; height: 3em !important; }
</style>
""", unsafe_allow_html=True)

# סילבוס מלא
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

# --- פונקציות לוגיקה ---

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
        prompt = f"צור שאלה אמריקאית אחת על {topic}. החזר אך ורק JSON: {json_fmt}"
        response = model.generate_content(prompt)
        match = re.search(r'\{.*\}', response.text, re.DOTALL)
        return json.loads(match.group()) if match else None
    except: return None

def stream_ai_lesson(prompt_text):
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content(f"הסבר מעמיק ומפורט על {prompt_text} כהכנה למבחן המתווכים.", stream=True)
        placeholder = st.empty()
        full_text = ""
        for chunk in response:
            full_text += chunk.text
            placeholder.markdown(full_text + "▌")
        placeholder.markdown(full_text)
        return full_text
    except: return "⚠️ תקלה בחיבור ל-AI."

# אתחול Session State
if "step" not in st.session_state:
    st.session_state.update({
        "user": None, "step": "login", "selected_topic": None, 
        "current_sub": None, "lesson_txt": ""
    })

def show_header():
    if st.session_state.get("user"):
        st.markdown(f"""<div class="header-container">
            <div class="header-title">🏠 מתווך בקליק</div>
            <div class="header-user">👤 <b>{st.session_state.user}</b></div>
        </div>""", unsafe_allow_html=True)

# --- ניתוב דפים ---

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
    if c1.button("📚 לימוד לפי נושאים"):
        st.session_state.step = "study"
        st.rerun()
    if c2.button("⏱️ גש/י למבחן"):
        st.session_state.step = "exam_frame"
        st.rerun()

elif st.session_state.step == "exam_frame":
    # כפתור חזרה עקבי בצד שמאל
    col_back, col_spacer = st.columns([1.5, 4.5])
    with col_back:
        if st.button("🏠 לתפריט הראשי"):
            st.session_state.step = "menu"
            st.rerun()

    # עיצוב מבודד למבחן כדי למנוע מריחה
    st.markdown("""
    <style>
        header { visibility: hidden !important; }
        .block-container { padding-top: 0 !important; padding-right: 15px !important; }
    </style>
    """, unsafe_allow_html=True)

    base_url = "https://fullrealestatebroker-yevuzewxde4obgrpgacrpc.streamlit.app/"
    exam_url = f"{base_url}?user={st.session_state.user}&embed=true"
    st.markdown(f'<iframe src="{exam_url}" style="width:100%; height:90vh; border:none;"></iframe>', unsafe_allow_html=True)

elif st.session_state.step == "study":
    show_header()
    sel = st.selectbox("בחר נושא לימוד:", ["בחר..."] + list(SYLLABUS.keys()))
    col_a, col_b = st.columns([1, 1])
    if col_a.button("טען נושא") and sel != "בחר...":
        reset_quiz_state()
        st.session_state.update({"selected_topic": sel, "step": "lesson_run", "lesson_txt": "", "current_sub": None})
        st.rerun()
    if col_b.button("🏠 לתפריט הראשי"):
        st.session_state.step = "menu"
        st.rerun()

elif st.session_state.step == "lesson_run":
    show_header()
    st.header(f"📖 {st.session_state.selected_topic}")
    subs = SYLLABUS.get(st.session_state.selected_topic, [])
    cols = st.columns(len(subs))
    for i, s in enumerate(subs):
        if cols[i].button(s, key=f"s_{i}"):
            reset_quiz_state()
            st.session_state.update({"current_sub": s, "lesson_txt": "LOADING"})
            st.rerun()
    
    if st.session_state.current_sub:
        st.divider()
        if st.session_state.lesson_txt == "LOADING":
            st.session_state.lesson_txt = stream_ai_lesson(f"הסבר על {st.session_state.current_sub}")
            st.rerun()
        else:
            st.markdown(st.session_state.lesson_txt)
            
            # לוגיקת שאלון תרגול
            if st.button("📝 התחל שאלון תרגול") and not st.session_state.get("quiz_active"):
                res = fetch_q_ai(st.session_state.current_sub)
                if res:
                    st.session_state.update({"q_data": res, "quiz_active": True})
                    st.rerun()
            
            if st.session_state.get("quiz_active") and st.session_state.get("q_data"):
                st.info("💡 שאלת תרגול:")
                q = st.session_state.q_data
                choice = st.radio(q['q'], q['options'], key="quiz_choice")
                if st.button("בדוק תשובה"):
                    st.session_state.checked = True
                    if choice == q['correct']: st.success("כל הכבוד! תשובה נכונה.")
                    else: st.error(f"לא מדויק. התשובה הנכונה היא: {q['correct']}")
                    st.write(f"**הסבר:** {q['explain']}")

    st.divider()
    if st.button("🏠 לתפריט הראשי", key="back_from_lesson"):
        st.session_state.step = "menu"
        st.rerun()

# --- End of File ---
# Version: 1218-G2-Full-Logic-Consistent | Date: 2026-02-21
