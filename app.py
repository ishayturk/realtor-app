import streamlit as st
import google.generativeai as genai
import json, re

# הגדרות תצוגה
st.set_page_config(
    page_title="מתווך בקליק", 
    layout="wide"
)

st.markdown("""
<style>
    * { direction: rtl; text-align: right; }
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
</style>
""", unsafe_allow_html=True)

SYLLABUS = {
    "חוק המתווכים": [
        "רישוי והגבלות", "הגינות וזהירות", 
        "הזמנה ובלעדיות", "פעולות שאינן תיווך"
    ],
    "תקנות המתווכים": [
        "פרטי הזמנה 1997", "פעולות שיווק 2004", "דמי תיווך"
    ],
    "חוק המקרקעין": [
        "בעלות וזכויות", "בתים משותפים", "עסקאות נוגדות", 
        "הערות אזהרה", "שכירות וזיקה"
    ],
    "חוק המכר (דירות)": [
        "מפרט וגילוי", "בדק ואחריות", 
        "איחור במסירה", "הבטחת השקעות"
    ],
    "חוק החוזים": [
        "כריתת חוזה", "פגמים בחוזה", 
        "תרופות והפרה", "ביטול והשבה"
    ],
    "חוק התכנון והבנייה": [
        "היתרים ושימוש חורג", "היטל השבחה", 
        "תוכניות מתאר", "מוסדות התכנון"
    ],
    "חוק מיסוי מקרקעין": [
        "מס שבח (חישוב ופפורים)", "מס רכישה", 
        "הקלות לדירת מגורים", "שווי שוק"
    ],
    "חוק הגנת הצרכן": ["ביטול עסקה", "הטעיה בפרסום"],
    "דיני ירושה": ["סדר הירושה", "צוואות"],
    "חוק העונשין": ["עבירות מרמה וזיוף"]
}

def fetch_q_ai(topic):
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        m = genai.GenerativeModel('gemini-2.0-flash')
        p = (
            f"צור שאלה אמריקאית קשה על {topic}. "
            "החזר JSON: {'q':'','options':['','','',''],'correct':'','explain':''}"
        )
        res = m.generate_content(p).text
        match = re.search(r'\{.*\}', res, re.DOTALL)
        if match: 
            return json.loads(match.group())
    except: 
        return None

def stream_ai_lesson(p):
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        m = genai.GenerativeModel('gemini-2.0-flash')
        full_p = (
            f"{p}. כתוב שיעור הכנה מעמיק ומפורט "
            "למבחן המתווכים עם סעיפי חוק ודוגמאות."
        )
        response = m.generate_content(full_p, stream=True)
        placeholder = st.empty()
        full_text = ""
        for chunk in response:
            full_text += chunk.text
            placeholder.markdown(full_text + "▌")
        placeholder.markdown(full_text)
        return full_text
    except: 
        return "⚠️ תקלה בטעינה."

if "step" not in st.session_state:
    st.session_state.update({
        "user": None, 
        "step": "login", 
        "lesson_txt": "",
        "q_data": None, 
        "q_count": 0, 
        "quiz_active": False,
        "correct_answers": 0, 
        "quiz_finished": False, 
        "ans_checked": False
    })

def show_header():
    if st.session_state.user:
        h_html = (
            '<div class="header
