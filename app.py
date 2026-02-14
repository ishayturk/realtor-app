import streamlit as st
import google.generativeai as genai

# הגדרות דף ועיצוב RTL
st.set_page_config(page_title="מנוע למידה - מתווכים", layout="centered")

st.markdown("""
    <style>
    .stApp { text-align: right; direction: rtl; }
    .stMarkdown, p, h1, h2, h3, li { text-align: right; direction: rtl; }
    button { width: 100%; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# חיבור ל-API
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    
    # התיקון הקריטי: שימוש בפורמט 'models/gemini-1.5-flash-latest'
    # לפעמים ה-SDK דורש את הקידומת models/ כדי למנוע 404
    model = genai.GenerativeModel('models/gemini-1.5-flash-latest')
else:
    st.error("חסרה סיסמת ה-API ב-Secrets!")
    st.stop()

def get_ai_content(prompt):
    try:
        # פנייה ל-AI
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        # אם גם זה נכשל, ננסה "נסיגה" למודל הכי פשוט באופן אוטומטי
        try:
            fallback_model = genai.GenerativeModel('models/gemini-1.5-flash')
            return fallback_model.generate_content(prompt).text
        except:
            return f"חלה שגיאה בחיבור (404): המודל לא נמצא בשרת. וודא שחבילת ה-requirements מעודכנת. פירוט: {str(e)}"

# --- מבנה האפליקציה ---
st.title("🎓 מתווך בקליק - למידה חכמה")

tab1, tab2 = st.tabs(["📚 שיעורי לימוד", "📝 מבחנים ותרגול"])

with tab1:
    st.subheader("בחר נושא ללימוד:")
    lesson_topics = ["חוק המתווכים", "חוק המקרקעין", "הגנת הצרכן"]
    selected_lesson = st.selectbox("נושא:", lesson_topics)
    
    if st.button("צור שיעור"):
        with st.spinner("מייצר..."):
            res = get_ai_content(f"כתוב שיעור על {selected_lesson} למבחן המתווכים")
            st.markdown(res)

with tab2:
    st.subheader("מבחן מהיר")
    if st.button("ייצר 5 שאלות"):
        with st.spinner("בונה..."):
            res = get_ai_content("ייצר 5 שאלות אמריקאיות למבחן המתווכים עם תשובות")
            st.markdown(res)
