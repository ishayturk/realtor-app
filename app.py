# Project: מתווך בקליק | Training_full_V05 | 21/02/2026 | 18:02
import streamlit as st
import google.generativeai as genai
import json
import re

# הגדרת דף
st.set_page_config(page_title="מתווך בקליק", layout="wide")

# עיצוב RTL בסיסי - משפיע על כל האפליקציה
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
    }
    .header-user { 
        font-size: 1.2rem !important; 
        font-weight: 900 !important; 
        color: #31333f; 
    }
    .stButton>button { 
        width: 100% !important; 
        border-radius: 8px !important; 
        font-weight: bold !important; 
        height: 3em !important; 
    }
</style>
""", unsafe_allow_html=True)

# סילבוס
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

# פונקציות
def reset_quiz_state():
    st.session_state.update({
        "quiz_active": False, "q_data": None, "q_count": 0,
        "checked": False, "quiz_finished": False, "correct_answers": 0
    })
    for key in list(st.session_state.keys()):
        if key.startswith("sc_"):
            del st.session_state[key]

def fetch_q_ai(topic):
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-2.0-flash')
        json_fmt = "{'q': '','options': ['','','',''], 'correct': '', 'explain': ''}"
        prompt = (f"צור שאלה אמריקאית אחת קשה על {topic} למבחן המתווכים. "
                  f"החזר אך ורק בפורמט JSON: {json_fmt}")
        response = model.generate_content(prompt)
        match = re.search(r'\{.*\}', response.text, re.DOTALL)
        return json.loads(match.group()) if match else None
    except: return None

def stream_ai_lesson(prompt_text):
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-2.0-flash')
        full_p = f"{prompt_text}. כתוב שיעור הכנה מעמיק למבחן המתווכים."
        response = model.generate_content(full_p, stream=True)
        placeholder = st.empty()
        full_text = ""
        for chunk in response:
            full_text += chunk.text
            placeholder.markdown(full_text + "▌")
        placeholder.markdown(full_text)
        return full_text
    except: return "⚠️ תקלה בטעינה."

# Init State
if "step" not in st.session_state:
    st.session_state.update({
        "user": None, "step": "login", "lesson_txt": "",
        "selected_topic": None, "current_sub": None,
        "quiz_active": False, "quiz_finished": False,
        "checked": False, "correct_answers": 0, "q_count": 0, "q_data": None
    })

def show_header():
    if st.session_state.get("user"):
        st.markdown(f"""<div class="header-container">
            <div class="header-title">🏠 מתווך בקליק</div>
            <div class="header-user">👤 <b>{st.session_state.user}</b></div>
        </div>""", unsafe_allow_html=True)

# --- Routing ---

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
    # CSS ספציפי למצב בחינה בלבד - ביטול מרווחים למעלה
    st.markdown("""
        <style>
            header {visibility: hidden;}
            .main .block-container { padding-top: 0px !important; }
            iframe { margin-top: -10px; }
        </style>
    """, unsafe_allow_html=True)
    
    # סטריפ עליון - כפתור חזרה צמוד לשמאל (עמודה אחרונה ב-RTL)
    c_empty, c_back = st.columns([5, 1])
    with c_back:
        if st.button("🏠 לתפריט"):
            st.session_state.step = "menu"
            st.rerun()
    
    # פריים מלא של אפליקציית הבחינה
    exam_url = f"https://fullrealestatebroker-yevuzewxde4obgrpgacrpc.streamlit.app/?user={st.session_state.user}&embed=true"
    st.markdown(f'<iframe src="{exam_url}" style="width:100%; height:95vh; border:none;"></iframe>', unsafe_allow_html=True)

elif st.session_state.step == "study":
    show_header()
    sel = st.selectbox("בחר נושא לימוד:", ["בחר..."] + list(SYLLABUS.keys()))
    col_a, col_b = st.columns([1, 1])
    if col_a.button("טען נושא") and sel != "בחר...":
        reset_quiz_state()
        st.session_state.update({"selected_topic": sel, "step": "lesson_run", "lesson_txt": "", "current_sub": None})
        st.rerun()
    if col_b.button("לתפריט הראשי"):
        reset_quiz_state()
        st.session_state.step = "menu"
        st.rerun()

elif st.session_state.step == "lesson_run":
    show_header()
    if not st.session_state.get("selected_topic"):
        st.session_state.step = "study"
        st.rerun()

    st.header(f"📖 {st.session_state.selected_topic}")
    subs = SYLLABUS.get(st.session_state.selected_topic, [])
    cols = st.columns(len(subs))
    for i, s in enumerate(subs):
        if cols[i].button(s, key=f"s_{i}"):
            reset_quiz_state()
            st.session_state.update({"current_sub": s, "lesson_txt": "LOADING"})
            st.rerun()

    if not st.session_state.get("current_sub"):
        st.write("")
        if st.button("לתפריט הראשי", key="back_no_sub"):
            reset_quiz_state()
            st.session_state.step = "menu"
            st.rerun()
    else:
        if st.session_state.get("lesson_txt") == "LOADING":
            st.session_state.lesson_txt = stream_ai_lesson(f"הסבר על {st.session_state.current_sub}")
            st.rerun()
        elif st.session_state.get("lesson_txt"):
            st.markdown(st.session_state.lesson_txt)

        if st.session_state.quiz_active and st.session_state.q_data and not st.session_state.quiz_finished:
            st.divider()
            q = st.session_state.q_data
            st.subheader(f"📝 שאלה {st.session_state.q_count} מתוך 10")
            ans = st.radio(q['q'], q['options'], index=None, key=f"q_{st.session_state.q_count}")
            qc1, qc2, qc3 = st.columns([2, 2, 2])
            if qc1.button("בדוק/י תשובה", disabled=(ans is None or st.session_state.checked)):
                st.session_state.checked = True
                st.rerun()
            if qc2.button("לשאלה הבאה" if st.session_state.q_count < 10 else "🏁 סיכום", disabled=not st.session_state.checked):
                if st.session_state.q_count < 10:
                    with st.spinner("טוען..."):
                        res = fetch_q_ai(st.session_state.current_sub)
                        if res:
                            st.session_state.update({"q_data": res, "q_count": st.session_state.q_count + 1, "checked": False})
                            st.rerun()
                else:
                    st.session_state.quiz_finished = True
                    st.rerun()
            if qc3.button("לתפריט הראשי", key="q_back"):
                reset_quiz_state()
                st.session_state.step = "menu"
                st.rerun()

            if st.session_state.checked:
                if ans == q['correct']:
                    st.success("נכון מאוד!")
                    if f"sc_{st.session_state.q_count}" not in st.session_state:
                        st.session_state.correct_answers += 1
                        st.session_state[f"sc_{st.session_state.q_count}"] = True
                else: st.error(f"טעות. הנכון הוא: {q['correct']}")
                st.info(f"הסבר: {q['explain']}")

        if (not st.session_state.quiz_active or st.session_state.quiz_finished) and st.session_state.get("current_sub"):
            if st.session_state.quiz_finished:
                st.success(f"🏆 ציון: {st.session_state.correct_answers} מתוך 10.")
            ca, cb = st.columns([1, 1])
            if ca.button("📝 שאלון תרגול" if not st.session_state.quiz_finished else "🔄 תרגול חוזר"):
                if st.session_state.get("lesson_txt") not in ["", "LOADING"]:
                    with st.spinner("מייצר שאלה..."):
                        res = fetch_q_ai(st.session_state.current_sub)
                        if res:
                            reset_quiz_state()
                            st.session_state.update({"q_data": res, "quiz_active": True, "q_count": 1, "checked": False})
                            st.rerun()
            if cb.button("לתפריט הראשי", key="main_back"):
                reset_quiz_state()
                st.session_state.step = "menu"
                st.rerun()

# סוף קובץ
