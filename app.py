import streamlit as st
import google.generativeai as genai

# הגדרת המפתח מהסיקרטס
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("חסר מפתח API בסיקרטס!")
    st.stop()

st.title("בדיקת חיבור סופית")

# ניסיון אחרון עם השם הכי בסיסי
try:
    # בגרסאות חדשות זה חייב להיות זה:
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content("האם אתה שומע אותי?")
    st.success("החיבור עובד!")
    st.write("תשובת הבינה המלאכותית: " + response.text)
except Exception as e:
    st.error(f"עדיין יש שגיאה: {e}")
    st.info("אם מופיע כאן 404, עלינו למחוק את האפליקציה ב-Streamlit Cloud ולהקים אותה מחדש.")
