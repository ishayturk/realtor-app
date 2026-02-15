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
.timer-box { font-size:20px; font-weight:bold; color:#d32f2f; text-align:center; background:#fff1f1; padding:10px; border-radius:10px; border:1px solid #d32f2f; margin-bottom:20px; }
</style>""", unsafe_allow_html=True)

S = st.session_state
if 'user' not in S:
    S.update({'user':'','step':'login','lt':'','qa':False,'qi':0,'qans':{},'qq':[],'cq':set(),'ei':0,'eans':{},'eq':[],'start_time':None})

def parse_j(t):
    try:
        m = re.search(r'\[\s*\{.*\}\s*\]', t, re.DOTALL)
        return json.loads(m.group()) if m else None
    except: return None

st.title("🏠 מתווך בקליק")

if S.user == "" or S.step == "login":
    u = st.text_input("שם מלא:")
    if st.button("כניסה"):
        if u: S.user, S.step = u, "menu"; st.rerun()
elif S.step == "menu":
    st.subheader(f"שלום, {S.user} 👋")
    if st.button("📚 שיעור עיוני + שאלון"):
        S.step, S.lt, S.qa = "study", "", False; st.rerun()
    if st.button("📝 סימולציה (25 שאלות)"):
        with st.spinner("מייצר סימולציה..."):
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            m = genai.GenerativeModel('gemini-2.0-flash')
            p = "צור 25 שאלות 'תיאור מקרה' למבחן המתווכים. החזר JSON בלבד: " + "[{'q':'','options':['א','ב','ג','ד'],'correct':'','reason':''}]"
            r = m.generate_content(p)
            d = parse_j(r.text)
            if d: S.eq, S.step, S.ei, S.cq, S.start_time = d, "full_exam", 0, set(), time.time(); st.rerun()
elif S.step == "study":
    all_t = ["חוק המתווכים", "תקנות המתווכים", "חוק המקרקעין", "חוק החוזים", "הגנת הצרכן", "חוק המכר", "תכנון ובנייה", "מיסוי מקרקעין", "הגנת הדייר", "חוק הירושה", "בתים משותפים", "חוק השמאות", "חוק העונשין", "דיני קניין", "אתיקה", "מקרקעי ישראל"]
    sel = st.selectbox("בחר נושא:", all_t)
    if not S.lt:
        if st.button("📖 התחל שיעור"):
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            m = genai.GenerativeModel('gemini-2.0-flash')
            res = m.generate_content(f"כתוב שיעור מפורט על {sel} למבחן המתווכים.", stream=True)
            ph, full = st.empty(), ""
            for ch in res:
                full += ch.text
                ph.markdown(f"<div class='lesson-box'>{full}</div>", unsafe_allow_html=True)
            S.lt = full; st.rerun()
    else:
        st.markdown(f"<div class='lesson-box'>{S.lt}</div>", unsafe_allow_html=True)
        if not S.qa:
            if st.button("✍️ בנה שאלון"):
                with st.spinner("מייצר שאלות..."):
                    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                    m = genai.GenerativeModel('gemini-2.0-flash')
                    p = "על בסיס: " + S.lt + ". צור 10 שאלות סיפוריות. החזר JSON: [{'q':'','options':['א','ב','ג','ד'],'correct':'','reason':''}]"
                    r = m.generate_content(p); d = parse_j(r.text)
                    if d: S.qq, S.qa, S.cq, S.qi = d, True, set(), 0; st.rerun()
        else:
            it = S.qq[S.qi]; st.markdown(f"### שאלה {S.qi+1}/10")
            p = st.radio(it['q'], it['options'], key=f"q{S.qi}", index=None)
            if p and S.qi not in S.cq:
                if st.button("🔍 בדוק"): S.qans[S.qi], _ = p, S.cq.add(S.qi); st.rerun()
            if S.qi in S.cq:
                ok = S.qans.get(S.qi) == it['correct']
                st.markdown(f"<div class='explanation-box {'success' if ok else 'error'}'>{it['reason']}</div>", unsafe_allow_html=True)
            if st.button("➡️ הבא") and S.qi < 9: S.qi += 1; st.rerun()
            if st.button("🏁 חזרה"): S.step = "menu"; st.rerun()
elif S.step == "full_exam":
    if S.start_time:
        el = int(time.time() - S.start_time); mins, secs = divmod(el, 60)
        st.markdown(f"<div class='timer-box'>⏱️ זמן: {mins:02d}:{secs:02d}</div>", unsafe_allow_html=True)
    it = S.eq[S.ei]; st.write(f"### שאלה {S.ei+1}/25")
    p = st.radio(it['q'], it['options'], key=f"e{S.ei}", index
