import streamlit as st
import google.generativeai as genai

# הגדרות תצוגה מיידיות
st.set_page_config(page_title="מתווך בקליק", layout="centered")
st.markdown("<style>.stApp {text-align: right; direction: rtl;}</style>", unsafe_allow_html=True)

st.title("🎓 מתווך בקליק")

# שלד האפליקציה (עולה תמיד)
tab1, tab2 = st.tabs(["📚 למידה", "📝 תרגול"])

with tab1:
    topic = st.selectbox("בחר נושא:", ["חוק המתווכים", "חוק המקרקעין", "דיני חוזים"])
    btn_learn = st.button("הצג שיעור")

with tab2:
    btn_exam = st.button("ייצר שאלות")

if btn_learn or btn_exam:
    with st.spinner("מתחבר ישירות לשרת..."):
        try:
            # הגדרת המפתח
            if "GEMINI_API_KEY" not in st.secrets:
                st.error("חסר API Key ב-Secrets")
                st.stop()
                
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            
            # ניסיון אחרון עם המודל הכי פשוט (Legacy)
            # אם v1beta תקוע, ננסה לקרוא למודל בלי קידומות
            model = genai.GenerativeModel('gemini-1.0-pro')
            
            prompt = f"הסבר בעברית על {topic}" if btn_learn else "ייצר 5 שאלות למבחן המתווכים"
            
            response = model.generate_content(prompt)
            st.markdown(response.text)
            
        except Exception as e:
            st.error("השרת של Streamlit חוסם את החיבור.")
            st.info("בצע את הפעולה הבאה בלוח הבקרה של Streamlit:")
            st.warning("1. כנס ל-Manage App\n2. לחץ על ה-3 נקודות (...)\n3. בחר Reboot App")
