import streamlit as st
import google.generativeai as genai

# --- הגדרות דף ועיצוב (עולה מייד) ---
st.set_page_config(page_title="מתווך בקליק", layout="centered")

st.markdown("""
    <style>
    .stApp { text-align: right; direction: rtl; }
    [data-testid="stHeader"] { direction: rtl; }
    .stTabs [data-baseweb="tab-list"] { direction: rtl; }
    .stMarkdown, p, h1, h2, h3, li, span { text-align: right; direction: rtl; }
    button { width: 100%; border-radius: 10px; height: 3em; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎓 מתווך בקליק")
st.write("בחר נושא והתחל ללמוד למבחן המתווכים.")

# --- בניית התפריט (השלד) ---
tab1, tab2 = st.tabs(["📚 שיעור לימוד", "📝 מבחן תרגול"])

with tab1:
    lesson_topics = ["חוק המתווכים", "חוק המקרקעין", "חוק הגנת הצרכן", "דיני חוזים"]
    selected_topic = st.selectbox("בחר נושא:", lesson_topics)
    btn_learn = st.button("התחל שיעור")

with tab2:
    btn_exam = st.button("ייצר 5 שאלות תרגול")

# --- לוגיקה לחיבור ל-AI (רק בלחיצה) ---
if btn_learn or btn_exam:
    with st.spinner("מחבר אותך למוח של הבינה המלאכותית..."):
        try:
            # 1. בדיקת המפתח
            if "GEMINI_API_KEY" not in st.secrets:
                st.error("חסר מפתח API ב-Secrets!")
                st.stop()
            
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            
            # 2. פתרון ה-404: מציאת מודל זמין באופן אוטומטי
            # אנחנו שואלים את גוגל: "איזה מודלים פתוחים לי כרגע?"
            model_list = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            
            if not model_list:
                st.error("לא נמצאו מודלים פעילים בחשבון שלך.")
            else:
                # בוחרים את המודל הראשון שגוגל מחזירה (בלי לנחש שמות)
                chosen_model = model_list[0]
                model = genai.GenerativeModel(chosen_model)
                
                # 3. יצירת התוכן
                if btn_learn:
                    prompt = f"ייצר שיעור משפטי מפורט בעברית על {selected_topic} למבחן המתווכים."
                else:
                    prompt = "ייצר 5 שאלות אמריקאיות למבחן המתווכים עם תשובה נכונה והסבר משפטי."
                
                response = model.generate_content(prompt)
                
                st.success(f"חובר בהצלחה (מודל: {chosen_model})")
                st.markdown("---")
                st.markdown(response.text)
                
        except Exception as e:
            st.error(f"ניסיתי הכל, אבל יש תקלה: {str(e)}")
            st.info("אם מופיע 404, וודא שקובץ ה-requirements.txt מכיל את השורה: google-generativeai>=0.8.0")
