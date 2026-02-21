# ==========================================
# Project: מתווך בקליק | Version: 1213 Final
# Status: Syntax Verified | Protocol: Clean Code (Safe-Split)
# ==========================================
import streamlit as st
import google.generativeai as genai
import json, re

st.set_page_config(page_title="מתווך בקליק", layout="wide")

# עיצוב כותרות מקורי (עוגן 1213)
st.markdown("""<style>
    * { direction: rtl; text-align: right; }
    .stButton>button { 
        width: 100% !important; border-radius: 8px !important; 
        font-weight: bold !important; height: 3em !important; 
    }
    .header-container { 
        display: flex; align-items: center; gap: 45px; margin-bottom: 30px; 
    }
    .header-title { 
        font-size: 2.5rem !important; font-weight: bold !important; 
        margin: 0 !important; 
    }
    .header-user { 
        font-size: 1.2rem !important; font-weight: 900 !important; 
        color: #31333f; 
    }
</style>""", unsafe_allow_html=True)

SYLLABUS = {
    "חוק המתווכים": [
        "רישוי והגבלות", "הגינות וזהירות", 
        "הזמנה ובלעדיות", "פעולות שאינן תיווך"
    ],
    "תקנות המתווכים": [
        "פרטי הזמנה 1997", "פעולות שיווק 2004", "דמי תיווך"
    ],
    "חוק המקרקעין": [
        "בעלות וזכויות", "בתים משותפים", "עסקאות נוגדות", 
        "הערות אזהרה", "שכירות וזיקה"
    ],
    "חוק המכר (דירות)": [
        "מפרט וגילוי", "בדק ואחריות", 
        "איחור במסירה", "הבטחת השקעות"
    ],
    "חוק החוזים": [
        "כריתת חוזה", "פגמים בחוזה", 
        "תרופות והפרה", "ביטול והשבה"
    ],
    "חוק התכנון והבנייה": [
        "היתרים ושימוש חורג", "היטל השבחה", 
        "תוכניות מתאר", "מוסדות התכנון"
    ],
    "חוק מיסוי מקרקעין": [
        "מס שבח (חישוב ופפורים)", "
