# ==========================================
# Project: מתווך בקליק
# Version: 1117
# Last Updated: 2026-02-16
# ==========================================

import streamlit as st
import google.generativeai as genai
import json, re, time

# הגדרות דף
st.set_page_config(page_title="מתווך בקליק", layout="centered")

# עיצוב UI
st.markdown("""
<style>
    * { direction: rtl; text-align: right; }
    .lesson-box { 
        background: #f9f9f9; padding: 25px; border-right: 6px solid #1E88E5; 
        line-height: 1.8; margin-top: 10px; border-radius: 5px;
    }
    .stButton>button { width: 100%; }
    .user-label { 
        font-size: 1rem; color: #666; padding: 5px 0; 
        border-bottom: 1px solid #eee; margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# ניהול State
S = st.session_state
for k in ['step','user','subs','lt','topic','sub_n','qq','qi','score','ans_d','l_qi']:
    if k not in S:
        if k in ['score','qi']: S[k] = 0
        elif k == 'ans_d': S[k] = False
        elif k in ['subs','qq']: S[k] = []
        elif k == 'step': S[k] = 'login'
        else: S[k] = ''

def ask_ai(p):
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    m = genai.GenerativeModel('gemini-2.0-flash')
    for attempt in range(2):
        try:
            r = m.generate_content(p)
            if r and r.text: return r.text
        except:
            time.sleep(1)
    return None

def reset_to_home():
    S.step = 'menu'
    S.subs = []
    S.lt = ""
    S.sub_n = ""
    S.topic = ""
    S.qq = []
    S.qi = 0
    S.ans_d = False

# מפת נושאים
T_MAP = {
    "חוק המתווכים": ["דרישת הכתב בחוזה תיווך", "פעולה כגורם יעיל בעסקה", "דמי תיווך ותקופת בלעדיות"],
    "חוק המקרקעין": ["זכויות בעלות ושיתוף", "רישום בפנקסי מקרקעין", "רישום הערות אזהרה במקרקעין"],
    "חוק המכר (הבטחת השקעות)": ["שיטות ליווי בנקאי", "מתן ערבויות חוק המכר", "תשלום באמצעות פנקס שוברים"],
    "חוק המכר (דירות)": ["מפרט המכר וצירופו לחוזה", "תקופת בדק ואחריות קבלן", "אחריות המוכר לתיקון אי התאמה"],
    "חוק הגנת הצרכן": ["איסור הטעיה וניצול מצוקה", "ביטול עסקת מכר מרחוק", "חובת גילוי מידע לצרכן"],
    "חוק החוזים (כללי)": ["תהליך כריתת חוזה", "פגמים בכריתת חוזה", "צורת החוזה ותוקפו המשפטי"],
    "חוק החוזים (תרופות)": ["אכיפת חוזה שהופר", "ביטול חוזה בשל הפרה", "פיצויים בגין הפרת חוזה"],
    "חוק העונשין": ["עבירות שוחד", "קבלת דבר במרמה", "זיוף מסמכים ותעודות"],
    "תמ\"א 38": ["רוב דרוש לביצוע הפרויקט", "זכויות בנייה והטבות מס", "מיגון וחיזוק מבנים קיימים"],
    "תכנון ובנייה": ["מוסדות תכנון ובנייה", "תהליך קבלת היתרי בנייה", "חובת תשלום היטל השבחה"],
    "מיסוי מקרקעין": ["חישוב מס שבח", "חובת תשלום מס רכישה", "פטורים ממס במכירת דירה"],
    "יחסי ממון": ["הסדר איזון משאבים", "עריכת הסכמי ממון", "זכויות בדירת המגורים המשותפת"],
    "חוק הירושה": ["ירושה על פי דין", "עריכת צוואות חוקיות", "מינוי וניהול עיזבון"],
    "הגנת הדייר": ["זכויות דיירות מוגנת", "תשלום דמי מפתח", "עילות פינוי דייר מוגן"],
    "חוק הוצאה לפועל": ["ביצוע עיקולי מקרקעין", "כינוס נכסים למכירה", "חקירת יכולת כלכלית לחייב"],
    "חוק שמאי מקרקעין": ["חובת רישוי שמאי", "אתיקה מקצועית בשמאות", "כללי עריכת שומת מקרקעין"]
}

if S.user:
    st.markdown(f"<div class='user-label'>👤 תלמיד/ה: {S.user}</div>", unsafe_allow_html=True)

st.title("🏠 מתווך בקליק")

if S.step == 'login':
    u = st.text_input("הזן שם מלא לכניסה:")
    if st.button("כניסה למערכת"):
        if u: S.user=u; S.step='menu'; st.rerun()

elif S.step == 'menu':
    c1, c2 = st.columns(2)
    with c1:
        if st.button("📚 לימוד לפי נושאים"): S.step='study'; st.rerun()
    with c2:
        if st.button("⏱️ סימולציית בחינה מלאה"): S.topic="כללי"; S.step='q_prep'; st.rerun()

elif S.step == 'study':
    sel = st.selectbox("בחר נושא לימוד מהרשימה:", ["בחר..."] + list(T_MAP.keys()))
    if sel != "בחר..." and st.button("📖 טען נושא"):
        S.subs=T_MAP[sel]; S.topic=sel; S.lt=""; S.sub_n=""; st.rerun()
    
    if S.subs:
        st.write("---")
        st.markdown(f"### {S.topic} - פרקי הלימוד")
        cols = st.columns(len(S.subs))
        for i, s in enumerate(S.subs):
            if cols[i].button(s, key=f"btn_{i}"):
                with st.spinner(f"טוען את השיעור: {s}..."):
                    res = ask_ai(f"שיעור מפורט על {s} למבחן המתווכים כולל סעיפי חוק.")
                    if res: S.lt=res; S.sub_n=s; st.rerun()
    
    if S.lt:
        st.markdown(f"## {S.sub_n}")
        st.markdown(f"<div class='lesson-box'>{S.lt}</div>", unsafe_allow_html=True)
        
        st.write(" ")
        bc1, bc2 = st.columns(2)
        with bc1:
            if st.button("⬆️ חזרה לראש העמוד"): st.rerun()
        with bc2:
            if st.button("✍️ תרגול שאלות בפרק זה"): S.step='q_prep'; st.rerun()
    
    st.write("---")
    if st.button("🏠 חזרה לתפריט הראשי"): reset_to_home(); st.rerun()

elif S.step == 'q_prep':
    with st.spinner(f"ה-AI בונה עבורך שאלות תרגול על {S.topic}..."):
        p = f"צור 10 שאלות על {S.topic}. החזר JSON בלבד: " + "[{'q':'','options':['','','',''],'correct':'','reason':''}]"
        res = ask_ai(p)
        if res:
            try:
                m = re.search(r'\[.*\]', res, re.DOTALL)
                if m: 
                    S.qq=json.loads(m.group()); S.qi=0; S.score=0; S.ans_d=False; S.step='quiz'; st.rerun()
            except:
                st.error("תקלה בעיבוד השאלות."); time.sleep(1); st.rerun()
    st.error("חוסר תגובה מה-AI. חוזר הביתה..."); time.sleep(2); reset_to_home(); st.rerun()

elif S.step == 'quiz':
    q = S.qq[S.qi]
    st.info(f"שאלה {S.qi+1}/10: {q['q']}")
    ans = st.radio("בחר תשובה:", q['options'], key=f"r{S.qi}", index=None, disabled=S.ans_d)
    if st.button("🔍 בדוק תשובה", disabled=S.ans_d):
        if ans: S.ans_d=True; st.rerun()
    if S.ans_d:
        if ans == q['correct']:
            st.success(f"נכון! {q['reason']}")
            if not hasattr(S, 'l_qi') or S.l_qi != S.qi: S.score += 1; S.l_qi = S.qi
        else: st.error(f"טעות. הנכון: {q['correct']}. {q['reason']}")
        if st.button("הבא ➡️" if S.qi < 9 else "🏁 סיום"):
            if S.qi < 9: S.qi += 1; S.ans_d = False; st.rerun()
            else: S.step = 'results'; st.rerun()

elif S.step == 'results':
    st.balloons()
    st.metric("ציון סופי", f"{S.score*10}%", f"{S.score}/10")
    if st.button("🏠 חזרה לתפריט הראשי"): reset_to_home(); st.rerun()
