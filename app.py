import streamlit as st
import google.generativeai as genai
import json
import re

# 1. הגדרות RTL ועיצוב משופר שמוודא נראות
st.set_page_config(page_title="מתווך בקליק", layout="wide")

st.markdown("""
<style>
    .stApp { direction: rtl !important; text-align: right !important; }
    
    /* הצמדת הסיידבר לימין */
    [data-testid="stSidebar"] {
        right: 0 !important;
        left: auto !important;
        direction: rtl !important;
    }

    /* כפתורים גדולים ובולטים */
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 3em;
        background-color: #f0f2f6;
        border: 1px solid #d1d5db;
        font-weight: bold;
    }
    
    /* כפתור "התחל" בצבע בולט */
    div.stButton > button:first-child {
        background-color: #1E88E5;
        color: white;
    }

    input { direction: rtl !important; text-align: right !important; }
</style>
""", unsafe_allow_html=True)

# 2. ניהול State
if "view_mode" not in st.session_state:
    st.session_state.update({
        "view_mode": "login", "user_name": "", "current_topic": "",
        "exam_questions": [], "user_answers": {}, "current_exam_idx": 0, "show_feedback": False
    })

# חיבור ל-Gemini
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-2.0-flash')

# 3. רשימת נושאים
FULL_TOPICS = [
    "חוק המתווכים במקרקעין", "תקנות המתווכים (פרטי הזמנה)", "חוק המקרקעין", 
    "חוק המכר (דירות)", "חוק הגנת הצרכן", "חוק החוזים", 
    "חוק הגנת הדייר", "חוק התכנון והבנייה", "חוק מיסוי מקרקעין", 
    "חוק העונשין", "חוק שמאי מקרקעין", "חוק הירושה", 
    "חוק מקרקעי ישראל", "מושגי יסוד בכלכלה"
]

# 4. פונקציית טעינת מבחן
def load_exam(topic, count=25):
    with st.spinner(f"מייצר {count} שאלות על {topic}..."):
        try:
            prompt = f"Create a {count}-question quiz in HEBREW about {topic}. Return ONLY JSON array: [{'q':'','options':['','','',''],'correct':0,'explanation':'','source':''}]"
            resp = model.generate_content(prompt)
            json_match = re.search(r'\[.*\]', resp.text, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                st.session_state.update({
                    "exam_questions": data, "user_answers": {}, "current_exam_idx": 0,
                    "view_mode": "exam_mode", "show_feedback": False, "current_topic": topic
                })
                st.rerun()
        except Exception as e:
            st.error(f"שגיאה: {e}")

# 5. סיידבר
with st.sidebar:
    st.header("🏠 מתווך בקליק")
    if st.session_state.user_name:
        st.success(f"שלום, {st.session_state.user_name}")
        if st.button("📚 חזרה לתפריט נושאים"):
            st.session_state.view_mode = "setup"; st.rerun()
        if st.button("🏆 מבחן סימולציה מלא"):
            load_exam("כל חומר הבחינה", 25)
        
        # לוח ניווט במבחן
        if st.session_state.view_mode == "exam_mode" and st.session_state.exam_questions:
            st.write("---")
            st.write("📍 ניווט שאלות:")
            cols = st.columns(5)
            for i in range(len(st.session_state.exam_questions)):
                with cols[i % 5]:
                    if st.button(str(i+1), key=f"n_{i}"):
                        st.session_state.current_exam_idx = i
                        st.session_state.show_feedback = False; st.rerun()

# 6. גוף האפליקציה (הפריים המרכזי)
if st.session_state.view_mode == "login":
    st.title("ברוכים הבאים למערכת הלימוד")
    name = st.text_input("הכנס שם מלא כדי להתחיל:")
    if st.button("התחל ללמוד עכשיו 🚀"):
        if name:
            st.session_state.user_name = name
            st.session_state.view_mode = "setup"; st.rerun()
        else:
            st.warning("בבקשה הכנס שם כדי שנוכל להתקדם.")

elif st.session_state.view_mode == "setup":
    st.header("בחירת נושא לימוד")
    st.write("לחץ על אחד הנושאים כדי להתחיל לתרגל:")
    for t in FULL_TOPICS:
        if st.button(f"📖 {t}"):
            st.session_state.current_topic = t
            load_exam(t, 10)

elif st.session_state.view_mode == "exam_mode":
    idx = st.session_state.current_exam_idx
    q = st.session_state.exam_questions[idx]
    
    st.subheader(f"שאלה {idx+1} מתוך {len(st.session_state.exam_questions)}")
    st.info(q['q'])
    
    ans = st.radio("בחר תשובה:", q['options'], key=f"q_{idx}")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ הקודם", disabled=idx==0):
            st.session_state.current_exam_idx -= 1; st.rerun()
    with col2:
        if idx < len(st.session_state.exam_questions) - 1:
            if st.button("הבא ➡️"):
                st.session_state.current_exam_idx += 1; st.rerun()
        else:
            if st.button("🏁 סיום ומבט על התוצאות"):
                st.balloons(); st.write("סיימת בהצלחה!")
