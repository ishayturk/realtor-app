import streamlit as st
import google.generativeai as genai

# הגדרות עיצוב RTL
st.set_page_config(page_title="מתווך בקליק", layout="centered")
st.markdown("<style>.stApp {text-align: right; direction: rtl;}</style>", unsafe_allow_html=True)

st.title("🎓 מתווך בקליק")

# שלד האפליקציה
topic = st.selectbox("מה תרצה ללמוד?", ["חוק המתווכים", "חוק המקרקעין", "דיני חוזים"])

if st.button("ייצר שיעור"):
    if "GEMINI_API_KEY" not in st.secrets:
        st.error("חסר מפתח API בסיקרטס")
    else:
        try:
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            
            # פקודה שמאלצת את המערכת להשתמש בגרסה היציבה ביותר
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            with st.spinner("מייצר תוכן..."):
                response = model.generate_content(f"הסבר בעברית על {topic}")
                st.markdown(response.text)
                
        except Exception as e:
            st.error(f"שגיאה: {e}")
            st.info("אם עדיין יש 404, סימן שהמפתח API שלך לא תומך במודל פלאש. נסה ליצור מפתח חדש ב-Google AI Studio.")
