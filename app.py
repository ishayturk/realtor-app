import streamlit as st
import google.generativeai as genai
import re
import time

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

def parse_quiz(quiz_text):
    questions = []
    parts = re.split(r"שאלה \d+:?", quiz_text)[1:]
    for part in parts:
        lines = [line.strip() for line in part.strip().split('\n') if line.strip()]
        if len(lines) >= 5:
            q_text = lines[0]
            options = lines[1:5]
            ans_match = re.search(r"תשובה נכונה:?\s*(\d)", part)
            correct_idx = int(ans_match.group(1)) - 1 if ans_match else 0
            questions.append({"q": q_text, "options": options, "correct": correct_idx})
    return questions

# --- תפריט פריים שמאלי (Sidebar) ---
if st.session_state.user_name:
    with st.sidebar:
        st.header(f"שלום, {st.session_state.user_name}")
        st.markdown("---")
        if st.button("➕ נושא חדש"):
            st.session_state.lesson_data = ""
            st.session_state.quiz_data = []
            st.rerun()
        st.subheader("📚 היסטוריה:")
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
        topic = st.selectbox("בחר נושא:", ["חוק המתווכים", "חוק המקרקעין", "דיני חוזים", "דיני תכנון ובנייה", "חוק הגנת הצרכן"])
        
        if st.button("כניסה לשיעור"):
            num = len(st.session_state.history) + 1
            st.session_state.current_title = f"שיעור {num}: {topic}"
            
            status_placeholder = st.empty()
            progress_bar = st.progress(0)
            status_placeholder.markdown("### **מכין את השיעור...**")
            progress_bar.progress(25)
            
            placeholder = st.empty()
            full_text = ""
            try:
                response = model.generate_content(f"כתוב שיעור מפורט על {topic} למבחן המתווכים.", stream=True)
                
                for chunk in response:
                    if not full_text:
                        progress_bar.progress(50)
                    full_text += chunk.text
                    placeholder.markdown(full_text)
                
                st.session_state.lesson_data = full_text
                
                status_placeholder.markdown("### **בונה מבחן תרגול...**")
                progress_bar.progress(80)
                
                quiz_prompt = f"צור 3 שאלות אמריקאיות על {topic}. פורמט: שאלה X: [טקסט] 1) [א] 2) [ב] 3) [ג] 4) [ד] תשובה נכונה: [מספר]"
                quiz_res = model.generate_content(quiz_prompt)
                st.session_state.quiz_data = parse_quiz(quiz_res.text)
                
                if topic not in st.session_state.history:
                    st.session_state.history.append(topic)
                
                progress_bar.progress(100)
                time.sleep(0.5)
                status_placeholder.empty()
                progress_bar.empty()
                st.rerun()
            except Exception as e:
                st.error(f"שגיאה בייצור השיעור: {e}")

    elif st.session_state.lesson_data:
        st.markdown(f'<div class="lesson-header"><h1>{st.session_state.current_title}</h1></div>', unsafe_allow_html=True)
        st.markdown(st.session_state.lesson_data)
        
        if st.session_state.quiz_data:
            st.markdown("---")
            st.subheader("📝 בחינה עצמית")
            for i, q in enumerate(st.session_state.quiz_data):
                st.write(f"**שאלה {i+1}: {q['q']}**")
                # index=None גורם לכך שלא תיבחר תשובה בדיפולט
                choice = st.radio("בחר תשובה:", q['options'], key=f"quiz_opt_{i}", index=None)
                
                if st.button("בדוק", key=f"btn_{i}"):
                    if choice is None:
                        st.warning("בחר תשובה לפני הבדיקה")
                    else:
                        idx = q['options'].index(choice)
                        if idx == q['correct']:
                            st.success("נכון מאוד!")
                        else:
                            st.error(f"טעות. התשובה הנכונה היא: {q['options'][q['correct']]}")
