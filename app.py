# גרסה: 1083 | תאריך: 16/02/2026 | שעה: 13:15 | סטטוס: תיקון Syntax בשורה 106

import streamlit as st
import google.generativeai as genai
import json, re, time

st.set_page_config(page_title="מתווך בקליק", layout="centered")

st.markdown("""
<style>
    * { direction: rtl !important; text-align: right !important; }
    .lesson-box { background-color: #f0f2f6; padding: 20px; border-radius: 10px; margin-bottom: 20px; }
    .question-card { background-color: #ffffff; padding: 25px; border-radius: 12px; border: 1px solid #ddd; margin-bottom: 20px; }
    .version-footer { color: #888888; font-size: 0.8rem; text-align: center !important; margin-top: 50px; }
    .q-count { color: #1E88E5; font-weight: bold; margin-bottom: 10px; font-size: 1.1rem; }
</style>
""", unsafe_allow_html=True)

S = st.session_state
if 'step' not in S:
    S.update({'user': '', 'step': 'login', 'lt': '', 'qi': 0, 'qq': [], 'current_topic': ''})

def fetch_content_with_retry(prompt, retries=3):
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-2.0-flash')
        for i in range(retries):
            try:
                r = model.generate_content(prompt)
                return r.text
            except Exception:
                if i < retries - 1:
                    time.sleep(2)
                    continue
                else: raise
    except Exception as e:
        st.error(f"שגיאת תקשורת: {str(e)}")
        return ""

st.title("🏠 מתווך בקליק")

if S.step == "login":
    u = st.text_input("שם מלא:")
    if st.button("כניסה"):
        if u: S.user = u; S.step = "menu"; st.rerun()

elif S.step == "menu":
    st.write(f"### שלום, {S.user}")
    if st.button("📚 לימוד לפי נושאים", use_container_width=True):
        S.step = "study"; st.rerun()
    if st.button("⏱️ סימולציית מבחן", use_container_width=True):
        S.current_topic = "מבחן כללי"; S.step = "quiz_prep"; st.rerun()

elif S.step == "study":
    topics = [
        "חוק המתווכים במקרקעין", 
        "חוק המקרקעין", 
        "חוק המכר (דירות)", 
        "חוק הגנת הצרכן", 
        "אתיקה מקצועית", 
        "חוק החוזים", 
        "מיסוי מקרקעין", 
        "חוק התכנון והבנייה", 
        "חוק הגנת הדייר", 
        "חוק הירושה"
    ]
    sel = st.selectbox("בחר נושא:", topics)
    if st.button("📖 התחל שיעור"):
        with st.spinner("מייצר שיעור..."):
            res = fetch_content_with_retry(f"כתוב שיעור קצר וממוקד על {sel} עבור מבחן המתווכים 2026.")
            if res:
                S.lt = res; S.current_topic = sel; st.rerun()
    
    if S.lt:
        st.markdown(f"<div class='lesson-box'>{S.lt}</div>", unsafe_allow_html=True)
        if st.button("✍️ עבור לשאלות תרגול"):
            S.step = "quiz_prep"; st.rerun()
    
    if st.button("🏠 חזרה לתפריט"):
        S.lt = ""; S.step = "menu"; st.rerun()

elif S.step == "quiz_prep":
    with st.spinner("מייצר 10 שאלות תרגול..."):
        p = f"צור 10 שאלות אמריקאיות על {S.current_topic}. החזר JSON בלבד: " + "[{'q':'','options':['','','',''],'correct':'','reason':''}]"
        res = fetch_content_with_retry(p)
        match = re.search(r'\[.*\]', res, re.DOTALL)
        if match:
            S.qq = json.loads(match.group())
            S.qi = 0; S.step = "quiz"; st.rerun()
        else:
            st.error("תקלה בייצור השאלות."); S.step = "menu"; st.rerun()

elif S.step == "quiz":
    if S.qq:
        q = S.qq[S.qi]
        total_q = len(S.qq)
        st.markdown(f"<div class='q-count'>שאלה {S.qi + 1} מתוך {total_q}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='question-card'><b>{q['q']}</b></div>", unsafe_allow_html=True)
        ans = st.radio("בחר תשובה:", q['options'], key=f"q_{S.qi}", index=None)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔍 בדוק"):
                if ans:
                    if ans == q['correct']: st.success(f"נכון! {q['reason']}")
                    else: st.error(f"טעות. הנכון: {q['correct']}")
                else: st.warning("אנא בחר תשובה.")
        with col2:
            if st.button("🏠 חזרה לתפריט"):
                S.step = "menu"; S.lt = ""; S.qq = []; st.rerun()
        
        if st.button("השאלה הבאה ➡️"):
            if S.qi < total_q - 1:
                S.qi += 1; st.rerun()
            else:
                st.success("סיימת את השאלון!"); time.sleep(2); S.step = "menu"; S.lt = ""; st.rerun()

st.markdown(f"<div class='version-footer'>גרסה: 1083 | 16/02/2026 13:15</div>", unsafe_allow_html=True)
