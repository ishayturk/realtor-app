import streamlit as st
import google.generativeai as genai
import json
import re

# ==========================================
# 1. עיצוב חזותי - נקי ויציב
# ==========================================
def apply_design():
    st.set_page_config(page_title="מתווך בקליק", layout="wide")
    st.markdown("""
    <style>
        html, body, [data-testid="stAppViewContainer"], .main, .block-container {
            direction: rtl !important; 
            text-align: right !important;
        }
        .main-header {
            text-align: center !important;
            background: linear-gradient(90deg, #1E88E5, #1565C0);
            color: white !important; 
            padding: 20px; 
            border-radius: 15px; 
            margin-bottom: 20px;
        }
        .lesson-box {
            background-color: #ffffff !important; 
            color: #1a1a1a !important; 
            padding: 25px; 
            border-radius: 15px;
            border-right: 8px solid #1E88E5; 
            box-shadow: 0 2px 12px rgba(0,0,0,0.1);
            line-height: 1.8; 
            font-size: 1.1rem; 
            direction: rtl !important;
            text-align: right !important;
            margin-bottom: 20px;
        }
        .stButton button { 
            width: 100% !important; 
            height: 3.5em !important; 
            border-radius: 12px !important; 
            font-weight: bold !important; 
        }
        [data-testid="stMarkdownContainer"] { 
            direction: rtl !important; 
            text-align: right !important; 
        }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. הסילבוס המלא (16 נושאים - בדוק)
# ==========================================
FULL_SYLLABUS = [
    "חוק המתווכים במקרקעין והתקנות", "חוק המקרקעין", "חוק המכר (דירות)",
    "חוק החוזים", "חוק הגנת הצרכן", "חוק הגנת הדייר",
    "חוק התכנון והבנייה", "חוק מיסוי מקרקעין", "חוק העונשין",
    "חוק שמאי מקרקעין", "חוק הירושה", "חוק יחסי ממון",
    "חוק איסור הלבנת הון", "פקודת הנזיקין", "מושגי יסוד בכלכלה", "רשות מקרקעי ישראל"
]

# ==========================================
# 3. מנוע AI
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
        text = resp.text.strip()
        match = re.search(r'\[\s*\{.*\}\s*\]', text, re.DOTALL)
        if match:
            return json.loads(match.group())
        return None
    except:
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

    # אתחול ה-Session State בזהירות
    if "view" not in st.session_state:
        st.session_state.view = "login"
    if "user" not in st.session_state:
        st.session_state.user = ""
    if "topic" not in st.session_state:
        st.session_state.topic = ""
    if "lesson" not in st.session_state:
        st.session_state.lesson = ""
    if "questions" not in st.session_state:
        st.session_state.questions = []
    if "idx" not in st.session_state:
        st.session_state.idx = 0
    if "show_f" not in st.session_state:
        st.session_state.show_f = False

    # כותרת קבועה
    st.markdown("""
        <div class="main-header">
            <h1 style='margin:0; color: white;'>🏠 מתווך בקליק</h1>
            <p style='margin:0; opacity:0.9; color: white;'>גרסה 104 - יציבה ובדוקה</p>
        </div>
    """, unsafe_allow_html=True)

    # --- דף כניסה ---
    if st.session_state.view == "login":
        name = st.text_input("הכנס שם מלא:", key="name_input")
        if st.button("כניסה למערכת"):
            if name: 
                st.session_state.user = name
                st.session_state.view = "menu"
                st.rerun()

    # --- תפריט ראשי ---
    elif st.session_state.view == "menu":
        st.write(f"### שלום {st.session_state.user}, מה נלמד היום?")
        selected = st.selectbox("בחר נושא ללמוד:", ["בחר נושא..."] + FULL_SYLLABUS)
        
        if selected != "בחר נושא...":
            st.session_state.topic = selected
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📖 פתח שיעור"):
                    st.session_state.lesson = "" 
                    st.session_state.view = "lesson"
                    st.rerun()
            with col2:
                if st.button("✍️ תרגול שאלות"):
                    with st.spinner("מכין שאלות..."):
                        qs = fetch_quiz(model, selected)
                        if qs:
                            st.session_state.questions = qs
                            st.session_state.view = "quiz"
                            st.session_state.idx = 0
                            st.session_state.show_f = False
                            st.rerun()

    # --- דף שיעור ---
    elif st.session_state.view == "lesson":
        st.subheader(f"📍 {st.session_state.topic}")
        if st.button("🏠 חזרה לתפריט"):
            st.session_state.view = "menu"
            st.rerun()
        
        if not st.session_state.lesson:
            full_text = ""
            placeholder = st.empty()
            with st.spinner("השיעור נכתב..."):
                try:
                    response = model.generate_content(f"כתוב שיעור מפורט למבחן המתווכים על {st.session_state.topic} בעברית.", stream=True)
                    for chunk in response:
                        full_text += chunk.text
                        placeholder.markdown(full_text + "▌")
                    st.session_state.lesson = full_text
                    # במקום rerun, פשוט מציגים את התוצאה הסופית בתוך ה-box
                    placeholder.markdown(f'<div class="lesson-box">{st.session_state.lesson}</div>', unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"שגיאה ביצירת שיעור: {e}")
        else:
            st.markdown(f'<div class="lesson-box">{st.session_state.lesson}</div>', unsafe_allow_html=True)
        
        if st.button("עבור לתרגול שאלות ✍️"):
            st.session_state.view = "menu" # מחזיר לתפריט כדי שיוכל ללחוץ על תרגול
            st.rerun()

    # --- דף שאלון ---
    elif st.session_state.view == "quiz":
        idx = st.session_state.idx
        if not st.session_state.questions:
             st.session_state.view = "menu"
             st.rerun()
             
        q = st.session_state.questions[idx]
        st.subheader(f"תרגול: {st.session_state.topic} ({idx+1}/10)")
        
        if st.button("🏠 חזרה לתפריט"):
            st.session_state.view = "menu"
            st.rerun()
        
        st.info(q['q'])
        choice = st.radio("בחר תשובה:", q['options'], key=f"q_{idx}")
        
        if st.button("בדוק תשובה ✅"):
            st.session_state.show_f = True
        
        if st.session_state.show_f:
            correct_idx = q['correct']
            correct_text = q['options'][correct_idx]
            if choice == correct_text:
                st.success("נכון מאוד!")
            else:
                st.error(f"לא נכון. התשובה הנכונה: {correct_text}")
            
            st.markdown(f'<div class="lesson-box"><b>הסבר:</b><br>{q["explanation"]}</div>', unsafe_allow_html=True)
            
            if idx < 9:
                if st.button("לשאלה הבאה ➡️"):
                    st.session_state.idx += 1
                    st.session_state.show_f = False
                    st.rerun()
            else:
                st.balloons()
                if st.button("🏁 סיום"):
                    st.session_state.view = "menu"
                    st.rerun()

if __name__ == "__main__":
    main()
