import streamlit as st

# הגדרות עיצוב - עולות בשבריר שנייה
st.set_page_config(page_title="מתווך בקליק", layout="centered")
st.markdown("<style>.stApp {text-align: right; direction: rtl;}</style>", unsafe_allow_html=True)

# הצגת הכותרת והתפריט מיד
st.title("🎓 מתווך בקליק")
st.write("המערכת מוכנה. בחר נושא ולחץ על הכפתור כדי להתחיל.")

tab1, tab2 = st.tabs(["📚 שיעור לימוד", "📝 מבחן תרגול"])

with tab1:
    topic = st.selectbox("בחר נושא:", ["חוק המתווכים", "חוק המקרקעין", "דיני חוזים"])
    btn_learn = st.button("התחל שיעור")

with tab2:
    btn_exam = st.button("ייצר מבחן מהיר")

# ה-AI נכנס לפעולה רק כאן, אחרי לחיצה
if btn_learn or btn_exam:
    with st.spinner("מתחבר למוח של ה-AI..."):
        try:
            import google.generativeai as genai
            
            # בדיקת מפתח
            if "GEMINI_API_KEY" not in st.secrets:
                st.error("חסר מפתח API ב-Secrets")
            else:
                genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                
                # ניסיון חיבור למודל
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                prompt = f"כתוב שיעור על {topic}" if btn_learn else "ייצר 5 שאלות למבחן המתווכים"
                response = model.generate_content(prompt)
                
                st.markdown("### תוצאה:")
                st.write(response.text)
                
        except Exception as e:
            st.error(f"השלד עובד, אבל יש תקלה בחיבור ל-AI: {e}")
