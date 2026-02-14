import streamlit as st
import google.generativeai as genai
import time

# 1. הגדרות דף ועיצוב CSS מתקדם לתיקון היישור
st.set_page_config(page_title="מתווך בקליק", layout="wide")

st.markdown("""
    <style>
    /* הגדרת כיוון כללית לכל האתר */
    html, body, [data-testid="stAppViewContainer"] {
        direction: rtl;
        text-align: right;
    }
    
    /* תיקון ספציפי לגוף המסך (שלא יקפוץ שמאלה) */
    [data-testid="stMainBlockContainer"] {
        margin-right: auto;
        margin-left: 0;
        padding-right: 5rem;
        padding-left: 2rem;
    }

    /* עיצוב הפריים השמאלי (Sidebar) - נשאר בשמאל אבל הטקסט בו מימין */
    section[data-testid="stSidebar"] {
        direction: rtl;
        text-align: right;
        background-color: #f8f9fa;
    }
    
    /* כותרות וטקסט - כפייה של RTL */
    h1, h2, h3, p, li, span, label, .stSelectbox {
        direction: rtl !important;
        text-align: right !important;
    }

    /* עיצוב כותרת השיעור */
    .lesson-header {
        background-color: #f0f7ff;
        padding: 25px;
        border-radius: 12px;
        border-right: 8px solid #1E88E5;
        margin-bottom: 30px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    /* כפתורים */
    div.stButton > button {
        width: 100%;
        border-radius: 8px;
        font-weight: bold;
        height: 3em;
        background-color: #1E88E5;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. אתחול משתנים
if "user_name" not in st.session_state: st.session_state.user_name = ""
if "history" not in st.session_state: st.session_state.history = []
if "lesson_data" not in st.session_state: st.session_state.lesson_data = ""
if "quiz_raw" not in st.session_state: st.session_state.quiz_raw = ""
if "current_title" not in st.session_state: st.session_state.current_title = ""

# 3. חיבור ל-AI
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-2.5-flash')

def reset_session():
    st.session_state.lesson_data = ""
    st.session_state.quiz_raw = ""
    st.session_state.current_title = ""

# --- סיידבר (הפריים הקבוע) ---
if st.session_state.user_name:
    with st.sidebar:
        st.header(f"שלום, {st.session_state.user_name}")
        st.markdown("---")
        if st.button("➕ נושא חדש"):
            reset_session()
            st.rerun()
        
        st.subheader("📚 מה למדנו:")
        if st.session_state.history:
            for item in st.session_state.history:
                st.write(f"🔹 {item}")
        else:
            st.write("רשימה ריקה")
        
        st.markdown("<br><br>", unsafe_allow_html=True)
        if st.button("🚪 יציאה"):
            st.session_state.user_name = ""
            reset_session()
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
        topic = st.selectbox("בחר מהרשימה:", 
                             ["חוק המתווכים", "חוק המקרקעין", "דיני חוזים", "דיני תכנון ובנייה", "חוק הגנת הצרכן"])
        
        if st.button("כניסה לשיעור"):
            num = len(st.session_state.history) + 1
            st.session_state.current_title = f"שיעור {num}: {topic}"
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                status_text.markdown("### **מכין את השיעור...**")
                progress_bar.progress(30)
                
                l_res = model.generate_content(f"כתוב שיעור על {topic} למבחן המתווכים.")
                progress_bar.progress(70)
                
                q_res = model.generate_content(f"צור 3 שאלות אמריקאיות על {topic} עם פתרונות.")
                
                st.session_state.lesson_data = l_res.text
                st.session_state.quiz_raw = q_res.text
                
                if topic not in st.session_state.history:
                    st.session_state.history.append(topic)
                
                progress_bar.progress(100)
                time.sleep(0.5)
                status_text.empty()
                progress_bar.empty()
                st.rerun()
                
            except Exception as e:
                st.error(f"שגיאה: {e}")

    # הצגת השיעור
    if st.session_state.lesson_data:
        st.markdown(f'<div class="lesson-header"><h1>{st.session_state.current_title}</h1></div>', unsafe_allow_html=True)
        st.markdown(st.session_state.lesson_data)
        
        st.markdown("---")
        with st.expander("📝 בחן את עצמך על השיעור"):
            st.markdown(st.session_state.quiz_raw)
