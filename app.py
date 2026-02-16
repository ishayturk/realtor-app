# גרסה 1067 | 16/02/2026 | 10:45

import streamlit as st
import google.generativeai as genai
import json, re, time

st.set_page_config(page_title="מתווך בקליק", layout="centered")

st.markdown("""
<style>
    * { direction: rtl !important; text-align: right !important; }
    .lesson-box { background-color: #fdfdfd; padding: 25px; border-radius: 12px; border-right: 6px solid #1E88E5; line-height: 1.8; margin-bottom: 20px; }
    .question-card { background-color: #ffffff; padding: 25px; border-radius: 12px; border: 1px solid #e0e0e0; margin-bottom: 20px; }
    .main-header { background: #1E88E5; color: white; padding: 15px; border-radius: 10px; text-align: center; margin-bottom: 15px; font-size: 24px; }
</style>
""", unsafe_allow_html=True)

S = st.session_state
if 'step' not in S:
    S.update({'user':'','step':'login','lt':'','qi':0,'qq':[],'current_topic':''})

def fetch_exam_content(topic, num=5):
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-1.5-flash') # שימוש במודל מהיר יותר ויציב למכסות
        p = f"התבסס על חומרי רשם המתווכים 2026. צור {num} שאלות רב-ברירה על {topic}. החזר אך ורק JSON נקי: " + "[{'q':'','options':['א','ב','ג','ד'],'correct':'','reason':''}]"
        r = model.generate_content(p)
        m = re.search(r'\[.*\]', r.text, re.DOTALL)
        return json.loads(m.group()) if m else []
    except:
        return []

st.markdown("<div class='main-header'>🏠 מתווך בקליק</div>", unsafe_allow_html=True)

if S.step == "login":
    u = st.text_input("שם מלא:")
    if st.button("כניסה"):
        if u: S.user = u; S.step = "menu"; st.rerun()

elif S.step == "menu":
    st.markdown(f"### שלום, {S.user} 👋")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("📚 למידה לפי נושאים", use_container_width=True): S.step = "study"; st.rerun()
    with c2:
        if st.button("⏱️ סימולציית בחינה", use_container_width=True): 
            with st.spinner("מייצר בחינה..."):
                d = fetch_exam_content("כללי", num=10)
                if d: S.qq, S.qi, S.step = d, 0, "quiz_mode"; st.rerun()

elif S.step == "study":
    all_t = ["חוק המתווכים במקרקעין", "תקנות המתווכים (פרטי הזמנה)", "אתיקה מקצועית", "חוק המקרקעין", "חוק המכר (דירות)", "חוק הגנת הצרכן"]
    if not S.lt:
        sel = st.selectbox("בחר נושא:", all_t)
        if st.button("📖 צור שיעור", use_container_width=True):
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            model = genai.GenerativeModel('gemini-1.5-flash')
            res = model.generate_content(f"כתוב שיעור ל-2026 על {sel}.", stream=True)
            ph, full_text = st.empty(), ""
            for chunk in res:
                full_text += chunk.text
                ph.markdown(f"<div class='lesson-box'>{full_text}</div>", unsafe_allow_html=True)
            S.lt, S.current_topic = full_text, sel; st.rerun()
    else:
        st.markdown(f"<div class='lesson-box'>{S.lt}</div>", unsafe_allow_html=True)
        if st.button("✍️ עבור לשאלון תרגול", use_container_width=True):
            with st.spinner("מייצר שאלות..."):
                # מחכה שנייה אחת כדי לתת ל-API לנשום מהשיעור
                time.sleep(1)
                q_data = fetch_exam_content(S.current_topic, num=5)
                if q_data:
                    S.qq, S.qi, S.step = q_data, 0, "quiz_mode"
                    st.rerun()
                else: st.error("ה-API עמוס. המתן 5 שניות ולחץ שוב.")
        if st.button("🏠 חזרה"): S.lt = ""; st.rerun()

elif S.step == "quiz_mode":
    if S.qq:
        it = S.qq[S.qi]
        st.markdown(f"<div class='question-card'><b>שאלה {S.qi+1}:</b><br>{it['q']}</div>", unsafe_allow_html=True)
        ans = st.radio("תשובה:", it['options'], key=f"q_{S.qi}")
        c1, c2 = st.columns(2)
        if c1.button("🔍 בדוק"):
            if ans == it['correct']: st.success(f"נכון! {it.get('reason','')}")
            else: st.error(f"טעות. הנכון: {it['correct']}")
        if c2.button("הבא ➡️"):
            if S.qi < len(S.qq)-1: S.qi += 1; st.rerun()
            else: S.step = "menu"; S.qq = []; st.rerun()
