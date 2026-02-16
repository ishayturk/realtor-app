# גרסה: 1100 | תאריך: 16/02/2026 | שעה: 12:00 | סטטוס: קוד שלם ללא חיתוכים

import streamlit as st
import google.generativeai as genai
import json, re, time

st.set_page_config(page_title="מתווך בקליק", layout="centered")

st.markdown("""
<style>
    * { direction: rtl !important; text-align: right !important; }
    .stApp { background-color: #ffffff; }
    .welcome-text { color: #1E88E5; font-weight: bold; margin-bottom: 10px; font-size: 2rem; }
    .lesson-title { color: #1E88E5; border-bottom: 2px solid #1E88E5; padding-bottom: 10px; margin-bottom: 20px; font-size: 1.8rem; }
    .lesson-box { 
        background-color: #f9f9f9; padding: 30px; border-right: 6px solid #1E88E5; 
        border-radius: 4px; line-height: 1.8; font-size: 1.1rem;
    }
    .question-card { background-color: #ffffff; padding: 25px; border: 1px solid #e0e0e0; border-radius: 12px; margin-bottom: 20px; }
    .stButton>button { width: auto; min-width: 150px; }
    .version-footer { color: #bbbbbb; font-size: 0.7rem; text-align: center !important; margin-top: 50px; }
</style>
""", unsafe_allow_html=True)

S = st.session_state
for k in ['step','user','sub_topics','lt','current_topic','current_sub','qq','qi','score','ans_done']:
    if k not in S:
        if k in ['score','qi']: S[k]=0
        elif k=='ans_done': S[k]=False
        elif k in ['sub_topics','qq']: S[k]=[]
        elif k=='step': S[k]='login'
        else: S[k]=''

def ask_ai(p):
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    m = genai.GenerativeModel('gemini-2.0-flash')
    try:
        r = m.generate_content(p)
        return r.text
    except: return None

T_MAP = {
    "חוק המתווכים": ["דרישת הכתב ופעולה יעילה", "איסור פעולות משפטיות", "דמי תיווך ובלעדיות"],
    "חוק המקרקעין": ["סוגי בעלות ושיתוף", "עסקאות ורישום בטאבו", "הערות אזהרה"],
    "חוק המכר (דירות)": ["מפרט המכר וחובות המוכר", "תקופת בדק ואחריות", "הבטחת השקעות"],
    "חוק הגנת הצרכן": ["הטעיה וניצול מצוקה", "ביטול עסקה", "חובת גילוי"],
    "אתיקה מקצועית": ["חובת הגינות וזהירות", "ניגוד עניינים", "פרסום והתנהגות"],
    "חוק החוזים": ["כריתת חוזה", "פגמים בכריתה", "תרופות בשל הפרה"],
    "מיסוי מקרקעין": ["מס שבח", "מס רכישה", "פטורים לדירה יחידה"],
    "חוק התכנון והבנייה": ["מוסדות התכנון", "היתרי בנייה", "היטל השבחה"],
    "חוק הגנת הדייר": ["דיירות מוגנת", "עילות פינוי", "זכויות דייר ממשיך"],
    "חוק הירושה": ["ירושה על פי דין", "צוואות", "ניהול עיזבון"]
}

st.title("🏠 מתווך בקליק")

if S.step == "login":
    u_in = st.text_input("שם מלא:")
    if st.button("כניסה"):
        if u_in: S.user=u_in; S.step="menu"; st.rerun()

elif S.step == "menu":
    st.markdown(f"<h2 class='welcome-text'>שלום, {S.user}</h2>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    if c1.button("📚 לימוד לפי נושאים"): S.step="study"; st.rerun()
    if c2.button("⏱️ סימולציית מבחן"):
        S.update({'current_topic':"מבחן כללי",'step':"q_prep",'score':0,'qi':0}); st.rerun()

elif S.step == "study":
    st.write(f"**תלמיד:** {S.user}")
    sel = st.selectbox("בחר נושא:", ["בחר..."] + list(T_MAP.keys()))
    if sel != "בחר..." and st.button("📖 כניסה לשיעור"):
        S.update({'sub_topics':T_MAP[sel],'current_topic':sel,'lt':""}); st.rerun()
    if S.sub_topics:
        st.write("---")
        cols = st.columns(len(S.sub_topics))
        for i, sub in enumerate(S.sub_topics):
            if cols[i].button(sub, key=f"btn_{i}"):
                with st.spinner(f"טוען {sub}..."):
                    res = ask_ai(f"כתוב שיעור מקיף על '{sub}' למבחן המתווכים. כלול סעיפי חוק ודוגמה.")
                    if res: S.lt=res; S.current_sub=sub; st.rerun()
    if S.lt:
        st.markdown(f"<h2 class='lesson-title'>{S.current_sub}</h2>", unsafe_allow_html=True)
        st.markdown(f"<div class='lesson-box'>{S.lt}</div>", unsafe_allow_html=True)
        if st.button("✍️ תרגול שאלות בנושא זה"):
            S.update({'step
