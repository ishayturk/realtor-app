import streamlit as st
import google.generativeai as genai

# הגדרות עיצוב RTL (מימין לשמאל)
st.set_page_config(page_title="מתווך בקליק", layout="centered")
st.markdown("<style>.stApp {text-align: right; direction: rtl;}</style>", unsafe_allow_html=True)

st.title("🎓 מתווך בקליק")

# שלד האפליקציה
topic = st.selectbox("בחר נושא ללימוד:", ["חוק המתווכים", "חוק המקרקעין", "דיני חוזים"])

if st.button("ייצר שיעור"):
    if "GEMINI_API_KEY" not in st.secrets:
        st.error("חסר מפתח API ב-Secrets!")
    else:
        try:
            # 1. הגדרת המפתח
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            
            # 2. שימוש במודל היציב ביותר (הגרסה שלא מקפיצה לעמודים אחרים)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            with st.spinner("מייצר שיעור..."):
                # 3. בקשת תוכן פשוטה
                response = model.generate_content(f"כתוב שיעור קצר בעברית על {topic} למבחן המתווכים בישראל.")
                
                if response.text:
                    st.success("החיבור הצליח!")
                    st.divider()
                    st.markdown(response.text)
                
        except Exception as e:
            # אם יש שגיאה, ננסה להציג אותה בצורה ברורה
            st.error(f"שגיאה: {str(e)}")
            st.info("אם מופיע 404, וודא שביצעת Reboot לאפליקציה ב-Streamlit Cloud.")
