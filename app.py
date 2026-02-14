import streamlit as st
import google.generativeai as genai
import json, re

st.set_page_config(page_title="מתווך בקליק", layout="centered")
st.markdown("""<style>
[data-testid="stAppViewContainer"],.main {direction:rtl!important; text-align:right!important;}
h1,h2,h3 {text-align:center!important; color:#1E88E5;}
.stButton>button {width:100%; font-weight:bold; border-radius:10px;}
.lesson-box {background:#fff; padding:20px; border-radius:15px; border-right:6px solid #1E88E5; line-height:1.6; margin-bottom:20px;}
.explanation-box {padding:15px; border-radius:10px; margin-top:10px; border-right:5px solid;}
.success {background:#e8f5e9; border-color:#4caf50;}
.error {background:#ffebee; border-color:#f44336;}
div[role="radiogroup"] {direction:rtl!important; text-align:right!important;}
</style>""", unsafe_allow_html=True)

S = st.session_state
keys = ['user','step','lt','qa','qi','qans','qq','cq','ei','eans','eq']
for k in keys:
    if k not in S: S[k] = "" if k in ['user','step','lt'] else (False if k=='qa' else (0 if 'i' in k else ([] if 'q' in k[0] else ({} if 'ans' in k else set()))))

def parse_j(t):
    try:
        m = re.search(r'\[\s*{.*}\s*\]', t, re.DOTALL)
        return json.loads(m.group()) if m else None
    except: return None

st.markdown("<h1>🏠 מתווך בקליק</h1>", unsafe_allow_html=True)

if S.user == "" or S.step == "login":
    name = st.text_input("הכנס שם מלא:")
    if st.button("כניסה"):
        if name: S.user, S.step = name, "menu"; st.rerun()

elif S.step == "menu":
    st.markdown(f"### שלום, {S.user} 👋")
    c1, c2 = st.columns(2)
    if c1.button("📚 שיעור + שאלון"): S.step, S.lt, S.qa = "study", "", False; st.rerun()
    if c2.button("📝 סימולציית 25"):
        S.eq = [{"q":f"שאלה {i+1}:","options":["א","ב","ג","ד"],"correct":"א","reason":"הסבר"} for i in range(25)]
        S.step, S.ei, S.cq = "full_exam", 0, set(); st.rerun()

elif S.step == "study":
    all_t = ["חוק המתווכים","תקנות המתווכים","חוק המקרקעין","חוק החוזים","חוק הגנת הצרכן","חוק המכר (דירות)","חוק התכנון והבנייה","מיסוי מקרקעין","חוק הגנת הדייר","חוק הירושה","בתים משותפים","חוק השמאות","חוק העונשין","דיני קניין","אתיקה מקצועית","חוק מקרקעי ישראל"]
    sel = st.selectbox("נושא:", all_t)
    if not S.lt:
        if st.button("📖 התחל שיעור"):
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            m = genai.GenerativeModel('gemini-2.0-flash')
            res = m.generate_content(f"כתוב שיעור על {sel} למבחן המתווכים.", stream=True)
            ph, full = st.empty(), ""
            for ch in res:
                full += ch.text
                ph.markdown(f"<div class='lesson-box'>{full}</div>", unsafe_allow_html=True)
            S.lt = full; st.rerun()
    if S.lt:
        st.markdown(f"<div class='lesson-box'>{S.lt}</div>", unsafe_allow_html=True)
        if not S.qa:
            if st.button("✍️ בנה שאלון"):
                m = genai.GenerativeModel('gemini-2.0-flash')
                p = f"על בסיס: {S.lt}. צור 10 שאלות JSON: [{{'q':'','options':['א','ב','ג','ד'],'correct':'','reason':''}}]"
                r = m.generate_content(p)
                d = parse_j(r.text)
                if d: S.qq, S.qa, S.cq, S.qi = d, True, set(), 0; st.rerun()
    if S.qa:
        it = S.qq[S.qi]
        st.markdown(f"#### שאלה {S.qi+1}/10")
        p = st.radio(it['q'], it['options'], key=f"q{S.qi}", index=None)
        if p and S.qi not in S.cq:
            if st.button("🔍 בדוק"): S.qans[S.qi], S.cq.add(S.qi); st.rerun()
        if S.qi in S.cq:
            ok = S.qans.get(S.qi) == it['correct']
            st.markdown(f"<div class='explanation-box {'success' if ok else 'error'}'><b>{'נכון' if ok else 'טעות'}</b><br>{it['reason']}</div>", unsafe_allow_html=True)
        c_p, c_n = st.columns(2)
        if c_p.button("⬅️") and S.qi > 0: S.qi -= 1; st.rerun()
        if c_n.button("➡️") and S.qi < 9: S.qi += 1; st.rerun()
        elif S.qi == 9: 
            if st.button("🏁 סיום"): S.step = "menu"; st.rerun()

elif S.step == "full_exam":
    ei = S.ei
    it = S.eq[ei]
    st.markdown(f"### שאלה {ei+1}/25")
    p = st.radio(it['q'], it['options'], key=f"e{ei}", index=None)
    if p and ei not in S.cq:
        if st.button("🔍 בדוק"): S.eans[ei], S.cq.add(ei); st.rerun()
    if ei in S.cq:
        ok = S.eans.get(ei) == it['correct']
        st.markdown(f"<div class='explanation-box {'success' if ok else 'error'}'>{it['reason']}</div>", unsafe_allow_html=True)
    b1, b2 = st.columns(2)
    if b1.button("⬅️") and ei > 0: S.ei -= 1; st.rerun()
    if b2.button("➡️") and ei < 24: S.ei += 1; st.rerun()
    else:
        if st.button("חזרה"): S.step = "menu"; st.rerun()
