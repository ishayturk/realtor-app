import streamlit as st
import requests

# הגדרות דף
st.set_page_config(page_title="מתווך בקליק 3.0", layout="centered")
st.markdown("<style>.stApp {text-align: right; direction: rtl;}</style>", unsafe_allow_html=True)

st.title("🚀 מתווך בקליק - Gemini 3")

# בחירת נושא
topic = st.selectbox("בחר נושא ללימוד:", ["חוק המתווכים", "חוק המקרקעין", "דיני חוזים"])

if st.button("ייצר שיעור"):
    if "GEMINI_API_KEY" not in st.secrets:
        st.error("חסר מפתח API ב-Secrets")
    else:
        api_key = st.secrets["GEMINI_API_KEY"]
        
        # שימוש בשם המדויק מהרשימה שלך (שורה 24)
        model_id = "gemini-3-flash-preview"
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_id}:generateContent?key={api_key}"
        
        payload = {
            "contents": [{
                "parts": [{"text": f"כתוב שיעור מפורט בעברית על {topic} למבחן המתווכים בישראל."}]
            }]
        }
        
        with st.spinner("מפעיל את Gemini 3 החדש..."):
            try:
                response = requests.post(url, json=payload)
                res_data = response.json()
                
                if response.status_code == 200:
                    # חילוץ התשובה מהמבנה של גוגל
                    answer = res_data['candidates'][0]['content']['parts'][0]['text']
                    st.success("החיבור הצליח!")
                    st.markdown("---")
                    st.markdown(answer)
                else:
                    st.error(f"שגיאה {response.status_code}")
                    st.json(res_data)
            except Exception as e:
                st.error(f"תקלה טכנית: {e}")
