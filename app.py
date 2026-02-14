import streamlit as st
import google.generativeai as genai
import json
import re

# 1. הגדרות תצוגה RTL ועיצוב
st.set_page_config(page_title="מתווך בקליק", layout="wide")

st.markdown("""
<style>
    .stApp { direction: rtl !important; text-align: right !important; }
    [data-testid="stSidebar"] { display: none; }
    .main .block-container { max-width: 850px; margin: 0 auto; }
    
    /* סרגל ניווט עליון קבוע */
    .nav-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 10px 20px;
        background-color: #f8f9fa;
        border-bottom: 2px solid #1E88E5;
        margin-bottom: 20px;
        border-radius: 10px;
    }

    .lesson-box { 
        background-color: #ffffff; padding: 30px; border-radius: 15px; 
        border-right: 8px solid #1E88E5; box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        font-size: 1.15rem; line-height: 1.8; margin-bottom: 25px;
    }
    
    .stButton > button { width: 100%; border-radius: 10px; font-weight: bold; height: 3em; }
</style>
""", unsafe_allow_html=True)

# 2. ניהול State
if "view" not in st.session_state:
    st.session_state.update({
        "view": "login", "user": "", "topic": "", "lesson": "",
        "questions": [], "answers": {}, "current_idx": 0, "feedback": False
    })

if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-2.0-flash')

# 3. פונקציות ליבה
def generate_lesson(topic):
    with st.spinner(f"מכין שיעור על {topic}..."):
        try:
            resp = model.generate_content(f"כתוב שיעור מפורט בעברית למבחן המתווכים על: {topic}. כלול סעיפי חוק.")
            st.session_state.lesson = resp.text
            st.session_state.view = "lesson"
            st.rerun()
        except: st.error("שגיאה בייצור השיעור")

def generate_questions(topic):
    with st.spinner("מייצר שאלות תרגול..."):
        try:
            # פרומפט נקי ללא תקלות JSON
            prompt = f"צור 10 שאלות אמריקאיות בעברית על {topic}. החזר אך ורק פורמט JSON כזה: [{{'q':'שאלה','options':['א','ב','ג','ד'],'correct':0,'explanation':'הסבר'}}] "
            resp = model.generate_content(prompt)
            raw_text = resp.text.replace("'", '"') # תיקון גרשיים
            match = re.search(r'\[.*\]', raw_text, re.DOTALL)
            if match:
                st.session_state.questions = json.loads(match.group())
                st.session_state.answers = {}
                st.session_state.current_idx = 0
                st.session_state.view = "quiz"
                st.rerun()
        except: st.error("ה-AI לא הצליח לייצר שאלות כרגע, נסה שוב")

# 4. רכיב תפריט עליון
def top_nav():
    col_r, col_l = st.columns([4, 1])
    with col_r:
        st.markdown(f"### 🏠 מתווך בקליק | {st.session_state.topic if st.session_state.topic else 'דף הבית'}")
    with col_l:
        if st.button("🏠 תפריט ראשי"):
            st.session_state.view = "menu"
            st.session_state.topic = ""
            st.rerun()
    st.markdown("---")

# 5. דפים
if st.session_state.view == "login":
    st.markdown("<h1 style='text-align: center;'>🏠 מתווך בקליק</h1>", unsafe_allow_html=True)
    name = st.text_input("שם מלא:", key="login_name")
    if st.button("התחל ללמוד"):
        if name: st.session_state.user = name; st.session_state.view = "menu"; st.rerun()

elif st.session_state.view == "menu":
    st.write(f"### שלום {st.session_state.user}, בחר נושא:")
    
    syllabus = [
        "חוק המתווכים במקרקעין", "חוק המקרקעין", "חוק המכר (דירות)", 
        "חוק החוזים", "חוק הגנת הצרכן", "חוק הגנת הדייר", 
        "חוק התכנון והבנייה", "חוק מיסוי מקרקעין", "חוק הירושה",
        "חוק יחסי ממון", "חוק איסור הלבנת הון", "פקודת הנזיקין",
        "חוק שמאי מקרקעין", "חוק העונשין (עבירות מרמה)", 
        "מושגי יסוד בכלכלה", "רשות מקרקעי ישראל"
    ]
    
    selected = st.selectbox("רשימת הנושאים המלאה:", ["בחר נושא..."] + syllabus)
    if selected != "בחר נושא...":
        st.session_state.topic = selected
        c1, c2 = st.columns(2)
        with c1: 
            if st.button("📖 פתח שיעור"): generate_lesson(selected)
        with c2: 
            if st.button("✍️ תרגול שאלות"): generate_questions(selected)

elif st.session_state.view == "lesson":
    top_nav()
    st.markdown(f'<div class="lesson-box">{st.session_state.lesson}</div>', unsafe_allow_html=True)
    if st.button(f"סיימתי לקרוא - עבור לתרגול ✍️"):
        generate_questions(st.session_state.topic)

elif st.session_state.view == "quiz":
    top_nav()
    idx = st.session_state.current_idx
    q = st.session_state.questions[idx]
    
    # לוח ניווט
    cols = st.columns(10)
    for i in range(len(st.session_state.questions)):
        with cols[i]:
            if st.button(f"{i+1}{'✓' if i in st.session_state.answers else ''}", key=f"n_{i}", type="primary" if i == idx else "secondary"):
                st.session_state.current_idx = i; st.session_state.feedback = False; st.rerun()

    st.info(q['q'])
    user_ans = st.session_state.answers.get(idx)
    choice = st.radio("בחר תשובה:", q['options'], key=f"q_{idx}", index=q['options'].index(user_ans) if user_ans in q['options'] else None)
    
    if choice: st.session_state.answers[idx] = choice

    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("⬅️ הקודם", disabled=idx==0): st.session_state.current_idx -= 1; st.session_state.feedback = False; st.rerun()
    with c2:
        if st.button("בדוק תשובה"): st.session_state.feedback = True
    with c3:
        if idx < 9:
            if st.button("הבא ➡️"): st.session_state.current_idx += 1; st.session_state.feedback = False; st.rerun()
        else:
            if st.button("סיום וציון 🏁"): st.session_state.view = "score"; st.rerun()

    if st.session_state.feedback and choice:
        if q['options'].index(choice) == q['correct']: st.success("✅ נכון!")
        else: st.error(f"❌ טעות. הנכון: {q['options'][q['correct']]}")
        st.write(f"**הסבר:** {q['explanation']}")

elif st.session_state.view == "score":
    top_nav()
    correct = sum(1 for i, q in enumerate(st.session_state.questions) if st.session_state.answers.get(i) == q['options'][q['correct']])
    st.metric("ציון סופי:", f"{correct*10}/100")
    if st.button("חזרה לתפריט הראשי"): st.session_state.view = "menu"; st.rerun()
