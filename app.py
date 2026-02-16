# גרסה: 1099 | תאריך: 16/02/2026 | שעה: 11:45 | סטטוס: תוכן עשיר, יציבות ו-10 נושאים מלאים

import streamlit as st
import google.generativeai as genai
import json, re, time

st.set_page_config(page_title="מתווך בקליק", layout="centered")

# עיצוב UI
st.markdown("""
<style>
    * { direction: rtl !important; text-align: right !important; }
    .stApp { background-color: #ffffff; }
    .welcome-text { color: #1E88E5; font-weight: bold; margin-bottom: 10px; font-size: 2rem; }
    .lesson-title { color: #1E88E5; border-bottom: 2px solid #1E88E5; padding-bottom: 10px; margin-bottom: 20px; font-size: 1.8rem; }
    .lesson-box { 
        background-color: #f9f9f9; padding: 30px; 
        border-right: 6px solid #1E88E5; border-radius: 4px; 
        line-height: 1.8; font-size: 1.1rem; box-shadow: inset 0 0 10px rgba(0,0,0,0.02);
    }
    .question-card { background-color: #ffffff; padding: 25px; border: 1px solid #e0e0e0; border-radius: 12px; margin-bottom: 20px; }
    .stButton>button { width: auto; min-width: 150px; margin: 5px; }
    .version-footer { color: #bbbbbb; font-size: 0.7rem; text-align: center !important; margin-top: 50px; }
</style>
""", unsafe_allow_html=True)

# אתחול Session State
for key in ['step', 'user', 'sub_topics', 'lt', 'current_topic', 'current_sub', 'qq', 'qi', 'score', 'answered']:
    if key not in st.session_state:
        if key in ['score', 'qi']: st.session_state[key] = 0
        elif key == 'answered': st.session_state[key] = False
        elif key in ['sub_topics', 'qq']: st.session_state[key] = []
        elif key == 'step': st.session_state[key] = 'login'
        else: st.session_state[key] = ''

S = st.session_state

def fetch_content(prompt):
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-2.0-flash')
    try:
        r = model.generate_content(prompt)
        return r.text
    except: return None

# מפת 10 הנושאים המלאה - לטעינה מהירה של תתי-נושאים
TOPIC_MAP = {
    "חוק המתווכים במקרקעין": ["דרישת הכתב ופעולה יעילה", "איסור פעולות משפטיות", "דמי תיווך ובלעדיות"],
    "חוק המקרקעין": ["סוגי בעלות ושיתוף", "עסקאות ורישום בטאבו", "הערות אזהרה ומשכנתאות"],
    "חוק המכר (דירות)": ["מפרט המכר וחובות המוכר", "תקופת בדק ואחריות", "הבטחת השקעות של רוכשי דירות"],
    "חוק הגנת הצרכן": ["הטעיה וניצול מצוקה", "ביטול עסקה ברוכלות", "חובת גילוי במקרקעין"],
    "אתיקה מקצועית": ["חובת הגינות וזהירות", "ניגוד עניינים וסודיות", "פרסום והתנהגות כלפי קולגות"],
    "חוק החוזים": ["כריתת חוזה - הצעה וקיבול", "פגמים בכריתה (טעות, הטעיה, כפייה)", "תרופות בשל הפרת חוזה"],
    "מיסוי מקרקעין": ["מס שבח וחישובו", "מס רכישה ומדרגות מס", "פטורים לדירה מזכה יחידה"],
    "חוק התכנון והבנייה": ["מוסדות התכנון", "היתרי בנייה ושימוש חורג", "היטל השבחה"],
    "חוק הגנת הדייר": ["דיירות מוגנת ודמי מפתח", "עילות פינוי", "זכויות דייר ממשיך"],
    "חוק הירושה": ["ירושה על פי דין", "צוואות וקיומן", "הסתלקות מירושה וניהול עיזבון"]
}

st.title("🏠 מתווך בקליק")

if S.step == "login":
    u_input = st.text_input("שם מלא:")
    if st.button("כניסה"):
        if u_input:
            S.user = u_input; S.step = "menu"; st.rerun()

elif S.step == "menu":
    st.markdown(f"<h2 class='welcome-text'>שלום, {S.user}</h2>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    if c1.button("📚 לימוד לפי נושאים"): S.step = "study"; st.rerun()
    if c2.button("⏱️ סימולציית מבחן"):
        S.update({'current_topic': "מבחן כללי מקיף", 'step': "quiz_prep", 'score': 0, 'qi': 0}); st.rerun()

elif S.step == "study":
    st.markdown(f"**תלמיד:** {S.user}")
    topics = ["בחר נושא..."] + list(TOPIC_MAP.keys())
    sel = st.selectbox("בחר נושא ראשי ללימוד:", topics)
    
    if sel != "בחר נושא..." and st.button("📖 כניסה לשיעור"):
        S.update({'sub_topics': TOPIC_MAP.get(sel), 'current_topic': sel, 'lt': ""}); st.rerun()
    
    if S.sub_topics:
        st.write("---")
        st.write(f"### פרקים ב{S.current_topic}:")
        cols = st.columns(len(S.sub_topics))
        for i, sub in enumerate(S.sub_topics):
            if cols[i].button(sub, key
