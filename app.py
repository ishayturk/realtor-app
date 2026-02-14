import streamlit as st
import google.generativeai as genai
import json
import re

# ==========================================
# 1. עיצוב ויישור - תיקון RTL עמוק
# ==========================================
def apply_design():
    st.set_page_config(page_title="מתווך בקליק", layout="wide")
    st.markdown("""
    <style>
        /* כפיית RTL על כל הגוף והקונטיינרים */
        html, body, [data-testid="stAppViewContainer"], .main, .block-container {
            direction: rtl !important;
            text-align: right !important;
        }
        
        /* תיקון ספציפי לטקסטים שנוצרים על ידי ה-AI */
        [data-testid="stMarkdownContainer"] {
            direction: rtl !important;
            text-align: right !important;
        }

        .main-header {
            text-align: center !important;
            background: linear-gradient(90deg, #1E88E5, #1565C0);
            color: white; padding: 20px; border-radius: 15px;
            margin-bottom: 25px;
        }
        
        .lesson-box {
            background-color: #ffffff; padding: 25px; border-radius: 15px;
            border-right: 8px solid #1E88E5; box-shadow: 0 2px 12px rgba(0,0,0,0.08);
            line-height: 1.8; font-size: 1.1rem;
        }

        .stButton button {
            width: 100% !important; height: 3.5em !important;
            border-radius: 12px !important; font-weight: bold !important;
        }
        
        /* יישור תיבות בחירה ורדיו */
        div[role="radiogroup"], .stSelectbox { direction: rtl !important; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. רשימת נושאים
# ==========================================
FULL_SYLLABUS = [
    "חוק המתווכים במקרקעין והתקנות", "חוק המקרקעין", "חוק המכר (דירות)",
    "חוק החוזים", "חוק הגנת הצרכן", "חוק הגנת הדייר",
    "חוק התכנון והבנייה", "חוק מיסוי מקרקעין", "חוק העונשין",
    "חוק שמאי מקרקעין", "חוק הירושה", "חוק יחסי ממון",
    "חוק איסור הלבנת הון", "פקודת הנזיקין", "מושגי יסוד בכלכלה",
    "רשות מקרקעי ישראל"
]

# ==========================================
# 3. לוגיקה
# ==========================================
def init_gemini():
    if "GEMINI_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        return genai.GenerativeModel('gemini-2.0-flash')
    return None

def main():
    apply_design()
    model = init_gemini()
    
    if "view" not in st.session_state:
        st.session_state.update({"view": "login", "user": "", "topic": "", "lesson": "", "questions": [], "idx": 0, "ans": {}, "show_f": False})

    st.markdown('<div class="main-header"><h1>🏠 מתווך בקליק</h1><p>הדרך המהירה לרישיון</p></div>', unsafe_allow_html=True)

    if st.session_state.view == "login":
        name = st.text_input("הכנס שם מלא:")
        if st.button("כניסה למערכת"):
            if name: st.session_state.user = name; st.session_state.view = "menu"; st.rerun()

    elif st.session_state.view == "menu":
        st.write(f"### שלום {st.session_state.user}")
        selected = st.selectbox("בחר נושא ללמוד:", ["בחר נושא..."] + FULL_SYLLABUS)
        
        if selected != "בחר נושא...":
            st.session_state.topic = selected
            c1, c2 = st.columns(2)
            with c1:
                if st.button("📖 קרא שיעור"):
                    with st.spinner("מכין את השיעור..."):
                        resp = model.generate_content(f"כתוב שיעור מפורט בעברית למבחן המתווכים על {selected}.")
                        if resp:
                            st.session_state.lesson = resp.text
                            st.session_state.view = "lesson"
                            st.rerun()
            with c2:
                if st.button("✍️ תרגול שאלות"):
                    with st.spinner("מייצר שאלות..."):
                        prompt = f"Create 10 MCQs in HEBREW about {selected}. Return ONLY JSON array: [{{'q':'','options':['','','',''],'correct':0,'explanation':''}}]"
                        resp = model.generate_content(prompt)
                        match = re.search(r'\[.*\]', resp.text.replace("'", '"'), re.DOTALL)
                        if match:
                            st.session_state.questions = json.loads(match.group())
                            st.session_state.view = "quiz"; st.session_state.idx = 0; st.session_state.show_f = False; st.rerun()

    elif st.session_state.view == "lesson":
        st.subheader(st.session_state.topic)
        if st.button("🏠 חזרה לתפריט"): st.session_state.view = "menu"; st.rerun()
        # עטיפה של השיעור בתיבה מיושרת לימין
        st.markdown(f'<div class="lesson-box">{st.session_state.lesson}</div>', unsafe_allow_html=True)
        if st.button("עבור לתרגול ✍️"):
            st.session_state.view = "menu" # פשטות לצורך טעינה מחדש של שאלות
            st.rerun()

    elif st.session_state.view == "quiz":
        idx = st.session_state.idx
        q = st.session_state.questions[idx]
        st.subheader(f"שאלה {idx+1}/10")
        if st.button("🏠 תפריט"): st.session_state.view = "menu"; st.rerun()
        
        st.info(q['q'])
        choice = st.radio("בחר תשובה:", q['options'], key=f"r_{idx}")
        
        if st.button("בדוק תשובה ✅"):
            st.session_state.show_f = True
            st.session_state.ans[idx] = choice

        if st.session_state.show_f:
            correct = q['options'][q['correct']]
            if choice == correct: st.success("נכון!")
            else: st.error(f"טעות. הנכון: {correct}")
            st.markdown(f'<div class="lesson-box"><b>הסבר:</b> {q["explanation"]}</div>', unsafe_allow_html=True)
            if idx < 9:
                if st.button("לשאלה הבאה ➡️"): st.session_state.idx += 1; st.session_state.show_f = False; st.rerun()
            else:
                if st.button("סיום"): st.session_state.view = "menu"; st.rerun()

if __name__ == "__main__":
    main()
