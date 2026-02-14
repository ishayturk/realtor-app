import streamlit as st
import google.generativeai as genai
import json
import re
import time
import random

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
            color: white !important; padding: 20px; border-radius: 15px; margin-bottom: 20px;
        }
        .lesson-box {
            background-color: #ffffff !important; color: #1a1a1a !important; 
            padding: 25px; border-radius: 15px; border-right: 8px solid #1E88E5; 
            box-shadow: 0 2px 12px rgba(0,0,0,0.1); line-height: 1.8; font-size: 1.1rem; 
            direction: rtl !important; text-align: right !important;
        }
        [data-testid="stSidebar"] { direction: rtl !important; background-color: #f8f9fa; }
        .stButton button { width: 100% !important; border-radius: 12px !important; font-weight: bold !important; }
        .timer-text {
            font-size: 24px; font-weight: bold; color: #d32f2f; text-align: center;
            background: #ffebee; padding: 10px; border-radius: 10px; border: 1px solid #d32f2f;
        }
        .score-box {
            background-color: #e3f2fd; padding: 15px; border-radius: 10px; text-align: center; font-weight: bold; margin-bottom: 10px;
        }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. סילבוס מלא
# ==========================================
FULL_SYLLABUS = [
    "חוק המתווכים במקרקעין והתקנות", "חוק המקרקעין", "חוק המכר (דירות)",
    "חוק החוזים", "חוק הגנת הצרכן", "חוק הגנת הדייר",
    "חוק התכנון והבנייה", "חוק מיסוי מקרקעין", "חוק העונשין",
    "חוק שמאי מקרקעין", "חוק הירושה", "חוק יחסי ממון",
    "חוק איסור הלבנת הון", "פקודת הנזיקין", "מושגי יסוד בכלכלה", "רשות מקרקעי ישראל"
]

# ==========================================
# 3. מנוע AI ועזרים
# ==========================================
def get_mock_exam():
    exam_qs = []
    for i in range(1, 26):
        exam_qs.append({
            "id": i, "q": f"שאלה {i}: בהתאם לחוק המקרקעין, מהו הדין במקרה של עסקה נוגדת?",
            "options": ["הראשון בזמן זוכה תמיד", "השני בזמן זוכה אם פעל בתום לב ובתמורה ורשם", "העסקה בטלה", "יש לפנות לבית המשפט"],
            "correct": 1, "explanation": "סעיף 9 לחוק המקרקעין קובע את סדרי העדיפויות."
        })
    return exam_qs

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
# 4. ניהול האפליקציה
# ==========================================
def main():
    apply_design()
    model = init_gemini()
    
    if "view" not in st.session_state:
        st.session_state.update({
            "view": "login", "user": "", "topic": "", "lesson": "", 
            "questions": [], "idx": 0, "show_f": False, "correct_answers": 0,
            "exam_active": False, "exam_questions": [], "user_answers": {}, 
            "start_time": None
        })

    st.markdown('<div class="main-header"><h1 style="margin:0; color: white;">🏠 מתווך בקליק</h1></div>', unsafe_allow_html=True)

    # --- דף כניסה ---
    if st.session_state.view == "login":
        name = st.text_input("הכנס שם מלא:", key="login_name")
        if st.button("כניסה למערכת"):
            if name: st.session_state.user = name; st.session_state.view = "menu"; st.rerun()

    # --- תפריט ראשי ---
    elif st.session_state.view == "menu":
        st.write(f"### שלום {st.session_state.user}")
        col1, col2 = st.columns(2)
        with col1:
            st.info("📚 לימוד לפי נושאים")
            selected = st.selectbox("בחר נושא:", ["בחר נושא..."] + FULL_SYLLABUS)
            if selected != "בחר נושא...":
                st.session_state.topic = selected
                if st.button("📖 פתח שיעור"):
                    st.session_state.lesson = ""; st.session_state.view = "lesson"; st.rerun()
        with col2:
            st.warning("⏱️ סימולציית מבחן רשמי")
            if st.button("🚀 התחל מבחן רישוי"):
                st.session_state.exam_questions = get_mock_exam()
                st.session_state.user_answers = {}; st.session_state.idx = 0; st.session_state.start_time = time.time(); st.session_state.view = "exam"; st.rerun()

    # --- שאלון קצר (סוף נושא) ---
    elif st.session_state.view == "quiz":
        idx = st.session_state.idx
        q = st.session_state.questions[idx]
        st.subheader(f"תרגול: {st.session_state.topic}")
        
        # תצוגת התקדמות
        st.markdown(f"""<div class="score-box">שאלה {idx+1} מתוך 10 | נכונות עד כה: {st.session_state.correct_answers}</div>""", unsafe_allow_html=True)

        if st.button("🏠 חזרה"): st.session_state.view = "menu"; st.rerun()
        
        st.info(q['q'])
        choice = st.radio("בחר תשובה:", q['options'], key=f"q_reg_{idx}", index=None)
        
        if st.button("בדוק תשובה ✅"):
            if choice: st.session_state.show_f = True
        
        if st.session_state.show_f:
            correct_text = q['options'][q['correct']]
            if choice == correct_text:
                if f"scored_{idx}" not in st.session_state: # מונע ספירה כפולה אם לוחצים שוב
                    st.session_state.correct_answers += 1
                    st.session_state[f"scored_{idx}"] = True
                st.success("נכון!")
            else:
                st.error(f"טעות. התשובה היא: {correct_text}")
            
            st.markdown(f'<div class="lesson-box"><b>הסבר:</b><br>{q["explanation"]}</div>', unsafe_allow_html=True)
            
            if idx < 9:
                if st.button("שאלה הבאה ➡️"):
                    st.session_state.idx += 1; st.session_state.show_f = False; st.rerun()
            else:
                st.balloons()
                final_score = st.session_state.correct_answers * 10
                st.markdown(f"### 🎉 כל הכבוד! סיימת את השאלון.")
                st.markdown(f"#### הציון הסופי שלך: {final_score}/100 ({st.session_state.correct_answers} מתוך 10)")
                if st.button("סיום וחזרה לתפריט"):
                    # איפוס מונים לשאלון הבא
                    for key in list(st.session_state.keys()):
                        if key.startswith("scored_"): del st.session_state[key]
                    st.session_state.correct_answers = 0
                    st.session_state.view = "menu"; st.rerun()

    # --- מבחן רישוי (אותו קוד מהגרסה הקודמת) ---
    elif st.session_state.view == "exam":
        elapsed = time.time() - st.session_state.start_time
        remaining = max(0, 90 * 60 - elapsed)
        mins, secs = divmod(int(remaining), 60)
        st.markdown(f'<div class="timer-text">⏱️ זמן נותר: {mins:02d}:{secs:02d}</div>', unsafe_allow_html=True)
        
        st.sidebar.title("📌 ניווט שאלות")
        for row in range(5):
            cols = st.sidebar.columns(5)
            for col in range(5):
                q_num = row * 5 + col + 1
                label = f"{q_num} ✅" if q_num in st.session_state.user_answers else f"{q_num}"
                if cols[col].button(label, key=f"nav_{q_num}"):
                    st.session_state.idx = q_num - 1; st.rerun()
        
        curr_idx = st.session_state.idx
        q = st.session_state.exam_questions[curr_idx]
        st.subheader(f"שאלה {curr_idx + 1} מתוך 25")
        st.info(q['q'])
        
        prev_ans = st.session_state.user_answers.get(curr_idx + 1, None)
        choice = st.radio("בחר תשובה:", q['options'], key=f"exam_q_{curr_idx}", index=None if prev_ans is None else q['options'].index(prev_ans))
        if choice: st.session_state.user_answers[curr_idx + 1] = choice

        c1, c2, c3 = st.columns([1,1,1])
        with c1:
            if curr_idx > 0:
                if st.button("⬅️ הקודם"): st.session_state.idx -= 1; st.rerun()
        with c2:
            if st.button("🏠 תפריט"): st.session_state.view = "menu"; st.rerun()
        with c3:
            if curr_idx < 24:
                if st.button("הבא ➡️"): st.session_state.idx += 1; st.rerun()
            else:
                if st.button("🏁 הגש מבחן"): st.session_state.view = "exam_results"; st.rerun()

    # --- דף שיעור ---
    elif st.session_state.view == "lesson":
        st.subheader(f"📍 {st.session_state.topic}")
        if st.button("🏠 חזרה"): st.session_state.view = "menu"; st.rerun()
        lesson_placeholder = st.empty()
        if not st.session_state.lesson:
            full_text = ""
            with st.spinner("השיעור נכתב..."):
                response = model.generate_content(f"כתוב שיעור מפורט על {st.session_state.topic} למבחן המתווכים.", stream=True)
                for chunk in response:
                    full_text += chunk.text
                    lesson_placeholder.markdown(f'<div class="lesson-box">{full_text}▌</div>', unsafe_allow_html=True)
                st.session_state.lesson = full_text; st.rerun()
        else:
            lesson_placeholder.markdown(f'<div class="lesson-box">{st.session_state.lesson}</div>', unsafe_allow_html=True)
        
        if st.button("עבור לתרגול שאלות ✍️"):
            with st.spinner("מכין שאלות..."):
                qs = fetch_quiz(model, st.session_state.topic)
                if qs:
                    st.session_state.questions = qs
                    st.session_state.correct_answers = 0 # איפוס מונה
                    st.session_state.view = "quiz"; st.session_state.idx = 0; st.session_state.show_f = False; st.rerun()

    # --- תוצאות מבחן רישוי ---
    elif st.session_state.view == "exam_results":
        st.header("🏁 סיכום מבחן רישוי")
        # לוגיקה לסיכום המבחן הגדול... (כפי שהיה בגרסה הקודמת)
        st.button("חזרה לתפריט", on_click=lambda: st.session_state.update({"view": "menu"}))

if __name__ == "__main__":
    main()
