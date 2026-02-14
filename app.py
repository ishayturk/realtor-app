import streamlit as st
import google.generativeai as genai
import json
import re

# 1. הגדרות תצוגה - כפיית RTL ועיצוב מותאם לנייד
st.set_page_config(page_title="מתווך בקליק", layout="wide")

st.markdown("""
<style>
    /* כפיית כיוון כתיבה לימין על כל האפליקציה */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stVerticalBlock"] {
        direction: rtl !important;
        text-align: right !important;
    }
    
    /* יישור טקסט רץ לימין - קריטי לנייד */
    div[data-testid="stMarkdownContainer"] > p, div[data-testid="stMarkdownContainer"] > h1, 
    div[data-testid="stMarkdownContainer"] > h2, div[data-testid="stMarkdownContainer"] > h3 {
        text-align: right !important;
        direction: rtl !important;
    }

    /* תיקון יישור כפתורי הרדיו (התשובות) */
    [data-testid="stWidgetLabel"] { text-align: right !important; width: 100%; }
    div[role="radiogroup"] { direction: rtl !important; text-align: right !important; }

    /* התאמת תוכן לרוחב המסך */
    .main .block-container { 
        padding-left: 1rem !important; 
        padding-right: 1rem !important; 
        max-width: 100% !important; 
    }
    
    .lesson-content, .feedback-box {
        background-color: #ffffff; padding: 15px; border-radius: 10px;
        border-right: 5px solid #1E88E5; line-height: 1.5; font-size: 1rem;
        margin-bottom: 15px; box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }

    /* עיצוב כפתורים שיהיו קלים ללחיצה באצבע */
    .stButton > button { 
        width: 100% !important; 
        height: 3.5rem !important; 
        font-size: 1.1rem !important;
        margin-bottom: 5px;
    }
</style>
""", unsafe_allow_html=True)

# 2. ניהול State
if "view" not in st.session_state:
    st.session_state.update({
        "view": "login", "user": "", "topic": "", "lesson_text": "",
        "questions": [], "answers": {}, "current_idx": 0, "show_feedback": False
    })

if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-2.0-flash')

# 3. פונקציות
def get_lesson_stream(topic):
    st.session_state.lesson_text = ""
    st.session_state.view = "lesson"
    placeholder = st.empty()
    full_response = ""
    try:
        responses = model.generate_content(f"כתוב שיעור מפורט בעברית על {topic}.", stream=True)
        for chunk in responses:
            full_response += chunk.text
            placeholder.markdown(f'<div class="lesson-content">{full_response}</div>', unsafe_allow_html=True)
        st.session_state.lesson_text = full_response
    except: st.error("תקלה בטעינה.")

def generate_questions(topic):
    with st.spinner("מייצר שאלות..."):
        try:
            prompt = f"Create 10 MCQs in HEBREW about {topic}. Return ONLY JSON array: [{{'q':'שאלה','options':['1','2','3','4'],'correct':0,'explanation':'הסבר'}}] "
            resp = model.generate_content(prompt)
            clean_json = re.search(r'\[.*\]', resp.text.replace("'", '"'), re.DOTALL)
            if clean_json:
                st.session_state.questions = json.loads(clean_json.group())
                st.session_state.answers = {}
                st.session_state.current_idx = 0
                st.session_state.show_feedback = False
                st.session_state.view = "quiz"
                st.rerun()
        except: st.error("שגיאה בייצור שאלות.")

# 4. דפים
if st.session_state.view == "login":
    st.markdown("<h2 style='text-align: center;'>🏠 מתווך בקליק</h2>", unsafe_allow_html=True)
    name = st.text_input("שם מלא:")
    if st.button("התחל ללמוד"):
        if name: st.session_state.user = name; st.session_state.view = "menu"; st.rerun()

elif st.session_state.view == "menu":
    st.write(f"### שלום {st.session_state.user}")
    syllabus = ["חוק המתווכים", "חוק המקרקעין", "חוק המכר", "חוק החוזים", "מיסוי מקרקעין"]
    selected = st.selectbox("בחר נושא:", ["בחר..."] + syllabus)
    if selected != "בחר...":
        st.session_state.topic = selected
        if st.button("📖 פתח שיעור"): get_lesson_stream(selected)
        if st.button("✍️ תרגול שאלות"): generate_questions(selected)

elif st.session_state.view == "lesson":
    st.write(f"### {st.session_state.topic}")
    if st.button("🏠 חזרה לתפריט"): st.session_state.view = "menu"; st.rerun()
    st.markdown(f'<div class="lesson-content">{st.session_state.lesson_text}</div>', unsafe_allow_html=True)
    if st.button("✍️ עבור לתרגול שאלות"): generate_questions(st.session_state.topic)

elif st.session_state.view == "quiz":
    idx = st.session_state.current_idx
    q = st.session_state.questions[idx]
    
    st.write(f"### שאלה {idx+1}/10")
    if st.button("🏠 תפריט"): st.session_state.view = "menu"; st.rerun()
    
    # ניווט שאלות מותאם לנייד (2 שורות של 5 כפתורים)
    for row in [range(0, 5), range(5, 10)]:
        cols = st.columns(5)
        for i in row:
            with cols[i % 5]:
                if st.button(f"{i+1}", key=f"n_{i}", type="primary" if i == idx else "secondary"):
                    st.session_state.current_idx = i; st.session_state.show_feedback = False; st.rerun()

    st.info(q['q'])
    user_choice = st.radio("בחר תשובה:", q['options'], key=f"r_{idx}")
    
    if st.button("בדוק תשובה ✅"):
        st.session_state.show_feedback = True
        st.session_state.answers[idx] = user_choice
    
    if st.session_state.show_feedback:
        if user_choice == q['options'][q['correct']]: st.success("נכון!")
        else: st.error(f"טעות. הנכון: {q['options'][q['correct']]}")
        st.markdown(f'<div class="feedback-box">{q["explanation"]}</div>', unsafe_allow_html=True)
        
    if idx < 9:
        if st.button("שאלה הבאה ➡️"):
            st.session_state.current_idx += 1; st.session_state.show_feedback = False; st.rerun()
    else:
        if st.button("🏁 סיום"): st.session_state.view = "menu"; st.rerun()
