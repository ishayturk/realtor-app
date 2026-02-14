import streamlit as st
import google.generativeai as genai

# הגדרת דף ועיצוב RTL
st.set_page_config(page_title="מנוע למידה - מתווכים", layout="centered")
st.markdown("""
    <style>
    .stApp { text-align: right; direction: rtl; }
    button { width: 100%; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# חיבור ל-API - בדיקה אם המפתח קיים בכלל
if "GEMINI_API_KEY" not in st.secrets:
    st.error("שגיאה: מפתח ה-API (Secret) לא הוגדר במערכת.")
    st.stop()

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# שינוי שם המודל לגרסה יציבה יותר
model = genai.GenerativeModel('gemini-1.5-flash')

def get_ai_content(prompt):
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"חלה שגיאה בחיבור לבינה המלאכותית: {str(e)}"

# --- תפריט ראשי ---
st.title("🎓 מתווך בקליק - למידה חכמה")

tab1, tab2 = st.tabs(["📚 שיעורי לימוד", "📝 מבחנים ותרגול"])

with tab1:
    st.subheader("בחר נושא ללימוד עמוק:")
    lesson_topics = [
        "חוק המתווכים - רישוי, קלון ואגרות",
        "בלעדיות ותקנות השיווק - סעיף 9ב",
        "חוק המקרקעין - עסקאות נוגדות (סעיף 9)",
        "חוק הגנת הצרכן וחוזים במקרקעין"
    ]
    
    selected_lesson = st.selectbox("נושאי השיעור:", lesson_topics)
    
    if st.button("צור שיעור עכשיו"):
        with st.spinner("מייצר שיעור עמוק ומעודכן..."):
            prompt = f"ייצר שיעור משפטי עמוק ומפורט למבחן המתווכים בנושא: {selected_lesson}. כלול פסיקה, סעיפי חוק קטנים, וסיכום."
            content = get_ai_content(prompt)
            st.markdown(content)

with tab2:
    st.subheader("מחולל מבחנים")
    if st.button("ייצר לי מבחן תרגול (5 שאלות)"):
        with st.spinner("בונה מבחן..."):
            prompt = "ייצר 5 שאלות אמריקאיות למבחן המתווכים עם תשובות והסברים."
            exam_content = get_ai_content(prompt)
            st.markdown(exam_content)
