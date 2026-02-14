import streamlit as st
import google.generativeai as genai

# הגדרות דף
st.set_page_config(page_title="מתווך בקליק", layout="centered")

# CSS מקצועי - יישור לימין ועיצוב נקי
st.markdown("""
    <style>
    .main, .block-container, div[data-testid="stVerticalBlock"] { direction: rtl; text-align: right; }
    .stMarkdown, p, li, h1, h2, h3, span { direction: rtl !important; text-align: right !important; }
    ul, ol { padding-right: 2rem; padding-left: 0; list-style-position: inside; }
    .stButton > button { width: 100%; background-color: #1E88E5; color: white; font-weight: bold; border-radius: 8px; }
    .user-box { background-color: #f0f2f6; padding: 15px; border-radius: 10px; margin-bottom: 20px; border-right: 5px solid #1E88E5; }
    </style>
    """, unsafe_allow_html=True)

# אתחול משתני מערכת (Session State)
if "user_name" not in st.session_state: st.session_state.user_name = ""
if "history" not in st.session_state: st.session_state.history = []
if "ready_test" not in st.session_state: st.session_state.ready_test = None

# מסך כניסה
if not st.session_state.user_name:
    st.title("🎓 ברוכים הבאים למתווך בקליק")
    name = st.text_input("לפני שנתחיל, איך קוראים לך?")
    if st.button("כניסה למערכת"):
        if name:
            st.session_state.user_name = name
            st.rerun()
else:
    # ממשק ראשי
    st.title(f"שלום {st.session_state.user_name} 👋")
    
    if "GEMINI_API_KEY" not in st.secrets:
        st.error("הגדר API_KEY ב-Secrets")
    else:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-2.5-flash')

        # בחירת נושא
        topic = st.selectbox("בחר נושא ללימוד:", 
                             ["חוק המתווכים", "חוק המקרקעין", "דיני חוזים", "דיני תכנון ובנייה"])

        if st.button("התחל שיעור"):
            st.session_state.ready_test = None # איפוס מבחן קודם
            placeholder = st.empty()
            full_response = ""
            
            # בניית הפרומפט לשיעור + שאלות סיכום
            lesson_prompt = f"""
            כתוב שיעור על {topic} עבור מבחן המתווכים. 
            המבנה חייב לכלול:
            1. הסבר תיאורטי ברור.
            2. דוגמה מעשית.
            3. חלק של 'שאלות סיכום' עם 3 שאלות רב-ברירה (אמריקאיות) כולל תשובות בסוף.
            הכל בעברית רהוטה ומקצועית.
            """
            
            try:
                responses = model.generate_content(lesson_prompt, stream=True)
                for chunk in responses:
                    full_response += chunk.text
                    placeholder.markdown(f'<div dir="rtl">{full_response}</div>', unsafe_allow_html=True)
                
                # עדכון היסטוריה
                if topic not in st.session_state.history:
                    st.session_state.history.append(topic)
                
                # --- יצירת מבחן ברקע (כאן הקסם קורה) ---
                test_prompt = f"צור מבחן של 5 שאלות אמריקאיות קשות על {topic} למבחן המתווכים, כולל פתרונות."
                # אנחנו שומרים את התוצאה בזיכרון בלי להציג אותה עדיין
                st.session_state.ready_test = model.generate_content(test_prompt).text
                
            except Exception as e:
                st.error(f"תקלה: {e}")

        # הצגת כפתור מבחן רק אם השיעור הסתיים
        if st.session_state.ready_test:
            st.markdown("---")
            if st.button("אני מוכן למבחן על הנושא!"):
                st.markdown("### 📝 מבחן תרגול")
                st.markdown(f'<div dir="rtl" style="background:#fff9c4; padding:15px; border-radius:10px;">{st.session_state.ready_test}</div>', unsafe_allow_html=True)

        # הצגת היסטוריה בצד
        if st.session_state.history:
            with st.sidebar:
                st.markdown("### 📚 היסטוריית למידה")
                for item in st.session_state.history:
                    st.write(f"✔️ {item}")
