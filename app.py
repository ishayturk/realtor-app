import streamlit as st
import google.generativeai as genai

# הגדרות שלד מהירות
st.set_page_config(page_title="מתווך בקליק", layout="centered")
st.markdown("<style>.stApp {text-align: right; direction: rtl;}</style>", unsafe_allow_html=True)

st.title("🎓 מתווך בקליק")

# טאבים
tab1, tab2 = st.tabs(["📚 שיעור לימוד", "📝 מבחן תרגול"])

with tab1:
    topic = st.selectbox("בחר נושא:", ["חוק המתווכים", "חוק המקרקעין", "דיני חוזים"])
    btn_learn = st.button("הצג שיעור")

with tab2:
    btn_exam = st.button("ייצר 5 שאלות")

if btn_learn or btn_exam:
    with st.spinner("מייצר תוכן..."):
        try:
            # הגדרת המפתח
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            
            # --- התיקון הקריטי ---
            # אנחנו משתמשים בשם המלא והגרסה היציבה ביותר (1.0 pro) 
            # כדי לעקוף את בעיית ה-v1beta של השרת שלך
            model = genai.GenerativeModel(model_name='models/gemini-1.0-pro')
            
            prompt = f"כתוב שיעור קצר בעברית על {topic}" if btn_learn else "ייצר 5 שאלות אמריקאיות למבחן המתווכים"
            
            # יצירת תוכן
            response = model.generate_content(prompt)
            
            if response.text:
                st.markdown("### תוצאה:")
                st.write(response.text)
            else:
                st.error("התקבלה תשובה ריקה מהשרת.")
                
        except Exception as e:
            # ניסיון אחרון ודי עם שם המודל הכי בסיסי בעולם
            try:
                model_fallback = genai.GenerativeModel('gemini-pro')
                res = model_fallback.generate_content(prompt)
                st.write(res.text)
            except Exception as e2:
                st.error(f"שגיאה סופית: {e2}")
                st.info("משהו בהגדרות השרת של Streamlit חוסם את המודלים החדשים. נסה לבצע Reboot לאפליקציה.")
