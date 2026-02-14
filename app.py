import streamlit as st
import google.generativeai as genai
import json
import re

# 1. הגדרות RTL ועיצוב מתקדם למניעת "דחיפת" הפריים
st.set_page_config(page_title="מתווך בקליק", layout="wide")

st.markdown("""
<style>
    /* הגדרת כיווניות כללית */
    html, body, [data-testid="stAppViewContainer"] {
        direction: rtl !important;
        text-align: right !important;
    }

    /* הצמדת הסיידבר (הפריים הימני) לקצה המסך */
    [data-testid="stSidebar"] {
        position: fixed;
        right: 0 !important;
        left: auto !important;
        direction: rtl !important;
        border-left: 1px solid #ddd;
    }

    /* ביטול הרווח הלבן שדוחף את התוכן שמאלה */
    [data-testid="stAppViewBlockContainer"] {
        max-width: 95% !important;
        margin-right: 0 !important;
        margin-left: auto !important;
        padding-right: 2rem !important;
    }

    /* התאמת כפתור התפריט (המבורגר) בנייד לצד ימין */
    [data-testid="stSidebarCollapsedControl"] {
        right: 10px !important;
        left: auto !important;
    }

    /* עיצוב רדיו וטקסט שיהיה נוח וקריא */
    .stRadio label { font-size: 1.1rem !important; }
    
    /* מירכוז מסך הכניסה */
    .login-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 50px;
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

# 3. רשימת נושאים (סילבוס)
FULL_TOPICS = [
    "חוק המתווכים במקרקעין", "תקנות המתווכים (פרטי הזמנה)", "חוק המקרקעין", 
    "חוק המכר (דירות) (הבטחת השקעות)", "חוק המכר (דירות) (חובת גילוי)", 
    "חוק הגנת הצרכן", "חוק החוזים (חלק כללי)", "חוק החוזים (תרופות)", 
    "חוק הגנת הדייר", "חוק התכנון והבנייה", "חוק מיסוי מקרקעין", 
    "חוק העונשין", "חוק שמאי מקרקעין", "חוק הירושה", 
    "חוק מקרקעי ישראל", "מושגי יסוד בכלכלה ושמאות"
]

# 4. פונקציית טעינת מבחן
def load_exam(topic, count=25):
    prompt = f"Create a {count}-question quiz in HEBREW about {topic}. Return ONLY JSON array: [{'q':'','options':['','','',''],'correct':0,'explanation':'','source':''}]"
    with st.spinner("מייצר שאלות..."):
        try:
            resp = model.generate_content(prompt)
            json_str = re.search(r'\[.*\]', resp.text, re.DOTALL).group()
            data = json.loads(json_str)
            st.session_state.update({
                "exam_questions": data, "user_answers": {}, "current_exam_idx": 0,
                "view_mode": "exam_mode", "show_feedback": False, "current_topic": topic
            })
            st.rerun()
        except: st.error("שגיאה בייצור שאלות. נסה שוב.")

# 5. סיידבר (התפריט הימני)
with st.sidebar:
    st.markdown("<h2 style='text-align:center;'>🏠 מתווך בקליק</h2>", unsafe_allow_html=True)
    if st.session_state.user_name:
        st.write(f"שלום, **{st.session_state.user_name}**")
        st.markdown("---")
        
        if st.button("📚 סילבוס שיעורים", use_container_width=True):
            st.session_state.view_mode = "setup"; st.rerun()
            
        if st.button("🏆 מבחן סימולציה מלא", use_container_width=True):
            load_exam("מבחן מתווכים ממשלתי מלא", 25)

        # ל
