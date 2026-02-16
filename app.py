# גרסה 1059 | 16/02/2026 | 09:40

import streamlit as st
import google.generativeai as genai
import json, re

st.set_page_config(page_title="מתווך בקליק", layout="centered")

# עיצוב UI
st.markdown("""
<style>
    * { direction: rtl !important; text-align: right !important; }
    .lesson-box { background-color: #fdfdfd; padding: 25px; border-radius: 12px; border-right: 6px solid #1E88E5; line-height: 1.8; margin-bottom: 20px; }
    .question-card { background-color: #ffffff; padding: 25px; border-radius: 12px; border: 1px solid #e0e0e0; margin-bottom: 20px; }
    .main-header { background: #1E88E5; color: white; padding: 15px; border-radius: 10px; text-align: center; margin-bottom: 15px; font-size: 24px; }
    .welcome-box { background-color: #e3f2fd; padding: 20px; border-radius: 10px; border: 1px solid #90caf9; margin-bottom: 25px; line-height: 1.6; }
</style>
""", unsafe_allow_html=True)

S = st.session_state
if 'step' not in S:
    S.update({'user':'','step':'login','lt':'','qi':0,'qq':[],'current_topic':''})

def fetch_exam_content(topic):
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-2.0-flash')
        p = f"התבסס על חומרי רשם המתווכים 2026. צור 10 שאלות תרגול רב-ברירה בנושא {topic}. JSON נקי בלבד: [{'q':'','options':['א','ב','ג','ד'],'correct':'','reason':''}]"
        r = model.generate_content(p)
        clean_txt = r.text.replace('```json', '').replace('```', '').strip()
        m = re.search(r'\[.*\]', clean_txt, re.DOTALL)
        return json.loads(m.group()) if m else []
    except Exception:
        st.error("המערכת עמוסה. אנא המתן כמה שניות ונסה ללחוץ שוב.")
        return []

st.markdown("<div class='main-header'>🏠 מתווך בקליק</div>", unsafe_allow_html=True)

if S.step == "login":
    u = st.text_input("שם מלא:")
    if st.button("כניסה"):
        if u: S.user = u; S.step = "menu"; st.rerun()

elif S.step == "menu":
    # החזרת ההסבר המורחב
    st.markdown(f"### שלום, {S.user} 👋")
    st.markdown("""
    <div class='welcome-box'>
    <b>ברוכים הבאים למערכת ההכנה הדינמית לבחינת רשם המתווכים.</b><br><br>
    המערכת סונכרנה מול חומרי הלימוד המעודכנים ביותר של משרד המשפטים לשנת 2026, כולל חוק המתווכים, חוק המקרקעין ותקנות האתיקה החדשות.<br><br>
    <b>מה ניתן לעשות כאן?</b><br>
    * 📚 <b>למידה ממוקדת:</b> בחרו נושא וקבלו שיעור מקיף שנוצר בזמן אמת.<br>
    * ✍️ <b>תרגול שאלות:</b> בסוף כל שיעור תוכלו לייצר שאלון של 10 שאלות לתרגול הידע.<br>
    * ⏱️ <b>סימולציה:</b> בקרוב תוכלו לבצע מבחן מלא המדמה את התנאים האמיתיים.<br><br>
    <i>מומלץ להתחיל בבחירת נושא ללימוד מהתפריט למטה. בהצלחה!</i>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("📚 התחל למידה לפי נושאים", use_container_width=True): 
        S.step = "study"
        st.rerun()

elif S.step == "study":
    all_t = ["חוק המתווכים במקרקעין", "תקנות המתווכים (פרטי הזמנה)", "אתיקה מקצועית", "חוק המקרקעין", "חוק המכר (דירות)", "חוק הגנת הצרכן", "חוק החוזים", "חוק הירושה", "חוק מיסוי מקרקעין"]
    if not S.lt:
        st.markdown("### בחר נושא ללימוד")
        sel = st.selectbox("נושאים זמינים:", all_t)
        c1, c2 = st.columns(2)
        if c1.button("📖 צור שיעור", use_container_width=True):
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            model = genai.GenerativeModel('gemini-2.0-flash')
            res = model.generate_content(f"כתוב שיעור מקיף ל-2026 על {sel}.", stream=True)
            ph = st.empty()
            full_text = ""
            for chunk in res:
                full_text += chunk.text
                ph.markdown(f"<div class='lesson-box'>{full_text}</div>", unsafe_allow_html=True)
            S.lt, S.current_topic = full_text, sel
            st.rerun()
        if c2.button("🏠 חזרה", use_container_width=True): S.step = "menu"; st.rerun()
    else:
        st.markdown(f"<div class='lesson-box'>{S.lt}</div>", unsafe_allow_html=True)
        if st.button("✍️ עבור לשאלון תרגול (10 שאלות)", use_container_width=True):
            with st.spinner("מייצר שאלות תרגול..."):
                d = fetch_exam_content(S.current_topic)
                if d: 
                    S.qq, S.qi, S.step = d, 0, "quiz_mode"
                    st.rerun()
        if st.button("🏠 חזרה לבחירת נושא"): S.lt = ""; st.rerun()

elif S.step == "quiz_mode":
    if S.qq:
        it = S.qq[S.qi]
        st.markdown(f"<div class='question-card'><b>שאלה {S.qi+1} מתוך {len(S.qq)}:</b><br>{it['q']}</div>", unsafe_allow_html=True)
        ans = st.radio("בחר תשובה:", it['options'], key=f"q_{S.qi}")
        c1, c2 = st.columns(2)
        if c1.button("🔍 בדוק", use_container_width=True):
            if ans == it['correct']: st.success(f"נכון! {it.get('reason','')}")
            else: st.error(f"טעות. התשובה הנכונה היא: {it['correct']}")
        if c2.button("הבא ➡️", use_container_width=True):
            if S.qi
