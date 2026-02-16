# גרסה: 1040 | תאריך: 16/02/2026 | שעה: 10:00
# סטטוס: Minimal Flow - Direct Action on Button Press

import streamlit as st
import google.generativeai as genai
import json, re, time
from google.api_core import exceptions

st.set_page_config(page_title="מתווך בקליק", layout="centered")

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
    S.update({'user':'','step':'login','lt':'','qi':0,'qans':{},'qq':[],'total_q':25,'start_time':0,'current_topic':'','mode':'exam','cq':set()})

def fetch_exam_content(mode='study', topic='כללי'):
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-2.0-flash')
        if mode == 'exam':
            p = "בחר מועד רשמי של בחינת רשם המתווכים. שלוף 5 שאלות מורכבות. החזר JSON: [{'q':'','options':['א','ב','ג','ד'],'correct':'','reason':''}]"
        else:
            p = f"צור 10 שאלות תרגול למבחן המתווכים בנושא {topic}. החזר JSON: [{'q':'','options':['א','ב','ג','ד'],'correct':'','reason':''}]"
        
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
    all_t = ["חוק המתווכים במקרקעין", "תקנות המתווכים (פרטי הזמנה)", "תקנות המתווכים (נושאי בחינה)", "חוק המקרקעין", "חוק המכר (דירות)", "חוק הגנת הצרכן", "חוק החוזים", "חוק העונשין", "חוק שמאי מקרקעין", "חוק התכנון והבנייה", "חוק הגנת הדייר", "חוק המקרקעין (חיזוק מפני רעידות אדמה)", "פקודת הנזיקין", "חוק הירושה", "חוק מיסוי מקרקעין", "חוק מקרקעי ישראל"]
    
    if not S.lt:
        sel = st.selectbox("בחר נושא ללימוד:", all_t)
        if st.button("📖 התחל שיעור"):
            try:
                genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                model = genai.GenerativeModel('gemini-2.0-flash')
                res = model.generate_content(f"כתוב שיעור מפורט למבחן המתווכים בנושא {sel}.", stream=True)
                ph = st.empty()
                full_text = ""
                for chunk in res:
                    if chunk.text:
                        full_text += chunk.text
                        ph.markdown(f"<div class='lesson-box'>{full_text}</div>", unsafe_allow_html=True)
                S.lt, S.current_topic = full_text, sel
                st.rerun()
            except: st.error("שגיאה בטעינה.")
    else:
        st.markdown(f"<div class='lesson-box'>{S.lt}</div>", unsafe_allow_html=True)
        # שני הכפתורים שביקשת בסוף השיעור
        c1, c2 = st.columns(2)
        if c1.button("✍️ עבור לשאלון תרגול"):
            with st.spinner("מכין שאלות, אנא המתן..."):
                d = fetch_exam_content(mode='study', topic=S.current_topic)
                if d:
                    S.qq, S.qi, S.mode, S.step = d, 0, 'study_quiz', "quiz_mode"
                    st.rerun()
                else:
                    st.error("לא הצלחנו לטעון שאלות. נסה שוב בעוד כמה שניות.")
        if c2.button("🏁 חזרה לתפריט"): S.lt = ""; S.step = "menu"; st.rerun()

elif S.step == "exam_lobby":
    st.info("סימולציה: 25 שאלות | 90 דקות")
    c1, c2 = st.columns(2)
    if c1.button("🚀 התחל בחינה"):
        with st.spinner("מכין בחינה..."):
            d = fetch_exam_content(mode='exam')
            if d: S.qq, S.qi, S.mode, S.step, S.start_time = d, 0, 'exam', "quiz_mode", time.time(); st.rerun()
    if c2.button("🏠 חזרה"): S.step = "menu"; st.rerun()

elif S.step == "quiz_mode":
    if S.mode == 'exam':
        rem = max(0, 5400 - int(time.time() - S.start_time))
        h, r = divmod(rem, 3600); m, s = divmod(r, 60)
        st.markdown(f"<div style='text-align:center; color:red; font-size:20px; font-weight:bold;'>⏳ {h:02d}:{m:02d}:{s:02d}</div>", unsafe_allow_html=True)

    it = S.qq[S.qi]
    st.markdown(f"<div class='question-card'><b>שאלה {S.qi+1}:</b><br>{it['q']}</div>", unsafe_allow_html=True)
    ans = st.radio("תשובות:", it['options'], key=f"q_{S.qi}", index=it['options'].index(S.qans[S.qi]) if S.qi in S.qans else None)
    if ans: S.qans[S.qi] = ans

    if S.mode == 'study_quiz' and S.qi in S.cq:
        if S.qans.get(S.qi) == it['correct']: st.success(f"נכון! {it.get('reason','')}")
        else: st.error(f"טעות. הנכון: {it['correct']}. {it.get('reason','')}")

    c1, c2, c3 = st.columns(3)
    if S.qi > 0 and c1.button("⬅️ הקודם"): S.qi -= 1; st.rerun()
    if c2.button("🏠 תפריט"): S.step = "menu"; st.rerun()
    if S.mode == 'study_quiz' and S.qi not in S.cq:
        if c3.button("🔍 בדוק"): S.cq.add(S.qi); st.rerun()
    elif S.qi < len(S.qq) - 1:
        if c3.button("הבא ➡️"): S.qi += 1; st.rerun()
    else:
        if c3.button("🏁 סיום"): S.step = "results"; st.rerun()

elif S.step == "results":
    correct = sum(1 for i, q in enumerate(S.qq) if S.qans.get(i) == q['correct'])
    st.markdown(f"<div class='main-header'>ציון: {int((correct/len(S.qq))*100)}</div>", unsafe_allow_html=True)
    if st.button("🏠 חזרה"): S.step = "menu"; st.rerun()
