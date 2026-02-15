# גרסה: 1014 | תאריך: 15/02/2026 | שעה: 23:35
import streamlit as st
import google.generativeai as genai
import json, re, time

st.set_page_config(page_title="מתווך בקליק", layout="centered")

# CSS מקצועי
st.markdown("""
<style>
    * { direction: rtl !important; text-align: right !important; }
    .stProgress > div > div > div > div { background-color: #1E88E5; }
    .lesson-box { background-color: #ffffff; color: #000; padding: 25px; border-radius: 12px; border-right: 6px solid #1E88E5; line-height: 1.8; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    .question-card { background-color: #ffffff; padding: 25px; border-radius: 12px; border: 1px solid #e0e0e0; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .timer-box { background: #fdf2f2; color: #d32f2f; padding: 15px; border-radius: 10px; text-align: center; font-weight: bold; border: 1px solid #ffcdd2; margin-bottom: 20px; font-size: 20px; }
    .main-header { background: #1E88E5; color: white; padding: 15px; border-radius: 10px; text-align: center; margin-bottom: 10px; font-size: 24px; font-weight: bold; }
    div.stButton > button { border-radius: 8px; height: 3.5em; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

S = st.session_state
if 'step' not in S:
    S.update({'user':'','step':'login','lt':'','qi':0,'qans':{},'qq':[],'total_q':25, 'start_time':0, 'is_loading': False, 'current_topic':''})

def fetch_chunk(topic, count=5):
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-2.0-flash')
        p = f"צור {count} שאלות אמריקאיות למבחן המתווכים בנושא {topic}. JSON נקי: [{{'q':'','options':['א','ב','ג','ד'],'correct':'טקסט מדויק','reason':''}}]"
        r = model.generate_content(p)
        m = re.search(r'\[.*\]', r.text, re.DOTALL)
        return json.loads(m.group()) if m else []
    except: return []

# Header קבוע
st.markdown("<div class='main-header'>🏠 מתווך בקליק</div>", unsafe_allow_html=True)
if S.user:
    st.markdown(f"<div style='text-align: center; margin-bottom: 20px;'>שלום, <b>{S.user}</b></div>", unsafe_allow_html=True)

# --- לוגיקת דפים ---
if S.step == "login":
    u = st.text_input("הזן שם מלא:", key="login_input")
    if st.button("כניסה למערכת"):
        if u: S.user = u; S.step = "menu"; st.rerun()

elif S.step == "menu":
    S.update({'qi':0,'qans':{},'qq':[],'lt':'','is_loading':False})
    c1, c2 = st.columns(2)
    if c1.button("📚 שיעורים ולימוד"): S.step = "study"; st.rerun()
    if c2.button("⏱️ סימולציית מבחן (90 דק')"): S.step = "exam_lobby"; st.rerun()

elif S.step == "study":
    all_t = ["חוק המתווכים במקרקעין", "חוק המקרקעין", "חוק החוזים", "חוק המכר (דירות)", "חוק הגנת הצרכן", "חוק הגנת הדייר", "חוק תכנון ובנייה", "חוק מיסוי מקרקעין", "אתיקה מקצועית"]
    if not S.lt:
        sel = st.selectbox("בחר נושא ללימוד:", all_t)
        if st.button("📖 התחל שיעור"):
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            model = genai.GenerativeModel('gemini-2.0-flash')
            res = model.generate_content(f"כתוב שיעור מפורט למבחן המתווכים על {sel}", stream=True)
            ph, full = st.empty(), ""
            for ch in res:
                full += ch.text
                ph.markdown(f"<div class='lesson-box'>{full}</div>", unsafe_allow_html=True)
            S.lt, S.current_topic = full, sel; st.rerun()
        if st.button("🏠 חזרה לתפריט"): S.step = "menu"; st.rerun()
    else:
        st.markdown(f"<div class='lesson-box'>{S.lt}</div>", unsafe_allow_html=True)
        if st.button("🏁 סיום וחזרה לתפריט"): S.lt = ""; S.step = "menu"; st.rerun()

elif S.step == "exam_lobby":
    st.write("### מוכן לסימולציה המלאה?")
    st.write("- 25 שאלות | 90 דקות | טעינה חכמה ברקע")
    if st.button("🚀 התחל בחינה"):
        with st.spinner("מייצר שאלות ראשונות..."):
            first = fetch_chunk("כללי: מתווכים, מקרקעין וחוזים", 5)
            if first:
                S.qq, S.start_time, S.step = first, time.time(), "exam_mode"
                st.rerun()
    if st.button("🏠 חזרה"): S.step = "menu"; st.rerun()

elif S.step == "exam_mode":
    # טיימר 90 דקות
    rem = max(0, 5400 - int(time.time() - S.start_time))
    h, r = divmod(rem, 3600); m, s = divmod(r, 60)
    st.markdown(f"<div class='timer-box'>⏳ זמן נותר: {h:02d}:{m:02d}:{s:02d}</div>", unsafe_allow_html=True)
    
    # טעינה ברקע
    if len(S.qq) < S.total_q and S.qi >= len(S.qq) - 2 and not S.is_loading:
        S.is_loading = True
        more = fetch_chunk("דיני מקרקעין וחוזים", 5)
        if more: S.qq.extend(more)
        S.is_loading = False

    st.progress((S.qi + 1) / S.total_q)
    it = S.qq[S.qi]
    st.markdown(f"<div class='question-card'><b>שאלה {S.qi+1}:</b><br>{it['q']}</div>", unsafe_allow_html=True)
    
    curr = S.qans.get(S.qi, None)
    ans = st.radio("בחר תשובה:", it['options'], key=f"ex_{S.qi}", index=it['options'].index(curr) if curr in it['options'] else None)
    if ans: S.qans[S.qi] = ans

    st.write("---")
    c1, c2, c3 = st.columns(3)
    if S.qi > 0:
        if c1.button("⬅️ הקודם"): S.qi -= 1; st.rerun()
    if c2.button("🏠 צא מהמבחן"): S.step = "menu"; st.rerun()
    if S.qi < S.total_q - 1:
        if c3.button("הבא ➡️"):
            if S.qi < len(S.qq) - 1: S.qi += 1; st.rerun()
            else: st.warning("טוען עוד שאלות... המתן שניה")
    else:
        if c3.button("🏁 הגש מבחן"): S.step = "results"; st.rerun()

elif S.step == "results":
    correct = sum(1 for i, q in enumerate(S.qq) if S.qans.get(i) == q['correct'])
    st.markdown(f"<div class='main-header'>ציון: {int((correct/S.total_q)*100)}</div>", unsafe_allow_html=True)
    if st.button("🏠 חזרה לתפריט"): S.step = "menu"; st.rerun()
