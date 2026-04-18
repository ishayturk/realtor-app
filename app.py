# Project: מתווך בקליק | Version: training_full_V18 | 2026-04-18
import streamlit as st
import google.generativeai as genai
import json
import re
import random
import smtplib
import time
from email.mime.text import MIMEText
from exam_insights import EXAM_INSIGHTS

st.set_page_config(page_title="מתווך בקליק", page_icon="favicon.svg", layout="wide", initial_sidebar_state="collapsed")

if "user" in st.query_params and st.session_state.get("user") is None:
    st.session_state.user = st.query_params.get("user")
    st.session_state.step = "menu"
    st.rerun()

st.markdown("""
<style>
    * { direction: rtl; text-align: right; }
    .header-container { display: flex; align-items: center; gap: 45px; margin-bottom: 30px; }
    .header-title { font-size: 2.5rem !important; font-weight: bold !important; margin: 0 !important; }
    .header-user { font-size: 1.2rem !important; font-weight: 900 !important; color: #31333f; }
    .stButton>button { width: 100% !important; border-radius: 8px !important; font-weight: bold !important; height: 3em !important; }
    @media (max-width: 768px) {
        .header-container { display: flex; flex-direction: row; justify-content: center; align-items: center; gap: 0; width: fit-content; margin: 0 auto 20px auto; }
        .header-title { font-size: 1.3rem !important; text-align: right; white-space: nowrap; }
        .header-spacer { display: inline-block; width: 3em; }
        .header-user { font-size: 1rem !important; text-align: left; white-space: nowrap; }
    }
    @media (min-width: 769px) { .header-spacer { display: none; } }
    .scroll-top-btn {
        position: fixed; bottom: 30px; left: 30px; z-index: 9999;
        background: #888; border-radius: 50%; width: 48px; height: 48px;
        display: flex; align-items: center; justify-content: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2); text-decoration: none;
    }
    .scroll-top-btn:hover { background: #666; }
</style>
""", unsafe_allow_html=True)

SYLLABUS = {
    "חוק המתווכים": ["רישוי והגבלות", "הגינות וזהירות", "הזמנה ובלעדיות", "פעולות שאינן תיווך"],
    "תקנות המתווכים": ["פרטי הזמנה 1997", "פעולות שיווק 2004", "דמי תיווך"],
    "תקנות האתיקה המקצועית תשפ״ד-2024": ["חובת נאמנות וגילוי", "ניגוד עניינים", "איסור הטעיה", "כבוד המקצוע וסודיות"],
    "דיני שליחות": ["מהות השליחות ויצירתה", "חריגה מהרשאה", "שליחות לכאורה", "ביטול השליחות"],
    "עשיית עושר ולא במשפט": ["יסודות העילה", "השבה ללא חוזה תקין", "דמי תיווך ללא הזמנה בכתב"],
    "פסיקה מרכזית": ["זכאות לדמי תיווך", "הסיבה המניעה ובלעדיות", "עסקאות נוגדות והערת אזהרה"],
    "חוק המקרקעין": ["בעלות וזכויות", "בתים משותפים", "עסקאות נוגדות", "הערות אזהרה", "שכירות וזיקה"],
    "חוק המכר (דירות)": ["מפרט וגילוי", "בדק ואחריות", "איחור במסירה", "הבטחת השקעות"],
    "חוק החוזים": ["כריתת חוזה", "פגמים בחוזה", "תרופות והפרה", "ביטול והשבה"],
    "חוק התכנון והבנייה": ["היתרים ושימוש חורג", "היטל השבחה", "תוכניות מתאר", "מוסדות התכנון"],
    "חוק מיסוי מקרקעין": ["מס שבח (חישוב ופטורים)", "מס רכישה", "הקלות לדירת מגורים", "שווי שוק"],
    "חוק הגנת הצרכן": ["ביטול עסקה", "הטעיה בפרסום"],
    "דיני ירושה": ["סדר הירושה", "צוואות"],
    "חוק העונשין": ["עבירות מרמה וזיוף"]
}

BACKDOOR_NAME = "ישי טורק"
BACKDOOR_EMAIL = "ishayturk@gmail.com"


def reset_quiz_state():
    st.session_state.update({
        "quiz_active": False, "q_data": None, "q_count": 0,
        "checked": False, "quiz_finished": False, "correct_answers": 0,
        "used_questions": []
    })
    keys_to_del = [k for k in st.session_state.keys() if k.startswith("sc_") or k.startswith("q_")]
    for k in keys_to_del:
        del st.session_state[k]


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


def stream_ai_lesson(sub_topic):
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-2.0-flash')
    insights = EXAM_INSIGHTS.get(sub_topic, "")
    system = """אתה מורה המכין נבחנים לבחינת רשם המתווכים בישראל.
כתוב שיעור הכנה מעמיק על הנושא שיינתן לך.
התמקד אך ורק במה שנדרש לבחינת רשם המתווכים.
כלול את כל הנקודות הרלוונטיות לבחינה באופן מלא ומקיף.
התייחס לסעיפי חוק רלוונטיים.
הדגש מלכודות, חריגים ותנאים שמופיעים בשאלות.

סגנון כתיבה — חובה:
* אל תפתח ב"שלום" או ברכה כלשהי
* אל תכתוב "היום נתמקד" — כתוב "שיעור זה מתמקד"
* אל תכתוב "שימו לב" — כתוב "שים לב" או "שימי לב"
* פנה ללומד בגוף יחיד, לא רבים
* התחל ישירות בתוכן — ללא הקדמות מיותרות"""
    if insights:
        prompt = f"{system}\n\nנושא: {sub_topic}\n\nמידע מבוסס מבחנים אמיתיים שחובה לכלול:\n{insights}\n\nהרחב והסבר את הנקודות הללו בצורה מעמיקה."
    else:
        prompt = f"{system}\n\nנושא: {sub_topic}"

    for attempt in range(3):
        try:
            if attempt > 0:
                time.sleep(2)
            response = model.generate_content(prompt, stream=True)
            placeholder = st.empty()
            full_text = ""
            for chunk in response:
                full_text += chunk.text
                placeholder.markdown(full_text + "▌")
            placeholder.markdown(full_text)
            return full_text
        except:
            if attempt < 2:
                continue
    return None


def fetch_q_ai(sub_topic, lesson_context, used_qs):
    if len(lesson_context.split()) < 100:
        return None
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
        st.markdown(f"""<a name="top"></a><div class="header-container">
            <div class="header-title">🏠 מתווך בקליק</div>
            <div class="header-spacer"></div>
            <div class="header-user">👤 <b>{st.session_state.user}</b></div>
        </div>""", unsafe_allow_html=True)


def show_scroll_top():
    st.markdown("""
        <a href="#top" class="scroll-top-btn" title="חזור לראש הדף">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                <path d="M12 4L4 12H9V20H15V12H20L12 4Z" fill="white"/>
            </svg>
        </a>
    """, unsafe_allow_html=True)


def show_bottom_nav(show_quiz_btn=False, quiz_finished=False):
    if show_quiz_btn:
        ca, cb = st.columns([1, 1])
        if ca.button("📝 שאלון תרגול" if not quiz_finished else "🔄 תרגול חוזר"):
            with st.spinner("מייצר שאלה..."):
                prev_questions = list(st.session_state.used_questions)
                res = fetch_q_ai(st.session_state.current_sub, st.session_state.lesson_txt, prev_questions)
                if res:
                    reset_quiz_state()
                    st.session_state.used_questions = prev_questions + [res['q']]
                    st.session_state.update({"q_data": res, "quiz_active": True, "q_count": 1, "checked": False})
                    st.rerun()
        if cb.button("לתפריט הראשי", key="main_back"):
            reset_quiz_state()
            st.session_state.step = "menu"
            st.rerun()
    else:
        if st.button("לתפריט הראשי", key="q_back"):
            reset_quiz_state()
            st.session_state.step = "menu"
            st.rerun()


# -------------------------
# LOGIN
# -------------------------
if st.session_state.step == "login":
    st.title("🏠 מתווך בקליק")
    st.markdown("""
    <style>
        div[data-testid="stTextInput"] input {
            background: transparent !important; border: 1px solid #000 !important;
            border-radius: 6px !important; padding: 10px !important;
            font-size: 1rem !important; max-width: 420px !important;
        }
        div[data-testid="stTextInput"], div[data-testid="stTextInput"] > div,
        div[data-testid="stTextInput"] > div > div {
            background: transparent !important; border: none !important; box-shadow: none !important;
        }
        div[data-testid="stTextInput"] label { display: none !important; }
    </style>
    """, unsafe_allow_html=True)

    u_in = st.text_input("שם", placeholder="שם מלא — שם ושם משפחה", autocomplete="off", label_visibility="collapsed").strip()
    email_in = st.text_input("מייל", placeholder="כתובת מייל", autocomplete="off", label_visibility="collapsed").strip()

    if u_in == BACKDOOR_NAME and email_in.lower() == BACKDOOR_EMAIL:
        if st.button("כניסה"):
            st.session_state.user = u_in
            st.session_state.step = "menu"
            st.rerun()
    else:
        if not st.session_state.get("otp_sent"):
            parts = u_in.split()
