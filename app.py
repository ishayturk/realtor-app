# גרסה: 1016 | תאריך: 15/02/2026 | שעה: 23:10
import streamlit as st
import google.generativeai as genai
import json, re, time

st.set_page_config(page_title="מתווך בקליק", layout="centered")

st.markdown("""
<style>
    * { direction: rtl !important; text-align: right !important; }
    .stProgress > div > div > div > div { background-color: #1E88E5; }
    .lesson-box { background-color: #ffffff; padding: 25px; border-radius: 12px; border-right: 6px solid #1E88E5; line-height: 1.8; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    .question-card { background-color: #ffffff; padding: 25px; border-radius: 12px; border: 1px solid #e0e0e0; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .explanation-box { padding: 15px; border-radius: 8px; margin: 10px 0; border-right: 5px solid; font-size: 14px; }
    .success { background-color: #e8f5e9 !important; color: #2e7d32 !important; border-color: #4caf50 !important; }
    .error { background-color: #ffebee !important; color: #c62828 !important; border-color: #f44336 !important; }
    .timer-box { background: #fdf2f2; color: #d32f2f; padding: 10px; border-radius: 10px; text-align: center; font-weight: bold; margin-bottom: 20px; }
    .main-header { background: #1E88E5; color: white; padding: 15px; border-radius: 10px; text-align: center; margin-bottom: 10px; font-size: 24px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

S = st.session_state
if 'step' not in S:
    S.update({'user':'','step':'login','lt':'','qi':0,'qans':{},'qq':[],'total_q':10, 'start_time':0, 'is_loading': False, 'current_topic':'', 'mode': 'study_quiz', 'cq': set()})

def fetch_chunk(topic, count=5):
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-2.0-flash')
        p = f"צור {count} שאלות אמריקאיות למבחן המתווכים בנושא {topic}. JSON נקי: [{{'q':'','options':['א','ב','ג','ד'],'correct':'טקסט מדויק','reason':''}}]"
        r = model.generate_content(p)
        m = re.search(r'\[.*\]', r.text, re.DOTALL)
        return json.loads(m.group()) if m else []
    except: return []

st.markdown("<div class='main-header'>🏠 מתווך בקליק</div>", unsafe_allow_html=True)
if S.user:
    st.markdown(f"<div style='text-align: center; margin-bottom: 20px;'>שלום, <b>{S.user}</b></div>", unsafe_allow_html=True)

if S.step == "login":
    u = st.text_input("הזן שם מלא:", key="login_input")
    if st.button("כניסה"):
        if u: S.user = u; S.step = "menu"; st.rerun()

elif S.step == "menu":
    S.update({'qi':0,'qans':{},'qq':[],'lt':'','is_loading':False, 'cq':set()})
    c1, c2 = st.columns(2)
    if c1.button("📚 שיעורים ולימוד"): S.step = "study"; st.rerun()
    if c2.button("⏱️ סימולציית מבחן"): S.step = "exam_lobby"; st.rerun()

elif S.step == "study":
    all_t = ["חוק המתווכים במקרקעין", "חוק המקרקעין", "חוק החוזים", "חוק המכר (דירות)", "חוק הגנת הצרכן"]
    if not S.lt:
        sel = st.selectbox("בחר נושא:", all_t)
        if st.button("📖 התחל שיעור"):
            with st.spinner("מכין שיעור..."):
                genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                model = genai.GenerativeModel('gemini-2.0-flash')
                res = model.generate_content(f"כתוב שיעור מפורט למבחן המתווכים על {sel}")
                S.lt, S.current_topic = res.text, sel; st.rerun()
        if st.button("🏠 חזרה"): S.step = "menu"; st.rerun()
    else:
        st.markdown(f"<div class='lesson-box'>{S.lt}</div>", unsafe_allow_html=True)
        if st.button(f"✍️ שאלון תרגול על {S.current_topic}"):
            with st.spinner("טוען שאלות..."):
                d = fetch_chunk(S.current_topic, 5)
                if d: S.qq, S.qi, S.total_q, S.mode, S.step = d, 0, 10, 'study_quiz', "quiz_mode"; st.rerun()
        if st.button("🏁 חזרה לתפריט"): S.lt = ""; S.step = "menu"; st.rerun()

elif S.step == "exam_lobby":
    if st.button("🚀 התחל בחינה (25 שאלות)"):
        with st.spinner("מכין שאלות..."):
            d = fetch_chunk("כללי", 5)
            if d: S.qq, S.qi, S.total_q, S.mode, S.step, S.start_time = d, 0, 25, 'exam', "quiz_mode", time.time(); st.rerun()

elif S.step == "quiz_mode":
    if S.mode == 'exam':
        rem = max(0, 5400 - int(time.time() - S.start_time))
        h, r = divmod(rem, 3600); m, s = divmod(r, 60)
        st.markdown(f"<div class='timer-box'>⏳ זמן נותר: {h:02d}:{m:02d}:{s:02d}</div>", unsafe_allow_html=True)

    # טעינה ברקע - רק אם חסר לנו שאלות עד היעד
    if len(S.qq) < S.total_q and S.qi >= len(S.qq) - 2 and not S.is_loading:
        S.is_loading = True
        more = fetch_chunk(S.current_topic if S.mode == 'study_quiz' else "דיני מקרקעין", 5)
        if more: S.qq.extend(more)
        S.is_loading = False

    st.progress(min((S.qi + 1) / S.total_q, 1.0))
    it = S.qq[S.qi]
    st.markdown(f"<div class='question-card'><b>שאלה {S.qi+1}:</b><br>{it['q']}</div>", unsafe_allow_html=True)
    
    curr = S.qans.get(S.qi, None)
    ans = st.radio("בחר תשובה:", it['options'], key=f"q_{S.qi}", index=it['options'].index(curr) if curr in it['options'] else None)
    if ans: S.qans[S.qi] = ans

    if S.mode == 'study_quiz' and S.qi in S.cq:
        corr = it['correct'].strip()
        if S.qans.get(S.qi) == corr:
            st.markdown(f"<div class='explanation-box success'>✅ <b>נכון!</b> {it['reason']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='explanation-box error'>❌ <b>טעות.</b> התשובה: {corr}<br>{it['reason']}</div>", unsafe_allow_html=True)

    st.write("---")
    c1, c2, c3 = st.columns(3)
    
    # ניווט קודם
    if S.qi > 0:
        if c1.button("⬅️ הקודם"): S.qi -= 1; st.rerun()

    # אמצע
    if c2.button("🏠 תפריט"): S.step = "menu"; st.rerun()

    # ניווט הבא / בדוק
    if S.mode == 'study_quiz' and S.qi not in S.cq:
        if c3.button("🔍 בדוק"): S.cq.add(S.qi); st.rerun()
    elif S.qi < S.total_q - 1:
        if c3.button("הבא ➡️"):
            if S.qi < len(S.qq) - 1: S.qi += 1; st.rerun()
            else: st.warning("טוען את השאלות הבאות...")
    else:
        if c3.button("🏁 סיום"): S.step = "results"; st.rerun()

elif S.step == "results":
    correct = sum(1 for i, q in enumerate(S.qq) if S.qans.get(i) == q['correct'])
    st.markdown(f"<div class='main-header'>ציון: {int((correct/len(S.qq))*100)}</div>", unsafe_allow_html=True)
    if st.button("🏠 תפריט"): S.step = "menu"; st.rerun()
