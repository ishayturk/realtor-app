import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="בדיקת חיבור", layout="centered")

st.title("🔍 בדיקת חיבור ל-Gemini")

# בדיקה אם המפתח קיים בכלל בסיקרטס
if "GEMINI_API_KEY" not in st.secrets:
    st.error("❌ לא נמצא מפתח API ב-Secrets של Streamlit!")
    st.info("לך ל-Settings -> Secrets ותוודא שכתוב שם GEMINI_API_KEY = 'הערך שלך'")
else:
    api_key = st.secrets["GEMINI_API_KEY"]
    st.write(f"✅ מפתח זוהה במערכת (מתחיל ב: {api_key[:5]}...)")

    if st.button("בדוק חיבור עכשיו"):
        try:
            genai.configure(api_key=api_key)
            
            # ניסיון למשוך את רשימת המודלים שזמינים לך
            # זו הבדיקה הכי אמינה שיש
            available_models = []
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    available_models.append(m.name)
            
            if available_models:
                st.success("🎉 החיבור הצליח! המפתח שלך תקין.")
                st.write("המודלים שזמינים לך הם:")
                st.json(available_models)
                
                # ניסיון ג'נרציה קטן
                model = genai.GenerativeModel(available_models[0])
                response = model.generate_content("תגיד שלום בעברית")
                st.balloons()
                st.markdown(f"**תגובת ה-AI:** {response.text}")
            else:
                st.warning("התחברנו, אבל לא נמצאו מודלים זמינים. בדוק אם המפתח מוגדר כ-Free Tier.")
                
        except Exception as e:
            st.error("❌ תקלה בהתחברות לגוגל")
            st.code(str(e))
            st.info("אם מופיע 404, המפתח כנראה לא הופעל עדיין בפרויקט חדש.")
