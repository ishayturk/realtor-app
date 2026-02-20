# ==========================================
# Project: מתווך בקליק | Version: 1213
# ==========================================
import streamlit as st
import google.generativeai as genai
import json, re

st.set_page_config(page_title="מתווך בקליק", layout="wide")
st.markdown('<div id="top"></div>', unsafe_allow_html=True)

# CSS לכפתורים שקופים מותאמי טקסט
st.markdown("""
<style>
    * { direction: rtl; text-align: right; }
    
    .stButton>button, .custom-btn { 
        width: auto !important; 
        min-width: 140px;
        padding: 0 25px;
        border-radius: 8px; 
        font-weight: bold; 
        height: 2.8em; 
        line-height: 2.8em;
        background-color: transparent !important;
        color: inherit !important;
        border: 1px solid #d1d5db !important;
        display: inline-block;
        text-decoration: none !important;
        box-sizing: border-box;
        text-align: center;
    }
    
    .stButton>button:hover, .custom-btn:hover {
        border-color: #ff4b4b !important;
        color: #ff4b4b !important;
    }

    .top-link { 
        display: inline-block; width: 100%; text-align: center; 
        border-radius: 8px; text-decoration: none; border: 1px solid #d1d5db;
        font-weight: bold; height: 2.8em; line-height: 2.8em;
        background-color: transparent; color: inherit;
    }
    .v-footer {
        text-align: center; color: rgba(255, 255, 255, 0.1);
        font-size: 0.7em; margin-top: 50px; width: 100%;
    }
</style>
""", unsafe_allow_html=True)

SYLLABUS = {
    "חוק המתווכים": ["רישוי והגבלות", "הגינות וזהירות", 
                     "הזמנה ובלעדיות", "פעולות שאינן תיווך"],
    "תקנות המתווכים": ["פרטי הזמנה 1997", "פעולות שיווק 2004", "דמי תיווך"],
    "חוק המקרקעין": ["בעלות וזכויות", "בתים משותפים", "עסקאות נוגדות", 
                     "הערות אזהרה", "שכירות וזיקה"],
    "חוק המכר (דירות)": ["מפרט וגילוי", "בדק ואחריות", 
                          "איחור במסירה", "הבטחת השקעות"],
    "חוק החוזים": ["כריתת חוזה", "פגמים בחוזה", 
                   "תרופות והפרה", "ביטול והשבה"],
    "חוק התכנון והבנייה": ["היתרים ושימוש חורג", "היטל השבחה", 
                           "תוכניות מתאר", "מוסדות התכנון"],
    "חוק מיסוי מקרקעין": ["מס שבח (חישוב ופפורים)", "מס רכישה", 
                          "הקלות לדירת מגורים", "שווי שוק"],
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
        "user": None, "step": "login", "q_count": 0, 
        "quiz_active": False, "show_ans": False, 
        "lesson_txt": "", "q_data": None, 
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
    
    cols = st.columns([1, 1, 4]) 
    with cols[0]:
        if st.button("📚 לימוד לפי נושאים"):
            st.session_state.step = "study"
            st.rerun()
    with cols[1]:
        u_name = st.session_state.user.replace(" ", "%20")
        b_url = "https://fullrealestatebroker-"
        b_url += "yevuzewxde4obgrpgacrpc.streamlit.app/"
        exam_url = f"{b_url}?user={u_name}"
        st.markdown(
            f'<a href="{exam_url}" target="_self" class="custom-btn">'
            f'⏱️ גש/י למבחן
