import streamlit as st
import google.generativeai as genai

# 1. הגדרות דף ועיצוב CSS "נועל"
st.set_page_config(page_title="מתווך בקליק", layout="centered")

st.markdown("""
    <style>
    /* ביטול סיידבר */
    [data-testid="stSidebar"] { display: none; }
    
    /* יישור לימין */
    .main, .block-container { direction: rtl; text-align: right; padding-top: 80px; }
    .stMarkdown, p, li, h1, h2, h3, span, label { direction: rtl !important; text-align: right !important; }

    /* קיבוע התפריט העליון - Sticky Header */
    header[data-testid="stHeader"] {
        background-color: rgba(255, 255, 255, 0.9);
        border-bottom: 2px solid #1E88E5;
        position: fixed;
        top: 0;
        z-index: 999;
    }
    
    /* עיצוב כותרת השיעור */
    .lesson-header {
        background-color: #f0f7ff;
        padding: 20px;
        border-radius: 10px;
        border-right: 8px solid #1E88E5;
        margin-bottom: 25px;
    }

    /* עיצוב כפתורי ניווט */
    .nav-bar {
        position: fixed;
        top: 50px;
        left: 0;
        width: 100%;
        background: white;
        z-index: 1000;
        padding: 10px;
        border-bottom: 1px solid #ddd;
        display: flex;
        justify-content: space-around;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. אתחול משתני מערכת
if "user_name" not in st.session_state: st.session_state.user_name = ""
if "history" not in st.session_state: st.session_state.history = []
if "lesson_data" not in st.session_state: st.session_state.lesson_data = ""
if "quiz_raw" not in st.session_state: st.session_state.quiz_raw = ""
if "current_title" not in st.session_state: st.session_state.current_title = ""

# 3. חיבור ל-AI
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-2.5-flash')

# פונקציית איפוס
def reset_session():
    st.session_state.lesson_data = ""
    st.session_state.quiz_raw = ""
    st.session_state.current_title = ""

# תפריט עליון קבוע (מופיע רק למחוברים)
if st.session_state.user_name:
    t1, t2, t3 = st.columns([1,1,1])
    with t1:
        if st.button("➕ נושא חדש"):
            reset_session()
            st.rerun()
    with t2:
        if st.button("📊 היסטוריה"):
            st.info(f"למדת עד כה: {', '.join(st.session_state.history) if st.session_state.history else 'כלום'}")
    with t3:
        if st.button("🚪 יציאה"):
            st.session_state.user_name = ""
            reset_session()
            st.rerun()
    st.markdown("---")

# מסך כניסה
if not st.session_state.user_name:
    st.title("🎓 מתווך בקליק")
    name = st.text_input("הזן שם כדי להתחיל:")
    if st.button("כניסה"):
        if name:
            st.session_state.user_name = name
            st.rerun()
else:
    # בחירת שיעור - מופיע רק כשאין שיעור פעיל
    if not st.session_state.lesson_data:
        st.subheader(f"שלום {st.session_state.user_name}, מה נלמד היום?")
        topic = st.selectbox("בחר נושא מהרשימה:", 
                             ["חוק המתווכים", "חוק המקרקעין", "דיני חוזים", "דיני תכנון ובנייה", "חוק הגנת הצרכן"])
        
        if st.button("ייצר שיעור"):
            num = len(st.session_state.history) + 1
            st.session_state.current_title = f"שיעור {num}: {topic}"
            
            with st.spinner("המרצה מכין את החומר..."):
                try:
                    # יצירת שיעור ומבחן
                    l_res = model.generate_content(f"כתוב שיעור על {topic} למבחן המתווכים.")
                    st.session_state.lesson_data = l_res.text
                    
                    q_res = model.generate_content(f"צור 3 שאלות אמריקאיות על {topic} עם פתרונות בסוף.")
                    st.session_state.quiz_raw = q_res.text
                    
                    if topic not in st.session_state.history:
                        st.session_state.history.append(topic)
                    st.rerun()
                except Exception as e:
                    st.error(f"תקלה בחיבור: {e}")

    # הצגת השיעור
    if st.session_state.lesson_data:
        st.markdown(f'<div class="lesson-header"><h1>{st.session_state.current_title}</h1></div>', unsafe_allow_html=True)
        st.markdown(st.session_state.lesson_data)
        
        st.markdown("---")
        with st.expander("📝 בחן את עצמך על השיעור"):
            st.markdown(st.session_state.quiz_raw)
