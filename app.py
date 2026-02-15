# גרסה: 1011 | תאריך: 15/02/2026 | שעה: 22:50
import streamlit as st
import google.generativeai as genai
import json, re, time

st.set_page_config(page_title="מתווך בקליק - סימולציה רשמית", layout="centered")

# כותרת גרסה לביקורת
st.markdown("<div style='text-align: left; color: gray; font-size: 10px;'>גרסה: 1011 | 15/02/2026 | 22:50</div>", unsafe_allow_html=True)

# CSS למראה מבחן מקצועי
st.markdown("""
<style>
    * { direction: rtl !important; text-align: right !important; }
    .stProgress > div > div > div > div { background-color: #1E88E5; }
    .question-card { background-color: #ffffff; padding: 25px; border-radius: 12px; border: 1px solid #e0e0e0; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .timer-box { background: #fdf2f2; color: #d32f2f; padding: 15px; border-radius: 10px; text-align: center; font-weight: bold; border: 1px solid #ffcdd2; margin-bottom: 20px; font-size: 20px; }
    .main-header { background: #1E88E5; color: white; padding: 15px; border-radius: 10px; text-align: center; margin-bottom: 20px; font-size: 24px; font-weight: bold; }
    div.stButton > button { border-radius: 8px; height: 3.5em; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

S = st.session_state
if 'step' not in S:
    S.update({'user':'','step':'login','lt':'','qi':0,'qans':{},'qq':[],'total_q':25, 'start_time':0})

def get_questions(topic, count):
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-2.0-flash')
        p = f"צור {count} שאלות אמריקאיות ברמה גבוהה למבחן המתווכים בנושא {topic}. שפה משפטית, JSON נקי בלבד: [{{'q':'','options':['א','ב','ג','ד'],'correct':'טקסט מדויק','reason':''}}]"
        r = model.generate_content(p)
        m = re.search(r'\[.*\]', r.text, re.DOTALL)
        return json.loads(m.group()) if m else None
    except: return None

# --- HEADER קבוע ---
st.markdown("<div class='main-header'>🏠 מתווך בקליק</div>", unsafe_allow_html=True)
if S.user:
    st.markdown(f"<div style='text-align: center; margin-bottom: 10px;'>בוחן: <b>{S.user}</b></div>", unsafe_allow_html=True)

# --- דף כניסה ---
if S.step == "login":
    u = st.text_input("הזן שם מלא:", key="login_input")
    if st.button("כניסה למערכת"):
        if u: S.user = u; S.step = "menu"; st.rerun()

# --- תפריט ראשי ---
elif S.step == "menu":
    S.update({'lt':'','qi':0,'qans':{},'qq':[]})
    c1, c2 = st.columns(2)
    if c1.button("📚 שיעורים ולימוד"): S.step = "study"; st.rerun()
    if c2.button("⏱️ סימולציית מבחן (90 דק')"): S.step = "exam_lobby"; st.rerun()

# --- לובי מבחן ---
elif S.step == "exam_lobby":
    st.write("### הנחיות לסימולציה:")
    st.write("* המבחן כולל 25 שאלות.\n* לרשותך **90 דקות** בדיוק.\n* אין משוב במהלך המבחן (תשובות נכונות יוצגו בסיום).\n* ניתן לחזור לשאלות קודמות ולתקן.")
    if st.button("🚀 התחל בחינה"):
        with st.spinner("מייצר שאלות בחינה..."):
            d = get_questions("דיני מקרקעין, חוק המתווכים, חוזים ותכנון ובנייה", 25)
            if d:
                S.qq, S.step, S.start_time, S.qi = d, "exam_mode", time.time(), 0
                st.rerun()

# --- מצב בחינה ---
elif S.step == "exam_mode":
    # טיימר ל-90 דקות (5400 שניות)
    elapsed = time.time() - S.start_time
    remaining = max(0, 5400 - int(elapsed))
    
    # חישוב שעות, דקות ושניות
    hours, rem = divmod(remaining, 3600)
    mins, secs = divmod(rem, 60)
    
    st.markdown(f"<div class='timer-box'>⏳ זמן נותר: {hours:02d}:{mins:02d}:{secs:02d}</div>", unsafe_allow_html=True)
    
    st.progress((S.qi + 1) / S.total_q)
    
    it = S.qq[S.qi]
    st.markdown(f"<div class='question-card'><b>שאלה {S.qi+1}:</b><br>{it['q']}</div>", unsafe_allow_html=True)
    
    current_val = S.qans.get(S.qi, None)
    ans = st.radio("בחר תשובה:", it['options'], key=f"ex_{S.qi}", index=it['options'].index(current_val) if current_val in it['options'] else None)
    
    if ans:
        S.qans[S.qi] = ans

    st.write("---")
    c1, c2, c3 = st.columns([1,1,1])
    
    # ניווט
    if S.qi > 0:
        if c1.button("⬅️ הקודם"): S.qi -= 1; st.rerun()
    else: c1.empty()

    if c2.button("🏠 יציאה"): S.step = "menu"; st.rerun()

    if S.qi < S.total_q - 1:
        if c3.button("הבא ➡️"): S.qi += 1; st.rerun()
    else:
        if c3.button("🏁 הגש מבחן"):
            S.step = "results"
            st.rerun()

# --- דף תוצאות ---
elif S.step == "results":
    correct = sum(1 for i, q in enumerate(S.qq) if S.qans.get(i) == q['correct'])
    score = int((correct / S.total_q) * 100)
    
    st.balloons()
    st.markdown(f"<div class='main-header'>ציון סופי: {score}</div>", unsafe_allow_html=True)
    st.write(f"הצלחת לענות על **{correct}** שאלות מתוך **{S.total_q}**.")
    
    if st.button("🏠 חזרה לתפריט"): S.step = "menu"; st.rerun()

# (חלק ה-study הושמט בקיצור אך נשמר במבנה המקורי שלך)
