# ==========================================
# Project: מתווך בקליק
# Version: 1116
# Last Updated: 2026-02-16
# ==========================================

import streamlit as st
import google.generativeai as genai
import json, re, time

# הגדרות דף
st.set_page_config(page_title="מתווך בקליק", layout="centered")

# עיצוב UI - הגדרות CSS נקיות בלבד
st.markdown("""
<style>
    * { direction: rtl; text-align: right; }
    .lesson-box { 
        background: #f9f9f9; padding: 25px; border-right: 6px solid #1E88E5; 
        line-height: 1.8; margin-top: 10px; border-radius: 5px;
    }
    .stButton>button { width: 100%; }
    .user-label { 
        font-size: 1rem; color: #666; padding: 5px 0; 
        border-bottom: 1px solid #eee; margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# ניהול State
S = st.session_state
for k in ['step','user','subs','lt','topic','sub_n','qq','qi','score','ans_d','l_qi']:
    if k not in S:
        if k in ['score','qi']: S[k] = 0
        elif k == 'ans_d': S[k] = False
        elif k in ['subs','qq']: S[k] = []
        elif k == 'step': S[k] = 'login'
        else: S[k] = ''

def ask_ai(p):
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    m = genai.GenerativeModel('gemini-2.0-flash')
    # ניסיון טעינה כפול ליציבות
    for attempt in range(2):
        try:
            r = m.generate_content(p)
            if r and r.text: return r.text
        except:
            time.sleep(1)
    return None

def reset_to_home():
    S.step = 'menu'
    S.subs = []
    S.lt = ""
    S.sub_n = ""
    S.topic = ""
    S.qq = []
    S.qi = 0
    S.ans_d = False

# מפת נושאים מקצועית
T_MAP = {
    "חוק המתווכים": ["דרישת הכתב בחוזה תיווך", "פעולה כגורם יעיל בעסקה", "דמי תיווך ותקופת בלעדיות"],
    "חוק המקרקעין": ["זכויות בעלות ושיתוף", "רישום בפנקסי מקרקעין", "רישום הערות אזהרה במקרקעין"],
    "חוק המכר (הבטחת השקעות)": ["שיטות ליווי בנקאי", "מתן ערבויות חוק המכר", "תשלום באמצעות פנקס שוברים"],
    "חוק המכר (דירות)": ["מפרט המכר וצירופו לחוזה", "תקופת בדק ואחריות קבלן", "אחריות המוכר לתיקון אי התאמה"],
    "חוק הגנת הצרכן": ["איסור הטעיה וניצול מצוקה", "ביטול עסקת מכר מרחוק", "חובת גילוי מידע לצרכן"],
    "חוק החוזים (כללי)": ["תהליך כריתת חוזה", "פגמים בכריתת חוזה", "צורת החוזה ותוקפו המשפטי"],
    "חוק החוזים (תרופות)": ["אכיפת חוזה שהופר", "ביטול חוזה בשל הפרה", "פיצויים בגין הפרת חוזה"],
    "חוק העונשין": ["עבירות שוחד", "קבלת דבר במרמה", "זיוף מסמכים ותעודות"],
    "תמ\"א 38": ["רוב דרוש לביצוע הפרויקט", "זכויות בנייה והטבות מס", "מיגון וחיזוק מבנים קיימים"],
    "תכנון ובנייה": ["מוסדות תכנון ובנייה", "תהליך קבלת היתרי בנייה", "חובת תשלום היטל השבחה"],
    "מיסוי מקרקעין": ["חישוב מס שבח", "חובת תשלום מס רכישה", "פטורים ממס במכירת דירה"],
    "יחסי ממון": ["הסדר איזון משאבים", "עריכת הסכמי ממון", "זכויות בדירת המגורים המשותפת"],
    "חוק הירושה": ["ירושה על פי דין", "עריכת צוואות חוקיות", "מינוי וניהול עיזבון"],
    "הגנת הדייר": ["זכויות דיירות מוגנת", "תשלום דמי מפתח", "עילות פינוי דייר מוגן"],
    "חוק הוצאה לפועל": ["ביצוע עיקולי מקרקעין", "כינוס נכסים למכירה", "חקירת יכולת כלכלית לחייב"],
    "חוק שמאי מקרקעין": ["חובת רישוי שמאי", "אתיקה מקצועית בשמאות", "כללי עריכת שומת מקרקעין"]
}

if S.user:
    st.markdown(f"<div class='user-label'>👤 תלמיד/ה: {S.user}</div>", unsafe_allow_html=True)

st.title("🏠 מתווך בקליק")

if S.step == 'login':
    u = st.text_input("הזן שם מלא לכניסה:")
    if st.button("כניסה למערכת"):
        if u: S.user=u; S.step='menu'; st.rerun()

elif S.step == 'menu':
    c1, c2 = st.columns(2)
    with c1:
        if st.button("📚 לימוד לפי נושאים"): S.step='study'; st.rerun()
    with c2:
        if st.button("⏱️ סימולציית בחינה מלאה"): S.topic="כללי"; S.step='q_prep'; st.rerun()

elif S.step == 'study':
    sel = st.selectbox("בחר נושא לימוד מהרשימה:", ["ב
