# ==========================================
# Project: מתווך בקליק | Version: 1173
# Last Updated: 2026-02-16 | 19:20
# ==========================================

import streamlit as st
import google.generativeai as genai
import json, re

# הגדרת דף בראש הקוד - מבטיח רוחב מלא
st.set_page_config(page_title="מתווך בקליק", layout="wide")

# CSS יציב לניהול רווחים ויישור
st.markdown("""
<style>
    * { direction: rtl; text-align: right; }
    .stButton>button { width: auto; min-width: 110px; border-radius: 8px; font-weight: bold; background-color: transparent !important; border: 1px solid #888 !important; color: #333 !important; }
    .nav-link { background: transparent; border: 1px solid #888; color: #333; padding: 6px 12px; text-decoration: none; border-radius: 8px; font-size: 14px; font-weight: bold; display: inline-block; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div id="top"></div>', unsafe_allow_html=True)

SYLLABUS = {
    "חוק המתווכים במקרקעין": ["רישוי והגבלות עיסוק", "חובת הגינות וזהירות", "הזמנת תיווך ובלעדיות"],
    "תקנות המתווכים (פרטי הזמנה)": ["דרישות חובה בטופס", "זיהוי נכס וצדדים", "פירוט דמי התיווך"],
    "תקנות המתווכים (פעולות שיווק)": ["פעולות שיווק", "הרחבות לבלעדיות", "חובת הוכחת פעילות"],
    "חוק המקרקעין": ["בעלות וזכויות", "בתים משותפים", "עסקאות נוגדות והערות אזהרה"],
    "חוק המכר (דירות)": ["מפרט וחובת גילוי", "בדק ואחריות", "איחור במסירה"],
    "חוק החוזים": ["כריתת חוזה", "פגמים בחוזה", "תרופות בשל הפרה"],
    "חוק התכנון והבנייה": ["היתרי בנייה", "היטל השבחה", "תוכניות מתאר"],
    "חוק מיסוי מקרקעין": ["מס שבח", "מס רכישה", "פטורים והקלות"]
}

def ask_ai(prompt):
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-2.0-flash')
        res = model.generate_content(prompt)
        return res.text if (res and res.text) else None
    except: return None

def fetch_content(topic, sub):
    p = f"כתוב שיעור מקצועי על '{sub}' בתוך '{topic}'. בלי הקדמות ובלי המילים 'מבחן מתווכים'."
    return ask_ai(p) or "⚠️ שגיאה בטעינה."

def fetch_q(topic):
    p = f"צור שאלה אמריקאית על {topic}. JSON: {{'q':'..','options':['..'],'correct':'..','explain':'..'}}"
    res = ask_ai(p)
    try:
        m = re.search(r'\{.*\}', res, re.DOTALL)
        return json.loads
