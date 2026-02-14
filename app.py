import streamlit as st
import google.generativeai as genai
import json, re

st.set_page_config(page_title="מתווך בקליק", layout="centered")
st.markdown("""<style>
* { direction: rtl !important; text-align: right !important; }
.lesson-box { background:#fdfdfd; padding:20px; border-radius:12px; border-right:6px solid #1E88E5; line-height:1.8; margin-bottom:20px; }
.explanation-box { padding:15px; border-radius:8px; margin-top:10px; border-right:5px solid; }
.success { background:#e8f5e9; border-color:#4caf50; color:#2e7d32; }
.error { background:#ffebee; border-color:#f44336; color:#c62828; }
</style>""", unsafe_allow_html=True)

S = st.session_state
if 'user' not in S:
    S.update({'user':'','step':'login','lt':'','qa':False,'qi':0,'qans':{},'qq':[],'cq':set(),'ei':0,'eans':{},'eq':[]})

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
    if st.button("📝 סימולציה 25 שאלות"):
        S.eq = [{"q":f"שאלה {i+1}:","options":["א","ב","ג","ד"],"correct":"א","reason":"הסבר"} for i in range(25)]
        S.step, S.ei, S.cq = "full_exam", 0, set(); st.rerun()

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
                with st.spinner("מנתח את השיעור ומייצר שאלות..."):
                    m = genai.GenerativeModel('gemini-2.0-flash')
                    p = f"על בסיס הטקסט הבא בלבד: {S.lt}\nצור 10 שאלות אמריקאיות. החזר אך ורק פורמט JSON תקין כרשימה: [{{'q': 'שאלה', 'options': ['א','ב','ג','ד'], 'correct': 'התשובה המדויקת מהרשימה', 'reason': 'הסבר'}}] "
                    r = m.generate_content(p)
                    d = parse_j(r.text)
                    if d: S.qq, S.qa, S.cq, S.qi = d, True, set(), 0; st.rerun()
                    else: st.error("ה-AI לא הצליח לייצר שאלות בפורמט תקין. נסה שוב.")
        else:
            it = S.qq[S.qi]
            st.markdown(f"### שאלה {S.qi+1} מתוך 10")
            p = st.radio(it['q'], it['options'], key=f"q{S.qi}", index=None)
            if p and S.qi not in S.cq:
                if st.button("🔍 בדוק תשובה"): S.qans[S.qi], _ = p, S.cq.add(S.qi); st.rerun()
            if S.qi in S.cq:
                ok = S.qans.get(S.qi) == it['correct']
                c = "success" if ok else "error"
                st.markdown(f"<div class='explanation-box {c}'><b>{'נכון!' if ok else 'טעות.'}</b><br>{it['reason']}</div>", unsafe_allow_html=True)
            
            c1, c2 = st.columns(2)
            if c1.button("➡️ הבא") and S.qi < 9: S.qi += 1; st.rerun()
            if c2.button("🏁 חזרה לתפריט"): S.step = "menu"; st.rerun()

elif S.step == "full_exam":
    it = S.eq[S.ei]
    st.write(f"### סימולציה: {S.ei+1}/25")
    p = st.radio(it['q'], it['options'], key=f"e{S.ei}", index=None)
    if p and S.ei not in S.cq:
        if st.button("🔍 בדוק"): S.eans[S.ei], _ = p, S.cq.add(S.ei); st.rerun()
    if S.ei in S.cq:
        ok = S.eans.get(S.ei) == it['correct']
        c = "success" if ok else "error"
        st.markdown(f"<div class='explanation-box {c}'>{it['reason']}</div>", unsafe_allow_html=True)
    if st.button("➡️ הבא") and S.ei < 24: S.ei += 1; st.rerun()
    if st.button("🏁 חזרה"): S.step = "menu"; st.rerun()
