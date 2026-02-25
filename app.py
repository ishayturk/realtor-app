# Project: מתווך בקליק | Version: training_full_V12 | 25/02/2026 | 08:50
# Status: Restored Question Logic | Protocol: Full File Delivery
# Claude 01 | Fix: Mobile header layout
# Claude 02 | Fix: Sub-topic button disable + screen cleanup on sub-topic change
# Claude 03 | Fix: Mobile header one line (logo+title right, username left) + lock all sub-topic buttons during loading
# Claude 04 | Fix: Mobile header centered box with spacing + remove unauthorized spinner
# Claude 05 | Fix: Gemini prompt - skip intro sentence, start directly with content
# Claude 06 | Fix: Sub-topic title displayed by app (+20% bold), Gemini instructed not to write title
# Claude 07 | Fix: Revert prompt (no title instruction), show sub-topic title as "שיעור: {current_sub}"
# Claude 08 | Fix: Revert to Gemini title (Claude 04 style) with CSS size limit, fix quiz buttons on mobile
import streamlit as st
import google.generativeai as genai
import json
import re
import random

# הגדרת דף
st.set_page_config(page_title="מתווך בקליק", layout="wide", initial_sidebar_state="collapsed")

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

    /* הקטנת כותרות H1/H2/H3 שGemini מייצר לתוכן השיעור */
    .lesson-content h1, .lesson-content h2, .lesson-content h3 {
        font-size: 1.25em !important;
        font-weight: bold !important;
    }

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
    try:
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
        response = model.generate_content(prompt)
        res_text = response.text.replace('```json', '').replace('```', '').strip()
        match = re.search(r'\{.*\}', res_text, re.DOTALL)
        if match: return json.loads(match.group())
        return None
    except: return None

def stream_ai_lesson(prompt_text):
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-2.0-flash')
        full_p = f"{prompt_text}. כתוב שיעור הכנה מעמיק למבחן המתווכים. התחל ישירות בתוכן ללא הקדמה, ברכה, או משפט פתיחה."
        response = model.generate_content(full_p, stream=True)
        placeholder = st.empty()
        full_text = ""
        for chunk in response:
            full_text += chunk.text
            placeholder.markdown(full_text + "▌")
        placeholder.markdown(full_text)
        return full_text
    except: return None

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
    u_in = st.text_input("שם מלא:")
    if st.button("כניסה") and u_in:
        st.session_state.user = u_in
        st.session_state.step = "menu"
        st.rerun()

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
    st.markdown("""<style>header { visibility: hidden !important; }.block-container { padding: 0 !important; }.nav-link-box { position: fixed; top: 10px; left: 10%; z-index: 1001; }.nav-link { text-decoration: none; color: #555; font-weight: bold; background: rgba(255,255,255,0.9); padding: 5px 15px; border-radius: 5px; border: 1px solid #ddd; }</style>
    <div class="nav-link-box"><a href="/?user=""" + st.session_state.user + """" target="_self" class="nav-link">לתפריט הראשי</a></div>""", unsafe_allow_html=True)
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

    is_loading = (st.session_state.get("lesson_txt") == "LOADING")

    loaded_sub = st.session_state.get("current_sub") if (
        st.session_state.get("lesson_txt") and
        st.session_state.get("lesson_txt") not in ("", "LOADING")
    ) else None

    for i, s in enumerate(subs):
        is_disabled = is_loading or (s == loaded_sub)
        if cols[i].button(s, key=f"s_{i}", disabled=is_disabled):
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
            result = stream_ai_lesson(f"הסבר על {st.session_state.current_sub}")
            if result:
                st.session_state.lesson_txt = result
            else:
                st.session_state.lesson_txt = ""
                st.session_state.current_sub = None
                st.error("⚠️ תקלה בטעינה. אנא בחר נושא מחדש.")
            st.rerun()
        elif st.session_state.get("lesson_txt"):
            # עוטפים את תוכן השיעור ב-div עם class lesson-content כדי לשלוט בגודל הכותרות
            st.markdown(f'<div class="lesson-content">', unsafe_allow_html=True)
            st.markdown(st.session_state.lesson_txt)
            st.markdown('</div>', unsafe_allow_html=True)

        if st.session_state.quiz_active and st.session_state.q_data and not st.session_state.quiz_finished:
            st.divider()
            q = st.session_state.q_data
            st.subheader(f"📝 שאלה {st.session_state.q_count} מתוך 10")
            ans = st.radio(q['q'], q['options'], index=None, key=f"q_{st.session_state.q_count}")
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
