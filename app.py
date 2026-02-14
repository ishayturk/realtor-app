import streamlit as st
import google.generativeai as genai
import time
import random

# 1. הגדרות תצוגה ויישור
st.set_page_config(page_title="מתווך בקליק", layout="centered")

# הזרקת CSS לתיקון המיקומים ועיצוב קבוע
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"], .main, .block-container {
        direction: rtl !important;
        text-align: right !important;
    }
    h1, h2, h3, .centered-header {
        text-align: center !important;
        width: 100%;
        display: block;
        color: #1E88E5;
    }
    .stButton > button {
        display: block;
        margin-right: 0;
        margin-left: auto;
        border-radius: 10px;
    }
    input { direction: rtl !important; text-align: right !important; }
    .lesson-box {
        border: 1px solid #ddd; padding: 15px; border-radius: 10px; 
        background: #fff; color: #1a1a1a; line-height: 1.6;
    }
    .timer-box {
        text-align: center; background: #ffebee; border: 1px solid #d32f2f;
        padding: 10px; border-radius: 10px; font-weight: bold; color: #d32f2f;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. אתחול משתני מערכת (Session State)
if "view" not in st.session_state:
    st.session_state.update({
        "view": "login", "user": "", "topic": "", "lesson": "",
        "exam_questions": [], "user_answers": {}, "idx": 0, "start_time": None
    })

# 3. פונקציות עזר ומאגר
def get_official_questions():
    # כאן יבוא המאגר המלא מהלינק. בנתיים 2 שוגמאות משוכפלות ל-25.
    pool = [
        {"q": "מהי תקופת הבלעדיות המקסימלית בדירת מגורים?", "options": ["3 חודשים", "6 חודשים", "שנה", "ללא הגבלה"], "correct": 1},
        {"q": "האם מתווך זכאי לדמי תיווך ללא הזמנה בכתב?", "options": ["כן", "רק אם הלקוח הסכים", "לא, חובה הזמנה בכתב חתומה", "רק בבלעדיות"], "correct": 2}
    ]
    full_list = (pool * 13)[:25]
    return full_list

def init_gemini():
    if "GEMINI_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        return genai.GenerativeModel('gemini-1.5-flash')
    return None

model = init_gemini()

# ==========================================
# לוגו וכותרת קבועה (מחוץ ל-IF - מופיע תמיד)
# ==========================================
st.markdown('<h1>🏠 מתווך בקליק</h1>', unsafe_allow_html=True)
st.write("---")

# ==========================================
# ניהול הדפים
# ==========================================

# --- דף כניסה ---
if st.session_state.view == "login":
    st.markdown('### ברוכים הבאים! הכנס שם כדי להתחיל.', unsafe_allow_html=True)
    name = st.text_input("שם מלא:", key="name_input")
    if st.button("כניסה למערכת 🔓"):
        if name:
            st.session_state.user = name
            st.session_state.view = "menu"
            st.rerun()

# --- תפריט ראשי ---
elif st.session_state.view == "menu":
    st.markdown(f'### שלום {st.session_state.user} 👋', unsafe_allow_html=True)
    
    if st.button("📚 לימוד לפי נושאים"):
        st.session_state.view = "select_topic"
        st.rerun()
        
    if st.button("🚀 התחל מבחן רישוי (25 שאלות)"):
        st.session_state.exam_questions = get_official_questions()
        st.session_state.user_answers = {}
        st.session_state.idx = 0
        st.session_state.start_time = time.time()
        st.session_state.view = "exam"
        st.rerun()

# --- בחירת נושא ---
elif st.session_state.view == "select_topic":
    st.markdown('### בחר נושא ללימוד', unsafe_allow_html=True)
    topic = st.selectbox("נושאים:", ["חוק המתווכים", "חוק המקרקעין", "חוק החוזים"])
    if st.button("התחל שיעור"):
        st.session_state.topic = topic
        st.session_state.lesson = ""
        st.session_state.view = "lesson"
        st.rerun()
    if st.button("חזרה לתפריט"):
        st.session_state.view = "menu"
        st.rerun()

# --- דף שיעור ---
elif st.session_state.view == "lesson":
    st.markdown(f'### שיעור: {st.session_state.topic}', unsafe_allow_html=True)
    if not st.session_state.lesson:
        with st.spinner("ה-AI מכין חומר..."):
            if model:
                resp = model.generate_content(f"כתוב שיעור קצר למבחן המתווכים על {st.session_state.topic}")
                st.session_state.lesson = resp.text
            else: st.warning("מפתח API חסר.")
    st.markdown(f'<div class="lesson-box">{st.session_state.lesson}</div>', unsafe_allow_html=True)
    if st.button("חזרה"):
        st.session_state.view = "select_topic"
        st.rerun()

# --- מבחן רישוי ---
elif st.session_state.view == "exam":
    # טיימר
    elapsed = time.time() - st.session_state.start_time
    rem = max(0, 90 * 60 - elapsed)
    st.markdown(f'<div class="timer-box">⏱️ זמן נותר: {int(rem//60):02d}:{int(rem%60):02d}</div>', unsafe_allow_html=True)
    
    idx = st.session_state.idx
    q = st.session_state.exam_questions[idx]
    
    st.markdown(f'### שאלה {idx + 1} / 25', unsafe_allow_html=True)
    st.info(q['q'])
    
    ans = st.session_state.user_answers.get(idx + 1)
    choice = st.radio("בחר תשובה:", q['options'], key=f"ex_{idx}", index=None if ans is None else q['options'].index(ans))
    if choice: st.session_state.user_answers[idx + 1] = choice

    # ניווט
    c1, c2 = st.columns(2)
    with c1:
        if idx > 0:
            if st.button("⬅️ הקודם"): st.session_state.idx -= 1; st.rerun()
    with c2:
        if idx < 24:
            if st.button("הבא ➡️"): st.session_state.idx += 1; st.rerun()
        else:
            if st.button("🏁 סיום"): st.session_state.view = "menu"; st.rerun()

    # רשת ניווט תחתונה
    st.write("---")
    st.write("🎯 **קפיצה לשאלה:**")
    for i in range(0, 25, 5):
        cols = st.columns(5)
        for j in range(5):
            n = i + j + 1
            if n <= 25:
                label = f"{n} ✅" if n in st.session_state.user_answers else f"{n}"
                if cols[j].button(label, key=f"btn_{n}", type="primary" if i+j == idx else "secondary"):
                    st.session_state.idx = i + j; st.rerun()
