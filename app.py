import streamlit as st
import google.generativeai as genai
import json
import re

# ==========================================
# 1. עיצוב חזותי (הלוגו והסטייל שאהבת)
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
            color: white; padding: 25px; border-radius: 15px; margin-bottom: 25px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        .lesson-box {
            background-color: #ffffff; padding: 25px; border-radius: 15px;
            border-right: 8px solid #1E88E5; box-shadow: 0 2px 12px rgba(0,0,0,0.08);
            line-height: 1.8; font-size: 1.1rem; direction: rtl !important;
        }
        .stButton button { width: 100% !important; height: 3.5em !important; border-radius: 12px !important; font-weight: bold !important; }
        div[role="radiogroup"] { direction: rtl !important; text-align: right !important; }
        [data-testid="stMarkdownContainer"] { direction: rtl !important; text-align: right !important; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. הסילבוס המלא (16 נושאים)
# ==========================================
FULL_SYLLABUS = [
    "חוק המתווכים במקרקעין והתקנות", "חוק המקרקעין", "חוק המכר (דירות)",
    "חוק החוזים", "חוק הגנת הצרכן", "חוק הגנת הדייר",
    "חוק התכנון והבנייה", "חוק מיסוי מקרקעין", "חוק העונשין",
    "חוק שמאי מקרקעין", "חוק הירושה", "חוק יחסי ממון",
    "חוק איסור הלבנת הון", "פקודת הנזיקין", "מושגי יסוד בכלכלה", "רשות מקרקעי ישראל"
]

# ==========================================
# 3. מנוע AI (Gemini)
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
        # ניקוי אגרסיבי של הטקסט כדי למצוא רק את ה-JSON
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
    
    # אתחול Session State
    if "view" not in st.session_state:
        st.session_state.update({"view": "login", "user": "", "topic": "", "lesson": "", "questions": [], "idx": 0, "show_f": False})

    # לוגו וכותרת
    st.markdown("""
        <div class="main-header">
            <h1 style='margin:0;'>🏠 מתווך בקליק</h1>
            <p style='margin:0; opacity:0.9;'>גרסה 100 - הלמידה מתחילה כאן</p>
        </div>
    """, unsafe_allow_html=True)

    # --- דף כניסה ---
    if st.session_state.view == "login":
        name = st.text_input("הכנס שם מלא:")
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
            c1, c2 = st.columns(2)
            with c1:
                if st.button("📖 פתח שיעור"):
                    st.session_state.view = "lesson"
                    st.session_state.lesson = "" 
                    st.rerun()
            with c2:
                if st.button("✍️ תרגול שאלות"):
                    with st.spinner("מכין שאלות..."):
                        qs = fetch_quiz(model, selected)
                        if qs:
                            st.session_state.questions = qs
                            st.session_state.view = "quiz"
                            st.session_state.idx = 0
                            st.session_state.show_f = False
                            st.rerun()
                        else: st.error("נסה שוב, ה-AI היה עסוק.")

    # --- דף שיעור ---
    elif st.session_state.view == "lesson":
        st.subheader(f"📍 {st.session_state.topic}")
        if st.button("🏠 חזרה לתפריט"): st.session_state.view = "menu"; st.rerun()
        
        lesson_placeholder = st.empty()
        if not st.session_state.lesson:
            full_text = ""
            with st.spinner("השיעור נכתב ברגע זה..."):
                response = model.generate_content(f"כתוב שיעור מפורט למבחן המתווכים על {st.session_state.topic} בעברית.", stream=True)
                for chunk in response:
                    full_text += chunk.text
                    lesson_placeholder.markdown(f'<div class="lesson-box">{full_text}</div>', unsafe_allow_html=True)
                st.session_state.lesson = full_text
        else:
            lesson_placeholder.markdown(f'<div class="lesson-box">{st.session_state.lesson}</div>', unsafe_allow_html=True)
        
        if st.button("עבור לתרגול שאלות ✍️"):
            with st.spinner("מייצר שאלות..."):
                qs = fetch_quiz(model, st.session_state.topic)
                if qs:
                    st.session_state.questions = qs
                    st.session_state.view = "quiz"
                    st.session_state.idx = 0
                    st.session_state.show_f = False
                    st.rerun()

    # --- דף שאלון ---
    elif st.session_state.view == "quiz":
        idx = st.session_state.idx
        q = st.session_state.questions[idx]
        st.subheader(f"תרגול: {st.session_state.topic} ({idx+1}/10)")
        
        if st.button("🏠 חזרה לתפריט"): st.session_state.view = "menu"; st.rerun()
        
        st.info(q['q'])
        choice = st.radio("בחר תשובה:", q['options'], key=f"r_{idx}")
        
        if st.button("בדוק תשובה ✅"):
            st.session_state.show_f = True
        
        if st.session_state.show_f:
            correct = q['options'][q['correct']]
            if choice == correct: st.success("נכון מאוד!")
            else: st.error(f"לא נכון. התשובה הנכונה היא: {correct}")
            st.markdown(f'<div class="lesson-box"><b>הסבר משפטי:</b><br>{q["explanation"]}</div>', unsafe_allow_html=True)
            
            if idx < 9:
                if st.button("לשאלה הבאה ➡️"):
                    st.session_state.idx += 1
                    st.session_state.show_f = False
                    st.rerun()
            else:
                st.balloons()
                if st.button("🏁 סיום וחזרה לתפריט"): st.session_state.view = "menu"; st.rerun()

if __name__ == "__main__":
    main()
