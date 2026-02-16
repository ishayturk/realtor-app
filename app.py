import streamlit as st
import google.generativeai as genai
import json, re

st.set_page_config(page_title="מתווך בקליק", layout="centered")

st.markdown("<style>* {direction: rtl; text-align: right;} .welcome-text {color: #1E88E5; font-size: 2.2rem; font-weight: bold;} .lesson-box {background: #f9f9f9; padding: 25px; border-right: 6px solid #1E88E5; line-height: 1.8;}</style>", unsafe_allow_html=True)

S = st.session_state
for k in ['step','user','subs','lt','topic','sub_n','qq','qi','score','ans_d']:
    if k not in S:
        if k in ['score','qi']: S[k] = 0
        elif k == 'ans_d': S[k] = False
        elif k in ['subs','qq']: S[k] = []
        elif k == 'step': S[k] = 'login'
        else: S[k] = ''

def ask_ai(p):
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    m = genai.GenerativeModel('gemini-2.0-flash')
    try:
        return m.generate_content(p).text
    except: return None

T_MAP = {
    "חוק המתווכים": ["דרישת הכתב", "פעולה יעילה", "בלעדיות"],
    "חוק המקרקעין": ["בעלות ושיתוף", "רישום בטאבו", "הערות אזהרה"],
    "חוק המכר": ["מפרט המכר", "תקופת בדק", "הבטחת השקעות"],
    "מיסוי": ["מס שבח", "מס רכישה", "פטורים"],
    "אתיקה": ["הגינות וזהירות", "ניגוד עניינים", "פרסום"],
    "חוזים": ["כריתת חוזה", "פגמים", "תרופות"],
    "תכנון ובנייה": ["מוסדות תכנון", "היתרים", "היטל השבחה"]
}

st.title("🏠 מתווך בקליק")

if S.step == 'login':
    u = st.text_input("שם מלא:")
    if st.button("כניסה"):
        if u: S.user=u; S.step='menu'; st.rerun()

elif S.step == 'menu':
    st.markdown(f"<p class='welcome-text'>שלום, {S.user}</p>", unsafe_allow_html=True)
    if st.button("📚 לימוד לפי נושאים"): S.step='study'; st.rerun()
    if st.button("⏱️ סימולציה"): S.topic="כללי"; S.step='q_prep'; st.rerun()

elif S.step == 'study':
    sel = st.selectbox("נושא:", ["בחר..."] + list(T_MAP.keys()))
    if sel != "בחר..." and st.button("📖 כניסה לשיעור"):
        S.subs=T_MAP[sel]; S.topic=sel; S.lt=""; st.rerun()
    if S.subs:
        st.write("---")
        cols = st.columns(len(S.subs))
        for i, s in enumerate(S.subs):
            if cols[i].button(s, key=f"b{i}"):
                with st.spinner(f"טוען {s}..."):
                    res = ask_ai(f"שיעור מפורט על {s} למבחן המתווכים כולל סעיפי חוק ודוגמה.")
                    if res: S.lt=res; S.sub_n=s; st.rerun()
    if S.lt:
        st.markdown(f"## {S.sub_n}")
        st.markdown(f"<div class='lesson-box'>{S.lt}</div>", unsafe_allow_html=True)
        if st.button("✍️ תרגול שאלות בנושא זה"): S.step='q_prep'; st.rerun()
    if st.button("🏠 חזרה"): S.step='menu'; S.subs=[]; S.lt=""; st.rerun()

elif S.step == 'q_prep':
    with st.spinner(f"מכין שאלות על {S.topic}..."):
        p = f"צור 10 שאלות על {S.topic}. החזר JSON: " + "[{'q':'','options':['','','',''],'correct':'','reason':''}]"
        res = ask_ai(p)
        if res:
            m = re.search(r'\[.*\]', res, re.DOTALL)
            if m: S.qq=json.loads(m.group()); S.qi=0; S.score=0; S.ans_d=False; S.step='quiz'; st.rerun()
    S.step='menu'; st.rerun()

elif S.step == 'quiz':
    q = S.qq[S.qi]
    st.info(f"שאלה {S.qi+1}/10: {q['q']}")
    ans = st.radio("תשובה:", q['options'], key=f"r{S.qi}", index=None, disabled=S.ans_d)
    if st.button("🔍 בדוק", disabled=S.ans_d):
        if ans: S.ans_d=True; st.rerun()
    if S.ans_d:
        if ans == q['correct']:
            st.success(f"נכון! {q['reason']}")
            if not hasattr(S, 'l_qi') or S.l_qi != S.qi: S.score += 1; S.l_qi = S.qi
        else: st.error(f"טעות. הנכון: {q['correct']}. {q['reason']}")
        if st.button("הבא ➡️" if S.qi < 9 else "סיום"):
            if S.qi < 9: S.qi += 1; S.ans_d = False; st.rerun()
            else: S.step = 'results'; st.rerun()

elif S.step == 'results':
    st.balloons()
    st.metric("ציון", f"{S.score*10}%", f"{S.score}/10")
    if st.button("🏠 תפריט"): S.step='menu'; S.qq=[]; st.rerun()
