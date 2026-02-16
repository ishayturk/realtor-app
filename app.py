# ==========================================
# Project: מתווך בקליק | Version: 1181
# ==========================================

import streamlit as st
import google.generativeai as genai
import json, re

# הגדרות דף
st.set_page_config(
    page_title="מתווך בקליק",
    layout="wide"
)

# CSS בסיסי
st.markdown(
    """
    <style>
        * { direction: rtl; text-align: right; }
        .stButton>button { 
            min-width: 140px; 
            border-radius: 8px; 
        }
        .nav-btn { 
            border: 1px solid #888; 
            padding: 8px; 
            text-decoration: none; 
            border-radius: 8px; 
            display: inline-block; 
            color: #333;
        }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown('<div id="top"></div>', unsafe_allow_html=True)

SYLLABUS = {
    "חוק המתווכים": ["רישוי", "הגינות", "בלעדיות"],
    "תקנות המתווכים": ["פרטי הזמנה", "שיווק"],
    "חוק המקרקעין": ["בעלות", "בתים", "אזהרה"],
    "חוק המכר": ["מפרט", "בדק", "איחור"],
    "חוק החוזים": ["כריתה", "פגמים", "תרופות"],
    "תכנון ובנייה": ["היתרים", "השבחה"],
    "מיסוי מקרקעין": ["שבח", "רכישה"]
}

def ask_ai(p):
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        m = genai.GenerativeModel('gemini-2.0-flash')
        r = m.generate_content(p)
        return r.text if r else None
    except:
        return None

def fetch_content(topic, sub):
    p = f"כתוב שיעור על {sub} בתוך {topic}."
    res = ask_ai(p)
    return res if res else "⚠️ שגיאה."

def fetch_q(topic):
    p = f"צור שאלה אמריקאית על {topic}. JSON."
    res = ask_ai(p)
    try:
        m = re.search(r'\{.*\}', res, re.DOTALL)
        return json.loads(m.group()) if m else None
    except:
        return None

# אתחול
if "step" not in st.session_state:
    st.session_state.update({
        "step": "login", "user": None,
        "selected_topic": None, "lesson_contents": {},
        "current_sub_idx": None, "quiz_active": False,
        "q_counter": 0, "current_q_data": None,
        "next_q_data": None, "show_feedback": False
    })

st.title("🏠 מתווך בקליק")

step = st.session_state.step

if step == 'login':
    u = st.text_input("שם מלא:")
    if st.button("כניסה") and u:
        st.session_state.user = u
        st.session_state.step = 'menu'
        st.rerun()

elif step == 'menu':
    st.write(f"👤 שלום, {st.session_state.user}")
    c1, c2 = st.columns(2)
    if c1.button("📚 לימוד לפי נושאים"):
        st.session_state.step = 'study'
        st.rerun()
    if c2.button("⏱️ סימולציה"):
        st.info("בקרוב")

elif step == 'study':
    opts = ["בחר..."] + list(SYLLABUS.keys())
    sel = st.selectbox("נושא:", opts)
    if sel != "בחר..." and st.button("טען"):
        st.session_state.update({
            "selected_topic": sel, "lesson_contents": {},
            "current_sub_idx": None, "quiz_active": False,
            "step": "lesson_run", "q_counter": 0
        })
        st.rerun()

elif step == 'lesson_run':
    cur_topic = st.session_state.selected_topic
    st.header(f"📖 {cur_topic}")
    subs = SYLLABUS.get(cur_topic, [])
    
    if subs:
        # פתרון חסין לחיתוך: חישוב אורך מראש
        num_subs = len(subs)
        t_cols = st.columns(num_subs)
        for i, t in enumerate(subs):
            if t_cols[i].button(t, key=f"s_{i}"):
                st.session_state.current_sub_idx = i
                st.session_state.quiz_active = False
                with st.spinner("טוען..."):
                    res = fetch_content(cur_topic, t)
                    st.session_state.lesson_contents[t] = res
                st.rerun()

    if st.session_state.current_sub_idx is not None:
        idx = st.session_state.current_sub_idx
        sub_name = subs[idx]
        txt = st.session_state.lesson_contents.get(sub_name, "")
        st.markdown(txt)

    if st.session_state.quiz_active:
        st.divider()
        if not st.session_state.current_q_data:
            st.session_state.current_q_data = fetch_q(cur_topic)
            st.rerun()
        
        q = st.session_state.current_q_data
        st.write(f"**שאלה {st.session_state.q_counter}**")
        
        q_text = q['q']
        q_opts = q['options']
        ans = st.radio(q_text, q_opts, index=None, key="qr")
        
        if st.session_state.show_feedback:
            if ans == q['correct']: st.success("✅ נכון")
            else: st.error(f"❌ טעות: {q['correct']}")

    st.write("---")
    b_cols = st.columns([2, 1.5, 1.5, 4])

    # טקסט כפתור
    btn_l = "📝 שאלון"
    if st.session_state.quiz_active:
        if not st.session_state.show_feedback: btn_l = "✅ בדיקה"
        elif st.session_state.q_counter < 10: btn_l = "➡️ הבאה"
        else: btn_l = "🔄 מחדש"

    with b_cols[0]:
        if st.button(btn_l):
            if "שאלון" in btn_l or "מחדש" in btn_l:
                st.session_state.update({
                    "quiz_active": True, "q_counter": 1,
                    "show_feedback": False, "current_q_data": None
                })
            elif "בדיקה" in btn_l and ans:
                st.session_state.show_feedback = True
                st.session_state.next_q_data = fetch_q(cur_topic)
            elif "הבאה" in btn_l:
                st.session_state.current_q_data = st.session_state.next_q_data
                st.session_state.q_counter += 1
                st.session_state.show_feedback = False
            st.rerun()

    with b_cols[1]:
        if st.button("🏠 תפריט"):
            st.session_state.step = 'menu'
            st.rerun()
    
    with b_cols[2]:
        st.markdown(
            '<a href="#top" class="nav-btn">🔝 למעלה</a>',
            unsafe_allow_html=True
        )
