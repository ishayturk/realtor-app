import streamlit as st
import google.generativeai as genai
import re

# 1. עיצוב ויישור RTL
st.set_page_config(page_title="מתווך בקליק", layout="wide")

st.markdown("""
<style>
html, body, [data-testid="stAppViewContainer"], .main, .block-container, 
div[data-testid="stMarkdownContainer"], h1, h2, h3, p, li, span, label {
    direction: rtl !important; text-align: right !important;
}
.sidebar-logo {
    font-size: 34px !important; font-weight: bold; text-align: center !important;
    margin-top: -50px !important; color: #1E88E5; display: block; width: 100%;
}
[data-testid="stSidebar"] button, div.stButton > button {
    width: 100% !important; border-radius: 8px; font-weight: bold;
    background-color: #1E88E5; color: white;
}
.quiz-card { 
    background-color: #f9f9f9; padding: 20px; border-radius: 12px; 
    border-right: 6px solid #1E88E5; margin-bottom: 20px;
}
</style>
""", unsafe_allow_html=True)

# 2. נושאים
TOPICS = [
    "בחר נושא...", "חוק המתווכים במקרקעין", "חוק המקרקעין", "חוק המכר (דירות)",
    "חוק הגנת הצרכן", "חוק החוזים", "דיני תכנון ובנייה",
    "מיסוי מקרקעין", "חוק העונשין", "חוק שמאי מקרקעין"
]

# 3. ניהול Session State
if "user_name" not in st.session_state: st.session_state.user_name = ""
if "view_mode" not in st.session_state: st.session_state.view_mode = "login"
if "lesson_data" not in st.session_state: st.session_state.lesson_data = ""
if "quiz_data" not in st.session_state: st.session_state.quiz_data = []
if "history" not in st.session_state: st.session_state.history = []
if "current_topic" not in st.session_state: st.session_state.current_topic = ""
if "quiz_ready" not in st.session_state: st.session_state.quiz_ready = False

if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash') # שימוש במודל יציב יותר לניתוח טקסט

def parse_quiz_robust(text):
    """מנגנון חילוץ שאלות משופר וחסין תקלות"""
    qs = []
    # פיצול לפי START_Q או פשוט לפי מספרי שאלות אם התגיות חסרות
    blocks = re.split(r"\[START_Q\]|שאלה \d+:?", text)[1:]
    
    for b in blocks:
        try:
            # ניקוי הטקסט מתגיות סגירה
            b = b.replace("[END_Q]", "").strip()
            
            # חילוץ השאלה - מחפש טקסט לפני האופציות
            q_part = re.split(r"\[OPTIONS\]|\d\)", b)[0].replace("[QUESTION]", "").strip()
            
            # חילוץ אופציות - מחפש את כל מה שבין OPTIONS ל-ANSWER
            opt_block = ""
            if "[OPTIONS]" in b:
                opt_block = re.split(r"\[OPTIONS\]", b)[1]
                opt_block = re.split(r"\[ANSWER\]", opt_block)[0]
            
            options = [re.sub(r"^\d+[\s\).\-]+", "", o.strip()) for o in opt_block.split('\n') if len(o.strip()) > 1]
            
            # חילוץ תשובה
            ans_match = re.search(r"\[ANSWER\]\s*(\d)", b)
            idx = int(ans_match.group(1)) - 1 if ans_match else 0
            
            # חילוץ הסבר חוקי
            law_part = "לא צוין מקור חוקי"
            if "[LAW]" in b:
                law_part = b.split("[LAW]")[1].strip()
            
            if q_part and len(options) >= 2:
                qs.append({"q": q_part, "options": options[:4], "correct": idx, "ref": law_part})
        except: continue
    return qs

# 4. סרגל צידי
if st.session_state.user_name:
    with st.sidebar:
        st.markdown('<div class="sidebar-logo">🎓 מתווך בקליק</div>', unsafe_allow_html=True)
        st.write(f"שלום, **{st.session_state.user_name}**")
        if st.button("➕ נושא חדש"):
            st.session_state.view_mode = "setup"
            st.session_state.current_topic = ""
            st.session_state.quiz_ready = False
            st.rerun()
        if st.session_state.current_topic:
            if st.session_state.view_mode == "quiz":
                if st.button("📖 חזרה לשיעור"):
                    st.session_state.view_mode = "lesson"; st.rerun()
            if st.session_state.quiz_ready and st.session_state.view_mode != "quiz":
                if st.button("📝 מעבר למבחן"):
                    st.session_state.view_mode = "quiz"; st.rerun()
        st.markdown("---")
        for h in st.session_state.history: st.caption(f"• {h}")

# 5. ניהול דפים
m = st.session_state.view_mode

if m == "login":
    st.title("🎓 מתווך בקליק")
    name = st.text_input("הזן שם:")
    if st.button("כניסה"):
        if name:
            st.session_state.user_name = name
            st.session_state.view_mode = "setup"; st.rerun()

elif m == "setup":
    st.title(f"מה נלמד, {st.session_state.user_name}?")
    t = st.selectbox("בחר נושא להתחלת למידה מיידית:", TOPICS)
    if t != "בחר נושא...":
        st.session_state.current_topic = t
        st.session_state.quiz_ready = False
        st.session_state.view_mode = "streaming_lesson"; st.rerun()

elif m == "streaming_lesson":
    st.title(f"שיעור: {st.session_state.current_topic}")
    placeholder = st.empty()
    full_txt = ""
    res = model.generate_content(f"כתוב שיעור מפורט על {st.session_state.current_topic} למבחן המתווכים.", stream=True)
    for chunk in res:
        full_txt += chunk.text
        placeholder.markdown(full_txt)
    st.session_state.lesson_data = full_txt
    
    with st.status("מכין שאלות תרגול בתפריט הצד..."):
        q_p = f"צור 3 שאלות אמריקאיות על {st.session_state.current_topic}. חובה להשתמש בפורמט: [START_Q] [QUESTION] שאלה [OPTIONS] 1) א 2) ב 3) ג 4) ד [ANSWER] מספר [LAW] סעיף חוק [END_Q]"
        q_res = model.generate_content(q_p)
        st.session_state.quiz_data = parse_quiz_robust(q_res.text)
        st.session_state.quiz_ready = len(st.session_state.quiz_data) > 0
    
    if st.session_state.current_topic not in st.session_state.history:
        st.session_state.history.append(st.session_state.current_topic)
    st.session_state.view_mode = "lesson"; st.rerun()

elif m == "lesson":
    st.title(st.session_state.current_topic)
    st.markdown(st.session_state.lesson_data)
    if not st.session_state.quiz_ready:
        st.warning("⚠️ השאלות לא נוצרו בהצלחה. נסה לבחור נושא שוב.")
    else:
        st.info("✅ המבחן מוכן! לחץ על 'מעבר למבחן' בתפריט הצד מימין.")

elif m == "quiz":
    st.title(f"תרגול: {st.session_state.current_topic}")
    if not st.session_state.quiz_data:
        st.error("לא נמצאו שאלות. חזור לשיעור ונסה שוב.")
    else:
        for i, q in enumerate(st.session_state.quiz_data):
            with st.container():
                st.markdown(f'<div class="quiz-card">', unsafe_allow_html=True)
                st.subheader(f"שאלה {i+1}")
                st.write(q['q'])
                ans = st.radio(f"בחר תשובה ל{i+1}:", q['options'], key=f"q{i}", index=None)
                if st.button(f"בדוק תשובה {i+1}", key=f"b{i}"):
                    if ans:
                        correct_idx = q['correct']
                        if q['options'].index(ans) == correct_idx:
                            st.success("נכון מאוד! 🌟")
                        else:
                            st.error(f"לא נכון. התשובה הנכונה היא: {q['options'][correct_idx]}")
                        st.info(f"⚖️ **המקור בחוק:** {q['ref']}")
                st.markdown('</div>', unsafe_allow_html=True)
