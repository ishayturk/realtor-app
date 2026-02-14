import streamlit as st
import google.generativeai as genai
import time

# --- 1. הגדרות תצוגה RTL ---
st.set_page_config(page_title="מתווך בקליק", layout="centered")

st.markdown("""
    <style>
    [data-testid="stAppViewContainer"], .main, .block-container { direction: rtl !important; text-align: right !important; }
    h1, h2, h3 { text-align: center !important; color: #1E88E5; }
    .stButton > button { width: 100%; font-weight: bold; height: 3.5em; border-radius: 10px; }
    .lesson-box { background: white; padding: 20px; border-radius: 12px; border-right: 5px solid #1E88E5; box-shadow: 0 2px 5px rgba(0,0,0,0.1); line-height: 1.8; color: #333; }
    .timer-box { text-align: center; background: #fff3e0; padding: 10px; border-radius: 10px; font-weight: bold; border: 1px solid #ff9800; }
    [data-testid="stMarkdownContainer"] p { text-align: right !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. אתחול משתנים ---
if "step" not in st.session_state:
    st.session_state.update({
        "step": "login", "user": "", "topic": "", "idx": 0, "user_answers": {}, "start_time": None
    })

# --- 3. מאגר שאלות ---
def get_questions():
    q_list = [
        {"q": "מהו התנאי לקבלת דמי תיווך לפי חוק המתווכים?", "options": ["הסכמה בעל פה", "הזמנה בכתב, רישיון בתוקף וגורם יעיל", "חתימה של עו\"ד", "פרסום בעיתון"], "correct": 1},
        {"q": "מהי תקופת הבלעדיות המקסימלית בדירת מגורים?", "options": ["3 חודשים", "6 חודשים", "9 חודשים", "שנה"], "correct": 1}
    ]
    return (q_list * 13)[:25]

# --- 4. לוגיקה ---
st.markdown("<h1>🏠 מתווך בקליק</h1>", unsafe_allow_html=True)

if st.session_state.step == "login":
    name = st.text_input("הכנס שם מלא:")
    if st.button("כניסה למערכת"):
        if name:
            st.session_state.user = name
            st.session_state.step = "menu"
            st.rerun()

elif st.session_state.step == "menu":
    st.markdown(f"<div style='direction: rtl; text-align: right;'><h3>שלום, {st.session_state.user} 👋</h3></div>", unsafe_allow_html=True)
    
    tab_lesson, tab_exam = st.tabs(["📚 לימוד עיוני", "📝 סימולציית מבחן"])
    
    with tab_lesson:
        topic_choice = st.selectbox("בחר נושא ללימוד:", ["חוק המתווכים", "חוק המקרקעין", "חוק החוזים", "דיני מקרקעין"])
        
        if st.button("📖 התחל שיעור"):
            try:
                genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                model = genai.GenerativeModel('gemini-2.0-flash')
                response = model.generate_content(f"כתוב שיעור מפורט למבחן המתווכים על {topic_choice} בעברית.", stream=True)
                
                st.write(f"---")
                placeholder = st.empty()
                full_text = ""
                for chunk in response:
                    full_text += chunk.text
                    placeholder.markdown(f"<div class='lesson-box'>{full_text}</div>", unsafe_allow_html=True)
            except Exception as e:
                st.error(f"שגיאה: {str(e)}")

    with tab_exam:
        if st.button("🚀 התחל מבחן חדש"):
            st.session_state.questions = get_questions()
            st.session_state.idx = 0
            st.session_state.user_answers = {}
            st.session_state.start_time = time.time()
            st.session_state.step = "exam"
            st.rerun()

elif st.session_state.step == "exam":
    elapsed = time.time() - st.session_state.start_time
    rem = max(0, 90 * 60 - elapsed)
    st.markdown(f"<div class='timer-box'>⏱️ זמן נותר: {int(rem//60):02d}:{int(rem%60):02d}</div>", unsafe_allow_html=True)
    
    idx = st.session_state.idx
    q = st.session_state.questions[idx]
    
    st.markdown(f"### שאלה {idx + 1} / 25")
    st.info(q['q'])
    
    current_ans = st.session_state.user_answers.get(idx)
    choice = st.radio("בחר תשובה:", q['options'], key=f"q_{idx}", index=None if current_ans is None else q['options'].index(current_ans))
    
    if choice:
        st.session_state.user_answers[idx] = choice

    col1, col2 = st.columns(2)
    with col1:
        if idx > 0:
            if st.button("⬅️ הקודם"):
                st.session_state.idx -= 1
                st.rerun()
    with col2:
        if idx < 24:
            if st.button("הבא ➡️"):
                st.session_state.idx += 1
                st.rerun()
        else:
            if st.button("🏁 סיום מבחן"):
                st.session_state.step = "menu"
                st.rerun()
