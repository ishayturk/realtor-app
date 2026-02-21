# Project: מתווך בקליק | Version: 1213-Anchor-Updated | File: app.py
import streamlit as st
import google.generativeai as genai
import json
import re

# הגדרת דף
st.set_page_config(page_title="מתווך בקליק", layout="wide")

# עיצוב RTL וסגנון כללי
st.markdown("""
<style>
    * {
        direction: rtl;
        text-align: right;
    }
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

# סילבוס מפורט
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

# פונקציות AI
def fetch_q_ai(topic):
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-2.0-flash')
        json_format = "{'q': '','options': ['','','',''], 'correct': '', 'explain': ''}"
        prompt = f"צור שאלה אמריקאית אחת ברמה קשה על {topic} מתוך חומר הלימוד למבחן המתווכים. החזר אך ורק בפורמט JSON: {json_format}"
        response = model.generate_content(prompt)
        match = re.search(r'\{.*\}', response.text, re.DOTALL)
        if match:
            return json.loads(match.group())
    except:
        return None

def stream_ai_lesson(prompt_text):
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-2.0-flash')
        full_prompt = f"{prompt_text}. כתוב שיעור הכנה מעמיק למבחן המתווכים, כולל התייחסות לסעיפי חוק רלוונטיים."
        response = model.generate_content(full_prompt, stream=True)
        placeholder = st.empty()
        full_text = ""
        for chunk in response:
            full_text += chunk.text
            placeholder.markdown(full_text + "▌")
        placeholder.markdown(full_text)
        return full_text
    except:
        return "⚠️ תקלה בטעינת השיעור."

# ניהול State
if "step" not in st.session_state:
    st.session_state.update({
        "user": None, "step": "login", "lesson_txt": "",
        "q_data": None, "q_count": 0, "quiz_active": False,
        "correct_answers": 0, "quiz_finished": False,
        "checked": False
    })

def show_header():
    if st.session_state.user:
        u = st.session_state.user
        header_html = f"""
        <div class="header-container">
            <div class="header-title">🏠 מתווך בקליק</div>
            <div class="header-user">👤 <b>{u}</b></div>
        </div>
        """
        st.markdown(header_html, unsafe_allow_html=True)

# --- ניהול שלבים ---

if st.session_state.step == "login":
    st.title("🏠 מתווך בקליק")
    user_input = st.text_input("שם מלא:")
    if st.button("כניסה"):
        if user_input:
            st.session_state.user = user_input
            st.session_state.step = "menu"
            st.rerun()

elif st.session_state.step == "menu":
    show_header()
    col1, col2, col3 = st.columns([1.5, 1.5, 3])
    with col1:
        if st.button("📚 לימוד לפי נושאים"):
            st.session_state.step = "study"
            st.rerun()
    with col2:
        if st.button("⏱️ גש/י למבחן"):
            st.session_state.step = "exam_frame"
            st.rerun()

elif st.session_state.step == "exam_frame":
    show_header()
    if st.button("לתפריט הראשי"):
        st.session_state.step = "menu"
        st.rerun()
    user_encoded = st.session_state.user.replace(" ", "%20")
    base_url = "https://fullrealestatebroker-yevuzewxde4obgrpgacrpc.streamlit.app/"
    st.components.v1.iframe(f"{base_url}?user={user_encoded}", height=1200, scrolling=True)

elif st.session_state.step == "study":
    show_header()
    selected_topic = st.selectbox("בחר נושא לימוד:", ["בחר..."] + list(SYLLABUS.keys()))
    if selected_topic != "בחר..." and st.button("טען נושא"):
        st.session_state.selected_topic = selected_topic
        st.session_state.step = "lesson_run"
        st.session_state.lesson_txt = ""
        st.rerun()

elif st.session_state.step == "lesson_run":
    show_header()
    st.header(f"📖 {st.session_state.selected_topic}")
    sub_topics = SYLLABUS.get(st.session_state.selected_topic, [])
    
    cols = st.columns(len(sub_topics))
    for i, sub in enumerate(sub_topics):
        if cols[i].button(sub, key=f"sub_{i}"):
            st.session_state.current_sub = sub
            st.session_state.lesson_txt = "LOADING"
            st.session_state.quiz_active = False
            st.session_state.q_count = 0
            st.session_state.checked = False
            st.rerun()

    if st.session_state.get("lesson_txt") == "LOADING":
        st.session_state.lesson_txt = stream_ai_lesson(f"הסבר מפורט על {st.session_state.current_sub}")
        st.rerun()
    elif st.session_state.get("lesson_txt"):
        st.markdown(st.session_state.lesson_txt)
    
    if st.session_state.quiz_active and st.session_state.q_data and not st.session_state.quiz_finished:
        st.divider()
        q = st.session_state.q_data
        st.subheader(f"📝 שאלה {st.session_state.q_count} מתוך 10")
        answer = st.radio(q['q'], q['options'], index=None, key=f"q_{st.session_state.q_count}")
        
        # בלוק כפתורי השליטה בשורה אחת
        c1, c2, c3 = st.columns([2, 2, 2])
        
        with c1: # כפתור בדיקה
            if st.button("בדוק/י תשובה", disabled=(answer is None or st.session_state.checked)):
                st.session_state.checked = True
                st.rerun()
        
        with c2: # כפתור שאלה הבאה / סיכום
            if st.session_state.q_count < 10:
                if st.button("לשאלה הבאה", disabled=not st.session_state.checked):
                    with st.spinner("מייצר שאלה..."):
                        res = fetch_q_ai(st.session_state.current_sub)
                        if res:
                            st.session_state.q_data = res
                            st.session_state.q_count += 1
                            st.session_state.checked = False
                            st.rerun()
            else:
                if st.button("🏁 סיכום שאלון", disabled=not st.session_state.checked):
                    st.session_state.quiz_finished = True
                    st.rerun()
                    
        with c3: # כפתור תפריט
            if st.button("לתפריט הראשי"):
                st.session_state.step = "menu"
                st.rerun()

        # הצגת תוצאות הבדיקה לאחר לחיצה
        if st.session_state.checked:
            if answer == q['correct']:
                st.success("נכון מאוד!")
                if "last_checked_q" not in st.session_state or st.session_state.last_checked_q != st.session_state.q_count:
                    st.session_state.correct_answers += 1
                    st.session_state.last_checked_q = st.session_state.q_count
            else:
                st.error(f"טעות. התשובה הנכונה היא: {q['correct']}")
            st.info(f"הסבר: {q['explain']}")

    if st.session_state.quiz_finished:
        st.divider()
        st.balloons()
        st.success(f"🏆 סיימת את השאלון! ענית נכון על {st.session_state.correct_answers} מתוך 10.")
        if st.button("לתפריט הראשי"):
            st.session_state.step = "menu"
            st.rerun()

    if st.session_state.get("lesson_txt") and st.session_state.lesson_txt != "LOADING" and not st.session_state.quiz_active:
        if st.button("📝 שאלון תרגול"):
            with st.spinner("מייצר שאלה..."):
                res = fetch_q_ai(st.session_state.current_sub)
                if res:
                    st.session_state.update({
                        "q_data": res, "quiz_active": True, 
                        "q_count": 1, "correct_answers": 0, 
                        "quiz_finished": False, "checked": False
                    })
                    st.rerun()

# סוף הקובץ
