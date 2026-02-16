# גרסה: 1043 | חזרה למקור שעבד
import streamlit as st
import google.generativeai as genai
import json, re, time

st.set_page_config(page_title="מתווך בקליק", layout="centered")

S = st.session_state
if 'step' not in S:
    S.update({'user':'','step':'login','lt':'','qi':0,'qans':{},'qq':[],'current_topic':'','mode':'exam','cq':set()})

def fetch_exam_content(topic):
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-2.0-flash')
    # בקשה פשוטה וישירה כמו בהתחלה
    p = f"צור 10 שאלות אמריקאיות למבחן המתווכים על {topic}. החזר JSON בלבד: [{'q':'','options':['א','ב','ג','ד'],'correct':'','reason':''}]"
    r = model.generate_content(p)
    m = re.search(r'\[.*\]', r.text, re.DOTALL)
    return json.loads(m.group()) if m else []

if S.step == "login":
    u = st.text_input("שם מלא:")
    if st.button("כניסה"):
        if u: S.user = u; S.step = "menu"; st.rerun()

elif S.step == "menu":
    S.update({'qi':0,'qans':{},'qq':[],'lt':'','cq':set()})
    if st.button("📚 שיעורים ולימוד"): S.step = "study"; st.rerun()

elif S.step == "study":
    all_t = ["חוק המתווכים במקרקעין", "חוק המקרקעין", "חוק החוזים", "חוק המכר"] # רשימה מקוצרת לבדיקה
    if not S.lt:
        sel = st.selectbox("בחר נושא:", all_t)
        if st.button("📖 התחל שיעור"):
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            model = genai.GenerativeModel('gemini-2.0-flash')
            res = model.generate_content(f"כתוב שיעור על {sel}", stream=True)
            ph = st.empty()
            full_text = ""
            for chunk in res:
                if chunk.text:
                    full_text += chunk.text
                    ph.write(full_text)
            S.lt, S.current_topic = full_text, sel
            st.rerun()
    else:
        st.write(S.lt)
        # הכפתורים שביקשת - בלי עיבודים מוקדמים
        if st.button("✍️ עבור לשאלון תרגול"):
            with st.spinner("המשתמש מחכה לשאלות..."):
                d = fetch_exam_content(S.current_topic)
                if d:
                    S.qq, S.qi, S.mode, S.step = d, 0, 'study_quiz', "quiz_mode"
                    st.rerun()
        if st.button("🏠 חזרה"): S.lt = ""; S.step = "menu"; st.rerun()

elif S.step == "quiz_mode":
    it = S.qq[S.qi]
    st.write(f"שאלה {S.qi+1}: {it['q']}")
    ans = st.radio("בחר:", it['options'], key=f"q_{S.qi}")
    if st.button("🔍 בדוק"):
        if ans == it['correct']: st.success("נכון!")
        else: st.error(f"טעות. הנכון: {it['correct']}")
    if st.button("הבא"):
        if S.qi < len(S.qq)-1: S.qi += 1; st.rerun()
        else: S.step = "menu"; st.rerun()
