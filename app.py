# גרסה: 1098 | תאריך: 16/02/2026 | שעה: 11:15 | סטטוס: תיקון SyntaxError וסגירת קוד מלאה

import streamlit as st
import google.generativeai as genai
import json, re, time

st.set_page_config(page_title="מתווך בקליק", layout="centered")

# עיצוב UI
st.markdown("""
<style>
    * { direction: rtl !important; text-align: right !important; }
    .stApp { background-color: #ffffff; }
    .welcome-text { color: #1E88E5; font-weight: bold; margin-bottom: 10px; }
    .lesson-title { color: #1E88E5; border-bottom: 2px solid #1E88E5; padding-bottom: 10px; margin-bottom: 20px; font-size: 1.8rem; }
    .lesson-box { 
        background-color: #f9f9f9; padding: 30px; 
        border-right: 6px solid #1E88E5; border-radius: 4px; 
        line-height: 1.8; font-size: 1.1rem;
    }
    .question-card { background-color: #ffffff; padding: 25px; border: 1px solid #e0e0e0; border-radius: 12px; margin-bottom: 20px; }
    .stButton>button { width: auto; min-width: 140px; }
    .version-footer { color: #bbbbbb; font-size: 0.7rem; text-align: center !important; margin-top: 50px; }
</style>
""", unsafe_allow_html=True)

# אתחול קשיח של Session State
for key in ['step', 'user', 'sub_topics', 'lt', 'current_topic', 'current_sub', 'qq', 'qi', 'score', 'answered']:
    if key not in st.session_state:
        if key in ['score', 'qi']: st.session_state[key] = 0
        elif key == 'answered': st.session_state[key] = False
        elif key in ['sub_topics', 'qq']: st.session_state[key] = []
        elif key == 'step': st.session_state[key] = 'login'
        else: st.session_state[key] = ''

S = st.session_state

def fetch_content(prompt):
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-2.0-flash')
    try:
        r = model.generate_content(prompt)
        return r.text
    except: return None

# מפת נושאים מהירה
TOPIC_MAP = {
    "חוק המתווכים במקרקעין": ["דרישת הכתב ופעולה יעילה", "איסור פעולות משפטיות", "דמי תיווך ובלעדיות"],
    "חוק המקרקעין": ["סוגי בעלות ושיתוף", "עסקאות ורישום בטאבו", "הערות אזהרה"],
    "חוק המכר (דירות)": ["מפרט המכר", "תקופת בדק ואחריות", "חובת גילוי של המוכר"],
    "אתיקה מקצועית": ["חובת הגינות וזהירות", "ניגוד עניינים", "פרסום והתנהגות מקצועית"],
    "חוק החוזים": ["הצעה וקיבול", "טעות והטעיה", "תרופות בשל הפרת חוזה"],
    "מיסוי מקרקעין": ["מס שבח", "מס רכישה", "פטורים לדירה יחידה"]
}

st.title("🏠 מתווך בקליק")

if S.step == "login":
    st.write("### ברוכים הבאים! אנא הזדהו כדי להתחיל.")
    u_input = st.text_input("שם מלא:")
    if st.button("כניסה למערכת"):
        if u_input:
            S.user = u_input; S.step = "menu"; st.rerun()

elif S.step == "menu":
    st.markdown(f"<h2 class='welcome-text'>שלום, {S.user}</h2>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    if c1.button("📚 לימוד לפי נושאים"): S.step = "study"; st.rerun()
    if c2.button("⏱️ סימולציית מבחן"):
        S.update({'current_topic': "מבחן כללי", 'step': "quiz_prep", 'score': 0, 'qi': 0}); st.rerun()

elif S.step == "study":
    st.markdown(f"**תלמיד:** {S.user}")
    topics = ["בחר נושא...", "חוק המתווכים במקרקעין", "חוק המקרקעין", "חוק המכר (דירות)", "אתיקה מקצועית", "חוק החוזים", "מיסוי מקרקעין"]
    sel = st.selectbox("בחר נושא ראשי:", topics)
    
    if sel != "בחר נושא..." and st.button("📖 כניסה לשיעור"):
        S.update({'sub_topics': TOPIC_MAP.get(sel, ["נושא א", "נושא ב", "נושא ג"]), 'current_topic': sel, 'lt': ""}); st.rerun()
    
    if S.sub_topics:
        st.write("---")
        cols = st.columns(len(S.sub_topics))
        for i, sub in enumerate(S.sub_topics):
            if cols[i].button(sub, key=f"s_{i}"):
                with st.spinner(f"טוען את {sub}..."):
                    res = fetch_content(f"כתוב שיעור מקיף על '{sub}' עבור מבחן המתווכים. כלול סעיף חוק ודוגמה.")
                    if res: S.lt = res; S.current_sub = sub; st.rerun()

    if S.lt:
        st.markdown(f"<h2 class='lesson-title'>{S.current_sub}</h2>", unsafe_allow_html=True)
        st.markdown(f"<div class='lesson-box'>{S.lt}</div>", unsafe_allow_html=True)
        if st.button("✍️ סיום ומעבר לתרגול"): S.update({'step': "quiz_prep", 'score': 0, 'qi': 0}); st.rerun()
    if st.button("🏠 חזרה"): S.update({'step': "menu", 'sub_topics': [], 'lt': ""}); st.rerun()

elif S.step == "quiz_prep":
    with st.spinner("מייצר שאלון..."):
        p = f"צור 10 שאלות אמריקאיות על {S.current_topic}. החזר JSON בלבד: " + "[{'q':'','options':['','','',''],'correct':'','reason':''}]"
        res = fetch_content(p)
        if res:
            match = re.search(r'\[.*\]', res, re.DOTALL)
            if match:
                S.update({'qq': json.loads(match.group()), 'qi': 0, 'score': 0, 'answered': False, 'step': "quiz"}); st.rerun()
    S.step = "menu"; st.rerun()

elif S.step == "quiz":
    q = S.qq[S.qi]
    st.markdown(f"**שאלה {S.qi + 1} מתוך {len(S.qq)}**")
    st.markdown(f"<div class='question-card'>{q['q']}</div>", unsafe_allow_html=True)
    ans = st.radio("בחר תשובה:", q['options'], key=f"quiz_{S.qi}", index=None, disabled=S.answered)
    
    c1, c2, c3 = st.columns(3)
    if c1.button("🔍 בדוק", disabled=S.answered):
        if ans: S.answered = True; st.rerun()
    
    if S.answered:
        if ans == q['correct']:
            st.success(f"**נכון!** {q['reason']}")
            if 'l_qi' not in S or S.l_qi != S.qi: S.score += 1; S.l_qi = S.qi
        else: st.error(f"**טעות.** הנכון: {q['correct']}. \n\n {q['reason']}")
        
        lbl = "לשאלה הבאה ➡️" if S.qi < len(S.qq) - 1 else "🏁 סיום"
        if st.button(lbl):
            if S.qi < len(S.qq) - 1: S.qi += 1; S.answered = False; st.rerun()
            else: S.step = "results"; st.rerun()
    if c3.button("🏠 חזרה"): S.step = "menu"; st.rerun()

elif S.step == "results":
    st.balloons()
    st.markdown(f"## {S.user}, הנה הציון:")
    st.metric("ציון", f"{int((S.score/len(S.qq))*100)}%", f"{S.score}/{len(S.qq)}")
    if st.button("🏠 חזרה לתפריט"): S.update({'step': "menu", 'qq': []}); st.rerun()

st.markdown(f"<div class='version-footer'>גרסה: 1098 | 16/02/2026 11:15</div>", unsafe_allow_html=True)
