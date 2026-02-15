# גרסה: 222 | תאריך: 2026-02-15 | שעה: 17:10 (Israel Time - GMT+2)

import streamlit as st
import google.generativeai as genai
import json, re, time

st.set_page_config(page_title="מתווך בקליק", layout="centered")

# CSS - עיצוב RTL מלא ושם משתמש קבוע
st.markdown("""<style>
* { direction: rtl !important; text-align: right !important; }
.lesson-box { 
    background-color: #ffffff !important; 
    color: #000000 !important; 
    padding: 25px; border-radius: 12px; border-right: 6px solid #1E88E5; 
    line-height: 1.8; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}
.explanation-box { padding: 15px; border-radius: 8px; margin: 15px 0; border-right: 5px solid; }
.success { background-color: #e8f5e9 !important; color: #2e7d32 !important; border-color: #4caf50 !important; }
.error { background-color: #ffebee !important; color: #c62828 !important; border-color: #f44336 !important; }
div.stButton > button { width: 100%; border-radius: 8px; font-weight: bold; height: 3em; margin-top: 10px; }
.user-header { 
    font-size: 22px; font-weight: bold; color: #ffffff; 
    background: #1E88E5; padding: 10px 20px; border-radius: 10px; 
    margin-bottom: 25px; text-align: center !important;
}
</style>""", unsafe_allow_html=True)

S = st.session_state
if 'step' not in S:
    S.update({
        'user':'','step':'login','lt':'','qa':False,'qi':0,'qans':{},'qq':[],'cq':set(),
        'ei':0,'eans':{},'eq':[],'start_time':None, 'current_topic':''
    })

def parse_j(t):
    try:
        m = re.search(r'\[\s*\{.*\}\s*\]', t, re.DOTALL)
        return json.loads(m.group()) if m else None
    except: return None

def get_questions(topic, count):
    try:
        if "GEMINI_API_KEY" not in st.secrets:
            st.error("חסר API KEY ב-Secrets!")
            return None
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        # שימוש במודל המדויק gemini-2.0-flash
        model = genai.GenerativeModel('gemini-2.0-flash')
        p = f"צור {count} שאלות למבחן המתווכים בנושא {topic}. החזר JSON נקי בלבד: "
        p += "[{'q':'','options':['א','ב','ג','ד'],'correct':'הטקסט המדויק מהאופציות','reason':''}]"
        r = model.generate_content(p)
        return parse_j(r.text)
    except Exception as e:
        st.error(f"שגיאת API (404/Connection): {str(e)}")
        return None

st.title("🏠 מתווך בקליק")

if S.user:
    st.markdown(f"<div class='user-header'>שלום, {S.user}</div>", unsafe_allow_html=True)

if S.step == "login":
    # שימוש ב-on_change או לחיצה ישירה ללא Form למניעת 404 של Streamlit
    u_name = st.text_input("הזן שם מלא:", key="login_field")
    if st.button("כניסה למערכת"):
        if u_name:
            S.user = u_name
            S.step = "menu"
            st.rerun()

elif S.step == "menu":
    c1, c2 = st.columns(2)
    if c1.button("📚 שיעורים בנושאי הלימוד"):
        S.step, S.lt, S.qa = "study", "", False
        st.rerun()
    if c2.button("📝 סימולציית מבחן רשמית"):
        S.step = "exam_lobby"
        st.rerun()

elif S.step == "exam_lobby":
    st.markdown("### 📝 הכנה לסימולציה\n25 שאלות מורכבות.")
    c1, c2 = st.columns(2)
    if c1.button("🚀 התחל מבחן"):
        S.ei, S.cq, S.start_time = 0, set(), time.time()
        S.step = "full_exam"
        st.rerun()
    if c2.button("🔙 חזרה"):
        S.step = "menu"
        st.rerun()

elif S.step == "study":
    all_t = ["חוק המתווכים במקרקעין", "חוק המקרקעין", "חוק החוזים", "חוק המכר (דירות)", "חוק הגנת הצרכן", "חוק הגנת הדייר", "חוק תכנון ובנייה", "חוק מיסוי מקרקעין", "חוק ההוצאה לפועל", "חוק הירושה", "חוק העונשין", "אתיקה מקצועית"]
    if not S.lt:
        sel = st.selectbox("בחר נושא:", all_t)
        c1, c2, c3 = st.columns(3)
        if c1.button("📖 התחל שיעור"):
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            model = genai.GenerativeModel('gemini-2.0-flash')
            p = f"כתוב שיעור מפורט למבחן המתווכים על {sel}."
            res = model.generate_content(p, stream=True)
            ph, full = st.empty(), ""
            for ch in res: 
                full += ch.text
                ph.markdown(f"<div class='lesson-box'>{full}</div>", unsafe_allow_html=True)
            S.lt, S.current_topic = full, sel
            st.rerun()
        if c2.button("📝 למבחן"):
            S.step = "exam_lobby"
            st.rerun()
        if c3.button("🏠 תפריט"):
            S.step = "menu"
            st.rerun()
    else:
        if not S.qa:
            st.markdown(f"<div class='lesson-box'>{S.lt}</div>", unsafe_allow_html=True)
            if st.button(f"✍️ שאלון: {S.current_topic}"):
                with st.spinner("טוען..."):
                    d = get_questions(S.current_topic, 10)
                    if d: S.qq, S.qa, S.qi, S.cq = d, True, 0, set(); st.rerun()
            if st.button("🏁 חזרה"): S.step, S.lt = "menu", ""; st.rerun()
        else:
            it = S.qq[S.qi]
            st.write(f"### שאלה {S.qi+1}/10")
            ans = st.radio(it['q'], it['options'], key=f"sq{S.qi}", index=None)
            if S.qi in S.cq:
                is_ok = str(S.qans.get(S.qi)).strip() == str(it['correct']).strip()
                st.markdown(f"<div class='explanation-box {'success' if is_ok else 'error'}'>{it['reason']}</div>", unsafe_allow_html=True)
            if ans and S.qi not in S.cq:
                if st.button("🔍 בדוק"): S.qans[S.qi] = ans; S.cq.add(S.qi); st.rerun()
            if S.qi in S.cq:
                if S.qi < 9:
                    if st.button("➡️ הבא"): S.qi += 1; st.rerun()
                else:
                    if st.button("🏠 סיום"): S.step, S.lt, S.qa = "menu", "", False; st.rerun()

elif S.step == "full_exam":
    if not S.eq:
        with st.spinner("מכין סימולציה..."):
            S.eq = get_questions("דיני מקרקעין", 25)
            if S.eq: st.rerun()
    if S.ei < len(S.eq):
        it = S.eq[S.ei]
        st.write(f"### שאלה {S.ei+1}/25")
        ans = st.radio(it['q'], it['options'], key=f"ex{S.ei}", index=None)
        if S.ei in S.cq:
            is_ok = str(S.eans.get(S.ei)).strip() == str(it['correct']).strip()
            st.markdown(f"<div class='explanation-box {'success' if is_ok else 'error'}'>{it['reason']}</div>", unsafe_allow_html=True)
        if ans and S.ei not in S.cq:
            if st.button("🔍 בדוק"): S.eans[S.ei] = ans; S.cq.add(S.ei); st.rerun()
        if S.ei in S.cq:
            if S.ei < 24:
                if st.button("➡️ הבא"): S.ei += 1; st.rerun()
            else:
                if st.button("🏁 סיום"): S.step, S.eq = "menu", []; st.rerun()
