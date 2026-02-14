import streamlit as st
import google.generativeai as genai
import json
import re

# 1. הגדרות תצוגה - הכל לימין ובמרכז
st.set_page_config(page_title="מתווך בקליק - לומדים להצליח", layout="wide")

st.markdown("""
<style>
    .stApp { direction: rtl !important; text-align: right !important; }
    [data-testid="stSidebar"] { display: none; }
    
    /* מרכוז התוכן */
    .main .block-container { max-width: 900px; padding-top: 2rem; }
    
    /* עיצוב כותרת עליונה */
    .app-header { text-align: center; color: #1E88E5; margin-bottom: 2rem; border-bottom: 2px solid #f0f2f6; padding-bottom: 10px; }
    
    /* תיבת שיעור */
    .lesson-box { 
        background-color: #ffffff; padding: 30px; border-radius: 15px; 
        border-right: 8px solid #1E88E5; box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        font-size: 1.2rem; line-height: 1.7; margin-bottom: 25px;
    }
    
    /* כפתורים */
    .stButton > button { width: 100%; border-radius: 10px; font-weight: bold; height: 3.5em; background-color: #1E88E5; color: white; }
    .stButton > button:hover { background-color: #1565C0; color: white; }
</style>
""", unsafe_allow_html=True)

# 2. ניהול זיכרון (State)
if "view" not in st.session_state:
    st.session_state.update({
        "view": "login", "user": "", "topic": "", "lesson": "",
        "questions": [], "answers": {}, "current_idx": 0, "feedback": False
    })

# חיבור ל-Gemini
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-2.0-flash')

# 3. פונקציות ליבה
def generate_lesson(topic):
    with st.spinner(f"ה-AI מכין עבורך שיעור על {topic}..."):
        prompt = f"כתוב שיעור מפורט ומקצועי בעברית למבחן המתווכים על: {topic}. כלול סעיפי חוק רלוונטיים והסברים פשוטים."
        resp = model.generate_content(prompt)
        st.session_state.lesson = resp.text
        st.session_state.view = "lesson"
        st.rerun()

def generate_questions(topic):
    with st.spinner("מכין שאלות תרגול..."):
        prompt = f"Create 10 multiple-choice questions in HEBREW about {topic}. Return ONLY JSON array: [{'q':'','options':['','','',''],'correct':0,'explanation':''}]"
        resp = model.generate_content(prompt)
        match = re.search(r'\[.*\]', resp.text, re.DOTALL)
        if match:
            st.session_state.questions = json.loads(match.group())
            st.session_state.answers = {}
            st.session_state.current_idx = 0
            st.session_state.view = "quiz"
            st.session_state.feedback = False
            st.rerun()

# 4. מבנה האפליקציה
st.markdown('<div class="app-header"><h1>🏠 מתווך בקליק</h1><p>הכנה חכמה למבחן המתווכים</p></div>', unsafe_allow_html=True)

if st.session_state.view == "login":
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        name = st.text_input("שם מלא:")
        if st.button("התחל ללמוד"):
            if name: st.session_state.user = name; st.session_state.view = "menu"; st.rerun()

elif st.session_state.view == "menu":
    st.subheader(f"שלום {st.session_state.user}, מה נלמד היום?")
    topic_list = ["חוק המתווכים", "חוק המקרקעין", "חוק המכר", "חוק הגנת הצרכן", "חוק החוזים", "מיסוי מקרקעין"]
    selected = st.selectbox("בחר נושא מהסילבוס:", ["בחר נושא..."] + topic_list)
    if selected != "בחר נושא...":
        st.session_state.topic = selected
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button(f"קרא שיעור ב{selected}"): generate_lesson(selected)
        with col_b:
            if st.button(f"תרגול שאלות בלבד"): generate_questions(selected)

elif st.session_state.view == "lesson":
    st.header(st.session_state.topic)
    st.markdown(f'<div class="lesson-box">{st.session_state.lesson}</div>', unsafe_allow_html=True)
    if st.button(f"סיימתי לקרוא, בוא נתרגל את {st.session_state.topic} ✍️"):
        generate_questions(st.session_state.topic)
    if st.button("חזרה לתפריט"): st.session_state.view = "menu"; st.rerun()

elif st.session_state.view == "quiz":
    idx = st.session_state.current_idx
    q = st.session_state.questions[idx]
    
    # לוח התקדמות
    cols = st.columns(10)
    for i in range(10):
        with cols[i]:
            btn_color = "primary" if i == idx else "secondary"
            if st.button(f"{i+1}", key=f"nav_{i}", type=btn_color):
                st.session_state.current_idx = i; st.session_state.feedback = False; st.rerun()

    st.subheader(f"שאלה {idx+1} מתוך 10")
    st.info(q['q'])
    
    # זיכרון בחירה
    old_ans = st.session_state.answers.get(idx)
    ans = st.radio("בחר תשובה:", q['options'], key=f"q_{idx}", index=q['options'].index(old_ans) if old_ans in q['options'] else None)
    
    if ans: st.session_state.answers[idx] = ans
    
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("⬅️ הקודם", disabled=idx==0): st.session_state.current_idx -= 1; st.session_state.feedback = False; st.rerun()
    with c2:
        if st.button("בדוק תשובה"): st.session_state.feedback = True
    with c3:
        if idx < 9:
            if st.button("הבא ➡️"): st.session_state.current_idx += 1; st.session_state.feedback = False; st.rerun()
        else:
            if st.button("סיום וציון 🏁"): st.session_state.view = "score"; st.rerun()

    if st.session_state.feedback and ans:
        if q['options'].index(ans) == q['correct']: st.success("✅ נכון!")
        else: st.error(f"❌ טעות. הנכון הוא: {q['options'][q['correct']]}")
        st.write(f"**הסבר:** {q['explanation']}")

elif st.session_state.view == "score":
    correct = sum(1 for i, q in enumerate(st.session_state.questions) if st.session_state.answers.get(i) == q['options'][q['correct']])
    st.header("🏁 סיכום התרגול")
    st.metric("הציון שלך:", f"{correct*10}/100")
    if correct >= 6: st.balloons(); st.success("כל הכבוד! עברת את התרגול.")
    else: st.warning("כדאי לחזור על השיעור ולנסות שוב.")
    if st.button("חזרה לתפריט הראשי"): st.session_state.view = "menu"; st.rerun()
