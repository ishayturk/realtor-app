import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="בדיקה", layout="centered")

# הגדרה ישירה
if "GEMINI_API_KEY" in st.secrets:
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        # כאן אנחנו משתמשים בשם המדויק והיציב
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        if st.button("לחץ כאן לבדיקה סופית"):
            response = model.generate_content("תגיד שלום")
            st.success(f"עובד! ה-AI אומר: {response.text}")
            st.balloons()
    except Exception as e:
        st.error(f"שגיאה: {e}")
else:
    st.error("המפתח לא הוזן ב-Secrets")
