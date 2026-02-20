import streamlit as st

# הגדרות דף מינימליסטיות
st.set_page_config(layout="wide")

# CSS להצמדה מוחלטת לתקרה (כי הסטריפ נמצא באפליקציה המארחת)
st.markdown("""
<style>
    .block-container {
        padding-top: 0rem !important;
        padding-right: 1rem !important;
        padding-left: 1rem !important;
    }
    .stApp header {
        visibility: hidden;
    }
    * {
        direction: rtl;
        text-align: right;
    }
</style>
""", unsafe_allow_html=True)

# תוכן דף ההסבר (הדאטה של האפליקציה השנייה)
st.header("📋 הוראות לנבחן")

st.markdown("""
ברוך הבא למערכת דימוי בחינת המתווכים. 
לפני שתתחיל, אנא קרא בעיון את ההנחיות:

* **מבנה הבחינה:** 25 שאלות רב-ברירתיות (אמריקאיות).
* **זמן מוקצב:** 90 דקות (שעה וחצי).
* **ציון עובר:** 60 ומעלה.
* **חומר עזר:** אין להשתמש בחומר עזר חיצוני במהלך הבחינה.
* **ניווט:** ניתן לעבור בין השאלות ולשנות תשובות עד לרגע ההגשה.

בהצלחה!
""")

st.write("---")

if st.button("⏱️ התחל בחינה", type="primary"):
    st.write("כאן תופעל הלוגיקה של ייצור השאלות (בשלב הבא)")
