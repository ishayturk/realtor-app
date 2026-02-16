# גרסה: 1094 | תאריך: 16/02/2026 | שעה: 16:40 | סטטוס: תיקון לוגיקת הצגת שיעור יציבה

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
        background-color: #ffffff; padding: 30px; 
        border-right: 6px solid #1E88E5; border-radius: 4px; 
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        margin-top: 20px; line-height: 1.8; font-size: 1.1rem;
    }
    .stButton>button { width: auto; min-width: 140px; }
    .version-footer { color: #bbbbbb; font-size: 0.7rem; text-align: center !important; margin-top: 50px; }
</style>
""", unsafe_allow_html=True)

# אתחול Session State
for key in ['user', 'step', 'sub_topics', 'lt', 'current_topic', 'qq', 'qi']:
    if key not in st.session_state:
        st.session_state[key] = '' if key != 'sub_topics' and key != 'qq' else []
if not st.session_state.step: st.session_state.step = 'login'

S = st.session_state

def fetch_content(prompt):
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-2.0-flash')
    try:
        r = model.generate_content(prompt)
        return r.text
    except: return None

st.title("🏠 מתווך בקליק")

if S.step == "login":
    u = st.text_input("שם מלא:", value=S.user)
    if st.button("כניסה"):
        if u: S.user = u; S.step = "menu"; st.rerun()

elif S.step == "menu":
    st.write(f"### שלום, {S.user}")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📚 לימוד לפי נושאים"): S.step = "study"; st.rerun()
    with col2:
        if st.button("⏱️ סימולציית מבחן"):
            S.current_topic = "כלל נושאי בחינת המתווכים"; S.step = "quiz_prep"; st.rerun()

elif S.step == "study":
    topics = ["חוק המתווכים במקרקעין", "חוק המקרקעין", "חוק המכר (דירות)", "חוק הגנת הצרכן", "אתיקה מקצועית", "חוק החוזים", "מיסוי מקרקעין", "חוק התכנון והבנייה", "חוק הגנת הדייר", "חוק הירושה"]
    sel = st.selectbox("בחר נושא ראשי:", topics)
    
    if st.button("📖 כניסה לשיעור"):
        with st.spinner("מנתח נושא..."):
            res = fetch_content(f"עבור {sel}, החזר רשימה של 3 תתי-נושאים קריטיים בלבד (מופרדים בפסיק).")
            if res:
                S.sub_topics = [x.strip() for x in res.split(',')]
                S.current_topic = sel
                S.lt = "" # איפוס טקסט ישן כשנכנסים לנושא חדש
                st.rerun()
    
    # הצגת תתי הנושאים אם הם קיימים ב-State
    if S.sub_topics:
        st.write("---")
        st.write(f"### פרקים ב{S.current_topic}:")
        cols = st.columns(len(S.sub_topics))
        for i, sub in enumerate(S.sub_topics):
            if cols[i].button(sub, key=f"btn_{sub}_{i}"):
                with st.spinner(f"טוען את {sub}..."):
                    content = fetch_content(f"כתוב שיעור מקיף ומקצועי על '{sub}' עבור מבחן המתווכים. כלול סעיפי חוק רלוונטיים ודוגמה אחת.")
                    if content:
                        S.lt = content
                        st.rerun()

    if S.lt:
        st.markdown(f"<div class='lesson-box'>{S.lt}</div>", unsafe_allow_html=True)
        if st.button("✍️ תרגול שאלות בנושא זה"):
            S.step = "quiz_prep"; st.rerun()

    if st.button("🏠 חזרה לתפריט"):
        S.step = "menu"; S.sub_topics = []; S.lt = ""; st.rerun()

elif S.step == "quiz_prep":
    with st.spinner("מייצר שאלות..."):
        p = f"צור 10 שאלות אמריקאיות על {S.current_topic}. החזר JSON בלבד: " + "[{'q':'','options':['','','',''],'correct':'','reason':''}]"
        res = fetch_content(p)
        if res:
            match = re.search(r'\[.*\]', res, re.DOTALL)
            if match:
                S.qq = json.loads(match.group()); S.qi = 0; S.step = "quiz"; st.rerun()
    S.step = "menu"; st.rerun()

elif S.step == "quiz":
    q = S.qq[S.qi]
    st.markdown(f"**שאלה {S.qi + 1} מתוך {len(S.qq)}**")
    st.markdown(f"<div class='question-card'>{q['q']}</div>", unsafe_allow_html=True)
    ans = st.radio("בחר תשובה:", q['options'], key=f"q_{S.qi}", index=None)
    
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("🔍 בדוק"):
            if ans == q['correct']: st.success(f"נכון! {q['reason']}")
            else: st.error(f"טעות. הנכון: {q['correct']}")
    with c2:
        if st.button("השאלה הבאה ➡️"):
            if S.qi < len(S.qq)-1: S.qi += 1; st.rerun()
            else: st.success("סיימת!"); time.sleep(1); S.step = "menu"; st.rerun()
    with c3:
        if st.button("🏠 חזרה"): S.step = "menu"; st.rerun()

st.markdown(f"<div class='version-footer'>גרסה: 1094 | 16/02/2026 16:40</div>", unsafe_allow_html=True)
