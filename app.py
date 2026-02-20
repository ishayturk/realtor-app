import streamlit as st
import google.generativeai as genai
import json
import re

# הגדרות עמוד
st.set_page_config(page_title="מתווך בקליק", layout="wide")

# סילבוס לימודים
SYLLABUS = {
    "חוק המתווכים במקרקעין, התשנ"ה-1995": [
        "רישוי והגבלות (סעיפים 2-13)",
        "חובת הגינות וזהירות (סעיף 8)",
        "הזמנה בכתב ובלעדיות (סעיף 9)",
        "פעולות שאינן פעולות תיווך (סעיף 12)",
        "דמי תיווך והגורם היעיל (סעיף 14)"
    ],
    "תקנות המתווכים במקרקעין": [
        "פרטי הזמנה בכתב (1997)",
        "פעולות שיווק (2004)"
    ],
    "חוק המקרקעין, התשכ"ט-1969": [
        "בעלות וזכויות במקרקעין",
        "עסקאות ורישום (סעיפים 6-10)",
        "הערות אזהרה (סעיפים 126-127)",
        "בתים משותפים",
        "שכירות, שאילה וזיקת הנאה"
    ],
    "חוק המכר (דירות), התשל"ג-1973": [
        "חובת גילוי ומפרט",
        "תקופת בדק ואחריות",
        "פיצוי על איחור במסירה"
    ],
    "חוק המכר (דירות) (הבטחת השקעות), התשל"ה-1974": [
        "ערבויות חוק מכר",
        "פנקס שוברים"
    ],
    "חוק החוזים (חלק כללי) ודיני חוזים": [
        "כריתת חוזה (הצעה וקיבול)",
        "פגמים בכריתה (טעות, הטעיה, כפייה ועושק)",
        "תרופות בשל הפרת חוזה"
    ],
    "חוק התכנון והבנייה, התשכ"ה-1965": [
        "מוסדות התכנון (מועצה ארצית, ועדה מחוזית/מקומית)",
        "היתרי בנייה ושימוש חורג",
        "היטל השבחה"
    ],
    "מיסוי מקרקעין": [
        "מס שבח (עקרונות ופטורים)",
        "מס רכישה (מדרגות ודירה יחידה)"
    ],
    "חוק הגנת הצרכן, התשמ"א-1981": [
        "איסור הטעיה",
        "ביטול עסקת רוכלות/מכר מרחוק"
    ],
    "חוק הירושה, התשכ"ה-1965": [
        "ירושה על פי דין",
        "צוואות (סוגים ועקרונות)"
    ],
    "חוק העונשין, התשל"ז-1977": [
        "עבירות מרמה, זיוף ושוחד"
    ]
}

# פונקציה לשליפת שאלה מה-AI
def fetch_question_from_ai(topic):
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        prompt = f"""
        צור שאלה אמריקאית אחת קשה ומאתגרת בנושא {topic} מתוך חומר הלימוד של בחינת רשם המתווכים.
        החזר את התשובה אך ורק בפורמט JSON תקני כזה:
        {{
            "question": "השאלה כאן",
            "options": ["אופציה 1", "אופציה 2", "אופציה 3", "אופציה 4"],
            "answer": "האופציה הנכונה בדיוק",
            "explanation": "הסבר מפורט כולל סעיף החוק הרלוונטי"
        }}
        """
        
        response = model.generate_content(prompt)
        raw_text = response.text
        json_match = re.search(r'\{.*\}', raw_text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
    except Exception as e:
        return None
    return None

# פונקציית סטרימינג לשיעור
def stream_lesson(topic):
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        prompt = f"כתוב שיעור הכנה מפורט ומעמיק לבחינת המתווכים בנושא: {topic}. פרט סעיפי חוק, הגדרות חשובות, ודוגמאות פרקטיות. כתוב בצורה מסודרת עם בולטים."
        
        response = model.generate_content(prompt, stream=True)
        
        placeholder = st.empty()
        full_response = ""
        
        for chunk in response:
            full_response += chunk.text
            placeholder.markdown(full_response + "▌")
        
        placeholder.markdown(full_response)
        return full_response
    except Exception as e:
        st.error(f"שגיאה בחיבור ל-AI: {str(e)}")
        return None

# ניהול מצבי אפליקציה
if "step" not in st.session_state:
    st.session_state.step = "login"
if "user_name" not in st.session_state:
    st.session_state.user_name = ""
if "selected_topic" not in st.session_state:
    st.session_state.selected_topic = None
if "lesson_content" not in st.session_state:
    st.session_state.lesson_content = ""
if "quiz_active" not in st.session_state:
    st.session_state.quiz_active = False

# עיצוב RTL
st.markdown("""
