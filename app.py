# גרסה: 1002 | תאריך: 15/02/2026 | שעה: 15:45
import streamlit as st
import google.generativeai as genai
import json, re, time

st.set_page_config(page_title="מתווך בקליק", layout="centered")

# כותרת גרסה
st.markdown("<div style='text-align: left; color: gray; font-size: 10px;'>גרסה: 1002 | 15/02/2026 | 15:45</div>", unsafe_allow_html=True)

# CSS - RTL ועיצוב מקורי
st.markdown("""<style>
* { direction: rtl !important; text-align: right !important; }
.lesson-box { 
    background-color: #ffffff !important; color: #000000 !important; 
    padding: 25px; border-radius: 12px; border-right: 6px solid #1E88E5; 
    line-height: 1.8; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}
.explanation-box { padding: 15px; border-radius: 8px; margin: 10px 0; border-right: 5px solid; }
.success { background-color: #e8f5e9 !important; color: #2e7d32 !important; border-color: #4caf50 !important; }
.error { background-color: #ffebee !important; color: #c62828 !important; border-color: #f44336 !important; }
div.stButton > button { width: 100%; border-radius: 8px; font-weight: bold; height: 3em; }
.user-header { background: #1E88E5; color: white; padding: 10px; border-radius: 10px; text-align: center; margin-bottom: 20px; }
</style>""", unsafe_allow_html=True)

S = st.session_state
if 'step' not in S:
    S.update({'user':'','step':'login','lt':'','qa':False,'qi':0,'qans':{},'qq':[],'cq':set(),'current_topic':''})

# פונקציה לקבלת שאלות (מודל gemini-2.0-flash נשאר קבוע)
def get_questions(topic, count):
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-2.0-flash')
        p = f"צור {count} שאלות למבחן המתווכים בנושא {topic}. החזר JSON נקי: [{{'q':'','options':['א','ב','ג','ד'],'correct':'טקסט מדויק מהאופציות','reason':''}}]"
        r = model.generate_content(p)
        m = re.search(r'\[.*\]', r.text, re.DOTALL)
        return json.loads(m.group()) if m else None
    except: return None

st.title("🏠 מתווך בקליק")

if S.user:
    st.markdown(f"<div class='user-header'>שלום, {S.user}</div>", unsafe_allow_html=True)

if S.step == "login":
    u = st.text_input("הזן שם מלא:", key="login_final")
    if st.button("כניסה למערכת"):
        if u: S.user = u; S.step = "menu"; st.rerun()

elif S.step == "menu":
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
            S.lt, S.current_topic = full, sel
            st.rerun()
        if st.button("🏠 תפריט"): S.step = "menu"; st.rerun()
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
            ans = st.radio(it['q'], it['options'], key=f"q{S.qi}", index=None)
            
            if S.qi in S.cq:
                correct_text = str(it['correct']).strip()
                is_ok = str(S.qans.get(S.qi)).strip() == correct_text
                if is_ok:
                    st.markdown(f"<div class='explanation-box success'>{it['reason']}</div>", unsafe_allow_html=True)
                else:
                    # מציאת מספר התשובה הנכונה (1-4)
                    try: idx = it['options'].index(correct_text) + 1
                    except: idx = "?"
                    st.markdown(f"<div class='explanation-box error'>טעות, תשובה {idx} היא הנכונה. {it['reason']}</div>", unsafe_allow_html=True)
            
            # כפתורי ניווט בשורה אחת
            cols = st.columns(3)
            if ans and S.qi not in S.cq:
                if cols[0].button("🔍 בדוק"): S.qans[S.qi] = ans; S.cq.add(S.qi); st.rerun()
            
            if S.qi in S.cq:
                if S.qi < 9:
                    if cols[1].button("➡️ השאלה הבאה"): S.qi += 1; st.rerun()
                else:
                    if cols[1].button("🏠 סיום"): S.step, S.lt, S.qa = "menu", "", False; st.rerun()
            
            if cols[2].button("🏁 חזרה לתפריט"): S.step, S.lt, S.qa = "menu", "", False; st.rerun()

elif S.step == "exam_lobby":
    st.write("### סימולציית מבחן מלאה (25 שאלות)")
    if st.button("🚀 התחל מבחן (טעינת שאלות...)"):
        with st.spinner("מכין 5 שאלות ראשונות..."):
            d = get_questions("דיני מקרקעין ותיווך - כללי", 5)
            if d:
                S.qq, S.qa, S.qi, S.cq, S.step = d, True, 0, set(), "study"
                S.current_topic = "סימולציה כללית"
                st.rerun()
    if st.button("🏠 חזרה"): S.step = "menu"; st.rerun()
