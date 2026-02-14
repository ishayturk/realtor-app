import streamlit as st
import google.generativeai as genai
import json
import re

# 1. הגדרות RTL ועיצוב ממוקד
st.set_page_config(page_title="מתווך בקליק", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    /* יישור RTL גלובלי חזק */
    .stApp, [data-testid="stAppViewContainer"], .main {
        direction: rtl !important;
        text-align: right !important;
    }
    
    /* הצמדת כותרות לימין */
    h1, h2, h3, h4, p {
        text-align: right !important;
    }

    /* הסתרת הסיידבר למניעת בעיות */
    [data-testid="stSidebar"] { display: none; }
    
    /* עיצוב תיבת הבחירה (Dropdown) */
    .stSelectbox label {
        font-size: 1.2rem !important;
        font-weight: bold !important;
    }

    /* עיצוב כפתורים */
    .stButton > button {
        width: 100%;
        border-radius: 8px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# 2. ניהול State
if "view_mode" not in st.session_state:
    st.session_state.update({
        "view_mode": "login", "user_name": "", "current_topic": "",
        "exam_questions": [], "user_answers": {}, "current_exam_idx": 0, "show_feedback": False
    })

if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-2.0-flash')

# 3. פונקציית טעינת מבחן
def load_exam(topic, count=10):
    with st.spinner(f"מייצר שאלות על {topic}..."):
        try:
            prompt = f"Create a {count}-question quiz in HEBREW about {topic}. Return ONLY JSON array: [{'q':'','options':['','','',''],'correct':0,'explanation':'','source':''}]"
            resp = model.generate_content(prompt)
            data = json.loads(re.search(r'\[.*\]', resp.text, re.DOTALL).group())
            st.session_state.update({
                "exam_questions": data, "user_answers": {}, "current_exam_idx": 0,
                "view_mode": "exam_mode", "show_feedback": False, "current_topic": topic
            })
            st.rerun()
        except: st.error("שגיאה בטעינה. נסה שוב.")

# 4. לוגיקת דפים
if st.session_state.view_mode == "login":
    st.title("מתווך בקליק 🏠")
    st.subheader("כניסה למערכת")
    name = st.text_input("הכנס שם מלא:")
    if st.button("התחל ללמוד"):
        if name:
            st.session_state.user_name = name
            st.session_state.view_mode = "setup"; st.rerun()

else:
    # תפריט עליון קטן
    c1, c2 = st.columns([4, 1])
    with c1: st.write(f"שלום, **{st.session_state.user_name}**")
    with c2: 
        if st.button("יציאה"): st.session_state.clear(); st.rerun()
    st.markdown("---")

    # מסך בחירת נושא (Drop Down)
    if st.session_state.view_mode == "setup":
        st.header("מה נתרגל היום?")
        
        topics_list = [
            "בחר נושא מהרשימה...",
            "חוק המתווכים במקרקעין",
            "חוק המקרקעין",
            "חוק המכר (דירות)",
            "חוק הגנת הצרכן",
            "חוק החוזים",
            "חוק מיסוי מקרקעין",
            "חוק התכנון והבנייה",
            "מושגי יסוד בכלכלה ושמאות",
            "סימולציית מבחן מלאה (25 שאלות)"
        ]
        
        selected = st.selectbox("בחר נושא לימוד:", topics_list)
        
        if selected != "בחר נושא מהרשימה...":
            num_q = 25 if "מלאה" in selected else 10
            if st.button(f"התחל תרגול ב{selected}"):
                load_exam(selected, num_q)

    # מסך המבחן (נשאר יציב)
    elif st.session_state.view_mode == "exam_mode":
        idx = st.session_state.current_exam_idx
        q = st.session_state.exam_questions[idx]
        
        st.write(f"**נושא:** {st.session_state.current_topic}")
        st.write(f"שאלה {idx+1} מתוך {len(st.session_state.exam_questions)}")
        
        # לוח ניווט שאלות
        nav_cols = st.columns(min(len(st.session_state.exam_questions), 10))
        for i in range(len(st.session_state.exam_questions)):
            with nav_cols[i % 10]:
                label = str(i+1)
                if i in st.session_state.user_answers: label += "✓"
                if st.button(label, key=f"nav_{i}", type="primary" if i == idx else "secondary"):
                    st.session_state.current_exam_idx = i; st.session_state.show_feedback = False; st.rerun()

        st.info(q['q'])
        ans = st.radio("בחר תשובה:", q['options'], key=f"q_{idx}")
        
        if st.button("בדוק תשובה"):
            st.session_state.user_answers[idx] = ans
            st.session_state.show_feedback = True
            
        if st.session_state.show_feedback:
            if q['options'].index(ans) == q['correct']: st.success("נכון!")
            else: st.error(f"לא נכון. התשובה הנכונה היא: {q['options'][q['correct']]}")
            st.write(f"**הסבר:** {q['explanation']}")

        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ הקודם", disabled=idx==0):
                st.session_state.current_exam_idx -= 1; st.session_state.show_feedback = False; st.rerun()
        with col2:
            if idx < len(st.session_state.exam_questions) - 1:
                if st.button("הבא ➡️"):
                    st.session_state.current_exam_idx += 1; st.session_state.show_feedback = False; st.rerun()
            else:
                if st.button("🏁 סיום"): st.session_state.view_mode = "setup"; st.rerun()
