# גרסה 1062 | 16/02/2026 | 09:55

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

def fetch_exam_content(topic, mode='study'):
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-2.0-flash')
        num = 10 if mode == 'study' else 25 # 25 שאלות למבחן מלא
        p = f"התבסס על חומרי רשם המתווכים 2026. צור {num} שאלות תרגול רב-ברירה בנושא {topic}. JSON נקי בלבד: [{'q':'','options':['א','ב','ג','ד'],'correct':'','reason':''}]"
        r = model.generate_content(p)
        clean_txt = r.text.replace('```json', '').replace('```', '').strip()
        m = re.search(r'\[.*\]', clean_txt, re.DOTALL)
        return json.loads(m.group()) if m else []
    except Exception:
        return []

st.markdown("<div class='main-header'>🏠 מתווך בקליק</div>", unsafe_allow_html=True)

if S.step == "login":
    u = st.text_input("שם מלא:")
    if st.button("כניסה"):
        if u: S.user = u; S.step = "menu"; st.rerun()

elif S.step == "menu":
    st.markdown(f"### שלום, {S.user} 👋")
    st.markdown("""
    <div class='welcome-box'>
    <b>ברוכים הבאים למערכת ההכנה המעודכנת (2026).</b><br>
    כאן תוכלו ללמוד נושאים ספציפיים או לבצע סימולציית בחינה מלאה.
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📚 למידה לפי נושאים", use_container_width=True): 
            S.step = "study"; st.rerun()
    with col2:
        if st.button("⏱️ סימולציית בחינה", use_container_width=True): 
            with st.spinner("מייצר בחינה מלאה..."):
                d = fetch_exam_content("כללי - מבחן מסכם", mode='exam')
                if d: S.qq, S.qi, S.step = d, 0, "quiz_mode"; st.rerun()

elif S.step == "study":
    all_t = ["חוק המתווכים במקרקעין", "תקנות המתווכים (פרטי הזמנה)", "אתיקה מקצועית", "חוק המקרקעין", "חוק המכר (דירות)", "חוק הגנת הצרכן", "חוק החוזים", "חוק הירושה", "חוק מיסוי מקרקעין"]
    if not S.lt:
        sel = st.selectbox("בחר נושא:", all_t)
        if st.button("📖 צור שיעור", use_container_width=True):
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            model = genai.GenerativeModel('gemini-2.0-flash')
            res = model.generate_content(f"כתוב שיעור ל-2026 על {sel}.", stream=True)
            ph, full_text = st.empty(), ""
            for chunk in res:
                full_text += chunk.text
                ph.markdown(f"<div class='lesson-box'>{full_text}</div>", unsafe_allow_html=True)
            S.lt, S.current_topic = full_text, sel; st.rerun()
        if st.button("🏠 חזרה"): S.step = "menu"; st.rerun()
    else:
        st.markdown(f"<div class='lesson-box'>{S.lt}</div>", unsafe_allow_html=True)
        if st.button("✍️ עבור לשאלון תרגול", use_container_width=True):
            with st.spinner("מייצר שאלות..."):
                d = fetch_exam_content(S.current_topic)
                if d: S.qq, S.qi, S.step = d, 0, "quiz_mode"; st.rerun()
        if st.button("🏠 חזרה לבחירת נושא"): S.lt = ""; st.rerun()

elif S.step == "quiz_mode":
    if S.qq:
        it = S.qq[S.qi]
        st.markdown(f"<div class='question-card'><b>שאלה {S.qi+1} מתוך {len(S.qq)}:</b><br>{it['q']}</div>", unsafe_allow_html=True)
        ans = st.radio("בחר תשובה:", it['options'], key=f"q_{S.qi}")
        c1, c2 = st.columns(2)
        if c1.button("🔍 בדוק"):
            if ans
