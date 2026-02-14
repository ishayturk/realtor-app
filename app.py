import streamlit as st
import google.generativeai as genai
import json
import re

# 1. הגדרות RTL ועיצוב רספונסיבי (תיקון הסיידבר הנדחף)
st.set_page_config(page_title="מתווך בקליק", layout="wide")

st.markdown("""
<style>
    /* יישור RTL גלובלי */
    .stApp { direction: rtl !important; text-align: right !important; }

    /* הצמדת הסיידבר לימין באופן מוחלט */
    [data-testid="stSidebar"] {
        position: fixed;
        right: 0 !important;
        left: auto !important;
        direction: rtl !important;
        border-left: 1px solid #ddd;
        border-right: none !important;
        width: 300px !important;
    }

    /* תיקון השוליים של התוכן המרכזי כדי שלא ידחוף את הסיידבר */
    [data-testid="stAppViewContainer"] {
        margin-right: 300px !important;
        margin-left: 0 !important;
    }

    /* התאמה לנייד - הסיידבר הופך לתפריט המבורגר */
    @media (max-width: 768px) {
        [data-testid="stAppViewContainer"] { margin-right: 0 !important; }
        [data-testid="stSidebar"] { width: 85% !important; }
    }

    /* העברת כפתור הפתיחה (החץ) לימין */
    [data-testid="stSidebarCollapsedControl"] {
        right: 10px !important;
        left: auto !important;
    }

    /* עיצוב רשימת תשובות */
    div[data-testid="stRadio"] > label {
        direction: rtl !important;
        text-align: right !important;
        width: 100%;
        padding: 10px;
    }

    input { direction: rtl !important; text-align: right !important; }
</style>
""", unsafe_allow_html=True)

# 2. רשימת נושאים מלאה (סילבוס)
FULL_TOPICS = [
    "חוק המתווכים במקרקעין", "תקנות המתווכים (פרטי הזמנה)", "חוק המקרקעין", 
    "חוק המכר (דירות) (הבטחת השקעות)", "חוק המכר (דירות) (חובת גילוי)", 
    "חוק הגנת הצרכן", "חוק החוזים (חלק כללי)", "חוק החוזים (תרופות)", 
    "חוק הגנת הדייר", "חוק התכנון והבנייה", "חוק מיסוי מקרקעין", 
    "חוק העונשין (מרמה וזיוף)", "חוק שמאי מקרקעין", "חוק הירושה", 
    "חוק מקרקעי ישראל", "מושגי יסוד בכלכלה ושמאות"
]

# 3. ניהול State
if "view_mode" not in st.session_state:
    st.session_state.update({
        "view_mode": "login", "user_name": "", "current_topic": "",
        "exam_questions": [], "user_answers": {}, "current_exam_idx": 0, "show_feedback": False
    })

# חיבור ל-Gemini
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-2.0-flash')

# 4. פונקציית טעינת שאלות (נושא או מבחן מלא)
def load_exam(topic, count=25):
    prompt = f"Create a {count}-question quiz in HEBREW about {topic}. Return ONLY JSON array: [{'q':'','options':['','','',''],'correct':0,'explanation':'','source':''}]"
    with st.spinner("בונה שאלון..."):
        try:
            resp = model.generate_content(prompt)
            # ניקוי ה-JSON מהתגובה
            json_str = re.search(r'\[.*\]', resp.text, re.DOTALL).group()
            data = json.loads(json_str)
            st.session_state.update({
                "exam_questions": data, "user_answers": {}, "current_exam_idx": 0,
                "view_mode": "exam_mode", "show_feedback": False, "current_topic": topic
            })
        except Exception as e:
            st.error(f"שגיאה בייצור השאלות: {e}")

# 5. סיידבר - מיתוג ותפריט
with st.sidebar:
    st.markdown("<h2 style='text-align:center;'>🏠 מתווך בקליק</h2>", unsafe_allow_html=True)
    if st.session_state.user_name:
        st.write(f"שלום, **{st.session_state.user_name}**")
        st.markdown("---")
        
        if st.button("📚 סילבוס ונושאי לימוד", use_container_width=True):
            st.session_state.view_mode = "setup"; st.rerun()
            
        if st.button("🏆 מבחן סימולציה מלא", use_container_width=True):
            load_exam("מבחן מתווכים ממשלתי מעורב", 25); st.rerun()

        # לוח ניווט שאלות (מוצג רק בתוך מבחן)
        if st.session_state.view_mode == "exam_mode" and st.session_state.exam_questions:
            st.markdown("---")
            st.write("🎯 **ניווט בשאלות:**")
            n_cols = 5
            for row in range(0, len(st.session_state.exam_questions), n_cols):
                cols = st.columns(n_cols)
                for i in range(n_cols):
                    idx = row + i
                    if idx < len(st.session_state.exam_questions):
                        with cols[i]:
                            # סימון וי אם השאלה נענתה
                            label = str(idx + 1)
                            if idx in st.session_state.user_answers: label += "✓"
                            
                            style = "primary" if idx == st.session_state.current_exam_idx else "secondary"
                            if st.button(label, key=f"n_{idx}", type=style, use_container_width=True):
                                st.session_state.current_exam_idx = idx
                                st.session_state.show_feedback = False; st.rerun()

# 6. לוגיקת דפים מרכזית
if st.session_state.view_mode == "login":
    st.title("מערכת הכנה למבחן המתווכים")
    u_name = st.text_input("הכנס שם מלא לכניסה:")
    if st.button("התחל ללמוד", use_container_width=True):
        if u_name:
            st.session_state.user_name = u_name
            st.session_state.view_mode = "setup"; st.rerun()

elif st.session_state.view_mode == "setup":
    st.header("סילבוס הלימודים המלא")
    st.write("בחר נושא כדי לקרוא שיעור ולתרגל:")
    
    col_a, col_b = st.columns(2)
    for i, topic in enumerate(FULL_TOPICS):
        with (col_a if i % 2 == 0 else col_b):
            if st.button(f"📖 {topic}", use_container_width=True):
                st.session_state.current_topic = topic
                st.session_state.view_mode = "lesson_view"; st.rerun()

elif st.session_state.view_mode == "lesson_view":
    st.header(st.session_state.current_topic)
    # כאן ניתן להוסיף קריאת Gemini לשיעור (לצורך הקיצור כרגע זה placeholders)
    st.info(f"כאן יופיע תוכן השיעור המפורט על {st.session_state.current_topic}")
    if st.button(f"התחל תרגול (10 שאלות) על {st.session_state.current_topic}", use_container_width=True):
        load_exam(st.session_state.current_topic, 10); st.rerun()

elif st.session_state.view_mode == "exam_mode":
    idx = st.session_state.current_exam_idx
    questions = st.session_state.exam_questions
    q = questions[idx]
    
    st.subheader(f"{st.session_state.current_topic} - שאלה {idx+1} מתוך {len(questions)}")
    st.write(f"### {q['q']}")
    
    # הצגת התשובות
    saved_ans = st.session_state.user_answers.get(idx)
    choice = st.radio("בחר תשובה:", q['options'], key=f"exam_q_{idx}", 
                      index=q['options'].index(saved_ans) if saved_ans else None)
    
    if choice:
        st.session_state.user_answers[idx] = choice
        if st.button("בדוק תשובה"):
            st.session_state.show_feedback = True

    if st.session_state.show_feedback:
        is_correct = (q['options'].index(choice) == q['correct'])
        if is_correct:
            st.success("✅ נכון מאוד!")
        else:
            st.error(f"❌ טעות. התשובה הנכונה: {q['options'][q['correct']]}")
        
        st.markdown(f"**הסבר:** {q['explanation']}")
        st.markdown(f"<span style='color:blue'>📍 מקור מהחוק: {q['source']}</span>", unsafe_allow_html=True)

    st.markdown("---")
    # ניווט תחתון
    c1, c2 = st.columns(2)
    with c1:
        if st.button("⬅️ הקודם", disabled=idx==0, use_container_width=True):
            st.session_state.current_exam_idx -= 1
            st.session_state.show_feedback = False; st.rerun()
    with c2:
        if idx < len(questions) - 1:
            if st.button("הבא ➡️", use_container_width=True):
                st.session_state.current_exam_idx += 1
                st.session_state.show_feedback = False; st.rerun()
        else:
            if st.button("🏁 סיום מבחן וציון", use_container_width=True):
                st.session_state.view_mode = "summary"; st.rerun()

elif st.session_state.view_mode == "summary":
    st.header("סיכום המבחן")
    # חישוב ציון...
    st.balloons()
    st.success("כל הכבוד על סיום המבחן!")
    if st.button("חזרה לסילבוס"):
        st.session_state.view_mode = "setup"; st.rerun()
