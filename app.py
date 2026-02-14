import streamlit as st
import google.generativeai as genai

# --- 1. הגדרות ועיצוב ---
st.set_page_config(page_title="מתווך בקליק", layout="centered")

st.markdown("""
    <style>
    [data-testid="stAppViewContainer"], .main, .block-container { direction: rtl !important; text-align: right !important; }
    h1, h2, h3 { text-align: center !important; }
    .stButton > button { width: 100%; font-weight: bold; }
    .lesson-box { background: white; padding: 20px; border-radius: 10px; border: 1px solid #ddd; direction: rtl; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. אתחול מוחלט ---
if "step" not in st.session_state: st.session_state.step = "login"
if "user" not in st.session_state: st.session_state.user = ""

# --- 3. לוגיקה באותו דף ---
st.markdown("<h1>🏠 מתווך בקליק</h1>", unsafe_allow_html=True)

if st.session_state.step == "login":
    name = st.text_input("שם מלא:")
    if st.button("כניסה"):
        if name:
            st.session_state.user = name
            st.session_state.step = "menu"
            st.rerun()

elif st.session_state.step == "menu":
    st.markdown(f"<h3 style='text-align: right;'>שלום, {st.session_state.user}</h3>", unsafe_allow_html=True)
    
    topic = st.selectbox("בחר נושא ללימוד:", ["חוק המתווכים", "חוק המקרקעין", "חוק החוזים"])
    
    if st.button("פתח שיעור בסטרימינג"):
        # כאן קורה הסטרימינג ישירות לדף הנוכחי
        try:
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            model = genai.GenerativeModel('gemini-2.0-flash')
            
            # יצירת הקריאה בסטרימינג
            response = model.generate_content(
                f"כתוב שיעור מפורט למבחן המתווכים על {topic} בעברית.",
                stream=True
            )
            
            st.write(f"### שיעור בנושא: {topic}")
            placeholder = st.empty()
            full_text = ""
            
            # הצגת הטקסט מילה אחרי מילה
            for chunk in response:
                full_text += chunk.text
                placeholder.markdown(f"<div class='lesson-box'>{full_text}</div>", unsafe_allow_html=True)
                
        except Exception as e:
            st.error(f"שגיאה: {str(e)}")

    st.write("---")
    if st.button("📝 עבור למבחן (בהקמה)"):
        st.info("המבחן יוטמע כאן בהמשך.")
