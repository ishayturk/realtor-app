import streamlit as st
import google.generativeai as genai

# הגדרות דף
st.set_page_config(page_title="מתווך בקליק 3.0", layout="centered")

# עיצוב RTL קשוח
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
    /* תיקון לנקודות של הרשימה שיופיעו בימין */
    ul, ol {
        padding-right: 2rem;
        padding-left: 0;
        list-style-position: inside;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🎓 מתווך בקליק")

if "GEMINI_API_KEY" not in st.secrets:
    st.error("חסר מפתח API ב-Secrets")
else:
    # הגדרת הספרייה של גוגל (יותר מהירה מ-Requests בסטרימינג)
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    
    topic = st.selectbox("בחר נושא ללימוד:", 
                         ["חוק המתווכים", "חוק המקרקעין", "דיני חוזים", "דיני תכנון ובנייה"])

    if st.button("ייצר שיעור מהיר"):
        # שימוש במודל Gemini 3 שראינו ברשימה שלך
        model = genai.GenerativeModel('gemini-3-flash-preview')
        
        st.markdown("---")
        
        # יצירת מקום ריק לטקסט שיזרום פנימה
        placeholder = st.empty()
        full_response = ""
        
        try:
            # הפעלת סטרימינג (stream=True)
            responses = model.generate_content(
                f"כתוב שיעור קצר וממוקד על {topic} למבחן המתווכים. השתמש בכותרות ונקודות.",
                stream=True
            )
            
            for chunk in responses:
                full_response += chunk.text
                # עדכון המסך בכל רגע שמתקבלת מילה חדשה
                placeholder.markdown(f'<div dir="rtl">{full_response}</div>', unsafe_allow_html=True)
                
            st.balloons()
            
        except Exception as e:
            st.error(f"תקלה: {e}")
