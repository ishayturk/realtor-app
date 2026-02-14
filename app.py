import streamlit as st
import google.generativeai as genai
import json
import re

# 1. הגדרות RTL בסיסיות וניקיון שוליים
st.set_page_config(page_title="מתווך בקליק", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    /* יישור עברית גלובלי */
    .stApp { direction: rtl !important; text-align: right !important; }
    
    /* הסתרת הסיידבר שגורם לבעיות */
    [data-testid="stSidebar"] { display: none; }
    
    /* עיצוב כפתורים רחבים ונוחים */
    .stButton > button {
        width: 100%;
        border-radius: 12px;
        padding: 10px;
        font-weight: bold;
    }

    /* תיבת שאלה בולטת */
    .question-box {
        background-color: #f0f7ff;
        padding: 20px;
        border-radius: 15px;
        border-right: 5px solid #1E88E5;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# 2. ניהול הזיכרון (State)
if "view_mode" not in st.session_state:
    st.session_state.update({
        "view_mode": "login", "user_name": "", "current_topic": "",
        "exam_questions": [], "user_answers": {}, "current_exam_idx": 0, "show_feedback": False
    })

# חיבור ל-Gemini
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-2.0-flash')

# 3. פונקציית טעינת מבחן
def load_exam(topic, count=10):
    with st.spinner(f"מייצר {count} שאלות..."):
        try:
            prompt = f"Create a {count}-question quiz in HEBREW about {topic}. Return ONLY JSON array: [{'q':'','options':['','','',''],'correct':0,'explanation':'','source':''}]"
            resp = model.generate_content(prompt)
            data = json.loads(re.search(r'\[.*\]', resp.text, re.DOTALL).group())
            st.session_state.update({
                "exam_questions": data, "user_answers": {}, "current_exam_idx": 0,
                "view_mode": "exam_mode", "show_feedback": False, "current_topic": topic
            })
            st.rerun()
        except: st.error("שגיאה בטעינת השאלות. נסה שוב.")

# --- תפריט ניווט עליון פשוט ---
def render_simple_nav():
    if st.session_state.user_name:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            if st.button("🏠 בית"): st.session_state.view_mode = "setup"; st.rerun()
        with col2:
            st.markdown(f"<h3 style='text-align: center;'>שלום, {st.session_state.user_name}</h3>", unsafe_allow_html=True)
        with col3:
            if st.button("🏆 מבחן מלא"): load_exam("מבחן מתווכים ממשלתי", 25)
        st.markdown("---")

# 4. לוגיקת הדפים
if st.session_state.view_mode == "login":
    st.title("מתווך בקליק 🏠")
    name = st.text_input("הכנס שם מלא:")
    if st.button("התחל ללמוד"):
        if name: st.session_state.user_name = name; st.session_state.view_mode = "setup"; st.rerun()

else:
    render_simple_nav()

    # דף בחירת נושא
    if st.session_state.view_mode == "setup":
        st.header("בחר נושא לתרגול")
        topics = ["חוק המתווכים", "חוק המקרקעין", "חוק המכר", "חוק הגנת הצרכן", "חוק החוזים", "מיסוי מקרקעין"]
        cols = st.columns(2)
        for i, t in enumerate(topics):
            with cols[i % 2]:
                if st.button(f"📖 {t}"): load_exam(t, 10)

    # דף המבחן
    elif st.session_state.view_mode == "exam_mode":
        idx = st.session_state.current_exam_idx
        q = st.session_state.exam_questions[idx]
        
        # לוח ניווט מהיר מעל השאלה
        st.write("📍 קפיצה לשאלה:")
        nav_cols = st.columns(min(len(st.session_state.exam_questions), 10))
        for i in range(len(st.session_state.exam_questions)):
            with nav_cols[i % 10]:
                label = str(i+1)
                if i in st.session_state.user_answers: label += "✓"
                style = "primary" if i == idx else "secondary"
                if st.button(label, key=f"n_{i}", type=style):
                    st.session_state.current_exam_idx = i; st.session_state.show_feedback = False; st.rerun()

        # הצגת השאלה
        st.markdown(f'<div class="question-box"><h4>{q["q"]}</h4></div>', unsafe_allow_html=True)
        
        ans = st.radio("בחר תשובה:", q['options'], key=f"q_{idx}", index=None if idx not in st.session_state.user_answers else q['options'].index(st.session_state.user_answers[idx]))
        
        if ans:
            st.session_state.user_answers[idx] = ans
            if st.button("בדוק תשובה"): st.session_state.show_feedback = True
        
        if st.session_state.show_feedback:
            if q['options'].index(ans) == q['correct']: st.success("נכון!")
            else: st.error(f"טעות. הנכון: {q['options'][q['correct']]}")
            st.info(f"**הסבר:** {q['explanation']}")

        # כפתורי הבא/הקודם
        st.markdown("---")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("⬅️ הקודם", disabled=idx==0): 
                st.session_state.current_exam_idx -= 1; st.session_state.show_feedback = False; st.rerun()
        with c2:
            if idx < len(st.session_state.exam_questions) - 1:
                if st.button("הבא ➡️"): 
                    st.session_state.current_exam_idx += 1; st.session_state.show_feedback = False; st.rerun()
            else:
                if st.button("🏁 סיום"): st.balloons(); st.session_state.view_mode = "setup"; st.rerun()
