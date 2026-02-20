import streamlit as st
import google.generativeai as genai
import json, re

# הגדרות דף בסיסיות
st.set_page_config(page_title="מתווך בקליק", layout="wide")

# CSS לניהול המבנה החדש והצמדת הפריימים
st.markdown("""
<style>
    /* ביטול מרווחים מובנים של Streamlit */
    .block-container { padding-top: 0rem !important; padding-bottom: 0rem !important; }
    .stApp header { visibility: hidden; }
    
    /* עיצוב הסטריפ העליון (Slim Strip) */
    .upper-strip {
        margin-top: 1.2rem; /* שורה אחת מתחת לתקרה */
        padding: 5px 20px;
        background-color: #ffffff;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border: none;
    }
    
    /* ביטול קווים מפרידים גלובלי */
    hr { margin: 0 !important; padding: 0 !important; display: none; }
    
    /* הגדרת ה-Iframe שיתפוס את כל השטח התחתון */
    .app-frame {
        width: 100%;
        height: 85vh;
        border: none;
        margin-top: 0px;
    }
    
    * { direction: rtl; text-align: right; }
</style>
""", unsafe_allow_html=True)

# סילבוס (עוגן 1213)
SYLLABUS = {
    "חוק המתווכים": ["רישוי והגבלות", "הגינות וזהירות", "הזמנה ובלעדיות", "פעולות שאינן תיווך"],
    "תקנות המתווכים": ["פרטי הזמנה 1997", "פעולות שיווק 2004", "דמי תיווך"],
    "חוק המקרקעין": ["בעלות וזכויות", "בתים משותפים", "עסקאות נוגדות", "הערות אזהרה", "שכירות וזיקה"],
    "חוק המכר (דירות)": ["מפרט וגילוי", "בדק ואחריות", "איחור במסירה", "הבטחת השקעות"],
    "חוק החוזים": ["כריתת חוזה", "פגמים בחוזה", "תרופות והפרה", "ביטול והשבה"],
    "חוק התכנון והבנייה": ["היתרים ושימוש חורג", "היטל השבחה", "תוכניות מתאר", "מוסדות התכנון"],
    "חוק מיסוי מקרקעין": ["מס שבח", "מס רכישה", "הקלות לדירת מגורים", "שווי שוק"],
    "חוק הגנת הצרכן": ["ביטול עסקה", "הטעיה בפרסום"],
    "דיני ירושה": ["סדר הירושה", "צוואות"],
    "חוק העונשין": ["עבירות מרמה וזיוף"]
}

# אתחול Session State
if "step" not in st.session_state:
    st.session_state.update({
        "user": None, "step": "login", "selected_topic": None, "lesson_txt": ""
    })

# פונקציות עזר (עוגן 1213)
def stream_ai_lesson(topic):
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        m = genai.GenerativeModel('gemini-2.0-flash')
        res = m.generate_content(f"כתוב שיעור מעמיק על {topic}", stream=True)
        ph = st.empty()
        full = ""
        for chunk in res:
            full += chunk.text
            ph.markdown(full + "▌")
        ph.markdown(full)
        return full
    except: return "⚠️ תקלה בחיבור ל-AI."

# --- ניהול דפים ---

# 1. דף כניסה
if st.session_state.step == "login":
    st.title("🏠 מתווך בקליק")
    u = st.text_input("שם מלא:")
    if st.button("כניסה") and u:
        st.session_state.user = u
        st.session_state.step = "menu"
        st.rerun()

# 2. תפריט ראשי
elif st.session_state.step == "menu":
    st.title("🏠 מתווך בקליק")
    st.subheader(f"👤 שלום, {st.session_state.user}")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("📚 לימוד לפי נושאים"):
            st.session_state.step = "study"; st.rerun()
    with c2:
        if st.button("⏱️ גש/י למבחן"):
            st.session_state.step = "exam_mode"; st.rerun()

# 3. מצב מבחן - שני פריימים
elif st.session_state.step == "exam_mode":
    # פריים עליון: סטריפ
    st.markdown(f"""
    <div class="upper-strip">
        <div style="font-size: 1.2rem; font-weight: bold;">🏠 מתווך בקליק</div>
        <div style="font-size: 1rem;">👤 נבחן: {st.session_state.user}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # כפתור חזרה (Streamlit לא מאפשר כפתור בתוך ה-Markdown של הסטריפ בקלות, אז נשים אותו צמוד)
    if st.button("↩️ חזרה לתפריט", key="back_home"):
        st.session_state.step = "menu"; st.rerun()

    # פריים תחתון: האפליקציה השנייה בתוך Iframe (ללא קו מפריד)
    exam_url = "https://ishayturk-realtor-app-app-kk1gme.streamlit.app/"
    st.markdown(f'<iframe src="{exam_url}" class="app-frame"></iframe>', unsafe_allow_html=True)

# 4. לימוד לפי נושאים
elif st.session_state.step == "study":
    st.title("📚 בחירת נושא לימוד")
    sel = st.selectbox("בחר נושא:", ["בחר..."] + list(SYLLABUS.keys()))
    if sel != "בחר..." and st.button("טען שיעור"):
        st.session_state.selected_topic = sel
        st.session_state.step = "lesson_run"
        st.rerun()
    if st.button("חזרה"): st.session_state.step = "menu"; st.rerun()

elif st.session_state.step == "lesson_run":
    st.header(f"📖 {st.session_state.selected_topic}")
    if not st.session_state.lesson_txt:
        st.session_state.lesson_txt = stream_ai_lesson(st.session_state.selected_topic)
    if st.button("חזרה"): 
        st.session_state.lesson_txt = ""
        st.session_state.step = "study"; st.rerun()

st.markdown('<p style="text-align:center; color:grey; font-size:0.7rem;">Version 1213-Exam</p>', unsafe_allow_html=True)
