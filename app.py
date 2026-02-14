import streamlit as st
import google.generativeai as genai

# 1. הגדרות דף ועיצוב
st.set_page_config(page_title="מתווך בקליק 3.0", layout="centered")

# 2. CSS ליישור לימין (RTL) - תיקון גורף
st.markdown("""
    <style>
    .main, .block-container, div[data-testid="stVerticalBlock"] {
        direction: rtl;
        text-align: right;
    }
    .stMarkdown, p, li, h1, h2, h3, span {
        direction: rtl !important;
        text-align: right !important;
    }
    ul, ol {
        padding-right: 2rem;
        padding-left: 0;
        list-style-position: inside;
    }
    div.stButton > button {
        width: 100%;
        background-color: #007bff;
        color: white;
        font-weight: bold;
        height: 3em;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🎓 מתווך בקליק")

# 3. בדיקת מפתח והגדרת מודל
if "GEMINI_API_KEY" not in st.secrets:
    st.error("חסר מפתח API ב-Secrets")
else:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    
    topic = st.selectbox("בחר נושא ללימוד:", 
                         ["חוק המתווכים", "חוק המקרקעין", "דיני חוזים", "דיני תכנון ובנייה"])

    if st.button("ייצר שיעור מהיר"):
        placeholder = st.empty()
        full_response = ""
        
        # בלוק ה-try מסודר עם הזחות תקינות
        try:
            # ניסיון להשתמש ב-2.5 פלאש (הוא יציב יותר מ-3 כרגע ומופיע אצלך ברשימה)
            model = genai.GenerativeModel('gemini-2.5-flash')
            
            with st.spinner("מייצר תוכן..."):
                responses = model.generate_content(
                    f"כתוב שיעור מפורט בעברית על {topic} למבחן המתווכים. השתמש בכותרות ונקודות.",
                    stream=True
                )
                
                for chunk in responses:
                    full_response += chunk.text
                    # הצגת הטקסט בתוך div עם כיוון ימין
                    placeholder.markdown(f'<div dir="rtl">{full_response}</div>', unsafe_allow_html=True)
                
                st.balloons()
                
        except Exception as e:
            st.error(f"תקלה בייצור התוכן: {e}")
            st.info("נסה ללחוץ שוב בעוד כמה שניות.")
