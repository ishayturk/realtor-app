import streamlit as st
import google.generativeai as genai
import json
import re

st.set_page_config(page_title="מתווך בקליק", layout="centered")

st.markdown("""
<style>
    * { direction: rtl !important; text-align: right !important; }
    .lesson-box { background-color: #f0f2f6; padding: 20px; border-radius: 10px; margin-bottom: 20px; }
    .question-card { background-color: #ffffff; padding: 20px; border-radius: 10px; border: 1px solid #ddd; margin-bottom: 20px; }
</style>
""", unsafe_allow_html=True)

S = st.session_state
if 'step' not in S:
    S.update({'user': '', 'step': 'login', 'lt': '', 'qi': 0, 'qq': [], 'current_topic': ''})

def fetch_content(prompt):
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        # מעבר למודל 2.0 פלאש כפי שביקשת
        model = genai.GenerativeModel('gemini-2.0-flash')
        r = model.generate_content(prompt)
        return r.text
    except Exception as e:
        st.error(f"שגיאה: {str(e)}")
        return ""

st.title("🏠 מתווך בקליק")

if S.step == "login":
    u = st.text_input("שם מלא:")
    if st.button("כניסה"):
        if u:
            S.user = u
            S.step = "menu"
            st.rerun()

elif S.step == "menu":
    st.write(f"### שלום, {S.user}")
    if st.button("📚 לימוד לפי נושאים", use_container_width=True):
        S.step = "study"
        st.rerun()
    if st.button("⏱️ סימולציית מבחן", use_container_width=True):
        S.current_topic = "מבחן כללי"
        S.step = "quiz_prep"
        st.rerun()

elif S.step == "study":
    topics = ["חוק המתווכים במקרקעין", "חוק המקרקעין", "חוק המכר (דירות)", "חוק הגנת הצרכן", "אתיקה מקצועית"]
    sel = st.selectbox("בחר נושא:", topics)
    if st.button("📖 התחל שיעור"):
        with st.spinner("מייצר שיעור..."):
            res = fetch_content(f"כתוב שיעור קצר וממוקד על {sel} עבור מבחן המתווכים 2026.")
            if res:
                S.lt = res
                S.current_topic = sel
                st.rerun()
    
    if S.lt:
        st.markdown(f"<div class='lesson-box'>{S.lt}</div>", unsafe_allow_html=True)
        if st.button("✍️ עבור לשאלות תרגול"):
            S.step = "quiz_prep"
            st.rerun()
    
    if st.button("🏠 חזרה לתפריט"):
        S.lt = ""
        S.step = "menu"
        st.rerun()

elif S.step == "quiz_prep":
    with st.spinner("מייצר שאלות..."):
        p = f"צור 5 שאלות אמריקאיות על {S.current_topic}. החזר JSON בלבד במבנה: " + "[{'q':'','options':['','','',''],'correct':'','reason':''}]"
        res = fetch_content(p)
        match = re.search(r'\[.*\]', res, re.DOTALL)
        if match:
            S.qq = json.loads(match.group())
            S.qi = 0
            S.step = "quiz"
            st.rerun()
        else:
            st.error("תקלה בייצור השאלות, נסה שוב.")
            if st.button("חזרה"): S.step = "menu"; st.rerun()

elif S.step == "quiz":
    if S.qq:
        q = S.qq[S.qi]
        st.markdown(f"<div class='question-card'><b>שאלה {S.qi+1}:</b><br>{q['q']}</div>", unsafe_allow_html=True)
        ans = st.radio("בחר תשובה:", q['options'], key=f"q_{S.qi}")
        if st.button("בדוק"):
            if ans == q['correct']:
                st.success(f"נכון! {q['reason']}")
            else:
                st.error(f"טעות. התשובה הנכונה היא: {q['correct']}")
        
        if st.button("השאלה הבאה ➡️"):
            if S.qi < len(S.qq) - 1:
                S.qi += 1
                st.rerun()
            else:
                st.success("סיימת את התרגול!")
                if st.button("חזרה לתפריט"):
                    S.step = "menu"
                    S.lt = ""
                    st.rerun()
