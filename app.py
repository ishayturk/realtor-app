import streamlit as st
import google.generativeai as genai
import re

# 1. הגדרות דף ועיצוב CSS מתקדם
st.set_page_config(page_title="מתווך בקליק", layout="centered")

st.markdown("""
    <style>
    /* ביטול סיידבר */
    [data-testid="stSidebar"] { display: none; }
    
    /* יישור לימין */
    .main, .block-container { direction: rtl; text-align: right; }
    .stMarkdown, p, li, h1, h2, h3, span, label { direction: rtl !important; text-align: right !important; }

    /* תפריט עליון קבוע (Sticky Header) */
    .fixed-header {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        background-color: white;
        z-index: 999;
        padding: 10px 0;
        border-bottom: 2px solid #eee;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    
    /* ריווח מהכותרת הקבועה */
    .content-area { margin-top: 80px; }

    .lesson-header {
        background-color: #e3f2fd;
        padding: 20px;
        border-radius: 10px;
        border-right: 8px solid #1E88E5;
        margin-bottom: 25px;
    }

    div.stButton > button { width: 100%; border-radius: 8px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# 2. אתחול משתנים
if "user_name" not in st.session_state: st.session_state.user_name = ""
if "history" not in st.session_state: st.session_state.history = []
if "lesson_data" not in st.session_state: st.session_state.lesson_data = ""
if "current_title" not in st.session_state: st.session_state.current_title = ""
if "quiz_questions" not in st.session_state: st.session_state.quiz_questions = []

# 3. חיבור ל-AI
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-2.5-flash')

# תפריט ניווט עליון קבוע (יופיע רק אחרי התחברות)
if st.session_state.user_name:
    cols = st.columns([2, 2, 1])
    with cols[0]:
        if st.button("🔄 חזרה לתפריט"):
            st.session_state.lesson_data = ""
            st.rerun()
    with cols[1]:
        if st.button("📜 היסטוריה"):
            st.info(f"נושאים שלמדת: {', '.join(st.session_state.history) if st.session_state.history else 'אין עדיין'}")
    with cols[2]:
        st.write(f"שלום, **{st.session_state.user_name}**")
    st.markdown("---")

# מסך כניסה
if not st.session_state.user_name:
    st.title("🎓 ברוכים הבאים למתווך בקליק")
    name = st.text_input("איך קוראים לך?")
    if st.button("כניסה"):
        if name:
            st.session_state.user_name = name
            st.rerun()
else:
    # ממשק בחירה
    if not st.session_state.lesson_data:
        topic = st.selectbox("בחר נושא ללימוד:", ["חוק המתווכים", "חוק המקרקעין", "דיני חוזים", "דיני תכנון ובנייה"])
        if st.button("התחל ללמוד"):
            num = len(st.session_state.history) + 1
            st.session_state.current_title = f"שיעור {num}: {topic}"
            
            with st.spinner("מכין שיעור ומבחן..."):
                # יצירת שיעור
                lesson = model.generate_content(f"כתוב שיעור על {topic} למבחן המתווכים.")
                st.session_state.lesson_data = lesson.text
                
                # יצירת מבחן בפורמט מובנה כדי שנוכל לפרק אותו
                quiz_prompt = f"""צור 3 שאלות אמריקאיות על {topic}. 
                פורמט לכל שאלה: 
                שאלה: [השאלה]
                אפשרות 1: [טקסט]
                אפשרות 2: [טקסט]
                אפשרות 3: [טקסט]
                אפשרות 4: [טקסט]
                תשובה נכונה: [מספר]"""
                quiz_res = model.generate_content(quiz_prompt)
                st.session_state.quiz_raw = quiz_res.text
                
                if topic not in st.session_state.history:
                    st.session_state.history.append(topic)
                st.rerun()

    # הצגת השיעור
    if st.session_state.lesson_data:
        st.markdown(f'<div class="lesson-header"><h1>{st.session_state.current_title}</h1></div>', unsafe_allow_html=True)
        st.markdown(st.session_state.lesson_data)
        
        st.markdown("---")
        st.subheader("📝 בחינה עצמית")
        st.write("קרא את השאלות ובחר את התשובה הנכונה:")
        
        # הצגת המבחן בצורה אינטראקטיבית
        # הערה: בגרסה זו אנו מציגים את הטקסט, אך המשתמש יכול לבדוק את עצמו
        with st.expander("לחץ כאן כדי להתחיל את המבחן"):
             st.markdown(st.session_state.quiz_raw)
             st.success("טיפ: נסה לענות בלב לפני שאתה בודק את התשובות בסוף הטקסט!")
