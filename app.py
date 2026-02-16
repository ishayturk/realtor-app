# גרסה: 1092 | תאריך: 16/02/2026 | שעה: 15:35 | סטטוס: תיקון SyntaxError במחרוזות

import streamlit as st
import google.generativeai as genai
import json, re, time

st.set_page_config(page_title="מתווך בקליק", layout="centered")

# עיצוב UI
st.markdown("""
<style>
    * { direction: rtl !important; text-align: right !important; }
    .stApp { background-color: #ffffff; }
    .lesson-box { 
        background-color: #ffffff; 
        padding: 30px; 
        border-right: 6px solid #1E88E5; 
        border-radius: 4px; 
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        margin-top: 20px;
        line-height: 1.8;
        font-size: 1.1rem;
    }
    .question-card { background-color: #ffffff; padding: 25px; border: 1px solid #e0e0e0; border-radius: 12px; margin-bottom: 20px; }
    .version-footer { color: #bbbbbb; font-size: 0.7rem; text-align: center !important; margin-top: 50px; }
    .stButton>button { width: auto; min-width: 140px; }
</style>
""", unsafe_allow_html=True)

S = st.session_state
def init_state():
    defaults = {'user': '', 'step': 'login', 'lt': '', 'qi': 0, 'qq': [], 'current_topic': '', 'sub_topics': []}
    for k, v in defaults.items():
        if k not in S: S[k] = v

init_state()

def fetch_content(prompt):
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-2.0-flash')
    try:
        r = model.generate_content(prompt)
        return r.text
    except Exception:
        return None

st.title("🏠 מתווך בקליק")

if S.step == "login":
    u = st.text_input("שם מלא:")
    if st.button("כניסה"):
        if u: S.user = u; S.step = "menu"; st.rerun()

elif S.step == "menu":
    st.write(f"### שלום, {S.user}")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📚 לימוד לפי נושאים"): S.step = "study"; st.rerun()
    with col2:
        if st.button("⏱️ סימולציית מבחן"):
            S.current_topic = "כלל נושאי בחינת המתווכים (חוק המתווכים, מקרקעין, מיסוי, חוזים)"; 
            S.step = "quiz_prep"; st.rerun()

elif S.step == "study":
    topics = ["חוק המתווכים במקרקעין", "חוק המקרקעין", "חוק המכר (דירות)", "חוק הגנת הצרכן", "אתיקה מקצועית", "חוק החוזים", "מיסוי מקרקעין", "חוק התכנון והבנייה", "חוק הגנת הדייר", "חוק הירושה"]
    sel = st.selectbox("בחר נושא ראשי:", topics)
    
    if st.button("📖 כניסה לשיעור"):
        with st.spinner("מנתח נושא ומכין תתי-נושאים..."):
            res = fetch_content(f"עבור {sel}, החזר רשימה של 3 תתי-נושאים קריטיים בלבד (מופרדים בפסיק).")
            if res:
                S.sub_topics = [x.strip() for x in res.split(',')]
                S.current_topic = sel
                st.rerun()
    
    if S.sub_topics:
        st.write("---")
        st.write("### בחר פרק ללימוד:")
        cols = st.columns(len(S.sub_topics))
        for i, sub in enumerate(S.sub_topics):
            if cols[i].button(sub):
                with st.spinner(f"טוען {sub}..."):
                    content = fetch_content(f"כתוב שיעור מקיף על '{sub}' עבור מבחן המתווכים. כלול סעיפי חוק רלוונטיים ודוגמה אחת.")
                    if content: S.lt = content; st.rerun()
    
    if S.lt:
        st.markdown(f"<div class='lesson-box'>{S.lt}</div>", unsafe_allow_html=True)
        if st.button("✍️ תרגול שאלות בנושא זה"): S.step = "quiz_prep"; st.rerun()

    if st.button("🏠 חזרה לתפריט"):
        S.update({'lt': '', 'step': 'menu', 'sub_topics': []}); st.rerun()

elif S.step == "quiz_prep":
    # התיקון לשורה שגרמה לשגיאה נמצא כאן:
    with st.spinner("מייצר 10 שאלות מותאמות..."):
        p = f"צור 10 שאלות אמריקאיות על {S.current_topic}. החזר JSON בלבד: " + "[{'q':'','options':['','','',''],'correct':'','reason':''}]"
        res = fetch_content(p)
        if res:
            match = re.search(r'\[.*\]', res, re.DOTALL)
            if match:
                S.qq = json.loads(match.group()); S.qi = 0; S.step = "quiz"; st.rerun()
        st.error("תקלה בייצור שאלות."); S.step = "menu"; st.rerun()

elif S.step == "quiz":
    if S.qq:
        q = S.qq[S.qi]
        st.markdown(f"<p style='color:#1E88E5; font-weight:bold;'>שאלה {S.qi + 1} מתוך {len(S.qq)}</p>", unsafe_allow_html=True)
        st.markdown(f"<div class='question-card'><b>{q['q']}</b></div>", unsafe_allow_html=True)
        ans = st.radio("בחר תשובה:", q['options'], key=f"q_{S.qi}", index=None)
        
        c1, c2, c3 = st.columns([1, 1, 1])
        with c1:
            if st.button("🔍 בדוק"):
                if ans:
                    if ans == q['correct']: st.success(f"נכון! {q['reason']}")
                    else: st.error(f"טעות. הנכון: {q['correct']}")
        with c2:
            if st.button("השאלה הבאה ➡️"):
                if S.qi < len(S.qq) - 1: S.qi += 1; st.rerun()
                else: st.success("סיימת!"); time.sleep(1); S.step = "menu"; st.rerun()
        with c3:
            if st.button("🏠 חזרה לתפריט"):
                S.update({'lt': '', 'step': 'menu', 'sub_topics': [], 'qq': []}); st.rerun()

st.markdown(f"<div class='version-footer'>גרסה: 1092 | 16/02/2026 15:35</div>", unsafe_allow_html=True)
