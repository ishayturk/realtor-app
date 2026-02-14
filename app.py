import streamlit as st
import google.generativeai as genai

# 1. הגדרות דף ועיצוב CSS
st.set_page_config(page_title="מתווך בקליק", layout="centered")

st.markdown("""
    <style>
    [data-testid="stSidebar"] { display: none; }
    .main, .block-container { direction: rtl; text-align: right; }
    .stMarkdown, p, li, h1, h2, h3, span, label { direction: rtl !important; text-align: right !important; }
    
    /* תפריט עליון קבוע */
    .stElementContainer:has(#fixed-nav) {
        position: sticky;
        top: 0;
        z-index: 1000;
        background: white;
        padding: 10px 0;
        border-bottom: 2px solid #1E88E5;
    }
    
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

# 2. אתחול משתנים (מניעת שגיאת AttributeError)
if "user_name" not in st.session_state: st.session_state.user_name = ""
if "history" not in st.session_state: st.session_state.history = []
if "lesson_data" not in st.session_state: st.session_state.lesson_data = ""
if "current_title" not in st.session_state: st.session_state.current_title = ""
if "quiz_raw" not in st.session_state: st.session_state.quiz_raw = ""

# 3. חיבור ל-AI
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-2.5-flash')

# תפריט ניווט עליון (מוצג תמיד כשהמשתמש מחובר)
if st.session_state.user_name:
    st.markdown('<div id="fixed-nav"></div>', unsafe_allow_html=True)
    nav_cols = st.columns([1, 1, 1])
    with nav_cols[0]:
        if st.button("🔄 נושא חדש"):
            st.session_state.lesson_data = ""
            st.session_state.quiz_raw = ""
            st.rerun()
    with nav_cols[1]:
        if st.button("📜 היסטוריה"):
            st.toast(f"נושאים: {', '.join(st.session_state.history) if st.session_state.history else 'ריק'}")
    with nav_cols[2]:
        st.write(f"שלום, **{st.session_state.user_name}**")
    st.markdown("---")

# מסך כניסה
if not st.session_state.user_name:
    st.title("🎓 ברוכים הבאים")
    name = st.text_input("איך קוראים לך?")
    if st.button("כניסה"):
        if name:
            st.session_state.user_name = name
            st.rerun()
else:
    # בחירת נושא
    if not st.session_state.lesson_data:
        topic = st.selectbox("בחר נושא ללימוד:", ["חוק המתווכים", "חוק המקרקעין", "דיני חוזים", "דיני תכנון ובנייה"])
        if st.button("התחל למידה"):
            num = len(st.session_state.history) + 1
            st.session_state.current_title = f"שיעור {num}: {topic}"
            
            with st.spinner("המערכת מכינה עבורך שיעור ומבחן..."):
                try:
                    # יצירת שיעור
                    l_res = model.generate_content(f"כתוב שיעור על {topic} למבחן המתווכים. ללא שאלות.")
                    st.session_state.lesson_data = l_res.text
                    
                    # יצירת מבחן
                    q_res = model.generate_content(f"צור 3 שאלות אמריקאיות על {topic}. כתוב כל שאלה עם 4 אפשרויות ובסוף ציין מה התשובה הנכונה.")
                    st.session_state.quiz_raw = q_res.text
                    
                    if topic not in st.session_state.history:
                        st.session_state.history.append(topic)
                    st.rerun()
                except Exception as e:
                    st.error(f"שגיאה: {e}")

    # הצגת התוכן
    if st.session_state.lesson_data:
        st.markdown(f'<div class="lesson-header"><h1>{st.session_state.current_title}</h1></div>', unsafe_allow_html=True)
        st.markdown(st.session_state.lesson_data)
        
        # מבחן תרגול
        if st.session_state.quiz_raw:
            st.markdown("---")
            st.subheader("✍️ מבחן תרגול (אינטראקטיבי)")
            with st.expander("לחץ כאן למעבר למבחן"):
                st.markdown(st.session_state.quiz_raw)
                st.info("קרא את השאלות למעלה וסמן לעצמך את התשובה. הפתרונות מופיעים בסוף המבחן.")
