import streamlit as st
import google.generativeai as genai
import json
import re

# 1. הגדרות RTL ועיצוב
st.set_page_config(page_title="מתווך בקליק", layout="wide")

st.markdown("""
<style>
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stMarkdownContainer"] {
        direction: rtl !important; text-align: right !important;
    }
    [data-testid="stSidebar"] { direction: rtl !important; text-align: right !important; border-left: 1px solid #ddd; }
    [data-testid="stSidebarCollapsedControl"] { right: 10px !important; left: auto !important; }
    .feedback-box { padding: 15px; border-radius: 8px; margin: 10px 0; border: 1px solid #eee; }
    .correct { background-color: #e6ffed; color: #1e4620; border-color: #b2f2bb; }
    .wrong { background-color: #fff5f5; color: #a91e2c; border-color: #ffa8a8; }
    .source-tag { background: #e7f3ff; color: #0d6efd; padding: 2px 8px; border-radius: 4px; font-weight: bold; font-size: 0.85em; }
</style>
""", unsafe_allow_html=True)

# 2. ניהול Session State
if "view_mode" not in st.session_state:
    st.session_state.update({
        "view_mode": "login", "user_name": "", "current_topic": "", 
        "lesson_data": "", "quiz_questions": []
    })

if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-2.0-flash')

def generate_quiz_json(topic):
    prompt = f"""
    Create a 5-question quiz in HEBREW about {topic} for the Israeli Real Estate exam.
    Return ONLY a JSON array: [{{"q": "...", "options": ["...", "..."], "correct": 0, "explanation": "...", "source": "..."}}]
    """
    try:
        response = model.generate_content(prompt)
        json_str = re.search(r'\[.*\]', response.text, re.DOTALL).group()
        return json.loads(json_str)
    except: return None

# 3. תפריט צד גלובלי (תמיד מופיע אחרי התחברות)
if st.session_state.user_name:
    with st.sidebar:
        st.title(f"שלום, {st.session_state.user_name}")
        st.markdown("---")
        
        if st.button("📚 בחירת נושא חדש"):
            st.session_state.update({"view_mode": "setup", "current_topic": "", "lesson_data": "", "quiz_questions": []})
            st.rerun()
            
        if st.session_state.current_topic:
            st.info(f"נושא פעיל: {st.session_state.current_topic}")
            if st.button("📖 חזרה לשיעור"):
                st.session_state.view_mode = "lesson_view"
                st.rerun()
            if st.button("✍️ שאלון תרגול"):
                st.session_state.view_mode = "lesson_quiz"
                st.rerun()
        st.markdown("---")
        if st.button("🚪 התנתק"):
            st.session_state.clear()
            st.rerun()

# 4. לוגיקת דפים
if st.session_state.view_mode == "login":
    st.title("🎓 מתווך בקליק")
    name = st.text_input("הכנס שם:")
    if st.button("כניסה"):
        if name: st.session_state.user_name = name; st.session_state.view_mode = "setup"; st.rerun()

elif st.session_state.view_mode == "setup":
    st.header("מה נלמד היום?")
    topics = ["חוק המתווכים", "חוק המקרקעין", "חוק המכר (דירות)", "חוק הגנת הצרכן", "חוק החוזים", "מיסוי מקרקעין"]
    t = st.selectbox("בחר נושא מהסילבוס:", topics)
    if st.button("התחל ללמוד"):
        st.session_state.update({"current_topic": t, "lesson_data": "", "quiz_questions": [], "view_mode": "lesson_view"})
        st.rerun()

elif st.session_state.view_mode == "lesson_view":
    st.header(st.session_state.current_topic)
    if not st.session_state.lesson_data:
        with st.spinner("מייצר שיעור מותאם..."):
            resp = model.generate_content(f"כתוב שיעור מפורט על {st.session_state.current_topic} למבחן המתווכים.")
            st.session_state.lesson_data = resp.text
    st.markdown(st.session_state.lesson_data)
    if st.button("🎯 הבנתי, בוא נתרגל!"):
        st.session_state.view_mode = "lesson_quiz"; st.rerun()

elif st.session_state.view_mode == "lesson_quiz":
    st.header(f"בוחן חכם: {st.session_state.current_topic}")
    
    if not st.session_state.quiz_questions:
        with st.spinner("מייצר שאלות עם פידבק..."):
            st.session_state.quiz_questions = generate_quiz_json(st.session_state.current_topic)
            if not st.session_state.quiz_questions: st.error("שגיאה ביצירה. נסה שוב."); st.button("נסה שוב", on_click=st.rerun)
            else: st.rerun()

    for i, q in enumerate(st.session_state.quiz_questions):
        st.subheader(f"שאלה {i+1}")
        st.write(q['q'])
        choice = st.radio(f"בחר תשובה:", q['options'], key=f"q_{i}", index=None)
        
        if choice:
            idx = q['options'].index(choice)
            if idx == q['correct']:
                st.markdown(f'<div class="feedback-box correct">✅ **נכון!** {q["explanation"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="feedback-box wrong">❌ **לא מדויק.** התשובה הנכונה היא: {q["options"][q["correct"]]}<br>{q["explanation"]}</div>', unsafe_allow_html=True)
            st.markdown(f'<span class="source-tag">📍 מקור: {q["source"]}</span>', unsafe_allow_html=True)
        st.markdown("---")
