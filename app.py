# גרסה: 1030 | חזרה לבסיס הבוקר המקורי

import streamlit as st
import google.generativeai as genai
import json, re, time

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
    S.update({'user':'','step':'login','lt':'','qi':0,'qans':{},'qq':[],'current_topic':'','mode':'exam'})

def fetch_exam_content(mode='study', topic='כללי'):
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-2.0-flash')
        if mode == 'exam':
            p = "בחר מועד רשמי של בחינת רשם המתווכים. שלוף 5 שאלות. JSON נקי: [{'q':'','options':['א','ב','ג','ד'],'correct':'','reason':''}]"
        else:
            p = f"צור 10 שאלות על {topic}. JSON נקי: [{'q':'','options':['א','ב','ג','ד'],'correct':'','reason':''}]"
        r = model.generate_content(p)
        m = re.search(r'\[.*\]', r.text, re.DOTALL)
        return json.loads(m.group()) if m else []
    except: return []

st.markdown("<div class='main-header'>🏠 מתווך בקליק</div>", unsafe_allow_html=True)

if S.step == "login":
    u = st.text_input("שם מלא:")
    if st.button("כניסה"):
        if u: S.user = u; S.step = "menu"; st.rerun()

elif S.step == "menu":
    c1, c2 = st.columns(2)
    if c1.button("📚 שיעורים ולימוד"): S.step = "study"; st.rerun()
    if c2.button("⏱️ סימולציית מבחן"): S.step = "exam_lobby"; st.rerun()

elif S.step == "study":
    all_t = ["חוק המתווכים במקרקעין", "חוק המקרקעין", "חוק החוזים"]
    if not S.lt:
        sel = st.selectbox("בחר נושא:", all_t)
        if st.button("📖 התחל שיעור"):
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            model = genai.GenerativeModel('gemini-2.0-flash')
            res = model.generate_content(f"כתוב שיעור על {sel}", stream=True)
            ph = st.empty()
            full_text = ""
            for chunk in res:
                if chunk.text:
                    full_text += chunk.text
                    ph.markdown(f"<div class='lesson-box'>{full_text}</div>", unsafe_allow_html=True)
            S.lt, S.current_topic = full_text, sel
            st.rerun()
    else:
        st.markdown(f"<div class='lesson-box'>{S.lt}</div>", unsafe_allow_html=True)
        if st.button("✍️ עבור לשאלון תרגול"):
            d = fetch_exam_content(mode='study', topic=S.current_topic)
            if d: S.qq, S.qi, S.step = d, 0, "quiz_mode"; st.rerun()

elif S.step == "quiz_mode":
    it = S.qq[S.qi]
    st.markdown(f"<div class='question-card'>{it['q']}</div>", unsafe_allow_html=True)
    ans = st.radio("תשובות:", it['options'], key=f"q_{S.qi}")
    if st.button("🔍 בדוק"):
        if ans == it['correct']: st.success("נכון!")
        else: st.error(f"טעות. הנכון: {it['correct']}")
    if st.button("הבא ➡️"):
        if S.qi < len(S.qq)-1: S.qi += 1; st.rerun()
        else: S.step = "menu"; st.rerun()
