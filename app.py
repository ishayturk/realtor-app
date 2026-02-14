import streamlit as st
import google.generativeai as genai

# 1. הגדרות דף ועיצוב RTL
st.set_page_config(page_title="מנוע למידה - מתווכים", layout="centered")

st.markdown("""
    <style>
    .stApp { text-align: right; direction: rtl; }
    [data-testid="stHeader"] { direction: rtl; }
    .stTabs [data-baseweb="tab-list"] { direction: rtl; }
    .stMarkdown, p, h1, h2, h3, li { text-align: right; direction: rtl; }
    button { width: 100%; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# 2. חיבור ל-API
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    # שימוש במודל יציב
    model = genai.GenerativeModel('gemini-pro')
else:
    st.error("חסרה סיסמת ה-API ב-Secrets!")
    st.stop()

def get_ai_content(prompt):
    try:
        context = "אתה מורה מומחה למבחן המתווכים בישראל. ענה בעברית רהוטה."
        full_prompt = f"{context}\n\n{prompt}"
        response = model.generate_content(full_prompt)
        return response.text
    except Exception as e:
        return f"חלה שגיאה בחיבור: {str(e)}"

# 3. מבנה האפליקציה
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
        with st.spinner("מייצר שיעור..."):
            prompt = f"ייצר שיעור משפטי מפורט למבחן המתווכים בנושא: {selected_lesson}. כלול פסיקה וסעיפי חוק."
            content = get_ai_content(prompt)
            st.markdown(content)

with tab2:
    st.subheader("מחולל מבחנים")
    if st.button("ייצר לי מבחן תרגול (5 שאלות)"):
        with st.spinner("בונה מבחן..."):
            # כאן הייתה השגיאה - וידאתי שהשורה סגורה עם מירכאות
            prompt = "ייצר 5 שאלות אמריקאיות ברמה גבוהה למבחן המתווכים. לכל שאלה הצג 4 אפשרויות, ולאחר מכן את התשובה הנכונה עם הסבר משפטי."
            exam_content = get_ai_content(prompt)
            st.markdown(exam_content)

st.divider()
st.info("האפליקציה מייצרת תוכן בזמן אמת באמצעות בינה מלאכותית.")
