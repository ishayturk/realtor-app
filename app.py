# גרסה: 1009 | תאריך: 15/02/2026 | שעה: 22:15
import streamlit as st
import google.generativeai as genai
import json, re

st.set_page_config(page_title="מתווך בקליק", layout="centered")

# CSS מקצועי - מבטיח RTL ומראה אחיד
st.markdown("""
<style>
    * { direction: rtl !important; text-align: right !important; }
    .stProgress > div > div > div > div { background-color: #1E88E5; }
    .lesson-box { background-color: #ffffff; color: #000; padding: 25px; border-radius: 12px; border-right: 6px solid #1E88E5; line-height: 1.8; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    .question-card { background-color: #f8f9fa; padding: 20px; border-radius: 10px; border: 1px solid #dee2e6; margin-bottom: 20px; font-weight: bold; }
    .explanation-box { padding: 15px; border-radius: 8px; margin: 10px 0; border-right: 5px solid; font-weight: normal; }
    .success { background-color: #e8f5e9 !important; color: #2e7d32 !important; border-color: #4caf50 !important; }
    .error { background-color: #ffebee !important; color: #c62828 !important; border-color: #f44336 !important; }
    div.stButton > button { width: 100%; border-radius: 8px; font-weight: bold; height: 3em; }
    .main-header { background: #1E88E5; color: white; padding: 15px; border-radius: 10px; text-align: center; margin-bottom: 20px; font-size: 24px; }
</style>
""", unsafe_allow_html=True)

S = st.session_state
if 'step' not in S:
    S.update({'user':'','step':'login','lt':'','qa':False,'qi':0,'qans':{},'qq':[],'cq':set(),'current_topic':'','total_q':10, 'loading_more': False})

def get_questions(topic, count):
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-2.0-flash')
        p = f"צור {count} שאלות למבחן המתווכים בנושא {topic}. רמה גבוהה, JSON נקי בלבד: [{{'q':'','options':['א','ב','ג','ד'],'correct':'טקסט מדויק','reason':''}}]"
        r = model.generate_content(p)
        m = re.search(r'\[.*\]', r.text, re.DOTALL)
        return json.loads(m.group()) if m else None
    except: return None

# --- Header קבוע ---
st.markdown("<div class='main-header'>🏠 מתווך בקליק</div>", unsafe_allow_html=True)
if S.user:
    st.markdown(f"<h3 style='text-align: center;'>שלום, {S.user}</h3>", unsafe_allow_html=True)

# --- ניווט דפים ---
if S.step == "login":
    u = st.text_input("הזן שם מלא:", key="login_input")
    if st.button("כניסה למערכת"):
        if u: S.user = u; S.step = "menu"; st.rerun()

elif S.step == "menu":
    S.lt, S.qa, S.qi, S.qq, S.cq = "", False, 0, [], set()
    c1, c2 = st.columns(2)
    if c1.button("📚 שיעורים בנושאי הלימוד"): S.step = "study"; st.rerun()
    if c2.button("📝 סימולציית מבחן רשמית"): S.step = "exam_lobby"; st.rerun()

elif S.step == "study":
    all_t = ["חוק המתווכים במקרקעין", "חוק המקרקעין", "חוק החוזים", "חוק המכר (דירות)", "חוק הגנת הצרכן", "חוק הגנת הדייר", "חוק תכנון ובנייה", "חוק מיסוי מקרקעין", "חוק ההוצאה לפועל", "חוק הירושה", "חוק העונשין", "אתיקה מקצועית"]
    if not S.lt:
        sel = st.selectbox("בחר נושא:", all_t)
        if st.button("📖 התחל שיעור"):
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            model = genai.GenerativeModel('gemini-2.0-flash')
            res = model.generate_content(f"כתוב שיעור מפורט למבחן המתווכים על {sel}", stream=True)
            ph, full = st.empty(), ""
            for ch in res:
                full += ch.text
                ph.markdown(f"<div class='lesson-box'>{full}</div>", unsafe_allow_html=True)
            S.lt, S.current_topic = full, sel; st.rerun()
        if st.button("🏠 תפריט"): S.step = "menu"; st.rerun()
    else:
        st.markdown(f"<div class='lesson-box'>{S.lt}</div>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        if c1.button(f"✍️ שאלון תרגול: {S.current_topic}"):
            with st.spinner("טוען שאלות..."):
                d = get_questions(S.current_topic, 10)
                if d: S.qq, S.qi, S.cq, S.total_q, S.step = d, 0, set(), 10, "quiz_mode"; st.rerun()
        if c2.button("🏁 חזרה"): S.lt = ""; st.rerun()

elif S.step == "exam_lobby":
    st.write("### סימולציית מבחן (25 שאלות)")
    if st.button("🚀 התחל מבחן"):
        with st.spinner("מכין שאלות..."):
            d = get_questions("מעורב: מתווכים, מקרקעין, חוזים", 5)
            if d: S.qq, S.qi, S.cq, S.total_q, S.step = d, 0, set(), 25, "quiz_mode"; st.rerun()
    if st.button("🏠 חזרה"): S.step = "menu"; st.rerun()

elif S.step == "quiz_mode":
    st.progress((S.qi + 1) / S.total_q)
    it = S.qq[S.qi]
    st.markdown(f"<div class='question-card'>שאלה {S.qi+1}: {it['q']}</div>", unsafe_allow_html=True)
    ans = st.radio("בחר תשובה:", it['options'], key=f"q_{S.qi}", index=None)
    
    if len(S.qq) - S.qi <= 2 and len(S.qq) < S.total_q and not S.loading_more:
        S.loading_more = True
        more = get_questions("דיני מקרקעין", 5)
        if more: S.qq.extend(more)
        S.loading_more = False

    if S.qi in S.cq:
        corr = str(it['correct']).strip()
        u_ans = str(S.qans.get(S.qi)).strip()
        if u_ans == corr:
            st.markdown(f"<div class='explanation-box success'><b>נכון!</b><br>{it['reason']}</div>", unsafe_allow_html=True)
        else:
            try: idx = it['options'].index(corr) + 1
            except: idx = "?"
            st.markdown(f"<div class='explanation-box error'><b>טעות.</b> תשובה {idx} היא הנכונה.<br>{it['reason']}</div>", unsafe_allow_html=True)

    st.write("---")
    c1, c2, c3 = st.columns(3)
    if ans and S.qi not in S.cq:
        if c1.button("🔍 בדוק"): S.qans[S.qi] = ans; S.cq.add(S.qi); st.rerun()
    if S.qi in S.cq:
        if S.qi < S.total_q - 1:
            if c2.button("➡️ השאלה הבאה"): S.qi += 1; st.rerun()
        else:
            if c2.button("🏁 סיום"): S.step = "menu"; st.rerun()
    if c3.button("🏠 תפריט"): S.step = "menu"; st.rerun()
