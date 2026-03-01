# Project: מתווך בקליק | Version: training_full_V12 | 25/02/2026 | 08:50
# Claude 20 | Login field styling - border, placeholder, no label
import streamlit as st
import google.generativeai as genai
import json
import re
import random

# הגדרת דף
st.set_page_config(page_title="מתווך בקליק", page_icon="favicon.svg", layout="wide", initial_sidebar_state="collapsed")

# Interceptor
if "user" in st.query_params and st.session_state.get("user") is None:
    st.session_state.user = st.query_params.get("user")
    st.session_state.step = "menu"
    st.rerun()

# עיצוב RTL (עוגן 1213)
st.markdown("""
<style>
    * { direction: rtl; text-align: right; }
    .header-container { display: flex; align-items: center; gap: 45px; margin-bottom: 30px; }
    .header-title { font-size: 2.5rem !important; font-weight: bold !important; margin: 0 !important; }
    .header-user { font-size: 1.2rem !important; font-weight: 900 !important; color: #31333f; }
    .stButton>button { width: 100% !important; border-radius: 8px !important; font-weight: bold !important; height: 3em !important; }

    /* תצוגת נייד בלבד */
    @media (max-width: 768px) {
        .header-container {
            display: flex;
            flex-direction: row;
            justify-content: center;
            align-items: center;
            gap: 0;
            width: fit-content;
            margin: 0 auto 20px auto;
        }
        .header-title {
            font-size: 1.3rem !important;
            text-align: right;
            white-space: nowrap;
        }
        .header-spacer {
            display: inline-block;
            width: 3em;
        }
        .header-user {
            font-size: 1rem !important;
            text-align: left;
            white-space: nowrap;
        }
    }

    /* הסתרת הספייסר במחשב */
    @media (min-width: 769px) {
        .header-spacer { display: none; }
    }
</style>
""", unsafe_allow_html=True)

SYLLABUS = {
    "חוק המתווכים": ["רישוי והגבלות", "הגינות וזהירות", "הזמנה ובלעדיות", "פעולות שאינן תיווך"],
    "תקנות המתווכים": ["פרטי הזמנה 1997", "פעולות שיווק 2004", "דמי תיווך"],
    "חוק המקרקעין": ["בעלות וזכויות", "בתים משותפים", "עסקאות נוגדות", "הערות אזהרה", "שכירות וזיקה"],
    "חוק המכר (דירות)": ["מפרט וגילוי", "בדק ואחריות", "איחור במסירה", "הבטחת השקעות"],
    "חוק החוזים": ["כריתת חוזה", "פגמים בחוזה", "תרופות והפרה", "ביטול והשבה"],
    "חוק התכנון והבנייה": ["היתרים ושימוש חורג", "היטל השבחה", "תוכניות מתאר", "מוסדות התכנון"],
    "חוק מיסוי מקרקעין": ["מס שבח (חישוב ופטורים)", "מס רכישה", "הקלות לדירת מגורים", "שווי שוק"],
    "חוק הגנת הצרכן": ["ביטול עסקה", "הטעיה בפרסום"],
    "דיני ירושה": ["סדר הירושה", "צוואות"],
    "חוק העונשין": ["עבירות מרמה וזיוף"]
}

def reset_quiz_state():
    st.session_state.update({
        "quiz_active": False, "q_data": None, "q_count": 0,
        "checked": False, "quiz_finished": False, "correct_answers": 0,
        "used_questions": []
    })
    keys_to_del = [k for k in st.session_state.keys() if k.startswith("sc_") or k.startswith("q_")]
    for k in keys_to_del:
        del st.session_state[k]

def fetch_q_ai(sub_topic, lesson_context, used_qs):
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-2.0-flash')
    json_fmt = '{"q": "","options": ["","","",""], "correct": "", "explain": ""}'
    history = "\n".join([f"- {q}" for q in used_qs]) if used_qs else "אין שאלות קודמות."
    prompt = f"""בהתבסס אך ורק על טקסט השיעור הבא בנושא {sub_topic}:
        ---
        {lesson_context}
        ---
        צור שאלה אמריקאית חדשה לבדיקת הבנה. אל תחזור על נושאים שכבר נשאלו כאן: {history}
        החזר אך ורק JSON תקני: {json_fmt}"""
    for _ in range(5):
        try:
            response = model.generate_content(prompt)
            res_text = response.text.replace('```json', '').replace('```', '').strip()
            match = re.search(r'\{.*\}', res_text, re.DOTALL)
            if match:
                return json.loads(match.group())
        except:
            pass
    return None

import smtplib
import random
import time
from email.mime.text import MIMEText

def send_otp(email, code):
    try:
        msg = MIMEText(f"קוד הכניסה שלך למתווך בקליק: {code}\n\nהקוד תקף ל-2 דקות.")
        msg['Subject'] = 'קוד כניסה - מתווך בקליק'
        msg['From'] = 'ishayturk@gmail.com'
        msg['To'] = email
        with smtplib.SMTP('smtp.gmail.com', 587) as s:
            s.starttls()
            s.login('ishayturk@gmail.com', st.secrets["GMAIL_PASS"])
            s.send_message(msg)
        return True
    except:
        return False
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-2.0-flash')
    full_p = f"{prompt_text}. כתוב שיעור הכנה מעמיק למבחן המתווכים."
    for _ in range(3):
        try:
            response = model.generate_content(full_p, stream=True)
            placeholder = st.empty()
            full_text = ""
            for chunk in response:
                full_text += chunk.text
                placeholder.markdown(full_text + "▌")
            placeholder.markdown(full_text)
            return full_text
        except:
            pass
    return "⚠️ תקלה בטעינה. אנא בחר נושא מחדש."

if "step" not in st.session_state:
    st.session_state.update({
        "user": None, "step": "login", "lesson_txt": "",
        "selected_topic": None, "current_sub": None,
        "quiz_active": False, "quiz_finished": False,
        "checked": False, "correct_answers": 0, "q_count": 0, "q_data": None,
        "used_questions": []
    })

def show_header():
    if st.session_state.get("user"):
        st.markdown(f"""<div class="header-container">
            <div class="header-title">🏠 מתווך בקליק</div>
            <div class="header-spacer"></div>
            <div class="header-user">👤 <b>{st.session_state.user}</b></div>
        </div>""", unsafe_allow_html=True)

if st.session_state.step == "login":
    st.title("🏠 מתווך בקליק")
    st.markdown("""
    <style>
        div[data-testid="stTextInput"] input {
            background: transparent !important;
            border: 1px solid #000 !important;
            border-radius: 6px !important;
            padding: 10px !important;
            font-size: 1rem !important;
            max-width: 420px !important;
        }
        div[data-testid="stTextInput"] label { display: none !important; }
    </style>
    """, unsafe_allow_html=True)

    if not st.session_state.get("otp_sent"):
        u_in = st.text_input("שם", placeholder="שם מלא — שם ושם משפחה", autocomplete="off", label_visibility="collapsed").strip()
        email_in = st.text_input("מייל", placeholder="כתובת מייל", autocomplete="off", label_visibility="collapsed").strip()
        parts = u_in.split()
        valid_name = len(parts) >= 2 and all(len(p) >= 2 for p in parts)
        valid_email = "@" in email_in and "." in email_in
        if u_in and not valid_name:
            st.caption("יש להזין שם ושם משפחה")
        if st.button("שלח קוד"):
            if valid_name and valid_email:
                code = str(random.randint(100000, 999999))
                if send_otp(email_in, code):
                    st.session_state.otp_code = code
                    st.session_state.otp_time = time.time()
                    st.session_state.otp_user = u_in
                    st.session_state.otp_email = email_in
                    st.session_state.otp_sent = True
                    st.rerun()
                else:
                    st.error("שגיאה בשליחת המייל. נסה שוב.")
            else:
                st.warning("יש למלא שם מלא וכתובת מייל תקינה.")
    else:
        st.info(f"קוד נשלח ל-{st.session_state.get('otp_email')}. תקף ל-2 דקות.")
        code_in = st.text_input("קוד", placeholder="הזן קוד", autocomplete="off", label_visibility="collapsed").strip()
        if st.button("אישור"):
            elapsed = time.time() - st.session_state.get("otp_time", 0)
            if elapsed > 120:
                st.error("הקוד פג תוקף. רענן את הדף ונסה שוב.")
                st.session_state.otp_sent = False
            elif code_in == st.session_state.get("otp_code"):
                st.session_state.user = st.session_state.otp_user
                st.session_state.step = "menu"
                st.session_state.otp_sent = False
                st.rerun()
            else:
                attempts = st.session_state.get("otp_attempts", 0) + 1
                st.session_state.otp_attempts = attempts
                if attempts >= 3:
                    st.error("3 ניסיונות כושלים — יש להתחיל מחדש.")
                    st.session_state.otp_sent = False
                    st.session_state.otp_attempts = 0
                else:
                    st.error(f"קוד שגוי. נותרו {3 - attempts} ניסיונות.")

elif st.session_state.step == "menu":
    show_header()
    c1, c2, _ = st.columns([1.5, 1.5, 3])
    if c1.button("📚 לימוד לפי נושאים"):
        st.session_state.step = "study"
        st.rerun()
    if c2.button("⏱️ גש/י למבחן"):
        st.session_state.step = "exam_frame"
        st.rerun()

elif st.session_state.step == "exam_frame":
    st.markdown(f"""
        <style>
            header {{ visibility: hidden !important; }}
            .block-container {{ padding: 0 !important; }}
            .nav-link-box {{ 
                position: fixed; 
                top: 15px; 
                left: 20px; 
                z-index: 9999; 
                background: white; 
                padding: 8px 15px; 
                border-radius: 8px; 
                border: 1px solid #ddd;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            .nav-link {{ 
                text-decoration: none !important; 
                color: #31333F !important; 
                font-weight: bold !important;
                font-family: sans-serif;
            }}
        </style>
        <div class="nav-link-box">
            <a href="/?user={st.session_state.user}" target="_self" class="nav-link">🏠 לתפריט הראשי</a>
        </div>
    """, unsafe_allow_html=True)
    base_url = "https://fullrealestatebroker-yevuzewxde4obgrpgacrpc.streamlit.app/"
    exam_url = f"{base_url}?user={st.session_state.user}&embed=true"
    st.markdown(f'<iframe src="{exam_url}" style="width:100%; height:100vh; border:none; margin-top:-40px;"></iframe>', unsafe_allow_html=True)

elif st.session_state.step == "study":
    show_header()
    sel = st.selectbox("בחר נושא לימוד:", ["בחר..."] + list(SYLLABUS.keys()))
    col_a, col_b = st.columns([1, 1])
    if col_a.button("טען נושא") and sel != "בחר...":
        reset_quiz_state()
        st.session_state.update({"selected_topic": sel, "step": "lesson_run", "lesson_txt": "", "current_sub": None})
        st.rerun()
    if col_b.button("לתפריט הראשי"):
        reset_quiz_state()
        st.session_state.step = "menu"
        st.rerun()

elif st.session_state.step == "lesson_run":
    show_header()
    if not st.session_state.get("selected_topic"):
        st.session_state.step = "study"
        st.rerun()
    st.header(f"📖 {st.session_state.selected_topic}")
    subs = SYLLABUS.get(st.session_state.selected_topic, [])
    cols = st.columns(len(subs))

    for i, s in enumerate(subs):
        if cols[i].button(s, key=f"s_{i}"):
            reset_quiz_state()
            st.session_state.update({"current_sub": s, "lesson_txt": "LOADING"})
            st.rerun()

    if not st.session_state.get("current_sub"):
        if st.button("לתפריט הראשי", key="back_no_sub"):
            reset_quiz_state()
            st.session_state.step = "menu"
            st.rerun()
    else:
        if st.session_state.get("lesson_txt") == "LOADING":
            st.session_state.lesson_txt = stream_ai_lesson(f"הסבר על {st.session_state.current_sub}")
            st.rerun()
        elif st.session_state.get("lesson_txt"):
            st.markdown(st.session_state.lesson_txt)

        if st.session_state.quiz_active and st.session_state.q_data and not st.session_state.quiz_finished:
            st.divider()
            q = st.session_state.q_data
            st.subheader(f"📝 שאלה {st.session_state.q_count} מתוך 10")
            ans = st.radio(q['q'], q['options'], index=None, key=f"q_{st.session_state.q_count}", disabled=st.session_state.checked)
            qc1, qc2, qc3 = st.columns([2, 2, 2])

            if qc1.button("בדוק/י תשובה", disabled=(ans is None or st.session_state.checked)):
                st.session_state.checked = True
                st.rerun()

            if qc2.button("לשאלה הבאה" if st.session_state.q_count < 10 else "🏁 סיכום", disabled=not st.session_state.checked):
                if st.session_state.q_count < 10:
                    with st.spinner("מביא שאלה חדשה..."):
                        res = fetch_q_ai(st.session_state.current_sub, st.session_state.lesson_txt, st.session_state.used_questions)
                        if res:
                            st.session_state.used_questions.append(res['q'])
                            st.session_state.update({"q_data": res, "q_count": st.session_state.q_count + 1, "checked": False})
                            st.rerun()
                else:
                    st.session_state.quiz_finished = True
                    st.rerun()

            if qc3.button("לתפריט הראשי", key="q_back"):
                reset_quiz_state()
                st.session_state.step = "menu"
                st.rerun()

            if st.session_state.checked:
                if ans == q['correct']:
                    st.success("נכון מאוד!")
                    if f"sc_{st.session_state.q_count}" not in st.session_state:
                        st.session_state.correct_answers += 1
                        st.session_state[f"sc_{st.session_state.q_count}"] = True
                else: st.error(f"טעות. הנכון הוא: {q['correct']}")
                st.info(f"הסבר: {q['explain']}")

        if (not st.session_state.quiz_active or st.session_state.quiz_finished) and st.session_state.get("current_sub"):
            if st.session_state.quiz_finished:
                st.success(f"🏆 ציון: {st.session_state.correct_answers} מתוך 10.")
            ca, cb = st.columns([1, 1])
            if ca.button("📝 שאלון תרגול" if not st.session_state.quiz_finished else "🔄 תרגול חוזר"):
                with st.spinner("מייצר שאלה..."):
                    res = fetch_q_ai(st.session_state.current_sub, st.session_state.lesson_txt, [])
                    if res:
                        reset_quiz_state()
                        st.session_state.used_questions = [res['q']]
                        st.session_state.update({"q_data": res, "quiz_active": True, "q_count": 1, "checked": False})
                        st.rerun()
            if cb.button("לתפריט הראשי", key="main_back"):
                reset_quiz_state()
                st.session_state.step = "menu"
                st.rerun()

# סוף קובץ
