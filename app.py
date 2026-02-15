# גרסה: 215 | תאריך: 2026-02-15 | שעה: 14:50 (Israel Time - GMT+2)

import streamlit as st
import google.generativeai as genai
import json, re, time

st.set_page_config(page_title="מתווך בקליק", layout="centered")

# CSS - עיצוב נקי, תמיכה ב-Dark Mode וסדר אלמנטים נכון
st.markdown("""<style>
* { direction: rtl !important; text-align: right !important; }
.lesson-box { 
    background-color: #ffffff !important; 
    color: #000000 !important; 
    padding: 25px; border-radius: 12px; border-right: 6px solid #1E88E5; 
    line-height: 1.8; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}
.lesson-box h1 { 
    color: #1E88E5 !important; font-size: 32px !important; font-weight: 900 !important; 
    border-bottom: 2px solid #eee; padding-bottom: 10px; margin-bottom: 15px; 
}
.explanation-box { padding: 15px; border-radius: 8px; margin: 15px 0; border-right: 5px solid; }
.success { background-color: #e8f5e9 !important; color: #2e7d32 !important; border-color: #4caf50 !important; }
.error { background-color: #ffebee !important; color: #c62828 !important; border-color: #f44336 !important; }
.timer-box { font-size: 18px; font-weight: bold; color: #d32f2f; text-align:center; background:#fff1f1; padding:10px; border-radius:10px; border:1px solid #d32f2f; margin-bottom:15px; }
div.stButton > button { width: 100%; border-radius: 8px; font-weight: bold; height: 3em; margin-top: 10px; }
.user-welcome { font-size: 28px; font-weight: bold; color: #1E88E5; }
.lobby-card { background: #f0f7ff !important; color: #000000 !important; padding: 30px; border-radius: 15px; border: 1px solid #d1e3f8; margin: 20px 0; }
</style>""", unsafe_allow_html=True)

S = st.session_state
if 'step' not in S:
    S.update({
        'user':'','step':'login','lt':'','qa':False,'qi':0,'qans':{},'qq':[],'cq':set(),
        'ei':0,'eans':{},'eq':[],'start_time':None, 'current_topic':'', 'is_loading': False
    })

def parse_j(t):
    try:
        m = re.search(r'\[\s*\{.*\}\s*\]', t, re.DOTALL)
        return json.loads(m.group()) if m else None
    except: return None

def get_questions(topic, count):
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        m = genai.GenerativeModel('gemini-2.0-flash')
        p = f"צור {count} שאלות למבחן המתווכים בנושא {topic}. החזר JSON נקי בלבד: "
        p += "[{'q':'','options':['א','ב','ג','ד'],'correct':'הטקסט המדויק מהאופציות','reason':''}]"
        r = m.generate_content(p)
        return parse_j(r.text)
    except: return None

def background_load():
    if len(S.eq) < 5 and not S.is_loading:
        S.is_loading = True
        new_qs = get_questions("דיני מקרקעין ותיווך בישראל", 5)
        if new_qs: S.eq.extend(new_qs)
        S.is_loading = False

st.title("🏠 מתווך בקליק")

# ניהול שלבי האפליקציה
if S.step == "login":
    u = st.text_input("שם מלא:")
    if st.button("כניסה למערכת"):
        if u:
            S.user, S.step = u, "menu"
            background_load()
            st.rerun()

elif S.step == "menu":
    st.markdown(f"<div class='user-welcome'>שלום, {S.user}</div>", unsafe_allow_html=True)
    if len(S.eq) < 5: background_load()
    c1, c2 = st.columns(2)
    if c1.button("📚 שיעורים ולימוד"):
        S.step, S.lt, S.qa = "study", "", False
        st.rerun()
    if c2.button("📝 סימולציית מבחן מלאה"):
        S.step = "exam_lobby"
        st.rerun()

elif S.step == "exam_lobby":
    st.markdown("<div class='lobby-card'><h2>📝 הכנה למבחן המלא</h2><p>25 שאלות מורכבות המדמות את המבחן האמיתי.</p></div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    if c1.button("🚀 התחל עכשיו"):
        S.ei, S.cq, S.start_time = 0, set(), time.time()
        S.step = "full_exam"
        st.rerun()
    if c2.button("🔙 חזרה"):
        S.step = "menu"
        st.rerun()

elif S.step == "study":
    all_t = ["חוק המתווכים", "חוק המקרקעין", "חוק החוזים", "חוק המכר", "הגנת הצרכן", "תכנון ובנייה", "מיסוי מקרקעין"]
    if not S.lt:
        sel = st.selectbox("בחר נושא:", all_t)
        c1, c2 = st.columns(2)
        if c1.button("📖 התחל שיעור"):
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            m = genai.GenerativeModel('gemini-2.0-flash')
            p = f"כתוב שיעור מפורט על {sel}. התחל בכותרת '# {sel}'."
            res = m.generate_content(p, stream=True)
            ph, full = st.empty(), ""
            for ch in res: 
                full += ch.text
                ph.markdown(f"<div class='lesson-box'>{full}</div>", unsafe_allow_html=True)
            S.lt, S.current_topic = full, sel
            st.rerun()
        if c2.button("🏠 חזרה לתפריט"):
            S.step = "menu"
            st.rerun()
    else:
        if not S.qa:
            st.markdown(f"<div class='lesson-box'>{S.lt}</div>", unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            if c1.button(f"✍️ בחן את עצמך על {S.current_topic}"):
                with st.spinner("מכין שאלות..."):
                    d = get_questions(S.current_topic, 10)
                    if d:
                        S.qq, S.qa, S.qi, S.cq = d, True, 0, set()
                        st.rerun()
            if c2.button("🔙 נושאים אחרים"):
                S.lt = ""
                st.rerun()
        else:
            # שאלון נושאי (10 שאלות)
            it = S.qq[S.qi]
            st.write(f"### שאלה {S.qi+1}/10")
            ans = st.radio(it['q'], it['options'], key=f"sq{S.qi}", index=None)
