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

# חיבור ל-API של Gemini (צריך להזין KEY)
# ב-GitHub שמים את זה ב-Secrets
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

def get_ai_content(prompt):
    response = model.generate_content(prompt)
    return response.text

# --- תפריט ראשי ---
st.title("🎓 מתווך בקליק - למידה חכמה")

# סדר הכפתורים לפי בקשתך: למידה מעל מבחנים
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
            prompt = f"ייצר שיעור משפטי עמוק ומפורט למבחן המתווכים בנושא: {selected_lesson}. כלול פסיקה, סעיפי חוק קטנים, וסיכום. בסוף השיעור הצג 3 שאלות אמריקאיות מכשילות לבדיקת הבנה."
            content = get_ai_content(prompt)
            st.markdown(content)
            st.success("השיעור הושלם! ניתן לחזור לתפריט או לעבור למבחן.")

with tab2:
    st.subheader("מחולל מבחנים ON THE FLY")
    if st.button("ייצר לי מבחן תרגול (5 שאלות)"):
        with st.spinner("בונה מבחן מכשיל..."):
            prompt = "ייצר 5 שאלות אמריקאיות ברמה גבוהה למבחן המתווכים מכל הנושאים. כלול תשובות מוסתרות עם הסברים משפטיים."
            exam_content = get_ai_content(prompt)
            st.markdown(exam_content)

st.divider()
st.info("האפליקציה מייצרת תוכן בזמן אמת באמצעות בינה מלאכותית")
