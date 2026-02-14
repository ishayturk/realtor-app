import streamlit as st
import google.generativeai as genai
import json
import re

# ==========================================
# 1. הגדרות עיצוב (CSS) - נעול ויציב
# ==========================================
def apply_design():
    st.set_page_config(page_title="מתווך בקליק", layout="wide")
    st.markdown("""
    <style>
        /* כפיית RTL על כל המערכת */
        html, body, [data-testid="stAppViewContainer"], [data-testid="stVerticalBlock"] {
            direction: rtl !important;
            text-align: right !important;
        }
        
        /* כותרת עליונה מעוצבת */
        .main-header {
            text-align: center !important;
            background: linear-gradient(90deg, #1E88E5, #1565C0);
            color: white; padding: 20px; border-radius: 15px;
            margin-bottom: 25px; box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        
        /* תיבות תוכן ושיעור */
        .lesson-box, .feedback-box {
            background-color: #ffffff; padding: 25px; border-radius: 15px;
            border-right: 8px solid #1E88E5; box-shadow: 0 2px 12px rgba(0,0,0,0.08);
            line-height: 1.8; font-size: 1.1rem; margin-bottom: 20px;
        }

        /* כפתורים מותאמים לנייד */
        .stButton button {
            width: 100% !important; height: 3.5em !important;
            border-radius: 12px !important; font-weight: bold !important;
            font-size: 1.1rem !important; margin-top: 10px;
        }
        
        /* יישור שאלון רדיו */
        div[role="radiogroup"] { direction: rtl !important; text-align: right !important; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. תוכן וסילבוס
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
# 3. לוגיקה ופונקציות AI
# ==========================================
def init_gemini():
    if "GEMINI_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        return genai.GenerativeModel('gemini-2.0-flash')
    return None

def generate_content(model, prompt, is_json=False):
    try:
        resp = model.generate_content(prompt)
        text = resp.text
        if is_json:
            match = re.search(r'\[.*\]', text.replace("'", '"'), re.DOTALL)
            return json.loads(match.group()) if match else None
        return text
    except Exception as e:
        st.error(f"תקלה בתקשורת: {e}")
        return None

# ==========================================
# 4. ניהול דפי האפליקציה
# ==========================================
def main():
    apply_design()
    model = init_gemini()
    
    if "view" not in st.session_state:
        st.session_state.update({"view": "login", "user": "", "topic": "", "lesson": "", "questions": [], "idx": 0, "ans": {}, "show_f": False})

    # כותרת קבועה
    st.markdown('<div class="main-header"><h1>🏠 מתווך בקליק</h1><p>הדרך המהירה לרישיון</p></div>', unsafe_allow_html=True)

    # דף כניסה
    if st.session_state.view == "login":
        name = st.text_input("שם מלא:")
        if st.button("התחל ללמוד"):
            if name: st.session_state.user = name; st.session_state.view = "menu"; st.rerun()

    # דף תפריט
    elif st.session_state.view == "menu":
        st.write(f"### שלום {st.session_state.user}, בחר נושא:")
        selected = st.selectbox("הסילבוס המלא:", ["בחר..."] + FULL_SYLLABUS)
        if selected != "בחר...":
            st.session_state.topic = selected
            c1, c2 = st.columns(2)
            with c1:
                if st.button("📖 שיעור"):
                    content = generate_content(model, f"כתוב שיעור מפורט למבחן המתווכים על {selected} בעברית.")
                    if content: st.session_state.lesson = content; st.session_state.view = "lesson"; st.rerun()
            with c2:
                if st.button("✍️ תרגול"):
                    qs = generate_content(model, f"Create 10 MCQs in HEBREW about {selected}. Return ONLY JSON array: [{{'q':'','options':['','','',''],'correct':0,'explanation':''}}]", True)
                    if qs: st.session_state.questions = qs; st.session_state.view = "quiz"; st.session_state.idx = 0; st.session_state.show_f = False; st.rerun()

    # דף שיעור
    elif st.session_state.view == "lesson":
        st.subheader(st.session_state.topic)
        if st.button("🏠 חזרה לתפריט"): st.session_state.view = "menu"; st.rerun()
        st.markdown(f'<div class="lesson-box">{st.session_state.lesson}</div>', unsafe_allow_html=True)
        if st.button("עבור לתרגול שאלות ✍️"):
            qs = generate_content(model, f"Create 10 MCQs in HEBREW about {st.session_state.topic}. Return ONLY JSON array: [{{'q':'','options':['','','',''],'correct':0,'explanation':''}}]", True)
            if qs: st.session_state.questions = qs; st.session_state.view = "quiz"; st.session_state.idx = 0; st.session_state.show_f = False; st.rerun()

    # דף שאלון
    elif st.session_state.view == "quiz":
        idx = st.session_state.idx
        q = st.session_state.questions[idx]
        st.subheader(f"שאלה {idx+1} מתוך 10")
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
            st.markdown(f'<div class="feedback-box"><b>הסבר:</b> {q["explanation"]}</div>', unsafe_allow_html=True)
            if idx < 9:
                if st.button("הבא ➡️"): st.session_state.idx += 1; st.session_state.show_f = False; st.rerun()
            else:
                st.balloons()
                if st.button("סיום"): st.session_state.view = "menu"; st.rerun()

if __name__ == "__main__":
    main()
