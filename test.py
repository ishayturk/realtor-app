import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="בדיקת חיבוריות Gemini")

st.title("🧪 בדיקת סטטוס API")

# 1. בדיקת קיום Secrets
if "GEMINI_API_KEY" not in st.secrets:
    st.error("❌ ה-API KEY לא נמצא ב-Secrets של Streamlit!")
    st.stop()

key = st.secrets["GEMINI_API_KEY"]
st.success("✅ ה-API KEY נמצא במערכת")

# 2. ניסיון התחברות ובדיקת מודל
try:
    genai.configure(api_key=key)
    
    st.write("מנסה לתקשר עם מודל: `gemini-2.0-flash`...")
    model = genai.GenerativeModel('gemini-2.0-flash')
    
    # בדיקה פשוטה מאוד כדי לא לבזבז טוקנים
    response = model.generate_content("היי, תענה במילה אחת בלבד: אוקיי")
    
    st.success(f"✅ תקשורת הצליחה! תגובה: {response.text}")
    st.balloons()

except Exception as e:
    err_str = str(e)
    
    st.error("❌ אירעה שגיאה בתקשורת")
    
    if "429" in err_str:
        st.warning("⚠️ **בעיית מכסה (Quota):** חרגת מכמות הבקשות המותרת לדקה או ליום.")
    elif "403" in err_str or "PermissionDenied" in err_str:
        st.warning("⚠️ **בעיית הרשאה:** המפתח קיים אך אין לו הרשאה למודל 2.0 פלאש.")
    elif "404" in err_str:
        st.warning("⚠️ **מודל לא נמצא:** ה-API לא מזהה את השם 'gemini-2.0-flash'.")
    elif "401" in err_str:
        st.warning("⚠️ **מפתח לא תקין:** ה-API KEY שהוזן שגוי.")
    else:
        st.code(err_str)

st.divider()
st.write("אם הכל ירוק למעלה - הבעיה הייתה בקוד האפליקציה. אם יש אדום/צהוב - הבעיה היא בהגדרות ה-API.")
