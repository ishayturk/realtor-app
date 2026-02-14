import streamlit as st
import google.generativeai as genai
import re

# 1. הגדרות דף ועיצוב CSS
st.set_page_config(page_title="מתווך בקליק", layout="wide")

st.markdown("""
    <style>
    html, body, [data-testid="stAppViewContainer"] { direction: rtl; text-align: right; }
    [data-testid="stMainBlockContainer"] { margin-right: auto; margin-left: 0; padding-right: 5rem; padding-left: 2rem; }
    section[data-testid="stSidebar"] { direction: rtl; text-align: right; background-color: #f8f9fa; }
    h1, h2, h3, p, li, span, label, .stSelectbox { direction: rtl !important; text-align: right !important; }
    .lesson-header { background-color: #f0f7ff; padding: 25px; border-radius: 12px; border-right: 8px solid #1E88E5; margin-bottom: 30px; }
    div.stButton > button { width: 100%; border-radius: 8px; font-weight: bold; height: 3em; background-color: #1E88E5; color: white; }
    .stRadio > div { direction: rtl; text-align: right; }
    </style>
    """, unsafe_allow_html=True)

# 2. אתחול משתנים
if "user_name" not in st.session_state: st.session_state.user_name = ""
if "history" not in st.session_state: st.session_state.history = []
if "lesson_data" not in st.session_state: st.session_state.lesson_data = ""
if "quiz_data" not in st.session_state: st.session_state.quiz_data = []
if "current_title" not in st.session_state: st.session_state.current_title = ""

# 3. חיבור ל-AI
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-2.5-flash')

# --- פונקציה לפירוק המבחן ---
def parse_quiz(quiz_text):
    questions = []
    # מחפש תבנית של שאלה, 4 אפשרויות ותשובה
    parts = re.split(r"שאלה \d+:?", quiz_text)[1:]
    for part in parts:
        lines = [line.strip() for line in part.strip().split('\n') if line.strip()]
        if len(lines) >= 5:
            q = lines[0]
            opts = lines[1:5]
            # ניסיון למצוא את התשובה הנכונה (מחפש מספר בסוף הטקסט)
            ans_match = re.search(r"תשובה נכונה:?\s*(\d)", part)
            ans = int(ans_match.group(1)) - 1 if ans_match else 0
            questions.append({"q": q, "options": opts, "correct": ans})
    return questions

# --- פריים שמאלי קבוע ---
if st.session_state.user_name:
    with st.sidebar:
        st.header(f"שלום, {st.session_state.user_name}")
        st.markdown("---")
        if st.button("➕ נושא חדש"):
            st.session_state.lesson_data = ""
            st.session_state.quiz_data = []
            st.rerun()
        st.subheader("📚 מה למדנו:")
        for item in st.session_state.history:
            st.write(f"🔹 {item}")
        if st.button("🚪 יציאה"):
            st.session_state.user_name = ""
            st.rerun()

# --- מרכז המסך ---
if not st.session_state.user_name:
    st.title("🎓 מתווך בקליק")
    name = st.text_input("הזן שם כדי להתחיל:")
    if st.button("כניסה"):
        if name:
            st.session_state.user_name = name
            st.rerun()
else:
    if not st.session_state.lesson_data:
        st.title("בחירת נושא לימוד")
        topic = st.selectbox("בחר מהרשימה:", ["חוק המתווכים", "חוק המקרקעין", "דיני חוזים", "דיני תכנון ובנייה", "חוק הגנת הצרכן"])
        
        if st.button("כניסה לשיעור"):
            num = len(st.session_state.history) + 1
            st.session_state.current_title = f"שיעור {num}: {topic}"
            st.markdown(f'<div class="lesson-header"><h1>{st.session_state.current_title}</h1></div>', unsafe_allow_html=True)
            
            placeholder = st.empty()
            full_text = ""
            
            try:
                # 1. הזרמת השיעור
                response = model.generate_content(f"כתוב שיעור מפורט על {topic} למבחן המתווכים.", stream=True)
                for chunk in response:
                    full_text += chunk.text
                    placeholder.markdown(full_text)
                st.session_state.lesson_data = full_text
                
                # 2. יצירת המבחן בפורמט קשיח לפירוק
                quiz_prompt = f"""צור 3 שאלות אמריקאיות על {topic}. חובה להשתמש בפורמט הזה בדיוק:
                שאלה 1: [טקסט השאלה]
                1) [אופציה 1]
                2) [אופציה 2]
                3) [אופציה 3]
                4) [אופציה 4]
                תשובה נכונה: [מספר האופציה]
                """
                quiz_res = model.generate_content(quiz_prompt)
                st.session_state.quiz_data = parse_quiz(quiz_res.text)
                
                if topic not in st.session_state.history:
                    st.session_state.history.append(topic)
                st.rerun()
                
            except Exception as e:
                st.error(f"שגיאה: {e}")

    elif st.session_state.lesson_data:
        st.markdown(f'<div class="lesson-header"><h1>{st.session_state.current_title}</h1></div>', unsafe_allow
