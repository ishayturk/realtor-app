import streamlit as st
import google.generativeai as genai
import json
import re

# 1. הגדרות RTL ועיצוב רספונסיבי למחשב ולנייד
st.set_page_config(page_title="מתווך בקליק", layout="wide")

st.markdown("""
<style>
    /* יישור RTL גלובלי */
    .stApp, [data-testid="stAppViewContainer"], p, li, h1, h2, h3, div, span, label {
        direction: rtl !important; text-align: right !important;
    }
    
    /* העברת הסיידבר (תפריט) לצד ימין */
    [data-testid="stSidebar"] { right: 0; left: auto; direction: rtl !important; border-left: 1px solid #ddd; border-right: none; }
    [data-testid="stSidebarCollapsedControl"] { right: 0; left: auto; }

    /* התאמת תוכן מרכזי בנייד ובמחשב */
    @media (min-width: 992px) {
        [data-testid="stAppViewContainer"] { margin-right: 20rem; margin-left: 0; }
    }
    
    /* עיצוב שדות קלט למרכז ולימין */
    input { direction: rtl !important; text-align: right !important; }
    
    /* תיבות פידבק */
    .feedback-box { padding: 15px; border-radius: 10px; margin: 10px 0; border: 1px solid #eee; }
    .law-source { font-size: 0.85em; color: #1E88E5; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# 2. ניהול מצב (State)
if "view_mode" not in st.session_state:
    st.session_state.update({
        "view_mode": "login", "user_name": "", "current_topic": "",
        "exam_questions": [], "user_answers": {}, "current_exam_idx": 0, "show_feedback": False
    })

# 3. הגדרת ה-AI (Gemini)
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-2.0-flash')

# 4. פונקציות ליבה
def load_questions(topic, count=25):
    prompt = f"Create a {count}-question quiz in HEBREW about {topic} for Israeli real estate exam. Return ONLY JSON array: [{'q':'','options':['','','',''],'correct':0,'explanation':'','source':''}]"
    with st.spinner("מכין שאלות..."):
        try:
            resp = model.generate_content(prompt)
            data = json.loads(re.search(r'\[.*\]', resp.text, re.DOTALL).group())
            st.session_state.update({
                "exam_questions": data, "user_answers": {}, "current_exam_idx": 0,
                "view_mode": "exam_mode", "show_feedback": False, "current_topic": topic
            })
        except: st.error("שגיאה ביצירת השאלות. נסה שוב.")

# 5. סיידבר (מופיע מימין)
with st.sidebar:
    st.markdown("<h2 style='text-align:center;'>🏠 מתווך בקליק</h2>", unsafe_allow_html=True)
    if st.session_state.user_name:
        st.write(f"שלום, **{st.session_state.user_name}**")
        st.markdown("---")
        
        if st.button("📚 סילבוס שיעורים", use_container_width=True):
            st.session_state.view_mode = "setup"; st.rerun()
            
        if st.button("🏆 מבחן סימולציה מלא", use_container_width=True):
            load_questions("כל חומר הבחינה הממשלתי", 25); st.rerun()

        # לוח ניווט 25 שאלות - מופיע רק בזמן מבחן
        if st.session_state.view_mode == "exam_mode" and st.session_state.exam_questions:
            st.markdown("---")
            st.write("📍 **ניווט מהיר לשאלה:**")
            n_cols = 5
            for row in range(0, len(st.session_state.exam_questions), n_cols):
                cols = st.columns(n_cols)
                for i in range(n_cols):
                    idx = row + i
                    if idx < len(st.session_state.exam_questions):
                        with cols[i]:
                            label = str(idx + 1)
                            if idx in st.session_state.user_answers: label += "✓"
                            btn_type = "primary" if idx == st.session_state.current_exam_idx else "secondary"
                            if st.button(label, key=f"nav_{idx}", type=btn_type, use_container_width=True):
                                st.session_state.current_exam_idx = idx
                                st.session_state.show_feedback = False; st.rerun()

# 6. לוגיקת דפים
if st.session_state.view_mode == "login":
    st.title("כניסה למערכת")
    name = st.text_input("הכנס שם מלא:")
    if st.button("התחל ללמוד", use_container_width=True):
        if name: st.session_state.user_name = name; st.session_state.view_mode = "setup"; st.rerun()

elif st.session_state.view_mode == "setup":
    st.header("סילבוס הלימודים")
    topics = [
        "חוק המתווכים", "תקנות המתווכים", "חוק המקרקעין", "חוק המכר (הבטחת השקעות)",
        "חוק המכר (חובת גילוי)", "חוק הגנת הצרכן", "חוק החוזים", "חוק הגנת הדייר",
        "חוק התכנון והבנייה", "חוק מיסוי מקרקעין", "חוק העונשין", "חוק שמאי מקרקעין",
        "חוק הירושה", "חוק מקרקעי ישראל", "מושגי יסוד בכלכלה", "אתיקה מקצועית"
]
