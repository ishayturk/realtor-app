import streamlit as st
import google.generativeai as genai
import json
import re

# 1. הגדרות RTL ועיצוב
st.set_page_config(page_title="מתווך בקליק", layout="wide")

st.markdown("""
<style>
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stMarkdownContainer"] {
        direction: rtl !important; text-align: right !important;
    }
    [data-testid="stSidebar"] { direction: rtl !important; text-align: right !important; }
    
    .sidebar-top-branding {
        text-align: center;
        margin-top: -50px; 
        margin-bottom: 20px;
        padding-bottom: 10px;
        border-bottom: 1px solid #eee;
    }
    .sidebar-logo-icon { font-size: 45px; }
    .sidebar-app-name { 
        color: #1E88E5; font-size: 24px; font-weight: 800; margin-top: -10px;
    }
    .feedback-box { padding: 15px; border-radius: 8px; margin: 10px 0; border: 1px solid #eee; }
    .correct { background-color: #e6ffed; color: #1e4620; border-color: #b2f2bb; }
    .wrong { background-color: #fff5f5; color: #a91e2c; border-color: #ffa8a8; }
</style>
""", unsafe_allow_html=True)

# 2. רשימת כל השיעורים - הסילבוס המלא
FULL_TOPICS_LIST = [
    "חוק המתווכים במקרקעין, התשנ\"ו-1996",
    "תקנות המתווכים (פרטי הזמנה בכתב)",
    "חוק המקרקעין (בעלות, חזקה, שיתוף, בתים משותפים)",
    "חוק המכר (דירות) (הבטחת השקעות)",
    "חוק המכר (דירות) (חובת גילוי ואחריות)",
    "חוק הגנת הצרכן (ביטול עסקאות ורוכלות)",
    "חוק החוזים (חלק כללי) - כריתה וביטול",
    "חוק החוזים (תרופות בשל הפרת חוזה)",
    "חוק הגנת הדייר (נוסח משולב)",
    "חוק התכנון והבנייה (היתרים ומוסדות)",
    "חוק מיסוי מקרקעין (שבח, רכישה ופטורים)",
    "חוק העונשין (עבירות מרמה ושוחד)",
    "חוק שמאי מקרקעין",
    "חוק הירושה (הורשה על פי דין וצוואה)",
    "חוק מקרקעי ישראל (רמ\"י)",
    "מושגי יסוד בכלכלה ושמאות"
]

# 3. ניהול Session State
if "view_mode" not in st.session_state:
    st.session_state.update({
        "view_mode": "login", "user_name": "", "current_topic": "", 
        "lesson_data": "", "quiz_questions": []
    })

if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-2.0-flash')

def generate_quiz_json(topic):
    prompt = f"Create a 5-question quiz in HEBREW about {topic}. Return ONLY a JSON array."
    try:
        response = model.generate_content(prompt)
        json_str = re.search(r'\[.*\]', response.text, re.DOTALL).group()
        return json.loads(json_str)
    except: return None

# 4. סיידבר - מיתוג עליון וניווט
with st.sidebar:
    st.markdown("""
    <div class="sidebar-top-branding">
        <div class="sidebar-logo-icon">🏠</div>
        <div class="sidebar-app-name">מתווך בקליק</div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.session_state.user_name:
        st.markdown(f"**שלום, {st.session_state.user_name}**")
        st.markdown("---")
        if st.button("📚 בחירת נושא חדש"):
            st.session_state.update({"view_mode": "setup", "quiz_questions": []})
            st.rerun()
        if st.session_state.current_topic:
            if st.button
