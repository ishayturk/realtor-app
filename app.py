import streamlit as st
import google.generativeai as genai
import re

# 1. הגדרות RTL נקיות ויישור בנייד
st.set_page_config(page_title="מתווך בקליק", layout="wide")

st.markdown("""
<style>
    /* יישור גלובלי לכל האפליקציה */
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stMarkdownContainer"] {
        direction: rtl !important;
        text-align: right !important;
    }
    
    /* תיקון סיידבר והמבורגר */
    [data-testid="stSidebar"] { direction: rtl !important; text-align: right !important; }
    [data-testid="stSidebarCollapsedControl"] { right: 10px !important; left: auto !important; }

    /* יישור כפתורים */
    .stButton button { width: 100%; text-align: right !important; }
    
    /* יישור רדיו (עיגול בצד ימין) */
    div[role="radiogroup"] { direction: rtl !important; }
    
    .main-header {
        font-size: 26px; font-weight: bold; text-align: center !important;
        color: #1E88E5; border-bottom: 2px solid #1E88E5;
        padding-bottom: 10px; margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# 2. Session State
for k, v in {
    "view_mode": "login", "user_name": "", "current_topic": "",
    "lesson_data": "", "lesson_quiz_data": [], "history": []
}.items():
    if k not in st.session_state: st.session_state[k] = v

if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-2.0-flash')

def parse_quiz(text):
    qs = []
    blocks = re.split(r"\[START_Q\]", text)[1:]
    for b in blocks:
        try:
            q = re.search(r"\[QUESTION\](.*?)\[OPTIONS\]", b, re.DOTALL).group(1).strip()
            opts = re.search(r"\[OPTIONS\](.*?)\[ANSWER\]", b, re.DOTALL).group(1).strip().split('\n')
            ans = re.search(r"\[ANSWER\]\s*(\d)", b).group(1)
            qs.append({"q": q, "options": [o.strip() for o in opts if o.strip()][:4], "correct": int(ans)-1})
        except: continue
    return qs[:5]

# 3. תפריט צד
if st.session_state.user_name:
    with st.sidebar:
        st.write(f"### שלום, {st.session_state.user_name}")
        if st.button("📚 בחירת נושא"):
            st.session_state.current_topic = ""
            st.session_state.view_mode = "setup"; st.rerun()
        
        if st.session_state.current_topic:
            st.markdown("---")
            if st.button("📖 קרא שיעור"):
                st.session_state.view_mode = "lesson_view"; st.rerun()
            if st.button("✍️ שאלון תרגול"):
                st.session_state.view_mode = "lesson_quiz"; st.rerun()
        
        if st.session_state.history:
            st.markdown("---")
            st.write("📊 **היסטוריה:**")
            for h in st.session_state.history:
                st.write(f"• {h['topic']}: {h['score']}/5")

# 4. לוגיקת דפים
if st.session_state.view_mode == "login":
    st.markdown('<div class="main-header">🎓 מתווך בקליק</div>', unsafe_allow_html=True)
    name = st.text_input("שם משתמש:")
    if st.button("התחבר"):
        if name:
            st.session_state.user_name = name
            st.session_state.view_mode = "setup"; st.rerun()

elif st.session_state.view_mode == "setup":
    st.markdown('<div class="main-header">מה נלמד היום?</div>', unsafe_allow_html=True)
    t = st.selectbox("בחר נושא:", ["חוק המתווכים", "חוק המקרקעין", "דיני חוזים", "מיסוי מקרקעין"])
    if st.button("התחל ללמוד"):
        st.session_state.current_topic = t
        st.session_state.lesson_data = ""
        st.session_state.lesson_quiz_data = []
        st.session_state.view_mode = "lesson_view"; st.rerun()

elif st.session_state.view_mode == "lesson_view":
    st.markdown(f'<div class="main-header">{st.session_state.current_topic}</div>', unsafe_allow_html=True)
    
    if not st.session_state.lesson_data:
        full_text = ""
        # יצירת אלמנט ריק ומילוי שלו בהזרמה
        placeholder = st.empty()
        try:
            resp = model.generate_content(f"כתוב שיעור מפורט למבחן המתווכים על {st.session_state.current_topic}. כתוב בעברית בלבד.", stream=True)
            for chunk in resp:
                full_text += chunk.text
                placeholder.markdown(full_text)
            st.session_state.lesson_data = full_text
        except Exception as e:
            st.error("שגיאה בטעינת השיעור. נסה שוב.")
    else:
        st.markdown(st.session_state.lesson_data)
    
    st.markdown("---")
    if st.button("🎯 סיימתי לקרוא, עבור לשאלון", type="primary"):
        st.session_state.view_mode = "lesson_quiz"; st.rerun()

elif st.session_state.view_mode == "lesson_quiz":
    st.markdown(f'<div class="main-header">תרגול: {st.session_state.current_topic}</div>', unsafe_allow_html=True)
    if not st.session_state.lesson_quiz_data:
        with st.spinner("מייצר שאלות..."):
            res = model.generate_content(f"צור 5 שאלות על {st.session_state.current_topic} בפורמט [START_Q] [QUESTION] [OPTIONS] [ANSWER]")
            st.session_state.lesson_quiz_data = parse_quiz(res.text)
            st.rerun()
    
    with st.form("quiz_form"):
        choices = []
        for i, q in enumerate(st.session_state.lesson_quiz_data):
            st.write(f"**{i+1}. {q['q']}**")
            c = st.radio(f"בחר תשובה {i+1}:", q['options'], key=f"q_{i}", index=None)
            choices.append(c)
            st.markdown("---")
        
        if st.form_submit_button("בדוק ציון"):
            score = 0
            for i, q in enumerate(st.session_state.lesson_quiz_data):
                if choices[i] and q['options'].index(choices[i]) == q['correct']:
                    score += 1
            st.success(f"הציון שלך: {score} מתוך 5")
            # הוספה להיסטוריה
            st.session_state.history.append({"topic": st.session_state.current_topic, "score": score})
