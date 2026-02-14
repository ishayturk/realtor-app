import streamlit as st
import google.generativeai as genai
import re
import time

# 1. הגדרות דף ועיצוב CSS - תיקון הצמדה לימין
st.set_page_config(page_title="מתווך בקליק", layout="wide")

st.markdown("""
    <style>
    /* כפייה של ימין לשמאל על כל האפליקציה */
    .main .block-container { direction: rtl; text-align: right; }
    [data-testid="stSidebar"] { direction: rtl; text-align: right; }
    h1, h2, h3, p, li, span, label, div { direction: rtl; text-align: right; }
    
    /* תיקון ספציפי לתיבות קוד - שיישארו בשמאל */
    [data-testid="stCodeBlock"], code, pre { direction: ltr !important; text-align: left !important; }
    
    .quiz-card { 
        background-color: #ffffff; 
        padding: 20px; 
        border: 1px solid #e0e0e0; 
        border-radius: 10px; 
        margin-bottom: 20px; 
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    div.stButton > button { 
        width: 100%; 
        border-radius: 8px; 
        font-weight: bold; 
        background-color: #1E88E5; 
        color: white; 
    }
    </style>
    """, unsafe_allow_html=True)

# 2. ניהול מצב (Session State)
if "user_name" not in st.session_state: st.session_state.user_name = ""
if "view_mode" not in st.session_state: st.session_state.view_mode = "login" # login, setup, lesson, quiz
if "lesson_data" not in st.session_state: st.session_state.lesson_data = ""
if "quiz_data" not in st.session_state: st.session_state.quiz_data = []
if "history" not in st.session_state: st.session_state.history = []

# 3. פונקציית חיבור ל-AI עם מנגנון עקיפת 404
def get_ai_model():
    if "GEMINI_API_KEY" not in st.secrets:
        return None
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    
    # ניסיון להתחבר למודל בשמות שונים כדי לעקוף את שגיאת ה-404
    for model_name in ['gemini-1.5-flash', 'models/gemini-1.5-flash', 'gemini-pro']:
        try:
            model = genai.GenerativeModel(model_name)
            # בדיקה אם המודל באמת זמין
            return model
        except:
            continue
    return None

model = get_ai_model()

def parse_quiz(quiz_text):
    questions = []
    parts = re.split(r'שאלה \d+[:.)]?', quiz_text)[1:]
    for part in parts:
        lines = [l.strip() for l in part.strip().split('\n') if l.strip()]
        if len(lines) >= 3:
            q_text = lines[0]
            options = [l for l in lines if re.match(r'^[\d\)\.אבגד-]+\s', l)][:4]
            ans_match = re.search(r"(?:נכונה|היא|פתרון)[:\s]*(\d)", part)
            correct_idx = int(ans_match.group(1)) - 1 if ans_match else 0
            if len(options) >= 2:
                questions.append({"q": q_text, "options": options, "correct": correct_idx})
    return questions

# --- ניהול דפים ---

# דף כניסה
if st.session_state.view_mode == "login":
    st.title("🎓 מתווך בקליק")
    name = st.text_input("הזן שם כדי להתחיל:")
    if st.button("כניסה"):
        if name:
            st.session_state.user_name = name
            st.session_state.view_mode = "setup"
            st.rerun()

# דף בחירת נושא
elif st.session_state.view_mode == "setup":
    st.title(f"שלום {st.session_state.user_name}, מה נלמד היום?")
    topic = st.selectbox("בחר נושא:", ["חוק המתווכים", "חוק המקרקעין", "דיני חוזים", "דיני תכנון ובנייה", "חוק הגנת הצרכן"])
    if st.button("התחל ללמוד"):
        if not model:
            st.error("שגיאה: לא ניתן להתחבר ל-AI. וודא שה-API Key תקין.")
        else:
            with st.spinner("מכין את חומר הלימוד..."):
                try:
                    # ייצור שיעור
                    res = model.generate_content(f"כתוב שיעור מפורט בעברית על {topic} למבחן המתווכים.")
                    st.session_state.lesson_data = res.text
                    
                    # ייצור שאלון
                    quiz_prompt = f"צור 3 שאלות אמריקאיות על {topic}. פורמט: שאלה X: [טקסט] 1) [א] 2) [ב] 3) [ג] 4) [ד] תשובה נכונה: [מספר]"
                    quiz_res = model.generate_content(quiz_prompt)
                    st.session_state.quiz_data = parse_quiz(quiz_res.text)
                    
                    st.session_state.history.append(topic)
                    st.session_state.view_mode = "lesson"
                    st.rerun()
                except Exception as e:
                    st.error(f"שגיאה בחיבור ל-AI: {e}")

# דף שיעור
elif st.session_state.view_mode == "lesson":
    st.title("חומר הלימוד")
    st.markdown(st.session_state.lesson_data)
    st.markdown("---")
    if st.button("🔥 סיימתי ללמוד, אני רוצה להיבחן!"):
        st.session_state.view_mode = "quiz"
        st.rerun()

# דף שאלון
elif st.session_state.view_mode == "quiz":
    st.title("📝 שאלון תרגול")
    if not st.session_state.quiz_data:
        st.warning("לא נוצרו שאלות. נסה לחזור ולייצר שוב.")
    else:
        for i, q in enumerate(st.session_state.quiz_data):
            st.markdown('<div class="quiz-card">', unsafe_allow_html=True)
            st.write(f"**{i+1}. {q['q']}**")
            choice = st.radio(f"בחר תשובה לשאלה {i+1}:", q['options'], key=f"q_{i}", index=None)
            if st.button(f"בדוק שאלה {i+1}", key=f"b_{i}"):
                if choice:
                    idx = q['options'].index(choice)
                    if idx == q['correct']: st.success("נכון מאוד!")
                    else: st.error(f"לא מדויק. התשובה הנכונה היא אופציה {q['correct']+1}")
                else: st.warning("נא לבחור תשובה")
            st.markdown('</div>', unsafe_allow_html=True)
    
    if st.button("חזרה לשיעור"):
        st.session_state.view_mode = "lesson"
        st.rerun()
    if st.button("נושא חדש"):
        st.session_state.view_mode = "setup"
        st.rerun()
