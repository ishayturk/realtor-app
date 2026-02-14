import streamlit as st
import google.generativeai as genai
import json
import re

# 1. הגדרות תצוגה RTL ועיצוב כפתורי ניווט
st.set_page_config(page_title="מתווך בקליק", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    .stApp { direction: rtl !important; text-align: right !important; }
    [data-testid="stSidebar"] { display: none; }
    
    /* עיצוב כפתורי המספרים בלוח הניווט */
    .nav-btn {
        display: inline-block;
        width: 40px;
        height: 40px;
        line-height: 40px;
        text-align: center;
        margin: 5px;
        border-radius: 5px;
        border: 1px solid #ccc;
        cursor: pointer;
        font-weight: bold;
    }
    .stButton > button { width: 100%; border-radius: 10px; font-weight: bold; }
    .question-card { background-color: #f8f9fa; padding: 20px; border-radius: 15px; border-right: 6px solid #1E88E5; margin-bottom: 20px; }
</style>
""", unsafe_allow_html=True)

# 2. ניהול State
if "view_mode" not in st.session_state:
    st.session_state.update({
        "view_mode": "login", "user_name": "", "current_topic": "בחר נושא...", 
        "lesson_content": "", "exam_questions": [], "user_answers": {}, 
        "current_exam_idx": 0, "show_feedback": False
    })

if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-2.0-flash')

# 3. פונקציות AI
def load_exam(topic, count=25):
    with st.spinner(f"מייצר {count} שאלות..."):
        try:
            prompt = f"Create a {count}-question quiz in HEBREW about {topic}. Return ONLY JSON array: [{'q':'','options':['','','',''],'correct':0,'explanation':''}]"
            resp = model.generate_content(prompt)
            match = re.search(r'\[\s*\{.*\}\s*\]', resp.text, re.DOTALL)
            if match:
                st.session_state.exam_questions = json.loads(match.group())
                st.session_state.update({"user_answers": {}, "current_exam_idx": 0, "view_mode": "exam_mode", "show_feedback": False})
                st.rerun()
        except: st.error("שגיאה בייצור המבחן")

# 4. לוגיקת דפים
if st.session_state.view_mode == "login":
    st.title("🏠 מתווך בקליק")
    name = st.text_input("הכנס שם מלא:")
    if st.button("כניסה"):
        if name: st.session_state.user_name = name; st.session_state.view_mode = "setup"; st.rerun()

elif st.session_state.view_mode == "setup":
    st.header(f"שלום {st.session_state.user_name}")
    topic = st.selectbox("בחר נושא לתרגול או מבחן מלא:", ["בחר נושא...", "חוק המתווכים", "חוק המקרקעין", "מבחן סימולציה מלא"])
    if topic != "בחר נושא...":
        num = 25 if "מלא" in topic else 10
        if st.button(f"התחל {topic}"):
            st.session_state.current_topic = topic
            load_exam(topic, num)

elif st.session_state.view_mode == "exam_mode":
    idx = st.session_state.current_exam_idx
    questions = st.session_state.exam_questions
    q = questions[idx]

    # --- לוח ניווט חכם (כאן מתבצע הקסם) ---
    st.write("### 📍 סטטוס שאלות:")
    nav_cols = st.columns(10) # מציג 10 שאלות בשורה
    for i in range(len(questions)):
        with nav_cols[i % 10]:
            # סימון אם נענתה
            label = f"{i+1}"
            if i in st.session_state.user_answers:
                label += " ✓"
            
            # צבע הכפתור לפי הסטטוס
            if i == idx:
                btn_type = "primary" # השאלה הנוכחית (צבע בולט)
            elif i in st.session_state.user_answers:
                btn_type = "secondary" # נענתה
            else:
                btn_type = "secondary" # טרם נענתה

            if st.button(label, key=f"nav_{i}", type=btn_type, use_container_width=True):
                st.session_state.current_exam_idx = i
                st.session_state.show_feedback = False
                st.rerun()
    
    st.markdown("---")

    # הצגת השאלה
    st.subheader(f"שאלה {idx+1}")
    st.markdown(f'<div class="question-card"><h4>{q["q"]}</h4></div>', unsafe_allow_html=True)
    
    # חישוב אינדקס התשובה הקודמת אם קיימת
    current_val = st.session_state.user_answers.get(idx)
    ans_idx = q['options'].index(current_val) if current_val in q['options'] else None

    ans = st.radio("בחר תשובה:", q['options'], key=f"ans_{idx}", index=ans_idx)
    
    if ans:
        st.session_state.user_answers[idx] = ans

    # כפתורי ניווט תחתונים
    col1, col2, col3 = st.columns([1,1,1])
    with col1:
        if st.button("⬅️ הקודם", disabled=idx==0):
            st.session_state.current_exam_idx -= 1; st.rerun()
    with col2:
        if st.button("בדוק תשובה"): st.session_state.show_feedback = True
    with col3:
        if idx < len(questions) - 1:
            if st.button("הבא ➡️"):
                st.session_state.current_exam_idx += 1; st.session_state.show_feedback = False; st.rerun()
        else:
            if st.button("🏁 סיים מבחן וקבל ציון"):
                st.session_state.view_mode = "summary"; st.rerun()

    if st.session_state.show_feedback and ans:
        if q['options'].index(ans) == q['correct']: st.success("נכון!")
        else: st.error(f"טעות. הנכון: {q['options'][q['correct']]}")
        st.write(f"הסבר: {q['explanation']}")

elif st.session_state.view_mode == "summary":
    st.header("🏁 סיכום המבחן")
    correct_count = 0
    for i, q in enumerate(st.session_state.exam_questions):
        user_ans = st.session_state.user_answers.get(i)
        if user_ans and q['options'].index(user_ans) == q['correct']:
            correct_count += 1
    
    score = int((correct_count / len(st.session_state.exam_questions)) * 100)
    st.metric("הציון שלך:", f"{score}/100")
    st.write(f"צדקת ב-{correct_count} שאלות מתוך {len(st.session_state.exam_questions)}")
    
    if score >= 60: st.balloons(); st.success("עברת את המבחן! כל הכבוד.")
    else: st.warning("לא עברת הפעם. צריך 60 לפחות. המשך לתרגל!")
    
    if st.button("חזרה לתפריט הראשי"):
        st.session_state.view_mode = "setup"; st.rerun()
