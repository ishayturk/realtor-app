# ==========================================
# Project: מתווך בקליק
# File: app.py
# Version: 1134
# Last Updated: 2026-02-16 | 20:45
# ==========================================

import streamlit as st
import google.generativeai as genai
import json, re

# --- הגדרות דף ---
st.set_page_config(page_title="מתווך בקליק", layout="wide")

def ask_ai(prompt):
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        if "429" in str(e): st.warning("⚠️ עומס במערכת. נסה שוב בעוד דקה.")
        return None

# --- לוגיקת תוכן ושאלות ---
def fetch_titles(topic):
    p = f"צור 3 כותרות קצרות (2-3 מילים) לתתי-נושאים בתוך {topic}. ללא המילים 'חלק' או 'פרק'. השתמש במושגים מקצועיים. החזר JSON בלבד: ['כותרת1', 'כותרת2', 'כותרת3']"
    res = ask_ai(p)
    try:
        match = re.search(r'\[.*\]', res, re.DOTALL)
        return json.loads(match.group())
    except: return ["יסודות החוק", "חובות וסמכויות", "הוראות מעשיות"]

def fetch_content(main_topic, sub_title):
    p = f"כתוב שיעור מפורט בפורמט Markdown על '{sub_title}' בתוך '{main_topic}'. כלול סעיפי חוק ודוגמאות."
    return ask_ai(p)

def fetch_single_question(topic):
    p = f"צור שאלה אמריקאית אחת קשה על {topic}. לכל שאלה: q (שאלה), options (רשימת 4 אפשרויות), correct (התשובה המדויקת). החזר JSON בלבד במבנה אובייקט {{}}."
    res = ask_ai(p)
    try:
        match = re.search(r'\{.*\}', res, re.DOTALL)
        return json.loads(match.group())
    except: return None

# --- ניהול Session State ---
if "step" not in st.session_state:
    st.session_state.update({
        "step": "login", "user": None, "selected_topic": None,
        "lesson_titles": [], "lesson_contents": {}, "current_sub_idx": None,
        "quiz_active": False, "current_q_data": None, "next_q_buffer": None,
        "q_counter": 0, "score": 0, "user_choice": None
    })

# --- CSS (Dark Mode Support & RTL) ---
st.markdown("""
<style>
    * { direction: rtl; text-align: right; }
    
    /* תמיכה במצב כהה ובהיר */
    :root { --text-color: inherit; --bg-card: rgba(255,255,255,0.05); }
    
    .user-strip { 
        background-color: var(--bg-card); 
        padding: 10px; border-radius: 8px; margin-bottom: 20px;
