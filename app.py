import streamlit as st
import google.generativeai as genai
import json, re, time

st.set_page_config(page_title="מתווך בקליק", layout="centered")
st.markdown("""<style>
* { direction: rtl !important; text-align: right !important; }
.lesson-box { background:#fdfdfd; padding:20px; border-radius:12px; border-right:6px solid #1E88E5; line-height:1.8; margin-bottom:20px; }
.explanation-box { padding:15px; border-radius:8px; margin-top:10px; border-right:5px solid; }
.success { background:#e8f5e9; border-color:#4caf50; color:#2e7d32; }
.error { background:#ffebee; border-color:#f44336; color:#c62828; }
.timer-box { font-size:18px; font-weight:bold; color:#d32f2f; text-align:center; background:#fff1f1; padding:10px; border-radius:10px; border:1px solid #d32f2f; margin-bottom:15px; }
div.stButton > button { width: 100%; border-radius: 8px; font-weight: bold; }
</style>""", unsafe_allow_html=True)

S = st.session_state
if 'step' not in S:
    S.update({'user':'','step':'login','lt':'','qa':False,'qi':0,'qans':{},'qq':[],'cq':set(),'ei':0,'eans':{},'eq':[],'start_time':None})

def parse_j(t):
    try:
        m = re.search(r'\[\s*\{.*\}\s*\]', t, re.DOTALL)
        return json.loads(m.group()) if m else None
    except: return None

def get_questions(topic, count, level="complex"):
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        m = genai.GenerativeModel('gemini-2.0-flash')
        type_q = "סיפוריות ומורכבות" if level=="complex" else "קצרות לבדיקת הבנה"
        p = f"צור {count} שאלות {type_q} למבחן המתווכים בנושא {topic}. "
        p += "החזר JSON נקי בלבד: [{'q':'','options':['א','ב','ג','ד'],'correct':'הטקסט המדויק מהאופציות','reason':''}]"
        r = m.generate_content(p)
        return parse_j(r.text)
    except: return None

st.title("🏠 מתווך בקליק")

if S.step == "login":
    u = st.text_input("שם מלא:")
    if st.button("כניסה"):
        if u: S.user, S.step = u, "menu"; st.rerun()

elif S.step == "menu":
    st.subheader(f"שלום, {S.user} 👋")
    c1, c2 = st.columns(2)
    if c1.button("📚 שיעור + שאלון הבנה"):
        S.step, S.lt, S.qa, S.qq = "study", "", False, []; st.rerun()
    if c2.button("📝 סימולציית מבחן רשמית (25 שאלות)"):
        S.eq, S.ei, S.cq, S.start_time = [], 0, set(), time.time()
        S.step = "full_exam"; st.rerun()

elif S.step == "study":
    # רשימה מלאה של כל נושאי הבחינה - מסודרת ללא שבירות שורה
    all_t = [
        "חוק המתווכים במקרקעין",
        "חוק המקרקעין",
        "חוק החוזים",
        "חוק המכר (דירות)",
        "חוק הגנת הצרכן",
        "חוק הגנת הדייר",
        "חוק תכנון ובנייה",
        "חוק מיסוי מקרקעין",
        "חוק ההוצאה לפועל",
        "חוק הירושה",
        "חוק העונשין (עבירות רלוונטיות)",
        "אתיקה מקצועית"
    ]
    sel = st.selectbox("בחר נושא ללימוד:", all_t)
    if not S.lt:
        if st.button("📖 התחל שיעור"):
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            m = genai.GenerativeModel('gemini-2.0-flash')
            res = m.generate_content(f"כתוב שיעור מפורט ומעמיק למבחן המתווכים על {sel}.", stream=True)
            ph, full = st.empty(), ""
            for ch in res: full += ch.text; ph.markdown(f"<div class='lesson-box'>{full}</div>", unsafe_allow_html=True)
            S.lt = full; st.rerun()
    else:
        st.markdown(f"<div class='lesson-box'>{S.lt}</div>", unsafe_allow_html=True)
        if not S.qa:
            if st.button(f"✍️ שאלון: {sel}"):
                with st.spinner("מייצר 10 שאלות הבנה..."):
                    d = get_questions(sel, 10, "simple")
                    if d: S.qq, S.qa, S.qi, S.cq = d, True, 0, set(); st.rerun()
        else:
            it = S.qq[S.qi]
            st.write(f"### שאלה {S.qi+1}/10")
            ans = st.radio(it['q'], it['options'], key=f"sq{S.qi}", index=None)
            
            col1, col2, col3 = st.columns(3)
            if ans and S.qi not in S.cq:
                if col1.button("🔍 בדוק"): S.qans[S.qi] = ans; S.cq.add(S.qi); st.rerun()
            
            if S.
