import streamlit as st
import google.generativeai as genai

# --- 1. הגדרות בסיסיות ---
st.set_page_config(page_title="מתווך בקליק", layout="centered")

st.markdown("""
    <style>
    [data-testid="stAppViewContainer"], .main, .block-container { direction: rtl !important; text-align: right !important; }
    h1, h2, h3 { text-align: center !important; }
    .stButton > button { width: 100%; font-weight: bold; height: 3em; }
    .lesson-box { background: white; padding: 20px; border-radius: 10px; border: 1px solid #ddd; direction: rtl; line-height: 1.6; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. אתחול משתנים ---
if "step" not in st.session_state:
    st.session_state.step = "login"
if "user" not in st.session_state:
    st.session_state.user = ""

# --- 3. לוגיקה ---
st.markdown("<h1>🏠 מתווך בקליק</h1>", unsafe_allow_html=True)
st.write("---")

# דף כניסה
if st.session_state.step == "login":
    name = st.text_input("הכנס שם מלא:")
    if st.button("כניסה למערכת"):
        if name:
            st.session_state.user = name
            st.session_state.step = "menu"
            st.rerun()  # זה מה שהיה חסר כדי להיכנס באמת

# תפריט ושיעור (באותו דף)
elif st.session_state.step == "menu":
    st.markdown(f"<h3 style='text-align: right;'>שלום, {st.session_state.user} 👋</h3>", unsafe_allow_html=True)
    
    topic = st.selectbox("בחר נושא ללימוד:", ["חוק המתווכים", "חוק המקרקעין", "חוק החוזים", "דיני מקרקעין"])
    
    if st.button("התחל שיעור בסטרימינג 🚀"):
        try:
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            model = genai.GenerativeModel('gemini-2.0-flash')
            
            # קריאה בסטרימינג
            response = model.generate_content(
                f"כתוב שיעור מפורט למבחן המתווכים על {topic} בעברית. השתמש בנקודות ברורות.",
                stream=True
            )
            
            st.write(f"### לומדים עכשיו: {topic}")
            placeholder = st.empty()
            full_text = ""
            
            for chunk in response:
                if chunk.text:
                    full_text += chunk.text
                    # עדכון חי של הטקסט על המסך
                    placeholder.markdown(f"<div class='lesson-box'>{full_text}</div>", unsafe_allow_html=True)
                
        except Exception as e:
            st.error(f"שגיאה: {str(e)}")

    st.write("---")
    if st.button("יציאה / החלף משתמש"):
        st.session_state.step = "login"
        st.rerun()
