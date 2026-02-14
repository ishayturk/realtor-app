import streamlit as st
import google.generativeai as genai
import re
import time

# 1. הגדרות דף ועיצוב CSS
st.set_page_config(page_title="מתווך בקליק", layout="wide")

st.markdown("""
    <style>
    /* יישור כללי לימין */
    html, body, [data-testid="stAppViewContainer"] { direction: rtl; text-align: right; }
    [data-testid="stMainBlockContainer"] { margin-right: auto; margin-left: 0; padding-right: 5rem; padding-left: 2rem; }
    section[data-testid="stSidebar"] { direction: rtl; text-align: right; background-color: #f8f9fa; }
    
    /* קיבוע תיבות קוד לשמאל */
    [data-testid="stCodeBlock"], code, pre { 
        direction: ltr !important; 
        text-align: left !important; 
        unicode-bidi: plaintext;
    }

    h1, h2, h3, p, li, span, label, .stSelectbox { direction: rtl !important; text-align: right !important; }
    
    .lesson-header { background-color: #f0f7ff; padding: 25px; border-radius: 12px; border-right: 8px solid #1E88E5; margin-bottom: 30px; }
    .quiz-card { background-color: #ffffff; padding: 20px; border: 1px solid #e0e0e0; border-radius: 10px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    
    div.stButton > button { width: 100%; border-radius: 8px; font-weight: bold; height: 3em; background-color: #1E88E5; color: white; }
    </style>
    """, unsafe_allow_html=True)

# 2. אתחול משתנים
if "user_name" not in st.session_state: st.session_state.user_name = ""
if "history" not in st.session_state: st.session_state.history = []
if "lesson_data" not in st.session_state: st.session_state.lesson_data = ""
if "quiz_data" not in st.session_state: st.session_state.quiz_data = []
if "current_title" not in st.session_state: st.session_state.current_title = ""
if "view_mode" not in st.session_state: st.session_state.view_mode = "setup"

# 3. חיבור ל-AI
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')

def parse_quiz(quiz_text):
    questions = []
    parts = re.split(r'שאלה \d+[:.)]?', quiz_text)[1:]
    for part in parts:
        lines = [l.strip() for l in part.strip().split('\n') if l.strip()]
        if len(lines) >= 5:
            q_text = lines[0]
            options = lines[1:5]
            ans_match = re.search(r"(?:נכונה|היא|פתרון)[:\s]*(\d)", part)
            correct_idx = int(ans_match.group(1)) - 1 if ans_match else 0
            questions.append({"q": q_text, "options": options, "correct": correct_idx})
    return questions

# --- סיידבר ---
if st.session_state.user_name:
    with st.sidebar:
        st.header(f"שלום, {st.session_state.user_name}")
        if st.button("➕ נושא חדש"):
            st.session_state.view_mode = "setup"
            st.session_state.lesson_data = ""
            st.session_state.quiz_data = []
            st.rerun()
        st.markdown("---")
        st.subheader("📚 היסטוריה:")
        for item in st.session_state.history:
            st.write(f"🔹 {item}")

# --- ניווט דפים ---
if not st.session_state.user_name:
    st.title("🎓 מתווך בקליק")
    name = st.text_input("הזן שם כדי להתחיל:")
    if st.button("כניסה"):
        if name:
            st.session_state.user_name = name
            st.rerun()

elif st.session_state.view_mode == "setup":
    st.title("מה נלמד היום?")
    topic = st.selectbox("בחר נושא:", ["חוק המתווכים", "חוק המקרקעין", "דיני חוזים", "דיני תכנון ובנייה", "חוק הגנת הצרכן"])
    if st.button("כניסה לשיעור"):
        num = len(st.session_state.history) + 1
        st.session_state.current_title = f"שיעור {num}: {topic}"
        
        status = st.empty()
        bar = st.progress(0)
        status.markdown("### **מכין את השיעור...**")
        
        placeholder = st.empty()
        full_text = ""
        try:
            response = model.generate_content(f"כתוב שיעור מפורט על {topic} למבחן המתווכים.", stream=True)
            for chunk in response:
                full_text += chunk.text
                placeholder.markdown(full_text)
            st.session_state.lesson_data = full_text
            
            status.markdown("### **בונה שאלות תרגול...**")
            bar.progress(70)
            quiz_prompt = "צור 3 שאלות אמריקאיות על הנושא. פורמט: שאלה X: [טקסט] 1) [א] 2) [ב] 3) [ג] 4) [ד] תשובה נכונה: [מספר]"
            quiz_res = model.generate_content(quiz_prompt)
            st.session_state.quiz_data = parse_quiz(quiz_res.text)
            
            if topic not in st.session_state.history:
                st.session_state.history.append(topic)
            
            bar.progress(100)
            time.sleep(0.5)
            status.empty()
            bar.empty()
            st.session_state.view_mode = "lesson"
            st.rerun()
        except Exception as e:
            st.error(f"שגיאה: {e}")

elif st.session_state.view_mode == "lesson":
    st.markdown(f'<div class="lesson-header"><h1>{st.session_state.current_title}</h1></div>', unsafe_allow_html=True)
    st.markdown(st.session_state.lesson_data)
    st.markdown("---")
    if st.button("🔥 סיימתי ללמוד, אני רוצה להיבחן!"):
        st.session_state.view_mode = "quiz"
        st.rerun()

elif st.session_state.view_mode == "quiz":
    st.markdown(f'<div class="lesson-header"><h1>📝 מבחן תרגול: {st.session_state.current_title}</h1></div>', unsafe_allow_html=True)
    
    if not st.session_state.quiz_data:
        st.warning("לא נוצרו שאלות.")
        if st.button("חזרה לשיעור"):
            st.session_state.view_mode = "lesson"
            st.rerun()
    else:
        for i, q in enumerate(st.session_state.quiz_data):
            st.markdown('<div class="quiz-card">', unsafe_allow_html=True)
            st.write(f"**שאלה {i+1}: {q['q']}**")
            choice = st.radio("בחר תשובה:", q['options'], key=f"q_{i}", index=None)
            if st.button("בדוק", key=f"btn_{i}"):
                if choice:
                    idx = q['options'].index(choice)
                    if idx == q['correct']:
                        st.success("נכון מאוד!")
                    else:
                        st.error(f"טעות. התשובה הנכונה היא אופציה {q['correct']+1}")
                else:
                    st.warning("נא לבחור תשובה")
            st.markdown('</div>', unsafe_allow_html=True)
        
        if st.button("⬅️ חזרה לטקסט השיעור"):
            st.session_state.view_mode = "lesson"
            st.rerun()
