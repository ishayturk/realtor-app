import streamlit as st
import google.generativeai as genai
import time

# --- 1. הגדרות תצוגה RTL ---
st.set_page_config(page_title="מתווך בקליק", layout="centered")

# הזרקת סטייל גלובלי חזק
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"], .main, .block-container { direction: rtl !important; text-align: right !important; }
    h1, h2, h3 { text-align: center !important; color: #1E88E5; width: 100%; }
    .stButton > button { width: 100%; font-weight: bold; height: 3.5em; border-radius: 10px; }
    .lesson-box { 
        background: white; padding: 20px; border-radius: 12px; 
        border-right: 5px solid #1E88E5; box-shadow: 0 2px 5px rgba(0,0,0,0.1); 
        line-height: 1.8; color: #333; text-align: right; direction: rtl;
    }
    .timer-box { text-align: center; background: #fff3e0; padding: 10px; border-radius: 10px; font-weight: bold; border: 1px solid #ff9800; }
    /* תיקון ליישור טקסט בתוך הטאבים ורכיבי בחירה */
    div[role="tabpanel"] { direction: rtl !important; text-align: right !important; }
    .stRadio > label { text-align: right !important; direction: rtl !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. אתחול משתנים (מניעת AttributeError) ---
if "step" not in st.session_state:
    st.session_state.update({
        "step": "login", "user": "", "topic": "", "idx": 0, "user_answers": {}, "start_time": None
    })

# --- 3. מאגר שאלות (25 שאלות לדוגמה) ---
def get_questions():
    q_list = [
        {"q": "מי מהבאים רשאי לעסוק בתיווך מקרקעין?", "options": ["כל אדם מעל גיל 18", "רק בעל רישיון תיווך בתוקף", "רק עורך דין", "רק מי שגר בישראל 5 שנים"], "correct": 1},
        {"q": "האם חובה לערוך הזמנת תיווך בכתב?", "options": ["לא, מספיק בעל פה", "כן, זו דרישה חקוקה לקבלת דמי תיווך", "רק אם העסקה מעל מיליון ש\"ח", "רק בבלעדיות"], "correct": 1}
    ]
    return (q_list * 13)[:25]

# --- 4. לוגיקה מרכזית ---
st.markdown("<h1>🏠 מתווך בקליק</h1>", unsafe_allow_html=True)

# דף כניסה
if st.session_state.step == "login":
    name = st.text_input("הכנס שם מלא לכניסה:")
    if st.button("התחבר"):
        if name:
            st.session_state.user = name
            st.session_state.step = "menu"
            st.rerun()

# תפריט ושיעור
elif st.session_state.step == "menu":
    st.markdown(f"<div style='text-align: right; direction: rtl;'><h3>שלום, {st.session_state.user} 👋</h3></div>", unsafe_allow_html=True)
    
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
                    # הזרקת הסטייל ישירות לתוך רכיב הסטרימינג למניעת בריחה שמאלה
                    placeholder.markdown(f"""
                        <div class='lesson-box' style='text-align: right; direction: rtl;'>
                            {full_text}
                        </div>
                    """, unsafe_allow_html=True)
            except Exception as e:
                st.error(f"שגיאה בחיבור ל-Gemini 2.0: {str(e)}")

    with tab_exam:
        if st.button("🚀 התחל מבחן חדש (25 שאלות)"):
            st.session_state.questions = get_questions()
            st.session_state.idx = 0
            st.session_state.user_answers = {}
            st.session_state.start_time = time.time()
            st.session_state.step = "exam"
            st.rerun()

# דף מבחן
elif st.session_state.step == "exam":
    elapsed = time.time() - st.session_state.start_time
    rem = max(0, 90 * 60 - elapsed)
    st.markdown(f"<div class='timer-box'>⏱️ זמן נותר: {int(rem//60):02d}:{int(rem%60):02d}</div>", unsafe_allow_html=True)
    
    idx = st.session_state.idx
    q = st.session_state
