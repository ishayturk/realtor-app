import streamlit as st
import google.generativeai as genai
import json
import re

# 1. הגדרות RTL ועיצוב גלובלי
st.set_page_config(page_title="מתווך בקליק", layout="wide")

st.markdown("""
<style>
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stMarkdownContainer"] {
        direction: rtl !important; text-align: right !important;
    }
    [data-testid="stSidebar"] { direction: rtl !important; text-align: right !important; }
    
    .app-header {
        background-color: #f8f9fa; padding: 25px; border-radius: 12px;
        text-align: center; border-bottom: 5px solid #1E88E5; margin-bottom: 30px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    .feedback-box { padding: 15px; border-radius: 8px; margin: 10px 0; border: 1px solid #eee; line-height: 1.6; }
    .correct { background-color: #e6ffed; color: #1e4620; border-color: #b2f2bb; }
    .wrong { background-color: #fff5f5; color: #a91e2c; border-color: #ffa8a8; }
    
    .score-banner {
        background: linear-gradient(90deg, #1E88E5, #1565C0);
        color: white; padding: 20px; border-radius: 15px;
        text-align: center; margin-top: 40px; font-size: 1.2em;
    }
    .source-tag { 
        display: inline-block; background: #e7f3ff; color: #0d6efd; 
        padding: 4px 12px; border-radius: 20px; font-size: 0.85em; margin-top: 8px;
    }
</style>
""", unsafe_allow_html=True)

# כותרת קבועה בראש האפליקציה
st.markdown("""
<div class="app-header">
    <div style="font-size: 60px; margin-bottom: 10px;">🎓</div>
    <h1 style='color: #1E88E5; margin: 0; font-size: 2.5em;'>מתווך בקליק</h1>
    <p style='color: #666; font-size: 1.1em;'>השותף החכם שלך למבחן המתווכים (Gemini 2.0 Flash)</p>
</div>
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
    """יצירת שאלון עם דרישה להסברים ומקורות"""
    prompt = f"""
    Create a 5-question multiple choice quiz in HEBREW about {topic} for the Israeli Real Estate license exam.
    Return ONLY a valid JSON array of objects.
    Each object MUST have:
    "q": "The question",
    "options": ["opt1", "opt2", "opt3", "opt4"],
    "correct": index (0-3),
    "explanation": "Brief legal explanation in Hebrew",
    "source": "Specific law section"
    """
    try:
        response = model.generate_content(prompt)
        json_str = re.search(r'\[.*\]', response.text, re.DOTALL).group()
        return json.loads(json_str)
    except: return None

# 3. תפריט צד קבוע
if st.session_state.user_name:
    with st.sidebar:
        st.markdown(f"### שלום, **{st.session_state.user_name}**")
        st.markdown("---")
        if st.button("🏠 דף הבית / בחירת נושא"):
            st.session_state.update({"view_mode": "setup", "quiz_questions": []})
            st.rerun()
        if st.session_state.current_topic:
            st.info(f"לומד כעת: {st.session_state.current_topic}")
            if st.button("📖 קרא שוב את השיעור"):
                st.session_state.view_mode = "lesson_view"; st.rerun()
            if st.button("✍️ תרגול נוסף (שאלות חדשות)"):
                st.session_state.quiz_questions = []
                st.session_state.view_mode = "lesson_quiz"; st.rerun()
        st.markdown("---")
        if st.button("🚪 יציאה"):
            st.session_state.clear(); st.rerun()

# 4. לוגיקת ניווט
if st.session_state.view_mode == "login":
    st.subheader("ברוך הבא! הכנס שם כדי להתחיל")
    name = st.text_input("שם המשתמש שלך:")
    if st.button("התחל ללמוד"):
        if name: st.session_state.user_name = name; st.session_state.view_mode = "setup"; st.rerun()

elif st.session_state.view_mode == "setup":
    st.header("מה נלמד היום?")
    topics = [
        "חוק המתווכים במקרקעין", "חוק המקרקעין", "חוק המכר (דירות)", 
        "חוק הגנת הצרכן", "חוק החוזים", "מיסוי מקרקעין", "דיני ירושה"
    ]
    t = st.selectbox("בחר נושא מהסילבוס:", topics)
    if st.button("צור שיעור מותאם"):
        st.session_state.update({
            "current_topic": t, "lesson_data": "", 
            "quiz_questions": [], "view_mode": "lesson_view"
        })
        st.rerun()

elif st.session_state.view_mode == "lesson_view":
    st.header(st.session_state.current_topic)
    if not st.session_state.lesson_data:
        with st.spinner("Gemini 2.0 מנתח את החוק וכותב שיעור..."):
            resp = model.generate_content(f"כתוב שיעור מפורט למבחן המתווכים על {st.session_state.current_topic}.")
            st.session_state.lesson_data = resp.text
    st.markdown(st.session_state.lesson_data)
    if st.button("🎯 הבנתי, בוא נבחן את הידע (שאלון)"):
        st.session_state.view_mode = "lesson_quiz"; st.rerun()

elif st.session_state.view_mode == "lesson_quiz":
    st.header(f"תרגול אקטיבי: {st.session_state.current_topic}")
    
    if not st.session_state.quiz_questions:
        with st.spinner("מייצר שאלות ברמת מבחן..."):
            st.session_state.quiz_questions = generate_quiz_json(st.session_state.current_topic)
            if not st.session_state.quiz_questions:
                st.error("הייתה תקלה ביצירה. נסה שוב.")
                if st.button("נסה שוב"): st.rerun()
            else: st.rerun()

    score = 0
    answered = 0
    
    for i, q in enumerate(st.session_state.quiz_questions):
        st.subheader(f"שאלה {i+1}")
        st.write(q['q'])
        choice = st.radio(f"בחר תשובה:", q['options'], key=f"q_final_{i}", index=None)
        
        if choice:
            answered += 1
            idx = q['options'].index(choice)
            if idx == q['correct']:
                st.markdown(f'<div class="feedback-box correct">✅ **נכון מאוד!** {q.get("explanation","")}</div>', unsafe_allow_html=True)
                score += 1
            else:
                st.markdown(f'<div class="feedback-box wrong">❌ **לא נכון.** התשובה הנכונה היא: {q["options"][q["correct"]]}<br>{q.get("explanation","")}</div>', unsafe_allow_html=True)
            st.markdown(f'<span class="source-tag">📍 מקור משפטי: {q.get("source","חוק")}</span>', unsafe_allow_html=True)
        st.markdown("---")

    if answered > 0:
        st.markdown(f"""
        <div class="score-banner">
            <h3>סיכום ביניים: {score} מתוך {len(st.session_state.quiz_questions)} תשובות נכונות</h3>
        </div>
        """, unsafe_allow_html=True)
        if score == 5:
