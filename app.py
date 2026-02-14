import streamlit as st
import google.generativeai as genai
import json
import re

# ==========================================
# 1. עיצוב חזותי (כולל תיקון למצב כהה בניידים)
# ==========================================
def apply_design():
    st.set_page_config(page_title="מתווך בקליק", layout="wide")
    st.markdown("""
    <style>
        /* הגדרות כלליות ליישור לימין */
        html, body, [data-testid="stAppViewContainer"], .main, .block-container {
            direction: rtl !important; 
            text-align: right !important;
        }
        
        /* כותרת ראשית */
        .main-header {
            text-align: center !important;
            background: linear-gradient(90deg, #1E88E5, #1565C0);
            color: white !important; 
            padding: 25px; 
            border-radius: 15px; 
            margin-bottom: 25px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }

        /* תיבת שיעור ותיבת הסבר - חסין ל-Dark Mode */
        .lesson-box {
            background-color: #ffffff !important; 
            color: #1a1a1a !important; /* טקסט כהה תמיד */
            padding: 25px; 
            border-radius: 15px;
            border-right: 8px solid #1E88E5; 
            box-shadow: 0 2px 12px rgba(0,0,0,0.08);
            line-height: 1.8; 
            font-size: 1.1rem; 
            direction: rtl !important;
            text-align: right !important;
        }

        /* עיצוב כפתורים */
        .stButton button { 
            width: 100% !important; 
            height: 3.5em !important; 
            border-radius: 12px !important; 
            font-weight: bold !important; 
        }

        /* תיקון צבעים לשאלות במצב כהה */
        div[role="radiogroup"] label {
            color: inherit !important;
        }
        
        [data-testid="stMarkdownContainer"] { 
            direction: rtl !important; 
            text-align: right !important; 
        }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. הסילבוס המלא
# ==========================================
FULL_SYLLABUS = [
    "חוק המתווכים במקרקעין והתקנות", "חוק המקרקעין", "חוק המכר (דירות)",
    "חוק החוזים", "חוק הגנת הצרכן", "חוק הגנת הדייר",
    "חוק התכנון והבנייה", "חוק מיסוי מקרקעין", "חוק העונשין",
    "חוק שמאי מקרקעין", "חוק הירושה", "חוק יחסי ממון",
    "חוק איסור הלבנת הון", "פקודת הנזיקין", "מושגי יסוד בכלכלה", "רשות מקרקעי ישראל"
]

# ==========================================
# 3. מנוע AI (עם ה-Prompt המשופר)
# ==========================================
def init_gemini():
    if "GEMINI_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        return genai.GenerativeModel('gemini-2.0-flash')
    return None

def fetch_quiz(model, topic):
    prompt = f"""
    צור 10 שאלות אמריקאיות בעברית על {topic} כהכנה למבחן המתווכים.
    החזר אך ורק פורמט JSON תקני במבנה הבא (ללא טקסט נוסף לפני או אחרי):
    [
      {{
        "q": "השאלה כאן",
        "options": ["אופציה 1", "אופציה 2", "אופציה 3", "אופציה 4"],
        "correct": 0,
        "explanation": "הסבר משפטי מפורט"
      }}
    ]
    ודא שהתשובה הנכונה (correct) היא האינדקס של התשובה בתוך הרשימה (0-3).
    """
    try:
        resp = model.generate_content(prompt)
        text = resp.text.strip()
        # חיפוש ה-JSON בתוך התשובה
        match = re.search(r'\[\s*\{.*\}\s*\]', text, re.DOTALL)
        if match:
            return json.loads(match.group())
        return None
    except Exception as e:
        st.error(f"שגיאה ביצירת שאלות: {e}")
        return None

# ==========================================
# 4. ניהול האפליקציה
# ==========================================
def main():
    apply_design()
    model = init_gemini()
    
    if not model:
        st.error("API Key חסר ב-Secrets!")
        return

    # אתחול Session State
    if "view" not in st.session_state:
        st.session_state.update({
            "view": "login", 
            "user": "", 
            "topic": "", 
            "lesson": "", 
            "questions": [], 
            "idx": 0, 
            "show_f": False
        })

    # לוגו וכותרת
    st.markdown("""
        <div class="main-header">
            <h1 style='margin:0; color: white;'>🏠 מתווך בקליק</h1>
            <p style='margin:0; opacity:0.9; color: white;'>גרסה 101 - הלמידה מתחילה כאן</p>
        </div>
    """, unsafe_allow_html=True)

    # --- דף כניסה ---
    if st.session_state.view == "login":
        name = st.text_input("הכנס שם מלא:")
        if st.button("כניסה למערכת"):
            if name: 
                st.session_state
