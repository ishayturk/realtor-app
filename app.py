import streamlit as st
import google.generativeai as genai
import json
import re

# ==========================================
# 1. עיצוב חזותי משופר (חסין תקלות)
# ==========================================
def apply_design():
    st.set_page_config(page_title="מתווך בקליק", layout="wide")
    st.markdown("""
    <style>
        html, body, [data-testid="stAppViewContainer"], .main, .block-container {
            direction: rtl !important; 
            text-align: right !important;
        }
        .main-header {
            text-align: center !important;
            background: linear-gradient(90deg, #1E88E5, #1565C0);
            color: white !important; 
            padding: 25px; 
            border-radius: 15px; 
            margin-bottom: 25px;
        }
        /* תיבת תוכן לבנה עם טקסט שחור מפורש */
        .lesson-box {
            background-color: #ffffff !important; 
            color: #000000 !important; 
            padding: 20px; 
            border-radius: 10px;
            border-right: 8px solid #1E88E5; 
            margin-top: 10px;
            margin-bottom: 10px;
            direction: rtl !important;
            text-align: right !important;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        .stButton button { width: 100%; border-radius: 10px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. סילבוס
# ==========================================
FULL_SYLLABUS = [
    "חוק המתווכים במקרקעין והתקנות", "חוק המקרקעין", "חוק המכר (דירות)",
    "חוק החוזים", "חוק הגנת הצרכן", "חוק הגנת הדייר",
    "חוק התכנון והבנייה", "חוק מיסוי מקרקעין", "חוק העונשין",
    "חוק שמאי מקרקעין", "חוק הירושה", "חוק יחסי ממון",
    "חוק איסור הלבנת הון", "פקודת הנזיקין", "מושגי יסוד בכלכלה", "רשות מקרקעי ישראל"
]

# ==========================================
# 3. מנוע AI
# ==========================================
def init_gemini():
    try:
        if "GEMINI_API_KEY" in st.secrets:
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            return genai.GenerativeModel('gemini-2.0-flash')
    except:
        pass
    return None

def fetch_quiz(model, topic):
    prompt = f"צור 10 שאלות אמריקאיות בעברית על {topic}. החזר רק JSON תקין: [{{'q':'','options':['','','',''],'correct':0,'explanation':''}}]"
    try:
        resp = model.generate_content(prompt)
        text = resp.text.strip()
        match = re.search(r'\[\s*\{.*\}\s*\]', text, re.DOTALL)
        if match:
            return json.loads(match.group())
    except:
        return None

# ==========================================
# 4. ניהול האפליקציה
# ==========================================
def main():
    apply_design()
    model = init_gemini()
    
    if "view" not in st.session_state:
        st.session_state.update({"view": "login", "user": "", "topic": "", "lesson": "", "questions": [], "idx": 0, "show_f": False})

    st.markdown('<div class="main-header"><h1>🏠 מתווך בקליק</h1><p>גרסה 102 - יציבה</p></div>', unsafe_allow_html=True)

    if st.session_state.view == "login":
        name = st.text_input("הכנס שם מלא:")
        if st.button("כניסה למערכת"):
            if name: 
                st.session_state.user = name
                st.session_state.view = "menu"
                st.rerun()

    elif st.session_state.view == "menu":
        st.write(f"### שלום {st.session_state.user}")
        selected = st.selectbox("בחר נושא:", ["בחר נושא..."] + FULL_SYLLABUS)
        if selected != "בחר נושא...":
            st.session_state.topic = selected
            if st.button("📖 פתח שיעור"):
                st.session_state.lesson = ""
                st.session_state.view = "lesson"
                st.rerun()

    elif st.session_state.view == "lesson":
        st.subheader(f"📍 {st.session_state.topic}")
        if st.button("🏠 חזרה"): st.session_state.view = "menu"; st.rerun()
        
        if not st.session_state.lesson:
            with st.spinner("כותב שיעור..."):
                try:
                    # שינוי: קודם מקבלים את הטקסט ואז מציגים
                    resp = model.generate_content(f"כתוב שיעור מפורט על {st.session_state.topic} למבחן המתווכים.")
                    st.session_state.lesson = resp.text
                except:
                    st.error("ה-AI לא הגיב. נסה שוב.")
        
        # הצגה בתוך התיבה המעוצבת
        if st.session_state.lesson:
            st.markdown(f'<div class="lesson-box">{st.session_state.lesson}</div>', unsafe_allow_html=True)
            if st.button("עבור לתרגול ✍️"):
                st.session_state.view = "menu" # או ישר ל-quiz אם תרצה
                st.rerun()

if __name__ == "__main__":
    main()
