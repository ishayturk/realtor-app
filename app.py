import streamlit as st
import requests

# הגדרות דף ועיצוב
st.set_page_config(page_title="מתווך בקליק 3.0", layout="centered")

# הזרקת CSS לעיצוב RTL ושיפור המראה
st.markdown("""
    <style>
    /* יישור כללי לימין */
    .stApp {
        direction: rtl;
        text-align: right;
    }
    
    /* עיצוב הכותרת */
    h1 {
        color: #2E4053;
        padding-bottom: 20px;
    }
    
    /* עיצוב תיבת הבחירה */
    .stSelectbox label {
        font-size: 1.2rem !important;
        font-weight: bold !important;
    }
    
    /* עיצוב הכפתור */
    div.stButton > button:first-child {
        background-color: #007bff;
        color: white;
        width: 100%;
        border-radius: 10px;
        height: 3em;
        font-size: 1.2rem;
        font-weight: bold;
        border: none;
        box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    div.stButton > button:hover {
        background-color: #0056b3;
        color: white;
    }

    /* עיצוב תיבת התוצאה */
    .result-box {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 15px;
        border-right: 5px solid #007bff;
        margin-top: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🎓 מתווך בקליק")
st.subheader("הכנה למבחן המתווכים בעזרת Gemini 3")

# יצירת טופס בחירה
with st.container():
    topic = st.selectbox(
        "בחר נושא ללימוד:", 
        ["חוק המתווכים", "חוק המקרקעין", "דיני חוזים", "דיני התכנון והבנייה", "חוק הגנת הצרכן"]
    )
    
    generate_btn = st.button("ייצר שיעור עכשיו")

if generate_btn:
    if "GEMINI_API_KEY" not in st.secrets:
        st.error("שגיאה: מפתח ה-API לא מוגדר ב-Secrets.")
    else:
        api_key = st.secrets["GEMINI_API_KEY"]
        model_id = "gemini-3-flash-preview"
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_id}:generateContent?key={api_key}"
        
        # הנחיה (Prompt) משופרת כדי שה-AI יכתוב יפה
        prompt = f"""
        אתה מרצה מומחה למקרקעין. 
        כתוב שיעור מקיף, ברור ומסודר בעברית על {topic} עבור סטודנטים המתכוננים למבחן רשם המתווכים.
        השתמש בנקודות (bullet points), כותרות משנה והדגשות.
        """
        
        payload = {
            "contents": [{"parts": [{"text": prompt}]}]
        }
        
        with st.spinner("Gemini 3 חושב ומייצר שיעור..."):
            try:
                response = requests.post(url, json=payload)
                res_data = response.json()
                
                if response.status_code == 200:
                    answer = res_data['candidates'][0]['content']['parts'][0]['text']
                    
                    st.markdown("---")
                    # הצגת התוצאה בתוך "קונטיינר" מעוצב
                    st.markdown(f'<div class="result-box">{answer}</div>', unsafe_allow_html=True)
                    st.balloons()
                else:
                    st.error(f"שגיאה {response.status_code}")
                    st.json(res_data)
            except Exception as e:
                st.error(f"תקלה: {e}")

# הערה בתחתית הדף
st.markdown("<br><p style='text-align: center; color: gray;'>פותח בעזרת בינה מלאכותית דור 3</p>", unsafe_allow_html=True)
