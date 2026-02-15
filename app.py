# גרסה: 1012 | תאריך: 15/02/2026 | שעה: 23:10
import streamlit as st
import google.generativeai as genai
import json, re, time

st.set_page_config(page_title="מתווך בקליק - סימולציה רשמית", layout="centered")

# כותרת גרסה
st.markdown("<div style='text-align: left; color: gray; font-size: 10px;'>גרסה: 1012 | 15/02/2026 | 23:10</div>", unsafe_allow_html=True)

st.markdown("""
<style>
    * { direction: rtl !important; text-align: right !important; }
    .stProgress > div > div > div > div { background-color: #1E88E5; }
    .question-card { background-color: #ffffff; padding: 25px; border-radius: 12px; border: 1px solid #e0e0e0; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .timer-box { background: #fdf2f2; color: #d32f2f; padding: 15px; border-radius: 10px; text-align: center; font-weight: bold; border: 1px solid #ffcdd2; margin-bottom: 20px; font-size: 20px; }
    .main-header { background: #1E88E5; color: white; padding: 15px; border-radius: 10px; text-align: center; margin-bottom: 20px; font-size: 24px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

S = st.session_state
if 'step' not in S:
    S.update({'user':'','step':'login','qi':0,'qans':{},'qq':[],'total_q':25, 'start_time':0, 'is_loading': False})

def fetch_chunk(topic, count=5):
    """פונקציה שמביאה מנה קטנה של שאלות"""
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-2.0-flash')
        p = f"צור {count} שאלות אמריקאיות קשות למבחן המתווכים בנושא {topic}. JSON נקי: [{{'q':'','options':['א','ב','ג','ד'],'correct':'טקסט מדויק','reason':''}}]"
        r = model.generate_content(p)
        m = re.search(r'\[.*\]', r.text, re.DOTALL)
        return json.loads(m.group()) if m else []
    except: return []

# Header קבוע
st.markdown("<div class='main-header'>🏠 מתווך בקליק</div>", unsafe_allow_html=True)
if S.user:
    st.markdown(f"<div style='text-align: center;'>נבחן: <b>{S.user}</b></div>", unsafe_allow_html=True)

if S.step == "login":
    u = st.text_input("הזן שם מלא:", key="login_input")
    if st.button("כניסה"):
        if u: S.user = u; S.step = "menu"; st.rerun()

elif S.step == "menu":
    S.update({'qi':0,'qans':{},'qq':[],'is_loading':False})
    if st.button("⏱️ התחל סימולציית מבחן (90 דק')"):
        S.step = "exam_lobby"; st.rerun()

elif S.step == "exam_lobby":
    st.write("בחינה של 25 שאלות. השאלות נטענות ברקע בזמן המבחן.")
    if st.button("🚀 צא לדרך"):
        with st.spinner("טוען שאלות ראשונות..."):
            first_chunk = fetch_chunk("חוק המתווכים ומקרקעין", 5)
            if first_chunk:
                S.qq = first_chunk
                S.start_time = time.time()
                S.step = "exam_mode"
                st.rerun()

elif S.step == "exam_mode":
    # 1. ניהול טיימר
    rem = max(0, 5400 - int(time.time() - S.start_time))
    h, r = divmod(rem, 3600); m, s = divmod(r, 60)
    st.markdown(f"<div class='timer-box'>⏳ זמן נותר: {h:02d}:{m:02d}:{s:02d}</div>", unsafe_allow_html=True)
    
    # 2. טעינה ברקע - אם הגענו לשאלה אחת לפני סוף המנה הנוכחית ואין לנו עדיין 25
    if len(S.qq) < S.total_q and S.qi >= len(S.qq) - 2 and not S.is_loading:
        S.is_loading = True
        with st.spinner("מכין את השאלות הבאות ברקע..."):
            more = fetch_chunk("דיני מקרקעין וחוזים", 5)
            if more: S.qq.extend(more)
        S.is_loading = False
        st.rerun()

    st.progress((S.qi + 1) / S.total_q)
    
    # הצגת השאלה
    if S.qi < len(S.qq):
        it = S.qq[S.qi]
        st.markdown(f"<div class='question-card'><b>שאלה {S.qi+1}:</b><br>{it['q']}</div>", unsafe_allow_html=True)
        
        curr = S.qans.get(S.qi, None)
        ans = st.radio("בחר תשובה:", it['options'], key=f"ex_{S.qi}", index=it['options'].index(curr) if curr in it['options'] else None)
        if ans: S.qans[S.qi] = ans

    st.write("---")
    c1, c2, c3 = st.columns(3)
    if S.qi > 0:
        if c1.button("⬅️ הקודם"): S.qi -= 1; st.rerun()
    
    if c2.button("🏠 תפריט"): S.step = "menu"; st.rerun()

    if S.qi < S.total_q - 1:
        if c3.button("הבא ➡️"):
            if S.qi < len(S.qq) - 1:
                S.qi += 1
                st.rerun()
            else:
                st.warning("השאלות הבאות בטעינה, המתן רגע...")
    else:
        if c3.button("🏁 הגש מבחן"): S.step = "results"; st.rerun()

elif S.step == "results":
    # לוגיקה של ציון (כפי שהייתה)
    correct = sum(1 for i, q in enumerate(S.qq) if S.qans.get(i) == q['correct'])
    st.markdown(f"<div class='main-header'>ציון: {int((correct/S.total_q)*100)}</div>", unsafe_allow_html=True)
    if st.button("חזרה לתפריט"): S.step = "menu"; st.rerun()
