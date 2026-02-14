import streamlit as st
import google.generativeai as genai
import re
import time

# 1. הגדרות ועיצוב
st.set_page_config(page_title="מתווך בקליק", layout="wide")

st.markdown("""
<style>
direction: rtl; text-align: right;
.main { direction: rtl; text-align: right; }
.stRadio > label { width: 100%; text-align: right; }
.summary-card { border: 1px solid #ddd; padding: 15px; border-radius: 10px; margin-bottom: 10px; background-color: #f9f9f9; }
.correct-ans { color: #28a745; font-weight: bold; }
.wrong-ans { color: #dc3545; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# 2. ניהול Session State
for k, v in {
    "view_mode": "login", "user_name": "", "current_topic": "",
    "full_exam_data": [], "full_exam_ready": False,
    "lesson_data": "", "lesson_quiz_data": [], "lesson_quiz_ready": False,
    "current_exam_idx": 0, "exam_answers": {}, "exam_start_time": None, "exam_finished": False
}.items():
    if k not in st.session_state: st.session_state[k] = v

if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-2.0-flash')

def parse_quiz(text):
    qs = []
    blocks = re.split(r"\[START_Q\]", text)[1:]
    for b in blocks:
        try:
            q = re.search(r"\[QUESTION\](.*?)\[OPTIONS\]", b, re.DOTALL).group(1).strip()
            opts = re.search(r"\[OPTIONS\](.*?)\[ANSWER\]", b, re.DOTALL).group(1).strip().split('\n')
            ans = re.search(r"\[ANSWER\]\s*(\d)", b).group(1)
            qs.append({"q": q, "options": [o.strip() for o in opts if o.strip()][:4], "correct": int(ans)-1})
        except: continue
    return qs

def prepare_full_exam():
    """מייצר מבחן סימולציה מלא - 25 שאלות"""
    prompt = "צור מבחן סימולציה מלא לרישיון תיווך עם 25 שאלות אינטגרטיביות. פורמט: [START_Q] [QUESTION]... [OPTIONS]... [ANSWER]..."
    try:
        res = model.generate_content(prompt)
        st.session_state.full_exam_data = parse_quiz(res.text)
        st.session_state.full_exam_ready = True
    except: pass

# 3. סרגל צידי - הניווט המרכזי
if st.session_state.user_name:
    with st.sidebar:
        st.title(f"שלום {st.session_state.user_name}")
        st.markdown("---")
        
        # בחירת נושא (Setup)
        if st.button("➕ החלף נושא למידה", use_container_width=True):
            st.session_state.view_mode = "setup"; st.rerun()
            
        if st.session_state.current_topic:
            st.markdown(f"**נושא נוכחי: {st.session_state.current_topic}**")
            if st.button("📖 קרא את השיעור", use_container_width=True):
                st.session_state.view_mode = "lesson_view"; st.rerun()
            
            if st.session_state.lesson_quiz_ready:
                if st.button("✍️ שאלון הבנה על הנושא", use_container_width=True):
                    st.session_state.view_mode = "lesson_quiz"; st.rerun()
        
        st.markdown("---")
        st.subheader("🏆 בחינה כוללת (25 שאלות)")
        if st.session_state.full_exam_ready:
            if st.button("📝 התחל מבחן סימולציה", use_container_width=True, type="primary"):
                st.session_state.view_mode = "full_exam"
                st.session_state.exam_start_time = time.time()
                st.session_state.exam_answers = {}
                st.session_state.current_exam_idx = 0
                st.session_state.exam_finished = False
                st.rerun()
        else:
            st.write("⌛ מכין מבחן ברקע...")

# 4. דפים
if st.session_state.view_mode == "login":
    st.title("🎓 מתווך בקליק")
    name = st.text_input("שם משתמש:")
    if st.button("כניסה"):
        st.session_state.user_name = name
        st.session_state.view_mode = "setup"
        prepare_full_exam()
        st.rerun()

elif st.session_state.view_mode == "setup":
    st.title("מה נלמד היום?")
    t = st.selectbox("בחר נושא:", ["חוק המתווכים", "חוק המקרקעין", "דיני חוזים", "מיסוי מקרקעין"])
    if st.button("הכן חומרי למידה"):
        st.session_state.current_topic = t
        st.session_state.lesson_data = ""
        st.session_state.lesson_quiz_ready = False
        st.session_state.view_mode = "lesson_view"; st.rerun()

elif st.session_state.view_mode == "lesson_view":
    st.title(f"שיעור: {st.session_state.current_topic}")
    if not st.session_state.lesson_data:
        ph = st.empty(); full_t = ""
        res = model.generate_content(f"כתוב שיעור מפורט על {st.session_state.current_topic}", stream=True)
        for chunk in res:
            full_t += chunk.text; ph.markdown(full_t)
        st.session_state.lesson_data = full_t
        # הכנת השאלון ברקע
        l_res = model.generate_content(f"צור 5 שאלות הבנה על {st.session_state.current_topic} בפורמט START_Q")
        st.session_state.lesson_quiz_data = parse_quiz(l_res.text)
        st.session_state.lesson_quiz_ready = True
        st.rerun()
    else:
        st.markdown(st.session_state.lesson_data)
        st.info("💡 השיעור הסתיים. ניתן לעבור לשאלון ההבנה מהתפריט הצידי.")

elif st.session_state.view_mode == "lesson_quiz":
    st.title(f"שאלון הבנה: {st.session_state.current_topic}")
    for i, q in enumerate(st.session_state.lesson_quiz_data):
        with st.container():
            st.markdown(f'<div class="summary-card">', unsafe_allow_html=True)
            st.write(f"**{i+1}. {q['q']}**")
            ans = st.radio(f"תשובה {i}", q['options'], key=f"lq_{i}", index=None)
            if st.button(f"בדוק תשובה {i+1}", key=f"lb_{i}"):
                if ans and q['options'].index(ans) == q['correct']: st.success("נכון!")
                else: st.error("טעות, נסה שוב.")
            st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.view_mode == "full_exam":
    # לוגיקת המבחן של 25 שאלות (כולל סיכום מפורט בסיום)
    if not st.session_state.exam_finished:
        st.title("📝 בחינה כוללת (25 שאלות)")
        col_m, col_n = st.columns([3, 1])
        with col_n:
            for i in range(25):
                lbl = f"שאלה {i+1}" + (" ✅" if i in st.session_state.exam_answers else "")
                if st.button(lbl, key=f"n_{i}", use_container_width=True):
                    st.session_state.current_exam_idx = i; st.rerun()
            if st.button("🏁 סיים והגש", type="primary", use_container_width=True):
                st.session_state.exam_finished = True; st.rerun()
        with col_m:
            idx = st.session_state.current_exam_idx
            q = st.session_state.full_exam_data[idx]
            st.subheader(f"שאלה {idx+1}")
            st.write(q['q'])
            ch = st.radio("בחר תשובה:", q['options'], index=st.session_state.exam_answers.get(idx), key=f"eq_{idx}")
            if ch: st.session_state.exam_answers[idx] = q['options'].index(ch)
    else:
        # הצגת תוצאות ופירוט
        st.header("🏁 תוצאות המבחן")
        correct = sum(1 for i, a in st.session_state.exam_answers.items() if a == st.session_state.full_exam_data[i]['correct'])
        st.metric("ציון", f"{int((correct/25)*100)}%")
        
        for i, q in enumerate(st.session_state.full_exam_data):
            with st.container():
                st.markdown('<div class="summary-card">', unsafe_allow_html=True)
                st.write(f"**שאלה {i+1}: {q['q']}**")
                user_idx = st.session_state.exam_answers.get(i)
                if user_idx is not None:
                    if user_idx == q['correct']:
                        st.markdown(f'<p class="correct-ans">ענית נכון: {q["options"][user_idx]}</p>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<p class="wrong-ans">ענית: {q["options"][user_idx]}</p>', unsafe_allow_html=True)
                        st.write(f"התשובה הנכונה: {q['options'][q['correct']]}")
                else:
                    st.write(f"לא ענית. התשובה הנכונה: {q['options'][q['correct']]}")
                st.markdown('</div>', unsafe_allow_html=True)
        
        st.session_state.full_exam_ready = False
        prepare_full_exam() # מכין את המבחן הבא
