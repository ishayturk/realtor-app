import streamlit as st
import google.generativeai as genai
import json
import re

# 1. הגדרות תצוגה - כפיית RTL אגרסיבית לנייד
st.set_page_config(page_title="מתווך בקליק", layout="wide")

st.markdown("""
<style>
    /* כפייה על כל אלמנט אפשרי במערכת */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stVerticalBlock"] {
        direction: rtl !important;
        text-align: right !important;
    }
    
    /* תיקון ספציפי לניידים שמתעקשים על שמאל */
    div[data-testid="stMarkdownContainer"] > p {
        text-align: right !important;
        direction: rtl !important;
    }

    .main .block-container { max-width: 800px; margin: 0 auto; }
    
    /* עיצוב תיבת השיעור שתהיה קריאה בנייד */
    .lesson-content {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        border-right: 5px solid #1E88E5;
        line-height: 1.6;
        font-size: 1.1rem;
        direction: rtl !important;
        text-align: right !important;
    }

    /* כפתור יציאה/חזרה בולט */
    .stButton > button { border-radius: 8px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# 2. ניהול State
if "view" not in st.session_state:
    st.session_state.update({
        "view": "login", "user": "", "topic": "", "lesson_text": "",
        "questions": [], "answers": {}, "current_idx": 0
    })

if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-2.0-flash')

# 3. פונקציות ליבה
def get_lesson_stream(topic):
    """מייצר שיעור בהזרמה כדי שלא תחכה"""
    st.session_state.lesson_text = ""
    st.session_state.view = "lesson"
    
    # יצירת הקשר לשיעור
    placeholder = st.empty()
    full_response = ""
    
    try:
        responses = model.generate_content(
            f"כתוב שיעור מקצועי ומפורט בעברית למבחן המתווכים על: {topic}. השתמש בכותרות וסעיפים.",
            stream=True
        )
        
        for chunk in responses:
            full_response += chunk.text
            # הצגת הטקסט תוך כדי שהוא נכתב
            placeholder.markdown(f'<div class="lesson-content">{full_response}</div>', unsafe_allow_html=True)
        
        st.session_state.lesson_text = full_response
    except:
        st.error("תקלה בטעינה. נסה שוב.")

def generate_questions(topic):
    with st.spinner("מכין שאלות..."):
        try:
            prompt = f"צור 10 שאלות אמריקאיות בעברית על {topic}. החזר אך ורק פורמט JSON: [{{'q':'שאלה','options':['1','2','3','4'],'correct':0,'explanation':'הסבר'}}] "
            resp = model.generate_content(prompt)
            clean_json = re.search(r'\[.*\]', resp.text.replace("'", '"'), re.DOTALL)
            if clean_json:
                st.session_state.questions = json.loads(clean_json.group())
                st.session_state.answers = {}
                st.session_state.current_idx = 0
                st.session_state.view = "quiz"
                st.rerun()
        except: st.error("שגיאה בייצור שאלות.")

# 4. זרימת דפים
if st.session_state.view == "login":
    st.markdown("<h1 style='text-align: center;'>🏠 מתווך בקליק</h1>", unsafe_allow_html=True)
    name = st.text_input("שם מלא:")
    if st.button("התחל"):
        if name: st.session_state.user = name; st.session_state.view = "menu"; st.rerun()

elif st.session_state.view == "menu":
    st.write(f"### שלום {st.session_state.user}")
    syllabus = ["חוק המתווכים", "חוק המקרקעין", "חוק המכר", "חוק החוזים", "חוק הגנת הצרכן", "מיסוי מקרקעין", "תכנון ובנייה"]
    selected = st.selectbox("בחר נושא:", ["בחר..."] + syllabus)
    if selected != "בחר...":
        st.session_state.topic = selected
        if st.button("📖 פתח שיעור (טעינה מהירה)"):
            get_lesson_stream(selected)

elif st.session_state.view == "lesson":
    st.write(f"### שיעור: {st.session_state.topic}")
    if st.button("🏠 חזרה לתפריט"): st.session_state.view = "menu"; st.rerun()
    
    # הצגת השיעור (אם כבר נטען) או הפעלת הזרמה
    if st.session_state.lesson_text:
        st.markdown(f'<div class="lesson-content">{st.session_state.lesson_text}</div>', unsafe_allow_html=True)
    
    if st.button("✍️ עבור לתרגול שאלות"):
        generate_questions(st.session_state.topic)

elif st.session_state.view == "quiz":
    # (לוגיקת השאלון נשארת דומה אך עם כפיית RTL על הרדיו)
    idx = st.session_state.current_idx
    q = st.session_state.questions[idx]
    
    if st.button("🏠 תפריט ראשי"): st.session_state.view = "menu"; st.rerun()
    
    st.write(f"**שאלה {idx+1} מתוך 10**")
    st.info(q['q'])
    
    ans = st.radio("בחר תשובה:", q['options'], key=f"q_{idx}")
    if ans: st.session_state.answers[idx] = ans

    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ הקודם", disabled=idx==0): st.session_state.current_idx -= 1; st.rerun()
    with col2:
        if idx < 9:
            if st.button("הבא ➡️"): st.session_state.current_idx += 1; st.rerun()
        else:
            if st.button("🏁 סיום"): st.session_state.view = "menu"; st.rerun()
