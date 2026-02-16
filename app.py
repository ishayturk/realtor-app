import streamlit as st
import google.generativeai as genai
import json, re, time

st.set_page_config(page_title="מתווך בקליק", layout="centered")

# עיצוב UI קבוע
st.markdown("""
<style>
    * { direction: rtl; text-align: right; }
    .welcome-text { color: #1E88E5; font-size: 2rem; font-weight: bold; }
    .lesson-box { 
        background: #f9f9f9; padding: 25px; border-right: 6px solid #1E88E5; 
        line-height: 1.8; margin-top: 10px;
    }
    .stButton>button { width: 100%; }
    .user-header { background: #e3f2fd; padding: 10px; border-radius: 5px; margin-bottom: 20px; }
</style>
""", unsafe_allow_html=True)

S = st.session_state
for k in ['step','user','subs','lt','topic','sub_n','qq','qi','score','ans_d']:
    if k not in S:
        if k in ['score','qi']: S[k] = 0
        elif k == 'ans_d': S[k] = False
        elif k in ['subs','qq']: S[k] = []
        elif k == 'step': S[k] = 'login'
        else: S[k] = ''

def ask_ai(p):
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    m = genai.GenerativeModel('gemini-2.0-flash')
    try:
        r = m.generate_content(p)
        return r.text if r else None
    except: return None

T_MAP = {
    "חוק המתווכים": ["דרישת הכתב", "פעולה יעילה", "דמי תיווך ובלעדיות"],
    "חוק המקרקעין": ["בעלות ושיתוף", "רישום", "הערות אזהרה"],
    "חוק המכר (הבטחת השקעות)": ["ליווי בנקאי", "ערבויות", "פנקס שוברים"],
    "חוק המכר (דירות)": ["מפרט המכר", "תקופת בדק", "אחריות המוכר"],
    "חוק הגנת הצרכן": ["הטעיה", "ביטול עסקה", "חובת גילוי"],
    "חוק החוזים (כללי)": ["כריתת חוזה", "פגמים בכריתה", "צורת החוזה"],
    "חוק החוזים (תרופות)": ["אכיפה", "ביטול", "פיצויים"],
    "חוק העונשין": ["עבירות שוחד", "קבלת דבר במרמה", "זיוף"],
    "תמ\"א 38": ["רוב דרוש", "זכויות בנייה", "מיגון וחיזוק"],
    "תכנון ובנייה": ["מוסדות תכנון", "היתרי בנייה", "היטל השבחה"],
    "מיסוי מקרקעין": ["מס שבח", "מס רכישה", "פטורים"],
    "יחסי ממון": ["איזון משאבים", "הסכם ממון", "דירת המגורים"],
    "חוק הירושה": ["ירושה על פי דין", "צוואות", "מנהל עיזבון"],
    "הגנת הדייר": ["דיירות מוגנת", "דמי מפתח", "פינוי"],
    "חוק הוצאה לפועל": ["עיקולים", "כינוס נכסים", "חקירת יכולת"],
    "חוק שמאי מקרקעין": ["חובת רישוי", "אתיקה", "שומה למקרקעין"]
}

st.title("🏠 מתווך בקליק")
if S.user:
    st.markdown(f"<div class='user-header'>👤 תלמיד/ה: <b>{S.user}</b></div>", unsafe_allow_html=True)

if S.step == 'login':
    u = st.text_input("שם מלא:")
    if st.button("כניסה"):
        if u: S.user=u; S.step='menu'; st.rerun()

elif S.step == 'menu':
    st.markdown(f"<p class='welcome-text'>שלום, {S.user}</p>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        if st.button("📚 לימוד לפי נושאים"): S.step='study'; st.rerun()
    with c2:
        if st.button("⏱️ סימולציית בחינה מלאה"): S.topic="כללי"; S.step='q_prep'; st.rerun()

elif S.step == 'study':
    sel = st.selectbox("בחר נושא לימוד:", ["בחר..."] + list(T_MAP.keys()))
    if sel != "בחר..." and st.button("📖 כנס לנושא"):
        S.subs=T_MAP[sel]; S.topic=sel; S.lt=""; S.sub_n=""; st.rerun()
    
    if S.subs:
        st.write("---")
        st.markdown("### 📖 פרקי הלימוד בנושא זה:")
        cols = st.columns(len(S.subs))
        for i, s in enumerate(S.subs):
            # ניטרול כפתור אם זה הפרק שמוצג כרגע
            btn_disabled = (S.sub_n == s)
            if cols[i].button(s, key=f"btn_{i}", disabled=btn_disabled):
                with st.spinner(f"טוען {s}..."):
                    res = ask_ai(f"שיעור מפורט על {s} למבחן המתווכים כולל סעיפי חוק.")
                    if res: S.lt=res; S.sub_n=s; st.rerun()
                    else: st.error("חלה שגיאה בטעינה. נסה שוב.")
    
    if S.lt:
        st.markdown(f"## {S.sub_n}")
        st.markdown(f"<div class='lesson-box'>{S.lt}</div>", unsafe_allow_html=True)
        st.write(" ")
        if st.button("✍️ תרגול שאלות בפרק זה"): S.step='q_prep'; st.rerun()
    
    # כפתור חזרה לתפריט הראשי
    if st.button("🏠 חזרה לתפריט הראשי"): 
        S.step='menu'; S.subs=[]; S.lt=""; S.sub_n=""; st.rerun()

elif S.step == 'q_prep':
    with st.spinner(f"ה-AI בונה עבורך 10 שאלות על {S.topic}..."):
        p = f"צור 10 שאלות על {S.topic}. החזר JSON בלבד: " + "[{'q':'','options':['','','',''],'correct':'','reason':''}]"
        res = ask_ai(p)
        if res:
            m = re.search(r'\[.*\]', res, re.DOTALL)
            if m: 
                S.qq=json.loads(m.group()); S.qi=0; S.score=0; S.ans_d=False; S.step='quiz'; st.rerun()
    st.error("לא הצלחתי לייצר שאלות."); S.step='menu'; time.sleep(2); st.rerun()

elif S.step == 'quiz':
    q = S.qq[S.qi]
    st.info(f"שאלה {S.qi+1}/10: {q['q']}")
    ans = st.radio("תשובה:", q['options'], key=f"r{S.qi}", index=None, disabled=S.ans_d)
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
    if st.button("🏠 חזרה לתפריט הראשי"): S.step='menu'; S.qq=[]; st.rerun()
