import streamlit as st
import requests
import json

st.set_page_config(page_title="מתווך בקליק", layout="centered")

# עיצוב RTL
st.markdown("<style>.stApp {text-align: right; direction: rtl;}</style>", unsafe_allow_html=True)
st.title("🎓 מתווך בקליק - חיבור ישיר")

topic = st.selectbox("בחר נושא:", ["חוק המתווכים", "חוק המקרקעין", "דיני חוזים"])

if st.button("ייצר שיעור"):
    if "GEMINI_API_KEY" not in st.secrets:
        st.error("חסר מפתח API ב-Secrets")
    else:
        api_key = st.secrets["GEMINI_API_KEY"]
        
        # שימוש בכתובת v1 (היציבה) במקום v1beta שעושה שגיאות 404
        url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={api_key}"
        
        payload = {
            "contents": [{
                "parts": [{"text": f"כתוב שיעור קצר בעברית על {topic}"}]
            }]
        }
        headers = {'Content-Type': 'application/json'}

        with st.spinner("מתחבר ישירות לשרתי גוגל..."):
            try:
                response = requests.post(url, headers=headers, json=payload)
                res_json = response.json()
                
                if response.status_code == 200:
                    answer = res_json['candidates'][0]['content']['parts'][0]['text']
                    st.success("החיבור הצליח!")
                    st.markdown("---")
                    st.write(answer)
                else:
                    st.error(f"שגיאה מהשרת: {response.status_code}")
                    st.json(res_json) # מציג את השגיאה המדויקת מגוגל
            except Exception as e:
                st.error(f"תקלה מקומית: {e}")
