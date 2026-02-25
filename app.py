# Project: מתווך בקליק | Version: training_full_V08 | 25/02/2026 | 07:25
# Status: Fixed Logic Only | Protocol: Simple & Direct
import streamlit as st
import google.generativeai as genai
import json
import re

# הגדרת דף
st.set_page_config(page_title="מתווך בקליק", layout="wide", initial_sidebar_state="collapsed")

# Interceptor - כניסה אוטומטית לפי שם משתמש ב-URL
if "user" in st.query_params and st.session_state.get("user") is None:
    st.session_state.user = st.query_params.get("user")
    st.session_state.step = "menu"
    st.rerun()

# עיצוב RTL בסיסי (עוגן 1213)
st.markdown("""
<style>
    * { direction: rtl; text-align: right; }
    .header-container { 
        display: flex; 
        align-items: center; 
        gap: 45px; 
        margin-bottom: 30px; 
    }
    .header-title { font-size: 2.5rem !important; font-weight: bold !important; margin: 0 !important; }
    .header-user { font-size: 1.2rem !important; font-weight: 900 !important; color: #31333f; }
    .stButton>button { width: 100% !important; border-radius: 8px !important; font-weight: bold !important; height: 3em !important; }
</style>
""", unsafe_allow_html=True)

# סילבוס
SYLLABUS = {
    "חוק המתווכים": ["רישוי והגבלות", "הגינות וזהירות", "הזמנה ובלעדיות", "פעולות שאינן תיווך"],
    "תקנות המתווכים": ["פרטי הזמנה 1997", "פעולות שיווק 2004", "דמי תיווך"],
    "חוק המקרקעין": ["בעלות וזכויות", "בתים משותפים", "עסקאות נוגדות", "הערות אזהרה", "שכירות וזיקה"],
    "חוק המכר (דירות)": ["מפרט וגילוי", "בדק ואחריות", "איחור במסירה", "הבטחת השקעות"],
    "חוק החוזים": ["כריתת חוזה", "פגמים בחוזה", "תרופות והפרה", "ביטול והשבה"],
    "חוק התכנון והבנייה": ["היתרים ושימוש חורג", "היטל השבחה", "תוכניות מתאר", "מוסדות התכנון"],
    "חוק מיסוי מקרקעין": ["מס שבח (חישוב ופטורים)", "מס רכישה", "הקלות לדירת מגורים", "שווי שוק"],
    "חוק הגנת הצרכן
