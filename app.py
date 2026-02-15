# גרסה: 1007 | תאריך: 15/02/2026 | שעה: 21:30
import streamlit as st
import google.generativeai as genai
import json, re

st.set_page_config(page_title="מתווך בקליק - סימולציה", layout="centered")

# CSS משופר למראה מבחן רשמי
st.markdown("""
<style>
    * { direction: rtl !important; text-align: right !important; }
    .stProgress > div > div > div > div { background-color: #1E88E5; }
    .question-card { background-color: #f8f9fa; padding: 20px; border-radius: 10px; border: 1px solid #dee2e6; margin-bottom: 20px; }
    .explanation-box { padding: 15px; border-radius: 8px; margin: 10px 0; border-right: 5px solid; }
    .success { background-color: #e8f5e9 !important; color: #2e7d32 !important; border-color: #4caf50 !important; }
    .error { background-color: #ffebee !important; color: #c62828 !important; border-color: #f44336 !important; }
    .user-header { background: #1E88E5; color: white; padding: 10px; border-radius: 10px; text-align: center; margin-bottom: 20px; }
</style>
""", unsafe_allow_html=True)

S = st.session_state
if 'step' not in S:
    S.update({'user':'','step':'login','lt':'','qa':False,'qi':0,'qans':{},'qq':[],'cq':set(),'current_topic':'','total_q':10, 'loading_more': False})

def get_questions(topic, count, level="high"):
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-2.0-flash')
        p = f"צור {count} שאלות אמריקאיות ברמה גבוהה למבחן המתווכים בנושא {topic}. " \
            f"השתמש בשפה משפטית, שאלות ארוכות ומבלבלות. החזר JSON נקי: " \
            f"[{{'q':'','options':['א','ב','ג','ד'],'correct':'טקסט מדויק','reason':''}}]"
        r = model.generate_content(p)
        m = re.search(r'\[.*\]', r.text, re.DOTALL)
        return json.loads(m.group()) if m else None
    except: return None

# --- דף כניסה ותפריט (ללא שינוי לוגי) ---
if S.step == "login":
    st.title("🏠 מתווך בקליק")
    u = st.text_input("הזן שם מלא:", key="login_input")
    if st.button("כניסה למערכת"):
        if u: S.user = u; S.step = "menu"; st.rerun()

elif S.step == "menu":
    st.title("🏠 מתווך בקליק")
    st.markdown(f"<div class='user-header'>שלום, {S.user}</div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    if c1.button("📚 שיעורים בנושאי הלימוד"): S.step = "study"; st.rerun()
    if c2.button("📝 סימולציית מבחן רשמית"): S.step = "exam_lobby"; st.rerun()

elif S.step == "study":
    all_t = ["חוק המתווכים במקרקעין", "חוק המקרקעין", "חוק החוזים", "חוק המכר (דירות)", "חוק הגנת הצרכן"]
    if not S.lt:
        sel = st.selectbox("בחר נושא:", all_t)
        if st.button("📖 התחל שיעור"):
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            model = genai.GenerativeModel('gemini-2.0-flash')
            res = model.generate_content(f"כתוב שיעור מפורט למבחן המתווכים על {sel}", stream=True)
            ph, full = st.empty(), ""
            for ch in res:
                full += ch.text
                ph.markdown(f"<div class='lesson-box'>{full}</div>", unsafe_allow_html=True)
            S.lt, S.current_topic = full, sel; st.rerun()
    else:
        st.markdown(f"<div class='lesson-box'>{S.lt}</div>", unsafe_allow_html=True)
        if st.button(f"✍️ התחל שאלון תרגול"):
            with st.spinner("מייצר שאלות תרגול..."):
                d = get_questions(S.current_topic, 10)
                if d: S.qq, S.qi, S.cq, S.total_q, S.step = d, 0, set(), 10, "quiz_mode"; st.rerun()

elif S.step == "exam_lobby":
    st.write("### ברוך הבא לסימולציה הרשמית")
    st.write("25 שאלות מעורבבות. המערכת תטען שאלות נוספות תוך כדי שתענה.")
    if st.button("🚀 התחל בחינה"):
        with st.spinner("מכין שאלות ראשונות..."):
            d = get_questions("חוק המתווכים והמקרקעין", 5)
            if d: S.qq, S.qi, S.cq, S.total_q, S.step = d, 0, set(), 25, "quiz_mode"; st.rerun()

elif S.step == "quiz_mode":
    # פס התקדמות
    progress = (S.qi + 1) / S.total_q
    st.progress(progress)
    st.write(f"**שאלה {S.qi+1} מתוך {S.total_q}**")
    
    it = S.qq[S.qi]
    with st.container():
        st.markdown(f"<div class='question-card'><b>{it['q']}</b></div>", unsafe_allow_html=True)
        ans = st.radio("בחר תשובה:", it['options'], key=f"q_{S.qi}", index=None)
    
    # טעינה מוקדמת (Background Fetching)
    # אם נשארו רק 2 שאלות בזיכרון, נביא עוד 5
    if len(S.qq) - S.qi <= 2 and len(S.qq) < S.total_q and not S.loading_more:
        S.loading_more = True
        # אנחנו לא עושים rerun כאן כדי לא להפריע למשתמש
        more = get_questions("דיני מקרקעין ותיווך", 5)
        if more: S.qq.extend(more)
        S.loading_more = False

    if S.qi in S.cq:
        corr = str(it['correct']).strip()
        user_ans = str(S.qans.get(S.qi)).strip()
        if user_ans == corr:
            st.markdown(f"<div class='explanation-box success'><b>נכון!</b><br>{it['reason']}</div>", unsafe_allow_html=True)
        else:
            try: idx = it['options'].index(corr) + 1
            except: idx = "?"
            st.markdown(f"<div class='explanation-box error'>טעות. תשובה {idx} היא הנכונה.<br>{it['reason']}</div>", unsafe_allow_html=True)

    st.write("---")
    c1, c2, c3 = st.columns(3)
    if ans and S.qi not in S.cq:
        if c1.button("🔍 בדוק תשובה"): S.qans[S.qi] = ans; S.cq.add(S.qi); st.rerun()
    
    if S.qi in S.cq:
        if S.qi < S.total_q - 1:
            if c2.button("➡️ השאלה הבאה"): S.qi += 1; st.rerun()
        else:
            if c2.button("🏁 סיום בחינה"): S.step = "menu"; S.lt = ""; st.rerun()
            
    if c3.button("🏠 צא לתפריט"): S.step = "menu"; S.lt = ""; st.rerun()
