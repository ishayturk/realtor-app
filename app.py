# גרסה: 1033 | תאריך: 16/02/2026 | שעה: 08:15
# מזהה פרויקט: REALTOR_EXAM_SIM_PRO_V2
# סטטוס: Full Production Ready - Real Exams & Stability

import streamlit as st
import google.generativeai as genai
import json, re, time, random
from google.api_core import exceptions

# הגדרות דף בסיסיות
st.set_page_config(page_title="מתווך בקליק - הגרסה הרשמית", layout="centered")

# עיצוב UI מתקדמת כולל RTL מלא
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Assistant:wght@300;400;700&display=swap');
    * { direction: rtl !important; text-align: right !important; font-family: 'Assistant', sans-serif; }
    .lesson-box { background-color: #ffffff; padding: 30px; border-radius: 15px; border-right: 8px solid #1E88E5; line-height: 1.9; margin-bottom: 25px; box-shadow: 0 4px 12px rgba(0,0,0,0.08); color: #2c3e50; }
    .question-card { background-color: #ffffff; padding: 25px; border-radius: 12px; border: 1px solid #eef2f7; margin-bottom: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }
    .main-header { background: linear-gradient(90deg, #1E88E5, #1565C0); color: white; padding: 20px; border-radius: 15px; text-align: center; margin-bottom: 20px; font-size: 28px; font-weight: bold; }
    .lobby-card { background: #fffde7; padding: 20px; border-radius: 10px; border: 1px dashed #fbc02d; margin-bottom: 20px; }
    .stButton > button { width: 100%; border-radius: 10px; font-weight: bold; height: 3.8em; transition: all 0.3s; }
    .stButton > button:hover { transform: translateY(-2px); box-shadow: 0 4px 8px rgba(0,0,0,0.1); }
</style>
""", unsafe_allow_html=True)

# אתחול Session State - בדיקה כפולה שכל המשתנים קיימים
S = st.session_state
if 'step' not in S:
    S.update({
        'user': '', 'step': 'login', 'lt': '', 'qi': 0, 'qans': {}, 'qq': [], 
        'total_q': 25, 'start_time': 0, 'is_loading': False, 'current_topic': '', 
        'mode': 'exam', 'cq': set(), 'exam_info': {}
    })

# פונקציית שליפת תוכן (שאלות) - מותאמת להנחיית "דליית בחינה מהרשת"
def fetch_exam_content(mode='study', topic='כללי'):
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        if mode == 'exam':
            # הנחיה לדליית בחינה רשמית מרשת האינטרנט/מאגר
            p = f"""מצא בחינה רשמית של רשם המתווכים משנים 2020-2025. 
            בחר מועד אקראי. שלוף 5 שאלות מורכבות מהבחינה (כולל אירועים משפטיים).
            זהה את גרסת השאלון והשתמש בקובץ התשובות הרשמי של אותו מועד.
            החזר JSON נקי בלבד במבנה:
            [ {{"q": "טקסט השאלה", "options": ["א","ב","ג","ד"], "correct": "התשובה המדויקת מהמפתח", "reason": "הסבר משפטי מהחוק", "source": "מועד/שנה"}} ]"""
        else:
            p = f"צור 10 שאלות תרגול ממוקדות בנושא {topic} למבחן המתווכים. JSON נקי: [{{'q':'','options':['א','ב','ג','ד'],'correct':'','reason':''}}]"
        
        r = model.generate_content(p)
        m = re.search(r'\[.*\]', r.text, re.DOTALL)
        return json.loads(m.group()) if m else []
    except Exception as e:
        return []

st.markdown("<div class='main-header'>🏠 מתווך בקליק - מערכת הכנה רשמית</div>", unsafe_allow_html=True)

# --- 1. מסך כניסה ---
if S.step == "login":
    u = st.text_input("ברוך הבא! הזן שם מלא להתחלה:", key="login_input")
    if st.button("כניסה למערכת"):
        if u: S.user = u; S.step = "menu"; st.rerun()

# --- 2. תפריט ראשי ---
elif S.step == "menu":
    S.update({'qi':0,'qans':{},'qq':[],'lt':'','is_loading':False, 'cq':set()})
    st.write(f"שלום, **{S.user}**. מה נלמד היום?")
    c1, c2 = st.columns(2)
    if c1.button("📚 שיעורים ולימוד"): S.step = "study"; st.rerun()
    if c2.button("⏱️ סימולציית מבחן"): S.step = "exam_lobby"; st.rerun()

# --- 3. לימוד ושיעורים (16 נושאים) ---
elif S.step == "study":
    all_t = [
        "חוק המתווכים במקרקעין", "תקנות המתווכים (פרטי הזמנה)", "תקנות המתווכים (נושאי בחינה)", 
        "חוק המקרקעין", "חוק המכר (דירות)", "חוק הגנת הצרכן", "חוק החוזים", 
        "חוק העונשין (פרקים רלוונטיים)", "חוק שמאי מקרקעין", "חוק התכנון והבנייה", 
        "חוק הגנת הדייר", "חוק המקרקעין (חיזוק מפני רעידות אדמה)", "פקודת הנזיקין", 
        "חוק הירושה", "חוק מיסוי מקרקעין", "חוק מקרקעי ישראל"
    ]
    
    if not S.lt:
        sel = st.selectbox("בחר נושא להעמקה:", all_t)
        c1, c2 = st.columns(2)
        if c1.button("📖 טען שיעור מפורט"):
            try:
                genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                model = genai.GenerativeModel('gemini-2.0-flash')
                res = model.generate_content(f"כתוב שיעור הכנה מפורט למבחן המתווכים בנושא {sel}. כלול סעיפי חוק, הגדרות ודוגמאות מעשיות.", stream=True)
                ph = st.empty()
                full_text = ""
                for chunk in res:
                    if chunk.text:
                        full_text += chunk.text
                        ph.markdown(f"<div class='lesson-box'>{full_text}</div>", unsafe_allow_html=True)
                S.lt, S.current_topic = full_text, sel
                st.rerun()
            except exceptions.ResourceExhausted:
                st.error("המערכת בעומס (מכסת גוגל). המתן 60 שניות ונסה שוב.")
            except Exception:
                st.error("קרתה שגיאה בטעינה.")
        if c2.button("🏠 חזרה לתפריט"): S.step = "menu"; st.rerun()
    else:
        st.markdown(f"<div class='lesson-box'>{S.lt}</div>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        if c1.button(f"✍️ בחן את עצמך בנושא {S.current_topic}"):
            with st.spinner("מייצר שאלות תרגול..."):
                d = fetch_exam_content(mode='study', topic=S.current_topic)
                if d: S.qq, S.qi, S.total_q, S.mode, S.step = d, 0, len(d), 'study_quiz', "quiz_mode"; st.rerun()
        if c2.button("🏁 סיום וחזרה"): S.lt = ""; S.step = "menu"; st.rerun()

# --- 4. לובי בחינה (מסך הסבר) ---
elif S.step == "exam_lobby":
    st.markdown("""
    <div class='lobby-card'>
    <h3>📋 הוראות לבחינת הסימולציה:</h3>
    <ul>
        <li>הבחינה מבוססת על שאלות ממועדי רשם המתווכים.</li>
        <li>משך הבחינה: <b>90 דקות</b>.</li>
        <li>מספר שאלות: <b>25 שאלות</b>.</li>
        <li>ציון עובר: <b>60</b>.</li>
        <li>במצב בחינה לא יינתן פידבק מיידי - התוצאות יוצגו בסיום בלבד.</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    if c1.button("🚀 התחל בחינה רנדומלית"):
        with st.spinner("דולה בחינה ממועדי רשם המתווכים..."):
            d = fetch_exam_content(mode='exam')
            if d:
                S.qq, S.qi, S.total_q, S.mode, S.step, S.start_time = d, 0, 25, 'exam', "quiz_mode", time.time()
                st.rerun()
    if c2.button("🏠 ביטול וחזרה"): S.step = "menu"; st.rerun()

# --- 5. מצב שאלון/בחינה (הלוגיקה המרכזית) ---
elif S.step == "quiz_mode":
    # טיימר למבחן
    if S.mode == 'exam':
        elapsed = int(time.time() - S.start_time)
        rem = max(0, 5400 - elapsed)
        h, r = divmod(rem, 3600); m, s = divmod(r, 60)
        st.markdown(f"<div style='text-align:
