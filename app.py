# Project: מתווך בקליק | Version: 1213-Anchor-Updated-V2 | File: app.py
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
    "חוק המתווכים": ["רישוי והגבלות", "הגינות וזהירות", 
                     "הזמנה ובלעדיות", "פעולות שאינן תיווך"],
    "תקנות המתווכים": ["פרטי הזמנה 1997", "פעולות שיווק 2004", "דמי תיווך"],
    "חוק המקרקעין": ["בעלות וזכויות", "בתים משותפים", "עסקאות נוגדות", 
                     "הערות אזהרה", "שכירות וזיקה"],
    "חוק המכר (דירות)": ["מפרט וגילוי", "בדק ואחריות", 
                          "איחור במסירה", "הבטחת השקעות"],
    "חוק החוזים": ["כריתת חוזה", "פגמים בחוזה", "תרופות והפרה", "ביטול והשבה"],
    "חוק התכנון והבנייה": ["היתרים ושימוש חורג", "היטל השבחה", 
                            "תוכניות מתאר", "מוסדות התכנון"],
    "חוק מיסוי מקרקעין": ["מס שבח (חישוב ופטורים)", "מס רכישה", 
                           "הקלות לדירת מגורים", "שווי שוק"],
    "חוק הגנת הצרכן": ["ביטול עסקה", "הטעיה בפרסום"],
    "דיני ירושה": ["סדר הירושה", "צוואות"],
    "חוק העונשין": ["עבירות מרמה וזיוף"]
}

# פונקציות AI
def fetch_q_ai(topic):
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-2.0-flash')
        json_fmt = "{'q': '','options': ['','','',''], 'correct': '', 'explain': ''}"
        prompt = (f"צור שאלה אמריקאית אחת ברמה קשה על {topic} "
                  f"מתוך חומר הלימוד למבחן המתווכים. החזר אך ורק "
                  f"בפורמט JSON: {json_fmt}")
        response = model.generate_content(prompt)
        match = re.search(r'\{.*\}', response.text, re.DOTALL)
        if match:
            return json.loads(match.group())
    except Exception:
        return None

def stream_ai_lesson(prompt_text):
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-2.0-flash')
        full_p = (f"{prompt_text}. כתוב שיעור הכנה מעמיק למבחן המתווכים, "
                  f"כולל התייחסות לסעיפי חוק רלוונטיים.")
        response = model.generate_content(full_p, stream=True)
        placeholder = st.empty()
        full_text = ""
        for chunk in response:
            full_text += chunk.text
            placeholder.markdown(full_text + "▌")
        placeholder.markdown(full_text)
        return full_text
    except Exception:
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
        h_html = f"""
        <div class="header-container">
            <div class="header-title">🏠 מתווך בקליק</div>
            <div class="header-user">👤 <b>{u}</b></div>
        </div>
        """
        st.markdown(h_html, unsafe_allow_html=True)

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
    u_enc = st.session_state.user.replace(" ", "%20")
    b_url = "https://fullrealestatebroker-yevuzewxde4obgrpgacrpc.streamlit.app/"
    st.components.v1.iframe(f"{b_url}?user={u_enc}", height=1200, scrolling=True)

elif st.session_state.step == "study":
    show_header()
    selected_topic = st.selectbox("בחר נושא לימוד:", 
                                  ["בחר..."] + list(SYLLABUS.keys()))
    
    c1, c2 = st.columns([1, 1])
    with c1:
        if st.button("טען נושא"):
            if selected_topic != "בחר...":
                st.session_state.selected_topic = selected_topic
                st.session_state.step = "lesson_run"
                st.session_state.lesson_txt = ""
                st.rerun()
    with c2:
        if st.button("לתפריט הראשי"):
            st.session_state.step = "menu"
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
        st.session_state.lesson_txt = stream_ai_lesson(
            f"הסבר מפורט על {st.session_state.current_sub}"
        )
        st.rerun()
    elif st.session_state.get("lesson_txt"):
        st.markdown(st.session_state.lesson_txt)
    
    # ניווט תחתון קבוע לשיעור
    if not st.session_state.quiz_active:
        c1, c2 = st.columns([1, 1])
        with c1:
            if st.session_state.get("lesson_txt") and \
               st.session_state.lesson_txt != "LOADING":
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
        with c2:
            if st.button("לתפריט הראשי", key="back_from_lesson"):
                st.session_state.step = "menu"
                st.rerun()

    # שלב השאלון בתוך הלימוד
    if st.session_state.quiz_active and st.session_state.q_data and \
       not st.session_state.quiz_finished:
        q = st.session_state.q_data
        st.subheader(f"📝 שאלה {st.session_state.q_count} מתוך 10")
        ans = st.radio(q['q'], q['options'], index=None, 
                       key=f"q_{st.session_state.q_count}")
        
        # שורת כפתורי שליטה בשאלון
        btn_c1, btn_c2, btn_c3 = st.columns([2, 2, 2])
        
        with btn_c1:
            if st.button("בדוק/י תשובה", 
                         disabled=(ans is None or st.session_state.checked)):
                st.session_state.checked = True
                st.rerun()
        
        with btn_c2:
            if st.session_state.q_count < 10:
                if st.button("לשאלה הבאה", 
                             disabled=not st.session_state.checked):
                    with st.spinner("מייצר שאלה..."):
                        res = fetch_q_ai(st.session_state.current_sub)
                        if res:
                            st.session_state.q_data = res
                            st.session_state.q_count += 1
                            st.session_state.checked = False
                            st.rerun()
            else:
                if st.button("🏁 סיכום שאלון", 
                             disabled=not st.session_state.checked):
                    st.session_state.quiz_finished = True
                    st.rerun()
                    
        with btn_c3:
            if st.button("לתפריט הראשי", key="back_from_quiz"):
                st.session_state.step = "menu"
                st.rerun()

        if st.session_state.checked:
            if ans == q['correct']:
                st.success("נכון מאוד!")
                # עדכון ניקוד רק פעם אחת לכל שאלה
                key_score = f"score_done_{st.session_state.q_count}"
                if key_score not in st.session_state:
                    st.session_state.correct_answers += 1
                    st.session_state[key_score] = True
            else:
                st.error(f"טעות. התשובה הנכונה היא: {q['correct']}")
            st.info(f"הסבר: {q['explain']}")

    if st.session_state.quiz_finished:
        st.divider()
        st.balloons()
        st.success(f"🏆 סיימת! ענית נכון על "
                   f"{st.session_state.correct_answers} מתוך 10.")
        if st.button("לתפריט הראשי", key="final_back"):
            st.session_state.step = "menu"
            st.rerun()

# סוף הקובץ
