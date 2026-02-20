# ==========================================
# Project: מתווך בקליק | Version: 1213
# ==========================================
import streamlit as st
import google.generativeai as genai
import json, re

st.set_page_config(page_title="מתווך בקליק", layout="wide")
st.markdown('<div id="top"></div>', unsafe_allow_html=True)

st.markdown("""
<style>
    * { direction: rtl; text-align: right; }
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; height: 3em; }
    
    /* התאמה מושלמת של כפתור המבחן לכפתורי המערכת */
    .exam-btn-final { 
        display: block; width: 100%; text-align: center; 
        border-radius: 8px; text-decoration: none !important; 
        border: 1px solid rgba(49, 51, 63, 0.2);
        font-weight: bold; height: 3em; line-height: 3em;
        background-color: #f0f2f6; 
        color: rgb(49, 51, 63) !important; /* צבע טקסט זהה לכפתור רגיל */
        box-sizing: border-box;
    }
    .exam-btn-final:hover {
        border-color: #ff4b4b;
        color: #ff4b4b !important;
    }

    .top-link { 
        display: inline-block; width: 100%; text-align: center; 
        border-radius: 8px; text-decoration: none; border: 1px solid #d1d5db;
        font-weight: bold; height: 2.8em; line-height: 2.8em;
        background-color: transparent; color: inherit;
    }
    .v-footer {
        text-align: center;
        color: rgba(255, 255, 255, 0.1);
        font-size: 0.7em;
        margin-top: 50px;
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

SYLLABUS = {
    "חוק המתווכים": ["רישוי והגבלות", "הגינות וזהירות", "הזמנה ובלעדיות", "פעולות שאינן תיווך"],
    "תקנות המתווכים": ["פרטי הזמנה 1997", "פעולות שיווק 2004", "דמי תיווך"],
    "חוק המקרקעין": ["בעלות וזכויות", "בתים משותפים", "עסקאות נוגדות", "הערות אזהרה", "שכירות וזיקה"],
    "חוק המכר (דירות)": ["מפרט וגילוי", "בדק ואחריות", "איחור במסירה", "הבטחת השקעות"],
    "חוק החוזים": ["כריתת חוזה", "פגמים בחוזה", "תרופות והפרה", "ביטול והשבה"],
    "חוק התכנון והבנייה": ["היתרים ושימוש חורג", "היטל השבחה", "תוכניות מתאר", "מוסדות התכנון"],
    "חוק מיסוי מקרקעין": ["מס שבח (חישוב ופפורים)", "מס רכישה", "הקלות לדירת מגורים", "שווי שוק"],
    "חוק הגנת הצרכן": ["ביטול עסקה", "הטעיה בפרסום"],
    "דיני ירושה": ["סדר הירושה", "צוואות"],
    "חוק העונשין": ["עבירות מרמה וזיוף"]
}

def fetch_q_ai(topic):
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        m = genai.GenerativeModel('gemini-2.0-flash')
        p = f"צור שאלה אמריקאית קשה על {topic}. החזר JSON תקני בלבד."
        res = m.generate_content(p).text
        match = re.search(r'\{.*\}', res, re.DOTALL)
        if match: return json.loads(match.group())
    except: return None

def stream_ai_lesson(p):
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        m = genai.GenerativeModel('gemini-2.0-flash')
        response = m.generate_content(p, stream=True)
        placeholder = st.empty()
        full_text = ""
        for chunk in response:
            full_text += chunk.text
            placeholder.markdown(full_text + "▌")
        placeholder.markdown(full_text)
        return full_text
    except: return "⚠️ תקלה בטעינה."

if "step" not in st.session_state:
    st.session_state.update({
        "user": None, "step": "login", "q_count": 0, "quiz_active": False, 
        "show_ans": False, "lesson_txt": "", "q_data": None, 
        "correct_answers": 0, "quiz_finished": False
    })

st.title("🏠 מתווך בקליק")

if st.session_state.step == "login":
    u = st.text_input("שם מלא:")
    if st.button("כניסה") and u:
        st.session_state.update({"user": u, "step": "menu"})
        st.rerun()

elif st.session_state.step == "menu":
    st.subheader(f"👤 שלום, {st.session_state.user}")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("📚 לימוד לפי נושאים"):
            st.session_state.step = "study"
            st.rerun()
    with c2:
        user_name = st.session_state.user.replace(" ", "%20")
        exam_url = f"https://fullrealestatebroker-yevuzewxde4obgrpgacrpc.streamlit.app/?user={user_name}"
        # שימוש בקישור שמעוצב בדיוק כמו הכפתור שמשמאל
        st.markdown(f'<a href="{exam_url}" target="_self" class="exam-btn-final">⏱️ גש/י למבחן</a>', unsafe_allow_html=True)

elif st.session_state.
