# גרסה: 1087 | תאריך: 16/02/2026 | שעה: 14:15 | סטטוס: החזרת Spinner לשאלון

import streamlit as st
import google.generativeai as genai
import json, re, time

st.set_page_config(page_title="מתווך בקליק", layout="centered")

st.markdown("""
<style>
    * { direction: rtl !important; text-align: right !important; }
    .stApp { background-color: #ffffff; }
    .lesson-box { 
        background-color: #ffffff; 
        padding: 30px; 
        border-right: 6px solid #1E88E5; 
        border-radius: 4px; 
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        margin-bottom: 25px; 
        line-height: 1.8;
        font-size: 1.1rem;
    }
    .question-card { 
        background-color: #ffffff; 
        padding: 25px; 
        border: 1px solid #e0e0e0; 
        border-radius: 12px; 
        margin-bottom: 20px; 
    }
    .version-footer { color: #bbbbbb; font-size: 0.7rem; text-align: center !important; margin-top: 50px; }
</style>
""", unsafe_allow_html=True)

S = st.session_state
if 'step' not in S:
    S.update({'user': '', 'step': 'login', 'lt': '', 'qi': 0, 'qq': [], 'current_topic': ''})

def fetch_content_stream(prompt):
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-2.0-flash')
    try:
        return model.generate_content(prompt, stream=True)
    except Exception as e:
        st.error(f"שגיאת תקשורת: {str(e)}")
        return None

st.title("🏠 מתווך בקליק")

if S.step == "login":
    u = st.text_input("שם מלא:")
    if st.button("כניסה"):
        if u: S.user = u; S.step = "menu"; st.rerun()

elif S.step == "menu":
    st.write(f"### שלום, {S.user}")
    if st.button("📚 לימוד לפי נושאים", use_container_width=True):
        S.step = "study"; st.rerun()
    if st.button("⏱️ סימולציית מבחן", use_container_width=True):
        S.current_topic = "מבחן כללי"; S.step = "quiz_prep"; st.rerun()

elif S.step == "study":
    topics = ["חוק המתווכים במקרקעין", "חוק המקרקעין", "חוק המכר (דירות)", "חוק הגנת הצרכן", "אתיקה מקצועית", "חוק החוזים", "מיסוי מקרקעין", "חוק התכנון והבנייה", "חוק הגנת הדייר", "חוק הירושה"]
    sel = st.selectbox("בחר נושא:", topics)
    
    if st.button("📖 התחל שיעור מקיף"):
        S.lt = ""
        placeholder = st.empty()
        full_text = ""
        parts = [
            f"חלק 1: כתוב מבוא מפורט וסעיפי חוק יסודיים עבור {sel} עבור מבחן המתווכים.",
            f"חלק 2: עבור {sel}, כתוב על חובות המתווך, איסורים, פסיקה רלוונטית ומקרים מיוחדים.",
            f"חלק 3: סיכום עבור {sel} - דגשים קריטיים למבחן, מוקשים וצ'ק-ליסט לשינון."
        ]
        for i, p in enumerate(parts):
            stream = fetch_content_stream(p)
            if stream:
                if i > 0: full_text += "\n\n---\n"
                for chunk in stream:
                    full_text += chunk.text
                    placeholder.markdown(f"<div class='lesson-box'>{full_text}</div>", unsafe_allow_html=True)
                time.sleep(1)
        S.lt = full_text
        S.current_topic = sel

    if S.lt:
        if st.button("✍️ עבור לשאלות תרגול"):
            S.step = "quiz_prep"; st.rerun()
    
    if st.button("🏠 חזרה לתפריט"):
        S.lt = ""; S.step = "menu"; st.rerun()

elif S.step == "quiz_prep":
    # החזרת החיווי הויזואלי כאן
    with st.spinner("מייצר 10 שאלות מותאמות אישית... אנא המתן"):
        p = f"צור 10 שאלות אמריקאיות על {S.current_topic}. החזר JSON בלבד: " + "[{'q':'','options':['','','',''],'correct':'','reason':''}]"
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-2.0-flash')
        try:
            res = model.generate_content(p).text
            match = re.search(r'\[.*\]', res, re.DOTALL)
            if match:
                S.qq = json.loads(match.group())
                S.qi = 0; S.step = "quiz"; st.rerun()
        except:
            st.error("עומס זמני ביצירת השאלות. חוזר לתפריט..."); time.sleep(2); S.step = "menu"; st.rerun()

elif S.step == "quiz":
    if S.qq:
        q = S.qq[S.qi]
        st.markdown(f"<p style='color:#1E88E5; font-weight:bold;'>שאלה {S.qi + 1} מתוך {len(S.qq)}</p>", unsafe_allow_html=True)
        st.markdown(f"<div class='question-card'><b>{q['q']}</b></div>", unsafe_allow_html=True)
        ans = st.radio("בחר תשובה:", q['options'], key=f"q_{S.qi}", index=None)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔍 בדוק"):
                if ans:
                    if ans == q['correct']: st.success(f"נכון! {q['reason']}")
                    else: st.error(f"טעות. הנכון: {q['correct']}")
                else: st.warning("אנא בחר תשובה.")
        with col2:
            if st.button("🏠 חזרה לתפריט"):
                S.step = "menu"; S.lt = ""; S.qq = []; st.rerun()
        
        if st.button("השאלה הבאה ➡️"):
            if S.qi < len(S.qq) - 1:
                S.qi += 1; st.rerun()
            else:
                st.success("סיימת את השאלון!"); time.sleep(2); S.step = "menu"; S.lt = ""; st.rerun()

st.markdown(f"<div class='version-footer'>גרסה: 1087 | 16/02/2026 14:15</div>", unsafe_allow_html=True)
