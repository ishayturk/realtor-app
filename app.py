# ==========================================
# Project: מתווך בקליק | Version: 1160
# Last Updated: 2026-02-17 | 01:40
# ==========================================

import streamlit as st
import google.generativeai as genai
import json, re

st.set_page_config(page_title="מתווך בקליק", layout="wide")
st.markdown('<div id="top"></div>', unsafe_allow_html=True)

SYLLABUS = {
    "חוק המתווכים במקרקעין": ["רישוי והגבלות עיסוק", "חובת הגינות וזהירות", "הזמנת תיווך ובלעדיות"],
    "תקנות המתווכים (פרטי הזמנה)": ["דרישות חובה בטופס", "זיהוי נכס וצדדים", "פירוט דמי התיווך"],
    "תקנות המתווכים (פעולות שיווק)": ["פעולות שיווק סטנדרטיות", "הרחבות לשיווק בבלעדיות", "חובת הוכחת פעילות"],
    "חוק המקרקעין": ["בעלות וזכויות במקרקעין", "בתים משותפים והצמדות", "עסקאות נוגדות והערות אזהרה"],
    "חוק הגנת הדייר": ["דיירות מוגנת ודמי מפתח", "עילות פינוי", "זכויות וחובות דייר מוגן"],
    "חוק המכר (דירות)": ["מפרט וחובת גילוי", "תקופות בדק ואחריות", "איחור במסירה ופיצויים"],
    "חוק החוזים": ["כריתת חוזה ותום לב", "פגמים בחוזה (טעות/הטעיה)", "תרופות בשל הפרת חוזה"],
    "חוק הגנת הצרכן": ["הטעיה בפרסום ושיווק", "ביטול עסקה והחזר כספי", "חובות גילוי כלפי צרכן"],
    "חוק עבירות עונשין": ["עבירות מרמה והונאה", "זיוף מסמכים במקרקעין", "אחריות פלילית של בעלי מקצוע"],
    "חוק שמאי מקרקעין": ["תפקיד השמאי והערכות", "סמכויות והגדרות", "בסיס השומה למכירה"],
    "חוק התכנון והבנייה": ["היתרי בנייה ושימוש חורג", "היטל השבחה", "תוכניות מתאר"],
    "חוק מיסוי מקרקעין": ["מס שבח", "מס רכישה", "פטורים והקלות במס"],
    "חוק הירושה": ["ירושה על פי דין מול צוואה", "ניהול עיזבון", "העברת מקרקעין בירושה"],
    "חוק הוצאה לפועל": ["עיקול מקרקעין", "מימוש משכנתאות", "פינוי נכסים"],
    "פקודת הנזיקין": ["רשלנות מקצועית", "מצג שווא", "חובת הזהירות כלפי צד ג'"]
}

def ask_ai(prompt):
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-2.0-flash')
        res = model.generate_content(prompt)
        return res.text if (res and res.text) else None
    except: return None

def fetch_content(topic, sub):
    p = f"כתוב שיעור Markdown מקצועי על '{sub}' בתוך '{topic}'. בלי הקדמות ובלי לציין 'מבחן מתווכים'."
    return ask_ai(p) or "⚠️ שגיאה בטעינה."

def fetch_q(topic):
    p = f"צור שאלה אמריקאית על {topic}. JSON: {{'q':'..','options':['..'],'correct':'..','explain':'..'}}"
    res = ask_ai(p)
    try:
        m = re.search(r'\{.*\}', res, re.DOTALL)
        return json.loads(m.group())
    except: return None

if "step" not in st.session_state:
    st.session_state.update({
        "step": "login", "user": None, "selected_topic": None,
        "lesson_contents": {}, "current_sub_idx": None,
        "quiz_active": False, "q_counter": 0, "score": 0,
        "current_q_data": None, "show_feedback": False
    })

st.markdown("""
<style>
