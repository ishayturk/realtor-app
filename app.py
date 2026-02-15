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
.timer-box { font-size:20px; font-weight:bold; color:#d32f2f; text-align:center; background:#fff1f1; padding:10px; border-radius:10px; border:1px solid #d32f2f; margin-bottom:15px; }
</style>""", unsafe_allow_html=True)

S = st.session_state
if 'step' not in S:
    S.update({'user':'','step':'login','lt':'','qa':False,'qi':0,'qans':{},'qq':[],'cq':set(),'ei':0,'eans':{},'eq':[],'start_time':None})

def parse_j(t):
    try:
        m = re.search(r'\[\s*\{.*\}\s*\]', t, re.DOTALL)
        return json.loads(m.group()) if m else None
    except: return None

st.title("🏠 מתווך בקליק")

if S.step == "login":
    u = st.text_input("שם מלא:")
    if st.button("כניסה"):
        if u: S.user, S.step = u, "menu"; st.rerun()

elif S.step == "menu":
    st.subheader(f"שלום, {S.user} 👋")
    c1, c2 = st.columns(2)
    if c1.button("📚 שיעור + שאלון"):
        S.step, S.lt, S.qa = "study", "", False; st.rerun()
    if c2.button("📝 סימולציה (20 שאלות)"):
        S.step = "prep_exam"; st.rerun()

elif S.step == "prep_exam":
    with st.spinner("מייצר סימולציה (גרסה 2.0)..."):
        try:
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            m = genai.GenerativeModel('gemini-2.0-flash')
            p = "צור 20 שאלות סיפוריות למבחן מתווכים. החזר JSON נקי בלבד: " 
            p += "[{'q':'','options':['א','ב','ג','ד'],'correct':'','reason':''}]"
            r = m.generate_content(p)
            d = parse_j(r.text)
            if d:
                S.eq, S.ei, S.cq, S.start_time, S.step = d, 0, set(), time.time(), "full_exam"
                st.rerun()
            else: st.error("ה-AI החזיר מבנה לא תקין. נסה שוב."); st.button("חזרה", on_click=lambda: S.update({"step":"menu"}))
        except Exception as e:
            st.error("המכסה (Quota) הסתיימה לדקה זו. המתן 60 שניות בדיוק ונסה שוב.")
            if st.button("חזרה לתפריט"): S.step = "menu"; st.rerun()

elif S.step == "study":
    all_t = ["חוק המתווכים", "חוק המקרקעין", "חוק החוזים", "חוק המכר", "תכנון ובנייה", "מיסוי מקרקעין", "אתיקה"]
    sel = st.selectbox("בחר נושא:", all_t)
    if not S.lt:
        if st.button("📖 התחל שיעור"):
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            m = genai.GenerativeModel('gemini-2.0-flash')
            res = m.generate_content(f"כתוב שיעור מפורט על {sel}.", stream=True)
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
                    m = genai.GenerativeModel('gemini-2.0-flash')
                    p = "על בסיס: " + S.lt + ". צור 10 שאלות סיפוריות. JSON: [{'q':'','options':['א','ב','ג','ד'],'correct':'','reason':''}]"
                    r = m.generate_content(p); d = parse_j(r.text)
                    if d: S.qq, S.qa, S.cq, S.qi = d, True, set(), 0; st.rerun()
        else:
            it = S.qq[S.qi]
            st.write(f"### שאלה {S.qi+1}/10")
            ans = st.radio(it['q'], it['options'], key=f"sq{S.qi}", index=None)
            if ans and S.qi not in S.cq:
                if st.button("🔍 בדוק"): S.qans[S.qi] = ans; S.cq.add(S.qi); st.rerun()
            if S.qi in S.cq:
                is_ok = S.qans.get(S.qi) == it['correct']
                color = "success" if is_ok else "error"
                label = "✅ נכון!" if is_ok else f"❌ טעות. התשובה הנכונה היא: {it['correct']}"
                st.markdown(f"<div class='explanation-box {color}'>{label}<br><br>{it['reason']}</div>", unsafe_allow_html=True)
            if st.button("➡️ הבא") and S.qi < 9: S.qi += 1; st.rerun()
            if st.button("🏁 חזרה"): S.step = "menu"; st.rerun()

elif S.step == "full_exam":
    if S.start_time:
        el = int(time.time() - S.start_time)
        mi, se = divmod(el, 60)
        st.markdown(f"<div class='timer-box'>⏱️ זמן: {mi:02d}:{se:02d}</div>", unsafe_allow_html=True)
    it = S.eq[S.ei]
    st.write(f"### שאלה {S.ei+1}/20")
    ans = st.radio(it['q'], it['options'], key=f"ex{S.ei}", index=None)
    if ans and S.ei not in S.cq:
        if st.button("🔍 בדוק"): S.eans[S.ei] = ans; S.cq.add(S.ei); st.rerun()
    if S.ei in S.cq:
        is_ok = S.eans.get(S.ei) == it['correct']
        color = "success" if is_ok else "error"
        label = "✅ נכון!" if is_ok else f"❌ טעות. הנכונה היא {it['correct']}"
        st.markdown(f"<div class='explanation-box {color}'>{label}<br><br>{it['reason']}</div>", unsafe_allow_html=True)
    if st.button("➡️ הבא") and S.ei < 19: S.ei += 1; st.rerun()
    if st.button("🏁 סיום"): S.step = "menu"; st.rerun()
