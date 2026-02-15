import streamlit as st
import google.generativeai as genai
import json, re, time

st.set_page_config(page_title="מתווך בקליק - גרסה יציבה", layout="centered")

# עיצוב RTL מלא ושם משתמש קבוע למעלה
st.markdown("""<style>
* { direction: rtl !important; text-align: right !important; }
.user-header { 
    background: #1E88E5; color: white; padding: 12px; 
    border-radius: 10px; text-align: center; font-weight: bold; margin-bottom: 25px;
    font-size: 20px; box-shadow: 0 2px 5px rgba(0,0,0,0.2);
}
.stButton > button { width: 100%; border-radius: 8px; font-weight: bold; height: 3.5em; background-color: #f8f9fa; }
.stButton > button:hover { border-color: #1E88E5; color: #1E88E5; }
</style>""", unsafe_allow_html=True)

S = st.session_state
if 'step' not in S:
    S.update({'user':'','step':'login','lt':'','qa':False,'qi':0,'qans':{},'qq':[],'cq':set()})

st.title("🏠 מתווך בקליק")

# 1. שם משתמש קבוע בראש המסך
if S.user:
    st.markdown(f"<div class='user-header'>👤 שלום, {S.user}</div>", unsafe_allow_html=True)

# 2. לוגיקת כניסה - לחיצה אחת בלבד (ללא Form)
if S.step == "login":
    u_name = st.text_input("הזן שם מלא לכניסה:", key="login_input")
    if st.button("כניסה למערכת", key="login_submit"):
        if u_name:
            S.user = u_name
            S.step = "menu"
            st.rerun()

# 3. תפריט ראשי עם הניסוחים המקוריים
elif S.step == "menu":
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📚 שיעורים בנושאי הלימוד"):
            S.step = "study"
            st.rerun()
    with col2:
        if st.button("📝 סימולציית מבחן רשמית"):
            st.info("בקרוב: המבחן המלא של 25 שאלות")

# 4. רשימת נושאים מלאה כפי שביקשת
elif S.step == "study":
    all_t = ["חוק המתווכים במקרקעין", "חוק המקרקעין", "חוק החוזים", "חוק המכר (דירות)", 
             "חוק הגנת הצרכן", "חוק הגנת הדייר", "חוק תכנון ובנייה", "חוק מיסוי מקרקעין", 
             "חוק ההוצאה לפועל", "חוק הירושה", "חוק העונשין", "אתיקה מקצועית"]
    
    sel = st.selectbox("בחר נושא ללימוד:", all_t)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📖 התחל שיעור"):
            st.write(f"טוען שיעור על {sel} באמצעות Gemini 2.0...")
            # כאן יבוא הקוד של ה-Gemini ברגע שנראה שהכניסה עובדת
    with col2:
        if st.button("🏠 חזרה לתפריט"):
            S.step = "menu"
            st.rerun()
