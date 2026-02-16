# --- CSS (Dark Mode Support & RTL) ---
st.markdown("""
<style>
    * { direction: rtl; text-align: right; }
    
    /* תמיכה במצב כהה ובהיר */
    :root { --text-color: inherit; --bg-card: rgba(255,255,255,0.05); }
    
    .user-strip { 
        background-color: var(--bg-card); 
        padding: 10px; border-radius: 8px; margin-bottom: 20px; 
        font-weight: bold; text-align: left; border: 1px solid rgba(128,128,128,0.3);
    }
    
    .stButton>button { width: 100%; border-radius: 8px; height: 3.5em; font-weight: bold; }
    
    .question-box { 
        background-color: rgba(128,128,128,0.1); 
        padding: 20px; border-radius: 10px; border: 1px solid rgba(128,128,128,0.2); 
        margin-top: 20px; color: var(--text-color);
    }

    [data-testid="stSidebar"] { direction: rtl; }
</style>
""", unsafe_allow_html=True)
