import streamlit as st
import google.generativeai as genai
import time

# 1. הגדרות תצוגה ויישור
st.set_page_config(page_title="מתווך בקליק", layout="centered")

# הזרקת CSS לתיקון המיקומים
st.markdown("""
    <style>
    /* יישור כללי לימין */
    [data-testid="stAppViewContainer"], .main, .block-container {
        direction: rtl !important;
        text-align: right !important;
    }
    /* מרכוז כותרות (h1, h2, h3) */
    h1, h2, h3, .centered-text {
        text-align: center !important;
        width: 100%;
        display: block;
    }
    /* יישור כפתורים לימין */
    .stButton > button {
        display: block;
        margin-right: 0;
        margin-left: auto;
    }
    /* תיקון לשדות טקסט */
    input {
        direction: rtl !important;
        text-align: right !important;
    }
    /* עיצוב קופסת השיעור */
    .lesson-box {
        border: 1px solid #ddd; 
        padding: 15px; 
        border-radius: 10px; 
        background: #fff; 
        color: #1a1a1a;
        line-height: 1.6;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. אתחול משתני מערכת
if "view" not in st.session_state:
    st.session_state.update({
        "view": "login",
        "user": "",
        "topic": "",
        "lesson": "",
        "idx": 0
    })

# 3. מנוע AI (Gemini)
def init_gemini():
    if "GEMINI_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        return genai.GenerativeModel('gemini-1.5-flash')
    return None

model = init_gemini()

# --- דף כניסה ---
if st.session_state.view == "login":
    st.markdown('# 🏠 מתווך בקליק', unsafe_allow_html=True)
    st.markdown('### ברוכים הבאים! אנא הכנס שם כדי להתחיל.', unsafe_allow_html=True)
    
    name = st.text_input("שם מלא:", key="name_input")
    
    if st.button("כניסה למערכת"):
        if name:
            st.session_state.user = name
            st.session_state.view = "menu"
            st.rerun()
        else:
            st.error("חובה להזין שם")

# --- תפריט ראשי ---
elif st.session_state.view == "menu":
    st.markdown(f'# שלום {st.session_state.user}', unsafe_allow_html=True)
    st.markdown('<p class="centered-text">מה תרצה לעשות היום?</p>', unsafe_allow_html=True)
    
    st.write("---") # קו מפריד
    
    if st.button("📚 לימוד לפי נושאים"):
        st.session_state.view = "select_topic"
        st.rerun()
        
    if st.button("🚀 סימולציית מבחן"):
        st.info("כאן נחזיר את המבחן המלא ברגע שהעיצוב יאושר.")

# --- בחירת נושא ---
elif st.session_state.view == "select_topic":
    st.markdown('## בחר נושא ללימוד', unsafe_allow_html=True)
    
    topic = st.selectbox("רשימת נושאים:", ["חוק המתווכים", "חוק המקרקעין", "חוק החוזים"])
    
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
    st.markdown(f'## שיעור: {st.session_state.topic}', unsafe_allow_html=True)
    
    if not st.session_state.lesson:
        with st.spinner("ה-AI מכין לך את החומר..."):
            if model:
                try:
                    resp = model.generate_content(f"כתוב שיעור קצר ומקצועי בעברית על {st.session_state.topic} למבחן המתווכים.")
                    st.session_state.lesson = resp.text
                except:
                    st.error("שגיאה בחיבור ל-AI.")
            else:
                st.warning("API Key לא נמצא ב-Secrets.")

    st.markdown(f'<div class="lesson-box">{st.session_state.lesson}</div>', unsafe_allow_html=True)
    
    if st.button("חזרה לבחירת נושא"):
        st.session_state.view = "select_topic"
        st.rerun()
