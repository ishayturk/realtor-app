# גרסה: 1006 | תאריך: 15/02/2026 | שעה: 21:10
import streamlit as st
import google.generativeai as genai
import json, re, time

# הגדרות עמוד
st.set_page_config(page_title="מתווך בקליק", layout="centered")

# כותרת גרסה
st.markdown("<div style='text-align: left; color: gray; font-size: 10px;'>גרסה: 1006 | 15/02/2026 | 21:10</div>", unsafe_allow_html=True)

# עיצוב CSS
st.markdown("""
<style>
    * { direction: rtl !important; text-align: right !important; }
    .lesson-box { background-color: #ffffff; color: #000; padding: 25px; border-radius: 12px; border-right: 6px solid #1E88E5; line-height: 1.8; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    .explanation-box { padding: 15px; border-radius: 8px; margin: 10px 0; border-right: 5px solid; }
    .success { background-color: #e8f5e9 !important; color: #2e7d32 !important; border-color: #4caf50 !important; }
    .error { background-color: #ffebee !important; color: #c62828 !important; border-color: #f44336 !important; }
    div.stButton > button { width: 100%; border-radius: 8px; font-weight: bold; height: 3em; }
    .user-header { background: #1E88E5; color: white; padding: 10px; border-radius: 10px; text-align: center; margin-bottom: 20px; }
</style>
""", unsafe_allow_html=True)

# ניהול מצב (Session State)
S = st.session_state
if 'step' not in S:
    S.update({'user':'','step':'login','lt':'','qa':False,'qi':0,'qans':{},'qq':[],'cq':set(),'current_topic':'','total_q':10})

def get_questions(topic, count):
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-2.0-flash')
        p = f"צור {count} שאלות למבחן המתווכים בנושא {topic}. החזר JSON נקי בלבד: [{{'q':'','options':['א','ב','ג','ד'],'correct':'טקסט מדויק','reason':''}}]"
        r = model.generate_content(p)
        m = re.search(r'\[.*\]', r.text, re.DOTALL)
        return json.loads(m.group()) if m else None
    except:
        return None

st.title("🏠 מתווך בקליק")

if S.user:
    st.markdown(f"<div class='user-header'>שלום, {S.user}</div>", unsafe_allow_html=True)

# --- ניווט דפים ---

if S.step == "login":
    u = st.text_input("הזן שם מלא:", key="login_input")
    if st.button("כניסה למערכת"):
        if u:
            S.user = u
            S.step = "menu"
            st.rerun()

elif S.step == "menu":
    S.qa = False
    c1, c2 = st.columns(2)
    if c1.button("📚 שיעורים בנושאי הלימוד"):
        S.step = "study"
        st.rerun()
    if c2.button("📝 סימולציית מבחן רשמית"):
        S.step = "exam_lobby"
        st.rerun()

elif S.step == "study":
    all_t = ["חוק המתווכים במקרקעין", "חוק המקרקעין", "חוק החוזים", "חוק המכר (דירות)", "חוק הגנת הצרכן", "חוק הגנת הדייר", "חוק תכנון ובנייה", "חוק מיסוי מקרקעין", "חוק ההוצאה לפועל", "חוק הירושה", "חוק העונשין", "אתיקה מקצועית"]
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
            S.lt, S.current_topic = full, sel
            st.rerun()
        if st.button("🏠 תפריט"):
            S.step = "menu"
            st.rerun()
    else:
        if not S.qa:
            st.markdown(f"<div class='lesson-box'>{S.lt}</div>", unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            if c1.button(f"✍️ שאלון: {S.current_topic}"):
                with st.spinner("טוען שאלות..."):
                    d = get_questions(S.current_topic, 10)
                    if d:
                        S.qq, S.qa, S.qi, S.cq, S.total_q = d, True, 0, set(), 10
                        S.step = "quiz_mode"
                        st.rerun()
            if c2.button("🏁 חזרה"):
                S.step, S.lt = "menu", ""
                st.rerun()

elif S.step == "exam_lobby":
    st.write("### סימולציית מבחן מלאה (25 שאלות)")
    if st.button("🚀 התחל מבחן"):
        with st.spinner("מייצר שאלות ראשונות..."):
            d = get_questions("דיני מקרקעין ותיווך", 5)
            if d:
                S.qq, S.qa, S.qi, S.cq, S.total_q = d, True, 0, set(), 25
                S.step = "quiz_mode"
                st.rerun()
    if st.button("🏠 חזרה"):
        S.step = "menu"
        st.rerun()

elif S.step == "quiz_mode":
    if not S.qq:
        S.step = "menu"
        st.rerun()
        
    it = S.qq[S.qi]
    st.write(f"### שאלה {S.qi+1} מתוך {S.total_q}")
    ans = st.radio(it['q'], it['options'], key=f"q_radio_{S.qi}", index=None)
    
    if S.qi in S.cq:
        corr = str(it['correct']).strip()
        user_ans = str(S.qans.get(S.qi)).strip()
        if user_ans == corr:
            st.markdown(f"<div class='explanation-box success'>נכון! {it['reason']}</div>", unsafe_allow_html=True)
        else:
            try:
                idx = it['options'].index(corr) + 1
            except:
                idx = "?"
            st.markdown(f"<div class='explanation-box error'>טעות, תשובה {idx} היא הנכונה. {it['reason']}</div>", unsafe_allow_html=True)

    st.write("---")
    b_cols = st.columns(3)
    
    # כפתור בדיקה
    if ans and S.qi not in S.cq:
        if b_cols[0].button("🔍 בדוק"):
            S.qans[S.qi] = ans
            S.cq.add(S.qi)
            st.rerun()
    
    # כפתור ניווט לשאלה הבאה
    if S.qi in S.cq:
        if S.qi < S.total_q - 1:
            if b_cols[1].button("➡️ השאלה הבאה"):
                if S.qi == len(S.qq)-1:
                    with st.spinner("טוען עוד שאלות..."):
                        more = get_questions("דיני מקרקעין ותיווך", 5)
                        if more:
                            S.qq.extend(more)
                S.qi += 1
                st.rerun()
        else:
            if b_cols[1].button("🏁 סיום"):
                S.step, S.lt, S.qa = "menu", "", False
                st.rerun()
            
    # כפתור חזרה לתפריט
    if b_cols[2].button("🏠 תפריט"):
        S.step, S.lt, S.qa = "menu", "", False
        st.rerun()
