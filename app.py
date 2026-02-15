import streamlit as st

st.set_page_config(page_title="מתווך בקליק", layout="centered")

# עיצוב בסיסי
st.markdown("<style> * { direction: rtl !important; text-align: right !important; } </style>", unsafe_allow_html=True)

if 'user' not in st.session_state:
    st.session_state.user = ""

st.title("🏠 מתווך בקליק - בדיקת עלייה")

if not st.session_state.user:
    u = st.text_input("הזן שם מלא לבדיקה:")
    if st.button("כניסה"):
        if u:
            st.session_state.user = u
            st.rerun()
else:
    st.success(f"שלום {st.session_state.user}, המערכת עלתה בהצלחה!")
    st.write("אם אתה רואה את ההודעה הזו, סידרנו את ה-404.")
    if st.button("התנתק"):
        st.session_state.user = ""
        st.rerun()
