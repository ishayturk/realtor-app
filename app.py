import streamlit as st
import google.generativeai as genai
import re

# 1. הגדרות RTL אגרסיביות - יישור ימין מלא לכל האלמנטים
st.set_page_config(page_title="מתווך בקליק", layout="wide")

st.markdown("""
<style>
    /* יישור גלובלי */
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stMarkdownContainer"] {
        direction: rtl !important;
        text-align: right !important;
    }

    /* יישור הסיידבר (הפריים הצידי) */
    [data-testid="stSidebar"] {
        direction: rtl !important;
        text-align: right !important;
        border-left: 1px solid #e0e0e0;
    }

    /* העברת כפתור ההמבורגר לימין בנייד */
    [data-testid="stSidebarCollapsedControl"] {
        right: 10px !important;
        left: auto !important;
    }

    /* תיקון בולטים (נקודות) */
    ul, ol {
        direction: rtl !important;
        text-align: right !important;
        padding-right: 1.5rem !important;
        list-style-position: inside !important;
    }
    
    li { text-align: right !important; }

    /* יישור כפתורים ורדיו */
    .stButton button { width: 100%; text-align: right !important; direction: rtl !important; }
    div[role="radiogroup"] { direction: rtl !important; }
    
    .main-header {
        font-size: 26px; font-weight: bold; text-align: center !important;
        color: #1E88E5; border-bottom: 2px solid #1E88E5;
        padding-bottom: 10px; margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# 2. ניהול מצב (Session State)
state_keys = {
    "view_mode": "login", 
    "user_name": "", 
    "current_topic": "",
    "lesson_data": "", 
    "lesson_quiz_data": [], 
    "history": []
}

for key, value in state_keys.items():
    if key not in st.session_state:
        st.session_state[key] = value

if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-2.0-flash')

def parse_quiz(text):
    qs = []
    blocks = re.split(r"\[START_Q\]", text)[1:]
    for b in blocks:
        try:
            q_match = re.search(r"\[QUESTION\](.*?)\[OPTIONS\]", b, re.DOTALL)
            o_match = re.search(r"\[OPTIONS\](.*?)\[ANSWER\]", b, re.DOTALL)
            a_match = re.search(r"\[ANSWER\]\s*(\d)", b)
            
            if q_match and o_match and a_match:
                q = q_match.group(1).strip()
                opts_text = o_match.group(1).strip()
                opts = [o.strip() for o in opts_text.split('\n') if o.strip()]
                ans = int(a_match.group(1)) - 1
                if q and len(opts) >= 2:
                    qs.append({"q": q, "options": opts[:4], "correct": ans})
        except:
            continue
    return qs[:5]

# 3. תפריט צד (Sidebar)
if st.session_state.user_name:
    with st.sidebar:
        st.markdown(f"### שלום, {st.session_state.user_name}")
        if st.button("📚 בחירת נושא"):
            st.session_state.view_mode = "setup"
            st.rerun()
        
        if st.session_state.current_topic:
            st.markdown("---")
            topic_display = st.session_state.current_topic
            st.write(f"📖 **נושא:** {topic_display}")
            if st.button("📖 קרא שיעור"):
                st.session_state.view_mode = "lesson_view"
                st.rerun()
            if st.button("✍️ שאלון תרגול"):
                st.session_state.view_mode = "lesson_quiz"
                st.rerun()
        
        if st.session_state.history:
            st.markdown("---")
            st.write("📊 **היסטוריית ציונים:**")
            for h in st.session_state.history:
                st.write(f"• {h['topic']}: {h['score']}/5")

# 4. לוגיקת דפים
if st.session_state.view_mode == "login":
    st.markdown('<div class="main-header">🎓 מתווך בקליק</div>', unsafe_allow_html=True)
    name = st.text_input("שם משתמש:")
    if st.button("התחבר"):
        if name:
            st.session_state.user_name = name
            st.session_state.view_mode = "setup"
            st.rerun()

elif st.session_state.view_mode == "setup":
    st.markdown('<div class="main-header">מה נלמד היום?</div>', unsafe_allow_html=True)
    topics = ["חוק המתווכים", "חוק המקרקעין", "דיני חוזים", "מיסוי מקרקעין"]
    t = st.selectbox("בחר נושא:", topics)
    if st.button("התחל ללמוד"):
        st.session_state.current_topic = t
        st.session_state.lesson_data = ""
        st.session_state.lesson_quiz_data = []
        st.session_state.view_mode = "lesson_view"
        st.rerun()

elif st.session_state.view_mode == "lesson_view":
    curr_t = st.session_state.current_topic
    st.markdown(f'<div class="main-header">{curr_t}</div>', unsafe_allow_html=True)
    
    if not st.session_state.lesson_data:
        full_text = ""
        placeholder = st.empty()
        prompt = f"כתוב שיעור מפורט למבחן המתווכים על {curr_t}. השתמש בבולטים."
        resp = model.generate_content(prompt, stream=True)
        for chunk in resp:
            full_text += chunk.text
            placeholder.markdown(full_text)
        st.session_state.lesson_data = full_text
    else:
        st.markdown(st.session_state.lesson_data)
    
    st.markdown("---")
    if st.button("🎯 עבור לשאלון תרגול", type="primary"):
        st.session_state.view_mode = "lesson_quiz"
        st.rerun()

elif st.session_state.view_mode == "lesson_quiz":
    curr_t = st.session_state.current_topic
    st.markdown(f'<div class="main-header">תרגול: {curr_t}</div>', unsafe_allow_html=True)
    
    if not st.session_state.lesson_quiz_data:
        with st.spinner("מייצר שאלות..."):
            p = f"צור 5 שאלות על {curr_t} בפורמט [START_Q] [QUESTION] [OPTIONS] [ANSWER]"
            res = model.generate_content(p)
            st.session_state.lesson_quiz_data = parse_quiz(res.text)
            st.rerun()
    
    with st.form("quiz_form"):
        choices = []
        for i, q in enumerate(st.session_state.lesson_quiz_data):
            st.write(f"**{i+1}. {q['q']}**")
            c = st.radio(f"בחירה {i+1}:", q['options'], key=f"q_{i}", index=None)
            choices.append(c)
            st.markdown("---")
        
        if st.form_submit_button("בדוק ציון"):
            score = 0
            for i, q in enumerate(st.session_state.lesson_quiz_data):
                if choices[i] and q['options'].index(choices[i]) == q['correct']:
                    score += 1
            st.success(f"הציון שלך: {score} מתוך 5")
            st.session_state.history.append({"topic": curr_t, "score": score})
