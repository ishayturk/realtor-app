# גרסה: 1044 | מבוססת על 1030 יציבה | תיקון רשימת נושאים וסינטקס

import streamlit as st
import google.generativeai as genai
import json, re, time

st.set_page_config(page_title="מתווך בקליק", layout="centered")

# עיצוב UI מקורי (מיושר לימין)
st.markdown("""
<style>
    * { direction: rtl !important; text-align: right !important; }
    .lesson-box { background-color: #fdfdfd; padding: 25px; border-radius: 12px; border-right: 6px solid #1E88E5; line-height: 1.8; margin-bottom: 20px; }
    .question-card { background-color: #ffffff; padding: 25px; border-radius: 12px; border: 1px solid #e0e0e0; margin-bottom: 20px; }
    .main-header { background: #1E88E5; color: white; padding: 15px; border-radius: 10px; text-align: center; margin-bottom: 15px; font-size: 24px; }
</style>
""", unsafe_allow_html=True)

S = st.session_state
if 'step' not in S:
    S.update({'user':'','step':'login','lt':'','qi':0,'qans':{},'qq':[],'current_topic':'','mode':'exam','cq':set()})

def fetch_exam_content(mode='study', topic='כללי'):
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-2.0-flash')
        if mode == 'exam':
            p = "בחר מועד רשמי של בחינת רשם המתווכים. שלוף 5 שאלות מורכבות. JSON נקי: [{'q':'','options':['א','ב','ג','ד'],'correct':'','reason':''}]"
        else:
            p = f"צור 10 שאלות תרגול למבחן המתווכים בנושא {topic}. JSON נקי: [{'q':'','options':['א','ב','ג','ד'],'correct':'','reason':''}]"
        
        r = model.generate_content(p)
        m = re.search(r'\[.*\]', r.text, re.DOTALL)
        return json.loads(m.group()) if m else []
    except:
        return []

st.markdown("<div class='main-header'>🏠 מתווך בקליק</div>", unsafe_allow_html=True)

if S.step == "login":
    u = st.text_input("שם מלא:", key="login_input")
    if st.button("כניסה"):
        if u: S.user = u; S.step = "menu"; st.rerun()

elif S.step == "menu":
    S.update({'qi':0,'qans':{},'qq':[],'lt':'','cq':set()})
    c1, c2 = st.columns(2)
    if c1.button("📚 שיעורים ולימוד"): S.step = "study"; st.rerun()
    if c2.button("⏱️ סימולציית מבחן"): S.step = "exam_lobby"; st.rerun()

elif S.step == "study":
    # הרשימה המלאה שהייתה חסרה
    all_t = [
        "חוק המתווכים במקרקעין", "תקנות המתווכים (פרטי הזמנה)", "תקנות המתווכים (נושאים)", 
        "חוק המקרקעין", "חוק המכר (דירות)", "חוק הגנת הצרכן", "חוק החוזים", 
        "חוק העונשין", "חוק שמאי מקרקעין", "חוק התכנון והבנייה", "חוק הגנת הדייר", 
        "חוק המקרקעין (תמ\"א 38)", "פקודת הנזיקין", "חוק הירושה", "חוק מיסוי מקרקעין", 
        "חוק מקרקעי ישראל", "חוק רישום קבלנים"
    ]
    
    if not S.lt:
        sel = st.selectbox("בחר נושא ללימוד:", all_t)
        if st.button("📖 התחל שיעור"):
            try:
                genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                model = genai.GenerativeModel('gemini-2.0-flash')
                res = model.generate_content(f"כתוב שיעור מקיף למבחן המתווכים בנושא {sel}.", stream=True)
                ph = st.empty()
                full_text = ""
                for chunk in res:
                    if chunk.text:
                        full_text += chunk.text
                        ph.markdown(f"<div class='lesson-box'>{full_text}</div>", unsafe_allow_html=True)
                S.lt, S.current_topic = full_text, sel
                st.rerun()
            except: st.error("חלה שגיאה בטעינה.")
    else:
        st.markdown(f"<div class='lesson-box'>{S.lt}</div>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        if c1.button("✍️ עבור לשאלון תרגול"):
            with st.spinner("מכין שאלות, המשתמש מחכה..."):
                d = fetch_exam_content(mode='study', topic=S.current_topic)
                if d:
                    S.qq, S.qi, S.mode, S.step = d, 0, 'study_quiz', "quiz_mode"
                    st.rerun()
        if c2.button("🏠 חזרה לתפריט"): S.lt = ""; S.step = "menu"; st.rerun()

elif S.step == "exam_lobby":
    st.info("סימולציה: 25 שאלות | 90 דקות")
    c1, c2 = st.columns(2)
    if c1.button("🚀 התחל בחינה"):
        with st.spinner("טוען שאלות..."):
            d = fetch_exam_content(mode='exam')
            if d: S.qq, S.qi, S.mode, S.step = d, 0, 'exam', "quiz_mode"; st.rerun()
    if c2.button("🏠 חזרה"): S.step = "menu"; st.rerun()

elif S.step == "quiz_mode":
    it = S.qq[S.qi]
    st.markdown(f"<div class='question-card'><b>שאלה {S.qi+1}:</b><br>{it['q']}</div>", unsafe_allow_html=True)
    ans = st.radio("בחר תשובה:", it['options'], key=f"q_{S.qi}")
    
    c1, c2, c3 = st.columns(3)
    if c1.button("🔍 בדוק"):
        if ans == it['correct']: st.success(f"נכון! {it.get('reason','')}")
        else: st.error(f"טעות. הנכון הוא {it['correct']}. {it.get('reason','')}")
    
    if c2.button("הבא ➡️"):
        if S.qi < len(S.qq) - 1:
            S.qi += 1
            st.rerun()
        else:
            S.step = "results"
            st.rerun()
    if c3.button("🏠 תפריט"): S.step = "menu"; st.rerun()

elif S.step == "results":
    st.markdown("<div class='main-header'>סיימת את השאלון!</div>", unsafe_allow_html=True)
    if st.button("🏠 חזרה לתפריט הראשי"): S.step = "menu"; st.rerun()
