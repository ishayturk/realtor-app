import streamlit as st
import google.generativeai as genai
import re
import time

# 1. הגדרות עיצוב ו-RTL
st.set_page_config(page_title="מתווך בקליק", layout="wide")

st.markdown("""
    <style>
    .main .block-container { direction: rtl; text-align: right; }
    [data-testid="stSidebar"] { direction: rtl; text-align: right; }
    h1, h2, h3, p, li, span, label { direction: rtl !important; text-align: right !important; }
    
    /* עיצוב כרטיס שאלה */
    .quiz-card { 
        background-color: #f9f9f9; 
        padding: 20px; 
        border-radius: 12px; 
        border-right: 5px solid #1E88E5;
        margin-bottom: 20px;
    }
    
    /* כפתורים */
    div.stButton > button { 
        width: 100%; 
        border-radius: 8px; 
        height: 3em; 
        background-color: #1E88E5; 
        color: white; 
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. ניהול הזיכרון (Session State)
if "user_name" not in st.session_state: st.session_state.user_name = ""
if "view_mode" not in st.session_state: st.session_state.view_mode = "login"
if "lesson_data" not in st.session_state: st.session_state.lesson_data = ""
if "quiz_data" not in st.session_state: st.session_state.quiz_data = []
if "history" not in st.session_state: st.session_state.history = []
if "current_topic" not in st.session_state: st.session_state.current_topic = ""

# 3. אתחול AI (מודל 2.0 פלאש)
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-2.0-flash')

def parse_quiz(quiz_text):
    questions = []
    # פיצול לפי מילת המפתח "שאלה"
    parts = re.split(r'שאלה \d+[:.)]?', quiz_text)[1:]
    for part in parts:
        lines = [l.strip() for l in part.strip().split('\n') if l.strip()]
        if len(lines) >= 5:
            q_text = lines[0]
            options = lines[1:5]
            # חיפוש התשובה הנכונה
            ans_match = re.search(r"תשובה נכונה[:\s]*(\d)", part)
            correct_idx = int(ans_match.group(1)) - 1 if ans_match else 0
            questions.append({"q": q_text, "options": options, "correct": correct_idx})
    return questions

# --- סרגל צד (היסטוריה) ---
if st.session_state.user_name:
    with st.sidebar:
        st.header(f"שלום, {st.session_state.user_name}")
        if st.button("➕ נושא חדש"):
            st.session_state.view_mode = "setup"
            st.rerun()
        st.markdown("---")
        st.subheader("📚 נושאים שלמדת:")
        for item in st.session_state.history:
            st.write(f"✅ {item}")

# --- ניווט דפים ---

# דף 1: כניסה
if st.session_state.view_mode == "login":
    st.title("🎓 מתווך בקליק")
    st.subheader("הכנה למבחן המתווכים בבינה מלאכותית")
    name = st.text_input("הזן שם כדי להתחיל:")
    if st.button("כניסה למערכת"):
        if name:
            st.session_state.user_name = name
            st.session_state.view_mode = "setup"
            st.rerun()

# דף 2: בחירת נושא
elif st.session_state.view_mode == "setup":
    st.title("מה נלמד היום?")
    topic = st.selectbox("בחר נושא מהסילבוס:", [
        "חוק המתווכים במקרקעין", 
        "חוק המקרקעין", 
        "דיני חוזים", 
        "חוק הגנת הצרכן", 
        "דיני תכנון ובנייה"
    ])
    
    if st.button("התחל שיעור"):
        st.session_state.current_topic = topic
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # שלב א: יצירת השיעור
            status_text.text("מכין את חומר הלימוד...")
            progress_bar.progress(25)
            lesson_res = model.generate_content(f"כתוב שיעור מפורט ומעמיק בעברית על {topic} למבחן המתווכים. השתמש בכותרות ונקודות.")
            st.session_state.lesson_data = lesson_res.text
            
            # שלב ב: יצירת המבחן (מאחורי הקלעים)
            progress_bar.progress(60)
            status_text.text("בונה שאלות תרגול מותאמות...")
            quiz_prompt = f"על בסיס הנושא {topic}, צור 3 שאלות אמריקאיות. פורמט: שאלה X: [טקסט] 1) [א] 2) [ב] 3) [ג] 4) [ד] תשובה נכונה: [מספר]"
            quiz_res = model.generate_content(quiz_prompt)
            st.session_state.quiz_data = parse_quiz(quiz_res.text)
            
            progress_bar.progress(100)
            if topic not in st.session_state.history:
                st.session_state.history.append(topic)
            
            time.sleep(1) # השהיה קלה לתחושת הצלחה
            st.session_state.view_mode = "lesson"
            st.rerun()
        except Exception as e:
            st.error(f"שגיאה: {e}")

# דף 3: תוכן השיעור
elif st.session_state.view_mode == "lesson":
    st.title(f"שיעור: {st.session_state.current_topic}")
    st.markdown(st.session_state.lesson_data)
    st.markdown("---")
    if st.button("🔥 סיימתי ללמוד, אני רוצה להיבחן!"):
        st.session_state.view_mode = "quiz"
        st.rerun()

# דף 4: שאלון תרגול
elif st.session_state.view_mode == "quiz":
    st.title(f"📝 תרגול: {st.session_state.current_topic}")
    
    if not st.session_state.quiz_data:
        st.warning("לא נוצרו שאלות תרגול לנושא זה.")
    else:
        for i, q in enumerate(st.session_state.quiz_data):
            st.markdown(f'<div class="quiz-card">', unsafe_allow_html=True)
            st.write(f"**שאלה {i+1}:** {q['q']}")
            choice = st.radio(f"בחר תשובה {i}:", q['options'], key=f"q_{i}", index=None, label_visibility="collapsed")
            
            if st.button(f"בדוק תשובה {i+1}", key=f"btn_{i}"):
                if choice:
                    idx = q['options'].index(choice)
                    if idx == q['correct']:
                        st.success("נכון מאוד! כל הכבוד.")
                    else:
                        st.error(f"לא נכון. התשובה הנכונה היא אופציה {q['correct']+1}")
                else:
                    st.warning("נא לבחור תשובה לפני הבדיקה.")
            st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    if st.button("⬅️ חזרה לשיעור"):
        st.session_state.view_mode = "lesson"
        st.rerun()
    if st.button("🔝 חזרה לבחירת נושא חדש"):
        st.session_state.view_mode = "setup"
        st.rerun()
