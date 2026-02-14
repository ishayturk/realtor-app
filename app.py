import streamlit as st
import google.generativeai as genai
import json
import re

# ==========================================
# 1. עיצוב חזותי
# ==========================================
def apply_design():
    st.set_page_config(page_title="מתווך בקליק", layout="wide")
    st.markdown("""
    <style>
        html, body, [data-testid="stAppViewContainer"], .main, .block-container {
            direction: rtl !important; text-align: right !important;
        }
        .main-header {
            text-align: center !important;
            background: linear-gradient(90deg, #1E88E5, #1565C0);
            color: white !important; padding: 25px; border-radius: 15px; margin-bottom: 25px;
        }
        .lesson-box {
            background-color: #ffffff !important; color: #000000 !important; 
            padding: 25px; border-radius: 15px; border-right: 8px solid #1E88E5; 
            box-shadow: 0 2px 12px rgba(0,0,0,0.1); line-height: 1.8;
        }
        .stButton button { width: 100%; border-radius: 12px; font-weight: bold; height: 3em; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. מנוע AI
# ==========================================
def init_gemini():
    if "GEMINI_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        return genai.GenerativeModel('gemini-2.0-flash')
    return None

def fetch_quiz(model, topic):
    prompt = f"צור 10 שאלות אמריקאיות בעברית על {topic}. החזר רק JSON: [{{'q':'','options':['','','',''],'correct':0,'explanation':''}}]"
    try:
        resp = model.generate_content(prompt)
        match = re.search(r'\[\s*\{.*\}\s*\]', resp.text, re.DOTALL)
        return json.loads(match.group()) if match else None
    except: return None

# ==========================================
# 3. ניהול האפליקציה
# ==========================================
def main():
    apply_design()
    model = init_gemini()
    
    if "view" not in st.session_state:
        st.session_state.update({"view": "login", "user": "", "topic": "", "lesson": "", "questions": [], "idx": 0, "show_f": False})

    st.markdown('<div class="main-header"><h1>🏠 מתווך בקליק</h1></div>', unsafe_allow_html=True)

    if st.session_state.view == "login":
        name = st.text_input("הכנס שם מלא:")
        if st.button("כניסה"):
            if name: st.session_state.user = name; st.session_state.view = "menu"; st.rerun()

    elif st.session_state.view == "menu":
        st.write(f"### שלום {st.session_state.user}")
        selected = st.selectbox("בחר נושא:", ["בחר נושא..."] + [
            "חוק המתווכים", "חוק המקרקעין", "חוק החוזים", "חוק הגנת הצרכן", "מיסוי מקרקעין"
        ]) # שמתי רשימה קצרה לדוגמה, תשאיר את FULL_SYLLABUS שלך
        if selected != "בחר נושא...":
            st.session_state.topic = selected
            if st.button("📖 פתח שיעור"):
                st.session_state.lesson = ""; st.session_state.view = "lesson"; st.rerun()

    elif st.session_state.view == "lesson":
        st.subheader(f"📍 {st.session_state.topic}")
        if st.button("🏠 חזרה"): st.session_state.view = "menu"; st.rerun()
        
        # --- כאן קורה הקסם של ה-Streaming ---
        if not st.session_state.lesson:
            full_text = ""
            # מקום ריק לכתיבה
            holder = st.empty() 
            try:
                # מפעילים הזרמה (stream=True)
                response = model.generate_content(f"כתוב שיעור מפורט על {st.session_state.topic} למבחן המתווכים.", stream=True)
                for chunk in response:
                    full_text += chunk.text
                    # מציגים למשתמש את מה שנכתב עד עכשיו (בלי ה-Box כדי לא להיתקע)
                    holder.markdown(full_text + "▌") 
                
                st.session_state.lesson = full_text
                st.rerun() # מרעננים פעם אחת לסיום כדי לעטוף בתיבה המעוצבת
            except:
                st.error("תקלה בתקשורת.")
        else:
            # מציג את השיעור המוכן בתוך התיבה המעוצבת
            st.markdown(f'<div class="lesson-box">{st.session_state.lesson}</div>', unsafe_allow_html=True)
            if st.button("עבור לתרגול ✍️"):
                st.info("כאן נפעיל את הפונקציה fetch_quiz")

if __name__ == "__main__":
    main()
