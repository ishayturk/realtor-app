import streamlit as st
import google.generativeai as genai
import json
import re

# 1. הגדרות דף בסיסיות
st.set_page_config(page_title="מתווך בקליק", layout="wide")

# CSS פשוט אך קשיח ליישור ימינה - עובד גם בנייד
st.markdown("""
<style>
    .stApp { direction: rtl; text-align: right; }
    p, h1, h2, h3, label, div { text-align: right !important; direction: rtl !important; }
    /* תיקון רדיו לנייד */
    div[role="radiogroup"] { direction: rtl !important; }
    .stButton button { width: 100%; height: 3em; margin-top: 10px; }
    .lesson-area { 
        background-color: #f9f9f9; 
        padding: 20px; 
        border-radius: 10px; 
        border-right: 5px solid #1E88E5;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# 2. אתחול משתנים
if "view" not in st.session_state:
    st.session_state.update({
        "view": "menu", "topic": "", "lesson_text": "",
        "questions": [], "answers": {}, "current_idx": 0, "feedback": False
    })

# חיבור ל-API
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-2.0-flash')

# 3. רשימת כל 16 הנושאים (סילבוס מלא)
SYLLABUS = [
    "חוק המתווכים במקרקעין", "חוק המקרקעין", "חוק המכר (דירות)",
    "חוק החוזים", "חוק הגנת הצרכן", "חוק הגנת הדייר",
    "חוק התכנון והבנייה", "חוק מיסוי מקרקעין", "חוק העונשין",
    "חוק שמאי מקרקעין", "חוק הירושה", "חוק יחסי ממון",
    "חוק איסור הלבנת הון", "פקודת הנזיקין", "מושגי יסוד בכלכלה",
    "רשות מקרקעי ישראל"
]

# 4. פונקציות ליבה
def load_lesson(topic):
    with st.spinner("טוען שיעור..."):
        try:
            res = model.generate_content(f"כתוב שיעור מפורט למבחן המתווכים על {topic} בעברית.")
            st.session_state.lesson_text = res.text
            st.session_state.topic = topic
            st.session_state.view = "lesson"
            st.rerun()
        except: st.error("תקלה בטעינה")

def load_quiz(topic):
    with st.spinner("מייצר שאלות..."):
        try:
            prompt = f"צור 10 שאלות אמריקאיות על {topic} ב-JSON: [{{'q':'','options':['','','',''],'correct':0,'explanation':''}}]"
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
        except: st.error("שגיאה בייצור שאלון")

# 5. ניווט דפים
if st.session_state.view == "menu":
    st.title("🏠 מתווך בקליק")
    st.write("בחר נושא מהסילבוס כדי להתחיל ללמוד:")
    
    choice = st.selectbox("רשימת נושאים:", ["בחר נושא..."] + SYLLABUS)
    if choice != "בחר נושא...":
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📖 קרא שיעור"): load_lesson(choice)
        with col2:
            if st.button("✍️ תרגול שאלות"): load_quiz(choice)

elif st.session_state.view == "lesson":
    st.subheader(f"נושא: {st.session_state.topic}")
    if st.button("⬅️ חזרה לתפריט"): st.session_state.view = "menu"; st.rerun()
    
    st.markdown(f'<div class="lesson-area">{st.session_state.lesson_text}</div>', unsafe_allow_html=True)
    
    if st.button("סיימתי ללמוד, עבור לשאלון ✍️"): load_quiz(st.session_state.topic)

elif st.session_state.view == "quiz":
    idx = st.session_state.current_idx
    q = st.session_state.questions[idx]
    
    st.subheader(f"שאלה {idx+1} מתוך 10")
    if st.button("🏠 תפריט ראשי"): st.session_state.view = "menu"; st.rerun()
    
    st.info(q['q'])
    ans = st.radio("בחר תשובה:", q['options'], key=f"ans_{idx}")
    
    if st.button("בדוק תשובה"):
        st.session_state.feedback = True
        st.session_state.answers[idx] = ans
        
    if st.session_state.feedback:
        correct_text = q['options'][q['correct']]
        if ans == correct_text:
            st.success("✅ תשובה נכונה!")
        else:
            st.error(f"❌ טעות. התשובה הנכונה היא: {correct_text}")
        st.write(f"**הסבר:** {q['explanation']}")
        
        if idx < 9:
            if st.button("שאלה הבאה ➡️"):
                st.session_state.current_idx += 1
                st.session_state.feedback = False
                st.rerun()
        else:
            st.balloons()
            if st.button("סיום וחזרה לתפריט"): st.session_state.view = "menu"; st.rerun()
