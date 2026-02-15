# גרסה: 204 | תאריך: 2024-05-23 | שעה: 18:45 (GMT+2)

import streamlit as st
import google.generativeai as genai
import json, re, time

st.set_page_config(page_title="מתווך בקליק", layout="centered")
st.markdown("""<style>
* { direction: rtl !important; text-align: right !important; }
.user-welcome { font-size: 28px; font-weight: bold; color: #1E88E5; margin-bottom: 5px; }
.user-sub { font-size: 16px; color: #666; margin-bottom: 20px; border-bottom: 2px solid #eee; padding-bottom: 10px; }
.lobby-card { background: #f0f7ff; padding: 30px; border-radius: 15px; border: 1px solid #d1e3f8; margin: 20px 0; }
.lesson-box { background:#fdfdfd; padding:20px; border-radius:12px; border-right:6px solid #1E88E5; line-height:1.8; margin-bottom:20px; }
.explanation-box { padding:15px; border-radius:8px; margin-top:10px; border-right:5px solid; }
.success { background:#e8f5e9; border-color:#4caf50; color:#2e7d32; }
.error { background:#ffebee; border-color:#f44336; color:#c62828; }
.timer-box { font-size:18px; font-weight:bold; color:#d32f2f; text-align:center; background:#fff1f1; padding:10px; border-radius:10px; border:1px solid #d32f2f; margin-bottom:15px; }
div.stButton > button { width: 100%; border-radius: 8px; font-weight: bold; height: 3em; }
</style>""", unsafe_allow_html=True)

S = st.session_state
if 'step' not in S:
    S.update({
        'user':'','step':'login','lt':'','qa':False,'qi':0,'qans':{},'qq':[],'cq':set(),
        'ei':0,'eans':{},'eq':[],'start_time':None, 'current_topic':'', 'is_loading': False
    })

def parse_j(t):
    try:
        m = re.search(r'\[\s*\{.*\}\s*\]', t, re.DOTALL)
        return json.loads(m.group()) if m else None
    except: return None

def get_questions(topic, count, level="complex"):
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        m = genai.GenerativeModel('gemini-2.0-flash')
        type_q = "סיפוריות ומורכבות" if level=="complex" else "קצרות לבדיקת הבנה"
        p = f"צור {count} שאלות {type_q} למבחן המתווכים בנושא {topic}. החזר JSON נקי בלבד: "
        p += "[{'q':'','options':['א','ב','ג','ד'],'correct':'הטקסט המדויק מהאופציות','reason':''}]"
        r = m.generate_content(p)
        return parse_j(r.text)
    except: return None

def background_load():
    if len(S.eq) < 25 and not S.is_loading:
        S.is_loading = True
        new_qs = get_questions("דיני מקרקעין ותיווך בישראל", 5, "complex")
        if new_qs: S.eq.extend(new_qs)
        S.is_loading = False

st.title("🏠 מתווך בקליק")
if S.user:
    st.markdown(f"<div class='user-welcome'>שלום, {S.user}</div>", unsafe_allow_html=True)

if S.step == "login":
    u = st.text_input("שם מלא:")
    if st.button("כניסה למערכת"):
        if u: 
            S.user, S.step = u, "menu"
            background_load()
            st.rerun()

elif S.step == "menu":
    st.markdown("<div class='user-sub'>מה נלמד היום?</div>", unsafe_allow_html=True)
    if len(S.eq) < 5: background_load()
    c1, c2 = st.columns(2)
    if c1.button("📚 שיעורים בנושאי הלימוד"):
        S.step, S.lt, S.qa = "study", "", False
        st.rerun()
    if c2.button("📝 סימולציית מבחן רשמית"):
        S.step = "exam_lobby"
        st.rerun()

elif S.step == "exam_lobby":
    st.markdown("""
    <div class='lobby-card'>
        <h2 style='text-align:center;'>📝 הכנה לסימולציה מלאה</h2>
        <p>קח נשימה עמוקה. הטיימר יתחיל ברגע שתלחץ על הכפתור למטה וימשיך לרוץ גם אם תצא מהדף.</p>
        <ul>
            <li><b>25 שאלות</b> במבנה המבחן הרשמי.</li>
            <li><b>טיימר חי:</b> עקוב אחר קצב ההתקדמות שלך.</li>
            <li><b>חוסן:</b> הזמן נשמר גם אם הדף מתרענן.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    if col1.button("🚀 אני מוכן, התחל מבחן"):
        S.ei, S.cq, S.start_time = 0, set(), time.time()
        S.step = "full_exam"
        st.rerun()
    if col2.button("🔙 חזרה לתפריט"):
        S.step = "menu"
        st.rerun()

elif S.step == "study":
    all_t = ["חוק המתווכים במקרקעין", "חוק המקרקעין", "חוק החוזים", "חוק המכר (דירות)", "חוק הגנת הצרכן", "חוק הגנת הדייר", "חוק תכנון ובנייה", "חוק מיסוי מקרקעין", "חוק ההוצאה לפועל", "חוק הירושה", "חוק העונשין", "אתיקה מקצועית"]
    if not S.lt:
        sel = st.selectbox("בחר נושא ללימוד:", all_t)
        c1, c2, c3 = st.columns(3)
        if c1.button("📖 התחל שיעור"):
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            m = genai.GenerativeModel('gemini-2.0-flash')
            p = f"כתוב שיעור מפורט למבחן המתווכים על {sel}. התחל ישירות בכותרת השיעור."
            res = m.generate_content(p, stream=True)
            ph, full = st.empty(), ""
            for ch in res: 
                full += ch.text
                ph.markdown(f"<div class='lesson-box'>{full}</div>", unsafe_allow_html=True)
            S.lt, S.current_topic = full, sel
            st.rerun()
        if c2.button("📝 למבחן המלא"):
            S.step = "exam_lobby"; st.rerun()
        if c3.button("🏠 תפריט"):
            S.step = "menu"; st.rerun()
    else:
        st.write(f"## {S.current_topic}")
        st.markdown(f"<div class='lesson-box'>{S.lt}</div>", unsafe_allow_html=True)
        if not S.qa:
            col_q, col_b = st.columns(2)
            if col_q.button(f"✍️ שאלון: {S.current_topic}"):
                with st.spinner("מכין שאלות..."):
                    d = get_questions(S.current_topic, 10, "simple")
                    if d: S.qq, S.qa, S.qi, S.cq = d, True, 0, set()
                    st.rerun()
            if col_b.button("🏁 חזרה לתפריט"):
                S.step, S.lt = "menu", ""; st.rerun()
        else:
            it = S.qq[S.qi]
            st.write(f"### שאלה {S.qi+1}/10")
            ans = st.radio(it['q'], it['options'], key=f"sq{S.qi}", index=None)
            c1, c2, c3 = st.columns(3)
            if ans and S.qi not in S.cq:
                if c1.button("🔍 בדוק"): S.qans[S.qi] = ans; S.cq.add(S.qi); st.rerun()
            if S.qi in S.cq:
                is_ok = str(S.qans.get(S.qi)).strip() == str(it['correct']).strip()
                st.markdown(f"<div class='explanation-box {'success' if is_ok else 'error'}'>{'✅ נכון!' if is_ok else '❌ טעות. הנכונה: '+it['correct']}<br><br>{it['reason']}</div>", unsafe_allow_html=True)
            if S.qi < 9:
                if c2.button("➡️ הבא"): S.qi += 1; st.rerun()
            else:
                st.success("סיימת את השאלון!")
                if st.button("🏁 סיום וחזרה לתפריט"): S.step, S.lt, S.qa = "menu", "", False; st.rerun()
            if c3.button("🏠 תפריט"): S.step, S.lt, S.qa = "menu", "", False; st.rerun()

elif S.step == "full_exam":
    if len(S.eq) < 25 and S.ei >= len(S.eq) - 1:
        background_load()
    
    # חישוב זמן חסין - מבוסס על זמן התחלה אבסולוטי
    if S.start_time:
        el = int(time.time() - S.start_time)
        mi, se = divmod(el, 60)
        st.markdown(f"<div class='timer-box'>⏱️ שאלה {S.ei+1}/25 | זמן: {mi:02d}:{se:02d}</div>", unsafe_allow_html=True)
        
    if S.ei < len(S.eq):
        it = S.eq[S.ei]
        ans = st.radio(it['q'], it['options'], key=f"ex{S.ei}", index=None)
        c1, c2, c3 = st.columns(3)
        if ans and S.ei not in S.cq:
            if c1.button("🔍 בדוק"): S.eans[S.ei] = ans; S.cq.add(S.ei); st.rerun()
        if S.ei in S.cq:
            is_ok = str(S.eans.get(S.ei)).strip() == str(it['correct']).strip()
            st.markdown(f"<div class='explanation-box {'success' if is_ok else 'error'}'>{'✅ נכון!' if is_ok else '❌ טעות. הנכונה: '+it['correct']}<br><br>{it['reason']}</div>", unsafe_allow_html=True)
        if S.ei < 24:
            if c2.button("➡️ הבא"): S.ei += 1; st.rerun()
        else:
            if c2.button("🏁 סיום"): S.step, S.eq = "menu", []; st.rerun()
        if c3.button("🏠 תפריט"): S.step, S.eq = "menu", []; st.rerun()
    else:
        st.info("מכין את השאלות הבאות...")
        time.sleep(2); st.rerun()
