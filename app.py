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
    all_t = ["חוק המתווכים", "חוק המקרקעין", "חוק החוזים", "חוק המכר", "תכנון ובנייה", "מיסוי מקרקעין", "אתיקה"]
    sel = st.selectbox("בחר נושא:", all_t)
    if not S.lt:
        if st.button("📖 התחל שיעור"):
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            m = genai.GenerativeModel('gemini-2.0-flash')
            res = m.generate_content(f"כתוב שיעור מפורט על {sel}.", stream=True)
            ph, full = st.empty(), ""
            for ch in res: full += ch.text; ph.markdown(f"<div class='lesson-box'>{full}</div>", unsafe_allow_html=True)
            S.lt = full; st.rerun()
    else:
        st.markdown(f"<div class='lesson-box'>{S.lt}</div>", unsafe_allow_html=True)
        if not S.qa:
            # שינוי שם הכפתור לפי הנושא
            if st.button(f"✍️ שאלון: {sel}"):
                with st.spinner("מייצר שאלות הבנה..."):
                    d = get_questions(sel, 5, "simple")
                    if d: S.qq, S.qa, S.qi, S.cq = d, True, 0, set(); st.rerun()
                    else: st.error("לא הצלחתי לייצר שאלות. נסה שוב.")
        else:
            it = S.qq[S.qi]
            st.write(f"### שאלה {S.qi+1}/5")
            ans = st.radio(it['q'], it['options'], key=f"sq{S.qi}", index=None)
            if ans and S.qi not in S.cq:
                if st.button("🔍 בדוק"): S.qans[S.qi] = ans; S.cq.add(S.qi); st.rerun()
            if S.qi in S.cq:
                is_ok = str(S.qans.get(S.qi)).strip() == str(it['correct']).strip()
                st.markdown(f"<div class='explanation-box {'success' if is_ok else 'error'}'>{'✅ נכון!' if is_ok else '❌ טעות. הנכונה: '+it['correct']}<br><br>{it['reason']}</div>", unsafe_allow_html=True)
            if st.button("➡️ הבא") and S.qi < 4: S.qi += 1; st.rerun()
            if st.button("🏁 חזרה"): S.step = "menu"; st.rerun()

elif S.step == "full_exam":
    if S.start_time:
        el = int(time.time() - S.start_time)
        mi, se = divmod(el, 60)
        st.markdown(f"<div class='timer-box'>⏱️ שאלה {S.ei+1}/25 | זמן: {mi:02d}:{se:02d}</div>", unsafe_allow_html=True)
    
    if S.ei >= len(S.eq) and S.ei < 25:
        with st.spinner(f"טוען שאלות {S.ei+1}-{min(S.ei+5, 25)}..."):
            new_q = get_questions("כללי - מבחן מתווכים", 5, "complex")
            if new_q: S.eq.extend(new_q); st.rerun()
            else: st.error("שגיאה בטעינה. נסה שוב.")

    if S.ei < len(S.eq):
        it = S.eq[S.ei]
        ans = st.radio(it['q'], it['options'], key=f"ex{S.ei}", index=None)
        if ans and S.ei not in S.cq:
            if st.button("🔍 בדוק"): S.eans[S.ei] = ans; S.cq.add(S.ei); st.rerun()
        if S.ei in S.cq:
            is_ok = str(S.eans.get(S.ei)).strip() == str(it['correct']).strip()
            st.markdown(f"<div class='explanation-box {'success' if is_ok else 'error'}'>{'✅ נכון!' if is_ok else '❌ טעות. הנכונה: '+it['correct']}<br><br>{it['reason']}</div>", unsafe_allow_html=True)
        
        if st.button("➡️ השאלה הבאה") and S.ei < 24: S.ei += 1; st.rer
