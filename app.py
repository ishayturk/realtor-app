import streamlit as st
import google.generativeai as genai
import json
import re

# 1. הגדרות עיצוב מתקדמות - דגש על רספונסיביות (ניידים)
st.set_page_config(page_title="מתווך בקליק", layout="wide")

st.markdown("""
<style>
    /* הגדרות בסיס RTL */
    .stApp { direction: rtl !important; text-align: right !important; }
    [data-testid="stSidebar"] { direction: rtl !important; text-align: right !important; min-width: 250px; }
    
    /* התאמה לניידים - כפתורי רדיו גדולים יותר */
    div[data-testid="stRadio"] > label {
        padding: 10px;
        background-color: #f9f9f9;
        border-radius: 8px;
        margin-bottom: 5px;
        border: 1px solid #eee;
    }

    /* לוח ניווט השאלות בסיידבר - מותאם ללחיצה בנייד */
    .nav-container {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        justify-content: center;
        padding: 10px 0;
    }
    
    /* כפתורי ניווט תחתונים רחבים בנייד */
    @media (max-width: 768px) {
        .stButton button {
            width: 100% !important;
            height: 50px;
            font-size: 18px !important;
        }
    }

    .feedback-box { padding: 15px; border-radius: 10px; margin: 10px 0; line-height: 1.6; }
    .law-source-tag { 
        display: inline-block; background: #e1f5fe; color: #01579b; 
        padding: 4px 12px; border-radius: 15px; font-weight: bold; font-size: 0.85em;
    }
</style>
""", unsafe_allow_html=True)

# 2. ניהול State
if "view_mode" not in st.session_state:
    st.session_state.update({
        "view_mode": "login", "user_name": "", "current_topic": "",
        "exam_questions": [], "user_answers": {}, "current_exam_idx": 0, "show_feedback": False
    })

if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-2.0-flash')

# 3. פונקציות עזר
def start_exam():
    prompt = "Create 25 Hebrew multiple choice questions for Israeli Real Estate exam. Return ONLY JSON array: [{'q':'','options':['','','',''],'correct':0,'explanation':'','source':''}]"
    with st.spinner("מכין סימולציה..."):
        try:
            resp = model.generate_content(prompt)
            data = json.loads(re.search(r'\[.*\]', resp.text, re.DOTALL).group())
            st.session_state.update({
                "exam_questions": data, "user_answers": {}, "current_exam_idx": 0, 
                "view_mode": "full_exam_mode", "show_feedback": False
            })
        except: st.error("נסה שוב בעוד רגע.")

# 4. סיידבר - בנייד הוא "מתחבא" תחת כפתור החץ
with st.sidebar:
    st.title("🏠 מתווך בקליק")
    if st.session_state.user_name:
        st.write(f"היי, {st.session_state.user_name}")
        st.markdown("---")
        
        if st.button("🏆 התחל מבחן חדש"):
            start_exam(); st.rerun()
            
        if st.session_state.view_mode == "full_exam_mode" and st.session_state.exam_questions:
            st.write("📍 **מעבר מהיר לשאלה:**")
            # יצירת רשת כפתורי ניווט בסיידבר
            for row in range(0, 25, 5):
                cols = st.columns(5)
                for i in range(5):
                    idx = row + i
                    if idx < 25:
                        with cols[i]:
                            # סימון ויזואלי לשאלה שנענתה
                            label = f"{idx+1}"
                            if idx in st.session_state.user_answers:
                                label = f"{idx+1}✓"
                            
                            if st.button(label, key=f"nav_{idx}", use_container_width=True, 
                                         type="primary" if idx == st.session_state.current_exam_idx else "secondary"):
                                st.session_state.current_exam_idx = idx
                                st.session_state.show_feedback = False
                                st.rerun()

# 5. דף המבחן
if st.session_state.view_mode == "login":
    name = st.text_input("הכנס שם מלא:")
    if st.button("התחל"):
        if name: st.session_state.user_name = name; st.session_state.view_mode = "setup"; st.rerun()

elif st.session_state.view_mode == "setup":
    st.header("ברוך הבא!")
    st.write("בחר נושא לימוד מהסילבוס או התחל מבחן מלא מהתפריט הצידי.")
    # (כאן תבוא רשימת הנושאים שהגדרנו קודם)

elif st.session_state.view_mode == "full_exam_mode":
    idx = st.session_state.current_exam_idx
    q = st.session_state.exam_questions[idx]
    
    # כותרת שאלה
    st.caption(f"שאלה {idx + 1} מתוך 25")
    st.write(f"### {q['q']}")
    
    # בחירת תשובה
    saved_ans = st.session_state.user_answers.get(idx)
    choice = st.radio("בחר את התשובה הנכונה ביותר:", q['options'], 
                      key=f"q_radio_{idx}", 
                      index=q['options'].index(saved_ans) if saved_ans else None)
    
    if choice:
        st.session_state.user_answers[idx] = choice
        st.session_state.show_feedback = True

    # הצגת הסבר וחוק רק אחרי בחירה
    if st.session_state.show_feedback and idx in st.session_state.user_answers:
        is_correct = (q['options'].index(choice) == q['correct'])
        if is_correct:
            st.success("תשובה נכונה!")
        else:
            st.error(f"לא מדויק. התשובה הנכונה היא: {q['options'][q['correct']]}")
        
        st.markdown(f"""
        <div class="feedback-box">
            <span class="law-source-tag">📍 {q['source']}</span><br><br>
            {q['explanation']}
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    
    # ניווט תחתון רספונסיבי
    col_prev, col_next = st.columns(2)
    with col_prev:
        if st.button("⬅️ שאלה קודמת", disabled=(idx == 0)):
            st.session_state.current_exam_idx -= 1
            st.session_state.show_feedback = False
            st.rerun()
    with col_next:
        if idx < 24:
            if st.button("שאלה הבאה ➡️"):
                st.session_state.current_exam_idx += 1
                st.session_state.show_feedback = False
                st.rerun()
        else:
            if st.button("🏁 סיים מבחן וקבל ציון"):
                st.session_state.view_mode = "summary"; st.rerun()
