import streamlit as st
import requests

st.set_page_config(page_title="מתווך בקליק 3.0", layout="centered")
st.markdown("<style>.stApp {text-align: right; direction: rtl;}</style>", unsafe_allow_html=True)

st.title("🚀 מתווך בקליק - דור 3")

if "GEMINI_API_KEY" not in st.secrets:
    st.error("חסר מפתח API ב-Secrets")
else:
    api_key = st.secrets["GEMINI_API_KEY"]
    
    # בגרסה 3, אנחנו משתמשים בנתיב ה-v1beta עם שם המודל החדש
    # ננסה את השם הנפוץ ביותר לגרסה 3 כרגע
    model_name = "gemini-3-flash-experimental" 
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"

    if st.button("ייצר שיעור עם Gemini 3"):
        payload = {
            "contents": [{"parts": [{"text": "כתוב הסבר קצר על חוק המתווכים בישראל"}]}]
        }
        
        try:
            response = requests.post(url, json=payload)
            res_data = response.json()

            if response.status_code == 200:
                text = res_data['candidates'][0]['content']['parts'][0]['text']
                st.success("התחברנו בהצלחה ל-Gemini 3!")
                st.write(text)
            else:
                st.warning(f"מודל {model_name} לא הגיב (שגיאה {response.status_code}).")
                st.info("מנסה למשוך את רשימת המודלים המדויקת שפתוחה לך...")
                
                # כאן הקוד בודק מה גוגל מרשה לך באמת
                list_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
                list_res = requests.get(list_url).json()
                
                # מציג לך את השמות שאנחנו צריכים להשתמש בהם
                st.write("אלו השמות שגוגל מאשרת למפתח שלך:")
                model_names = [m['name'] for m in list_res.get('models', [])]
                st.json(model_names)
                
        except Exception as e:
            st.error(f"תקלה: {e}")
