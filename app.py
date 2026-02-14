import streamlit as st
import google.generativeai as genai

# הגדרות דף בסיסיות
st.set_page_config(page_title="מתווך בקליק", layout="centered")

# עיצוב מימין לשמאל
st.markdown("""
    <style>
    .stApp { text-align: right; direction: rtl; }
    button { width: 100%; border-radius: 10px; height: 3em; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎓 מתווך בקליק")

# בחירת נושא
topic = st.selectbox("בחר נושא לשיעור:", ["חוק המתווכים", "חוק המקרקעין", "דיני חוזים"])

if st.button("הפעל"):
    if "GEMINI_API_KEY" not in st.secrets:
        st.error("חסר מפתח API ב-Secrets!")
    else:
        try:
            # הגדרה
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            
            # ניסיון חיבור למודל הכי נפוץ
            # אם gemini-1.5-flash עושה בעיות, נסה להחליף ל-gemini-pro
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            with st.spinner("מייצר תוכן..."):
                response = model.generate_content(f"כתוב שיעור קצר בעברית על {topic}")
                
                if response:
                    st.success("החיבור הצליח!")
                    st.markdown("---")
                    st.write(response.text)
                
        except Exception as e:
            st.error(f"שגיאה בחיבור: {e}")
            st.info("אם מופיע 404, וודא שביצעת Reboot לאפליקציה בלוח הבקרה של Streamlit.")
