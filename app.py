import streamlit as st
import google.generativeai as genai

# הגדרות דף
st.set_page_config(page_title="מתווך בקליק", layout="centered")

# CSS ליישור לימין, עיצוב כותרות וביטול סיידבר
st.markdown("""
    <style>
    [data-testid="stSidebar"] { display: none; }
    .main, .block-container { direction: rtl; text-align: right; }
    .stMarkdown, p, li, h1, h2, h3, span, label { direction: rtl !important; text-align: right !important; }
    
    /* עיצוב כותרת השיעור */
    .lesson-header {
        background-color: #e3f2fd;
        padding: 20px;
        border-radius: 10px;
        border-right: 8px solid #1E88E5;
        margin-bottom: 25px;
    }
    
    div.stButton > button { width: 100%; border-radius: 10px; height: 3em; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# אתחול משתנים
if "user_name" not in st.session_state: st.session_state.user_name = ""
if "history" not in st.session_state: st.session_state.history = []
if "lesson_data" not in st.session_state: st.session_state.lesson_data = ""
if "current_lesson_title" not in st.session_state: st.session_state.current_lesson_title = ""

# הגדרת AI
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-2.5-flash')

# מסך כניסה
if not st.session_state.user_name:
    st.title("🎓 ברוכים הבאים")
    name = st.text_input("איך קוראים לך?")
    if st.button("כניסה"):
        if name:
            st.session_state.user_name = name
            st.rerun()
else:
    st.title(f"שלום, {st.session_state.user_name}")

    # תפריט נושאים
    topic = st.selectbox("בחר נושא ללימוד:", ["חוק המתווכים", "חוק המקרקעין", "דיני חוזים", "דיני תכנון ובנייה"])

    # כפתור התחל שיעור
    if st.button("התחל שיעור"):
        # חישוב מספר השיעור
        lesson_num = len(st.session_state.history) + 1
        st.session_state.current_lesson_title = f"שיעור {lesson_num}: {topic}"
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            status_text.write("בונה את השיעור עבורך...")
            progress_bar.progress(50)
            
            lesson_prompt = f"כתוב שיעור ממוקד על {topic} למבחן המתווכים. ללא הקדמות מיותרות."
            lesson = model.generate_content(lesson_prompt)
            
            st.session_state.lesson_data = lesson.text
            
            # הוספה להיסטוריה אם לא קיים
            if topic not in st.session_state.history:
                st.session_state.history.append(topic)
                
            progress_bar.progress(100)
            time_to_wait = 1 # קצת השהייה לתחושת זרימה
            status_text.empty()
            progress_bar.empty()
            st.rerun()
            
        except Exception as e:
            st.error(f"תקלה: {e}")

    # הצגת השיעור עם הכותרת החדשה
    if st.session_state.lesson_data:
        st.markdown(f"""
            <div class="lesson-header">
                <h1>{st.session_state.current_lesson_title}</h1>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f'<div dir="rtl">{st.session_state.lesson_data}</div>', unsafe_allow_
