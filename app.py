import streamlit as st
import google.generativeai as genai
import json
import re

# 1. הגדרות תצוגה - הכל לימין ובמרכז
st.set_page_config(page_title="מתווך בקליק - הסילבוס המלא", layout="wide")

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
        text-align: right !important;
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
    with st.spinner(f"ה-AI מכין עבורך שיעור מקיף על {topic}..."):
        prompt = f"כתוב שיעור מפורט ומקצועי בעברית למבחן המתווכים על: {topic}. כלול סעיפי חוק רלוונטיים, דוגמאות וסיכום למבחן."
        resp = model.generate_content(prompt)
        st.session_state.lesson = resp.text
        st.session_state.view = "lesson"
        st.rerun()

def generate_questions(topic):
    with st.spinner("מייצר 10 שאלות תרגול ברמת בחינה..."):
        prompt = f"Create 10 multiple-choice questions in HEBREW about {topic} based on Israeli law. Return ONLY JSON array: [{'q':'','options':['','','',''],'correct':0,'explanation':''}]"
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
st.markdown('<div class="app-header"><h1>🏠 מתווך בקליק</h1><p>קורס דיגיטלי מלא למבחן המתווכים</p></div>', unsafe_allow_html=True)

if st.session_state.view == "login":
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        name = st.text_input("הכנס שם כדי להתחיל:")
        if st.button("כניסה"):
            if name: st.session_state.user = name; st.session_state.view = "menu"; st.rerun()

elif st.session_state.view == "menu":
    st.subheader(f"שלום {st.session_state.user}, בחר נושא ללימוד:")
    
    # הרשימה המלאה של 16 הנושאים הרשמיים
    full_syllabus = [
        "חוק המתווכים במקרקעין והתקנות",
        "חוק המקרקעין (בעלות, שכירות, משכנתא)",
        "חוק המכר (דירות) (הבטחת השקעות)",
        "חוק החוזים (חלק כללי ותרופות)",
        "חוק הגנת הצרכן",
        "חוק הגנת הדייר",
        "חוק התכנון והבנייה (פרקים נבחרים)",
        "חוק מיסוי מקרקעין (שבח ורכישה)",
        "חוק העונשין (עבירות מרמה וזיוף)",
        "חוק שמאי מקרקעין",
        "חוק הירושה",
        "חוק יחסי ממון בין בני זוג",
        "חוק איסור הלבנת הון",
        "פקודת הנזיקין (רשלנות ותרמית)",
        "מושגי יסוד בכלכלה ושמאות",
        "חוק מקרקעי ישראל ורשות מקרקעי ישראל"
    ]
    
    selected = st.selectbox("רשימת הנושאים המלאה:", ["בחר נושא מהרשימה..."] + full_syllabus)
    
    if selected != "בחר נושא מהרשימה...":
        st.session_state.topic = selected
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button(f"📖 פתח שיעור"): generate_lesson(selected)
        with col_b:
            if st.button(f"✍️ דלג לתרגול"): generate_questions(selected)

elif st.session_state.view == "lesson":
    st.header(st.session_state.topic)
    st.markdown(f'<div class="lesson-box">{st.session_state.lesson}</div>', unsafe_allow_html=True)
    
    col_back, col_next = st.columns(2)
    with col_back:
        if st.button("חזרה לתפריט"): st.session_state.view = "menu"; st.rerun()
    with col_next:
        if st.button(f"עבור לתרגול שאלות ב{st.session_state.topic}"): generate_questions(st.session_state.topic)

elif st.session_state.view == "quiz":
    idx = st.session_state.current_idx
    q = st.session_state.questions[idx]
    
    # לוח התקדמות - 10 שאלות
    cols = st.columns(10)
    for i in range(10):
        with cols[i]:
            btn_type = "primary" if i == idx else "secondary"
            btn_label = f"{i+1}"
            if i in st.session_state.answers: btn_label += "✓"
            if st.button(btn_label, key=f"nav_{i}", type=btn_type):
                st.session_state.current_idx = i; st.session_state.feedback = False; st.rerun()

    st.markdown("---")
    st.subheader(f"שאלה {idx+1}")
    st.info(q['q'])
    
    # הצגת התשובות
    old_ans = st.session_state.answers.get(idx)
    ans = st.radio("בחר את התשובה הנכונה:", q['options'], key=f"q_{idx}", index=q['options'].index(old_ans) if old_ans in q['options'] else None)
    
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
        else: st.error(f"❌ טעות. התשובה הנכונה היא: {q['options'][q['correct']]}")
        st.write(f"**הסבר:** {q['explanation']}")

elif st.session_state.view == "score":
    correct = sum(1 for i, q in enumerate(st.session_state.questions) if st.session_state.answers.get(i) == q['options'][q['correct']])
    st.header("🏁 סיכום התרגול")
    st.metric("הציון שלך:", f"{correct*10}/100")
    if correct >= 6: st.balloons(); st.success("עברת את התרגול! אתה בדרך הנכונה.")
    else: st.warning("מומלץ לקרוא שוב את השיעור ולנסות שוב.")
    if st.button("חזרה לתפריט הראשי"): st.session_state.view = "menu"; st.rerun()
