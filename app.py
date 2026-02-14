import streamlit as st
import google.generativeai as genai

# הגדרות עיצוב מהירות
st.set_page_config(page_title="מתווך בקליק", layout="centered")
st.markdown("<style>.stApp {text-align: right; direction: rtl;}</style>", unsafe_allow_html=True)

st.title("🎓 מתווך בקליק")

# טאבים בשלד
tab1, tab2 = st.tabs(["📚 שיעור לימוד", "📝 מבחן תרגול"])

with tab1:
    topic = st.selectbox("בחר נושא:", ["חוק המתווכים", "חוק המקרקעין", "דיני חוזים"])
    btn_learn = st.button("הצג שיעור")

with tab2:
    btn_exam = st.button("ייצר 5 שאלות")

# לוגיקת AI משופרת
if btn_learn or btn_exam:
    with st.spinner("מייצר תוכן... זה עשוי לקחת כמה שניות"):
        try:
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            
            # בחירה ידנית של המודל המהיר ביותר כדי לחסוך זמן
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            prompt = f"כתוב שיעור קצר וממוקד בעברית על {topic} למבחן המתווכים" if btn_learn else "ייצר 5 שאלות אמריקאיות למבחן המתווכים עם תשובות"
            
            # בקשה מהירה (Streaming)
            response = model.generate_content(prompt)
            
            # בדיקה אם התוכן קיים
            if response and response.text:
                st.success("התוכן מוכן!")
                st.markdown("---")
                st.markdown(response.text)
            else:
                st.warning("ה-AI החזיר תשובה ריקה. נסה ללחוץ שוב.")
                
        except Exception as e:
            # אם ה-Flash המהיר נכשל, ננסה את ה-Pro היציב
            try:
                model_alt = genai.GenerativeModel('gemini-pro')
                res = model_alt.generate_content(prompt)
                st.markdown(res.text)
            except:
                st.error(f"שגיאה בהפקת התוכן: {e}")

st.divider()
st.caption("מערכת למידה מבוססת AI")
