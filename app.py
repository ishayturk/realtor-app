import streamlit as st
import google.generativeai as genai

# הכנס את המפתח שלך כאן לבדיקה מהירה
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

st.title("בדיקת חיבור ל-AI")

# ניסיון גישה למודל בפורמט שונה
try:
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content("היי, אתה עובד?")
    st.write("תשובת ה-AI:")
    st.write(response.text)
except Exception as e:
    st.error(f"שגיאה נוספת: {e}")
    st.info("נסה לשנות את שם המודל ל-'gemini-pro' בקוד")
