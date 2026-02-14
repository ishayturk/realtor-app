import streamlit as st
import google.generativeai as genai
import json
import re

# 1. הגדרות דף - יישור לימין וכפייה על ניידים
st.set_page_config(page_title="מתווך בקליק", layout="wide")

st.markdown("""
<style>
    /* כפיית כיוון RTL על כל האפליקציה */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stVerticalBlock"] {
        direction: rtl !important;
        text-align: right !important;
    }
    
    /* תיקון רדיו וכפתורים לנייד */
    div[role="radiogroup"] { direction: rtl !important; }
    .stButton button { width: 100%; height: 3.5em; margin-top: 10px; border-radius: 10px; }
    
    /* תיבת שיעור מעוצבת */
    .lesson-box {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 12px;
        border-right: 6px solid #1E88E5;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin-bottom: 20px;
        line-height: 1.7;
    }
</style>
""", unsafe_allow_html=True)

# 2. ניהול מצב (Session State)
if "view" not in st.session_state:
    st.session_state.update({
        "view": "login", "user": "", "topic": "", "lesson_text": "",
        "questions": [], "answers": {}, "current_idx": 0, "feedback": False
    })

# חיבור ל-API
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-2.0-flash')

# 3. רשימת כל 16 הנושאים הרשמיים
SYLLABUS = [
    "חוק המתווכים במקרקעין והתקנות",
    "חוק המקרקעין (בעלות, שכירות, משכנתא)",
    "חוק המכר (דירות) (הבטחת השקעות)",
    "חוק החוזים (חלק כללי ותרופות)",
    "חוק הגנת הצרכן",
    "חוק הגנת הדייר",
    "חוק התכנון והבנייה (פרקים נבחרים)",
    "חוק מיסוי מקרקעין (שבח ורכישה)",
    "חוק העונשין (עבירות מרמה וזיוף)",
    "חוק שמאי מקרקעין",
    "חוק הירושה",
    "חוק יחסי ממון בין בני זוג",
    "חוק איסור הלבנת הון",
    "פקודת הנזיקין (רשלנות ותרמית)",
    "מושגי יסוד בכלכלה ושמאות",
    "חוק מקרקעי ישראל ורשות מקרקעי ישראל"
]

# 4. פונקציות טעינה
def load_lesson(topic):
    with st.spinner("מכין את חומר הלימוד..."):
        try:
            res = model.generate_content(f"כתוב שיעור מפורט למבחן המתווכים על {topic} בעברית.")
            st.session_state.lesson_text = res.text
            st.session_state.topic = topic
            st.session_state.view = "lesson"
            st.rerun()
        except: st.error("שגיאה בטעינת השיעור")

def load_quiz(topic):
    with st.spinner("מייצר שאלות תרגול..."):
        try:
            prompt = f"Create 10 MCQs in HEBREW about {topic}. Return ONLY JSON array: [{{'q':'שאלה','options':['1','2','3','4'],'correct':0,'explanation':'הסבר'}}] "
            res = model.generate_content(prompt)
            data = re.search(r'\[.*\]', res.text.replace("'", '"'), re.DOTALL)
            if data:
                st.session_state.questions = json.loads(data.group())
                st.session_state.topic = topic
                st.session_state.current_idx = 0
                st.session_state.answers = {}
                st.session_state.feedback = False
                st.session_state.view = "quiz"
                st.rerun()
        except: st.error("שגיאה בייצור השאלון")

# 5. ניווט דפים
if st.session_state.view == "login":
    st.title("🏠 מתווך בקליק")
    st.write("ברוכים הבאים לאפליקציית הלימוד למבחן המתווכים")
    name = st.text_input("הכנס שם מלא כדי להתחיל:")
    if st.button("כניסה למערכת הלימוד"):
        if name:
            st.session_state.user = name
            st.session_state.view = "menu"
            st.rerun()

elif st.session_state.view == "menu":
    st.subheader(f"שלום {st.session_state.user}, בחר נושא ללימוד:")
    choice = st.selectbox("רשימת הנושאים (הסילבוס המלא):", ["בחר נושא..."] + SYLLABUS)
    
    if choice != "בחר נושא...":
        st.info(f"נושא נבחר: {choice}")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📖 פתח שיעור"): load_lesson(choice)
        with col2:
            if st.button("✍️ תרגול שאלות"): load_quiz(choice)

elif st.session_state.view == "lesson":
    st.subheader(st.session_state.topic)
    if st.button("🏠 חזרה לתפריט הראשי"): st.session_state.view = "menu"; st.rerun()
    
    st.markdown(f'<div class="lesson-box">{st.session_state.lesson_text}</div>', unsafe_allow_html=True)
    
    if st.button("סיימתי לקרוא, עבור לתרגול שאלות ✍️"):
        load_quiz(st.session_state.topic)

elif st.session_state.view == "quiz":
    idx = st.session_state.current_idx
    q = st.session_state.questions[idx]
    
    st.subheader(f"תרגול: {st.session_state.topic}")
    st.write(f"**שאלה {idx+1} מתוך 10**")
    
    st.info(q['q'])
    ans = st.radio("בחר את התשובה הנכונה:", q['options'], key=f"ans_{idx}")
    
    if st.button("בדוק תשובה ✅"):
        st.session_state.feedback = True
        st.session_state.answers[idx] = ans
        
    if st.session_state.feedback:
        correct_text = q['options'][q['correct']]
        if ans == correct_text:
            st.success("כל הכבוד! תשובה נכונה.")
        else:
            st.error(f"טעות. התשובה הנכונה היא: {correct_text}")
        st.write(f"**הסבר:** {q['explanation']}")
        
        if idx < 9:
            if st.button("שאלה הבאה ➡️"):
                st.session_state.current_idx += 1
                st.session_state.feedback = False
                st.rerun()
        else:
            st.balloons()
            if st.button("סיום וחזרה לתפריט"): st.session_state.view = "menu"; st.rerun()
