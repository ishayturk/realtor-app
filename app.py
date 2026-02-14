import streamlit as st
import google.generativeai as genai
import re

# 1. הגדרות עיצוב - הגרסה החסינה
st.set_page_config(page_title="מתווך בקליק", layout="wide")

st.markdown("""
    <style>
    /* יישור גלובלי כולל הזרמת טקסט */
    html, body, [data-testid="stAppViewContainer"], .main, .block-container, 
    div[data-testid="stMarkdownContainer"], h1, h2, h3, p, li, span, label {
        direction: rtl !important;
        text-align: right !important;
    }
    
    /* תיקון נקודות ברשימות (בולטים) */
    ul, ol { padding-right: 2rem !important; padding-left: 0 !important; }

    /* לוגו בסיידבר - נעול למרכז וגבוה */
    .sidebar-logo {
        font-size: 34px !important;
        font-weight: bold;
        text-align: center !important;
        margin-top: -50px !important;
        color: #1E88E5;
        display: block;
        width: 100%;
    }

    /* עיצוב כפתורים אחיד */
    [data-testid="stSidebar"] button, div.stButton > button {
        width: 100% !important;
        border-radius: 8px;
        font-weight: bold;
        background-color: #1E88E5;
        color: white;
    }

    /* כרטיסיות שאלון */
    .quiz-card { 
        background-color: #f9f9f9; padding: 20px; border-radius: 12px; 
        border-right: 6px solid #1E88E5; margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. ניהול משתני מערכת
for key, default in [
    ("user_name", ""), ("view_mode", "login"), ("lesson_data", ""), 
    ("quiz_data", []), ("history", []), ("lesson_count", 0), 
    ("user_answers", {}), ("current_topic", ""), ("quiz_ready", False)
]:
    if key not in st.session_state: st.session_state[key] = default

if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-2.0-flash')

def parse_quiz(text):
    questions = []
    blocks = re.findall(r"\[START_Q\](.*?)\[END_Q\]", text, re.DOTALL)
    for b in blocks:
        try:
            q = re.search(r"\[QUESTION\](.*?)\[OPTIONS\]", b, re.DOTALL).group(1).strip()
            opts_raw = re.search(r"\[OPTIONS\](.*?)\[ANSWER\]", b, re.DOTALL).group(1).strip()
            ans = re.search(r"\[ANSWER\](.*?)(?:\[LAW\]|$)", b, re.DOTALL).group(1).strip()
            law = re.search(r"\[LAW\](.*?)$", b, re.DOTALL).group(1).strip()
            options = [re.sub(r"^\d+[\s\).\-]+", "", o.strip()) for o in opts_raw.split('\n') if o.strip()]
            questions.append({"q": q, "options": options[:4], "correct": int(re.search(r'\d', ans).group())-1, "ref": law})
        except: continue
    return questions

# 3. סרגל צידי (Sidebar)
if st.session_state.user_name:
    with st.sidebar:
        st.markdown('<div class="sidebar-logo">🎓 מתווך בקליק</div>', unsafe_allow_html=True)
        st.write(f"שלום, **{st.session_state.user_name}**")
        st.markdown("---")
        
        if st.button("➕ נושא חדש"):
            for k in ["lesson_data", "quiz_data", "user_answers", "current_topic"]: st.session_state[k] = default
            st.session_state.view_mode = "setup"
            st.session_state.quiz_ready = False
            st.rerun()
            
        if st.session_state.current_topic:
            st.info(f"נושא פעיל: {st.session_state.current_topic}")
            if st.button("📖 חזרה לשיעור"):
                st.session_state.view_mode = "lesson"
                st.rerun()
            if st.session_state.quiz_ready:
                if st.button("📝 מעבר למבחן"):
                    st.session_state.view_mode = "quiz"
                    st.rerun()
        
        st.markdown("---")
        for h in st.session_state.history: st.caption(f"• {h}")

# 4. ניהול דפים
if st.session_state.view_mode == "login":
    st.title("🎓 מתווך בקליק")
    name = st.text_input("הזן שם כדי להתחיל:")
    if st.button("כניסה למערכת"):
        if name: st.session_state.user_name = name; st.session_state.view_mode = "setup"; st.rerun()

elif st.session_state.view_mode == "setup":
    st.title(f"מה נלמד היום, {st.session_state.user_name}?")
    topic = st.selectbox("בחר נושא מרשימת המבחן:", ["חוק המתווכים", "חוק המקרקעין", "דיני חוזים", "דיני תכנון ובנייה", "חוק הגנת הצרכן"])
    if st.button("התחל ללמוד"):
        st.session_state.current_topic = topic
        st.session_state.lesson_count += 1
        st.session_state.view_mode = "streaming_lesson"
        st.rerun()

elif st.session_state.view_mode == "streaming_lesson":
    st.title(f"שיעור {st.session_state.lesson_count}: {st.session_state.current_topic}")
    
    # הזרמת תוכן השיעור
    placeholder = st.empty()
    full_text = ""
    try:
        response = model.generate_content(f"כתוב שיעור מפורט על {st.session_state.current_topic} למבחן המתווכים במקרקעין.", stream=True)
        for chunk in response:
            full_text += chunk.text
            placeholder.markdown(full_text)
        
        st.session_state.lesson_data = full_text
        
        # ייצור שאלון לאחר סיום השיעור
        with st.status("מכין שאלות תרגול...", expanded=False) as status:
            q_res = model.generate_content(f"צור 3 שאלות אמריקאיות על {st.session_state.current_topic}. פורמט: [START_Q] [QUESTION] שאלה [OPTIONS] 1) א 2) ב 3) ג 4) ד [ANSWER] מספר [LAW] סעיף [END_Q]")
            st.session_state.quiz_data = parse_quiz(q_res.text)
            st.session_state.quiz_ready = True
            status.update(label="המבחן מוכן!", state="complete")

        if st.session_state.current_topic not in [h.split(". ", 1)[-1] for h in st.session_state
