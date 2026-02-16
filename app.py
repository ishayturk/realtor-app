# גרסה 1053 | 16/02/2026 | 09:10

import streamlit as st
import google.generativeai as genai
import json, re, time

st.set_page_config(page_title="מתווך בקליק", layout="centered")

# עיצוב UI וממשק
st.markdown("""
<style>
    * { direction: rtl !important; text-align: right !important; }
    .lesson-box { background-color: #fdfdfd; padding: 25px; border-radius: 12px; border-right: 6px solid #1E88E5; line-height: 1.8; margin-bottom: 20px; }
    .question-card { background-color: #ffffff; padding: 25px; border-radius: 12px; border: 1px solid #e0e0e0; margin-bottom: 20px; }
    .main-header { background: #1E88E5; color: white; padding: 15px; border-radius: 10px; text-align: center; margin-bottom: 15px; font-size: 24px; }
    .welcome-box { background-color: #e3f2fd; padding: 15px; border-radius: 8px; border: 1px solid #90caf9; margin-bottom: 20px; text-align: center !important; }
</style>
""", unsafe_allow_html=True)

S = st.session_state
if 'step' not in S:
    S.update({'user':'','step':'login','lt':'','qi':0,'qans':{},'qq':[],'current_topic':'','mode':'exam'})

# פונקציה לשליפת שאלות
def fetch_exam_content(mode='study', topic='כללי'):
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-2.0-flash')
        base_prompt = "התבסס על חומרי הלימוד הרשמיים של רשם המתווכים 2026 (חלק א, ב ותקנות האתיקה)."
        if mode == 'exam':
            p = f"{base_prompt} שלוף 5 שאלות רב-ברירה. JSON נקי בלבד: [{'q':'','options':['א','ב','ג','ד'],'correct':'','reason':''}]"
        else:
            p = f"{base_prompt} צור 10 שאלות תרגול בנושא {topic}. JSON נקי בלבד: [{'q':'','options':['א','ב','ג','ד'],'correct':'','reason':''}]"
        r = model.generate_content(p)
        m = re.search(r'\[.*\]', r.text, re.DOTALL)
        return json.loads(m.group()) if m else []
    except Exception as e:
        return []

st.markdown("<div class='main-header'>🏠 מתווך בקליק</div>", unsafe_allow_html=True)

if S.step == "login":
    u = st.text_input("שם מלא:")
    if st.button("כניסה"):
        if u: 
            S.user = u
            S.step = "menu"
            st.rerun()

elif S.step == "menu":
    st.markdown(f"### שלום, {S.user} 👋")
    st.markdown("""
    <div class='welcome-box'>
    ברוכים הבאים למערכת ההכנה המעודכנת לבחינת רשם המתווכים (2026).<br>
    כאן תוכלו ללמוד את חומרי הלימוד הרשמיים, לתרגל שאלות ממוקדות ולבצע סימולציות בחינה.<br>
    <b>מומלץ לבחור נושא ללימוד לפני שמתחילים בתרגול. בהצלחה!</b>
    </div>
    """, unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    if c1.button("📚 שיעורים ולימוד", use_container_width=True): 
        S.step = "study"
        st.rerun()
    if c2.button("⏱️ סימולציית מבחן", use_container_width=True): 
        S.step = "exam_lobby"
        st.rerun()

elif S.step == "study":
    all_t = [
        "חוק המתווכים במקרקעין", "תקנות המתווכים (פרטי הזמנה)", "תקנות המתווכים (נושאי בחינה)", 
        "אתיקה מקצועית", "חוק המקרקעין", "חוק המכר (דירות)", "חוק הגנת הצרכן", 
        "חוק החוזים", "חוק העונשין", "חוק שמאי מקרקעין", "חוק התכנון והבנייה", 
        "חוק הגנת הדייר", "חוק המקרקעין (חיזוק מפני רעידות אדמה)", "פקודת הנזיקין", 
        "חוק הירושה", "חוק מיסוי מקרקעין", "חוק מקרקעי ישראל"
    ]
    if not S.lt:
        sel = st.selectbox("בחר נושא ללימוד:", all_t)
        c1, c2 = st.columns(2)
        if c1.button("📖 התחל שיעור", use_container_width=True):
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            model = genai.GenerativeModel('gemini-2.0-flash')
            res = model.generate_content(f"כתוב שיעור מקיף ומעודכן ל-2026 על {sel} בהתבסס על חומרי רשם המתווכים.", stream=True)
            ph = st.empty()
            full_text = ""
            for chunk in res:
                if chunk.text:
                    full_text += chunk.text
                    ph.markdown(f"<div class='lesson-box'>{full_text}</div>", unsafe_allow_html=True)
            S.lt, S.current_topic = full_text, sel
            st.rerun()
        if c2.button("🏠 חזרה לתפריט", use_container_width=True): 
            S.step = "menu"
            st.rerun()
    else:
        st.markdown(f"<div class='lesson-box'>{S.lt}</div>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        if c1.button("✍️ עבור לשאלון תרגול", use_container_width=True):
            with st.spinner("מכין שאלות מעודכנות..."):
                d = fetch_exam_content(mode='study', topic=S.current_topic)
                if d: 
                    S.qq, S.qi, S.step = d, 0, "quiz_mode"
                    st.rerun()
        if c2.button("🏠 חזרה", use_container_width=True): 
            S.lt = ""
            S.step = "menu"
            st.rerun()

elif S.step == "quiz_mode":
    if S.qq:
        it = S.qq[S.qi]
        st.markdown(f"<div class='question-card'><b>שאלה {S.qi+1}:</b><br>{it['q']}</div>", unsafe_allow_html=True)
        ans = st.radio("בחר תשובה:", it['options'], key=f"q_{S.qi}")
        c1, c2 = st.columns(2)
        if c1.button("🔍 בדוק", use_container_width=True):
            if ans == it['correct']: st.success(f"נכון! {it.get('reason','')}")
            else: st.error(f"טעות. התשובה הנכונה היא: {it['correct']}")
        if c2.button("הבא ➡️", use_container_width=True):
            if S.qi < len(S.qq)-1: 
                S.qi += 1
                st.rerun()
            else: 
                S.step = "menu"
                st.rerun()
    else:
        st.error("לא נמצאו שאלות.")
        if st.button("חזרה לתפריט"):
            S.step = "menu"
            st.rerun()
