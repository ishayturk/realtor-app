def show_exam_system_intro():
    # CSS להצמדת הסטריפ לראש העמוד וביטול מרווחים של Streamlit
    st.markdown("""
        <style>
            .block-container { padding-top: 0rem !important; padding-bottom: 0rem !important; }
            .stApp header { visibility: hidden; }
            .upper-strip { 
                background-color: #ffffff; 
                padding: 5px 0px; 
                margin-bottom: 0px; 
            }
            .logo-img { vertical-align: middle; }
            .instruction-box { margin-top: 0px; padding-top: 10px; }
        </style>
    """, unsafe_allow_html=True)

    # --- פריים 1: סטריפ עליון (שורה 1-2 מהקצה) ---
    with st.container():
        c1, c2, c3 = st.columns([1, 2, 1])
        with c1:
            # לוגוPlaceholder - ניתן להחליף בנתיב לקובץ לוגו אמיתי
            st.markdown("### 🏠 מתווך בקליק") 
        with c2:
            st.markdown(f"<p style='text-align:center; padding-top:10px;'>👤 {st.session_state.user}</p>", unsafe_allow_html=True)
        with c3:
            if st.button("חזרה לתפריט", key="back_btn"):
                st.session_state.step = "menu"
                st.rerun()
    
    # --- פריים 2: תוכן הסבר (הכי צמוד שאפשר) ---
    st.markdown('<div class="instruction-box">', unsafe_allow_html=True)
    st.header("הוראות לנבחן")
    
    # דף ההסבר כפי שנשמר
    st.markdown("""
    מבחן זה נועד להכין אותך למבחן רישוי המתווכים הממשלתי. המבחן כולל 25 שאלות שנבחרו באופן רנדומלי מתוך מאגר השאלות שלמדנו, תוך הקפדה על חלוקה נכונה בין נושאי הסילבוס.
    
    * **משך הבחינה:** 90 דקות.
    * **מבנה:** 25 שאלות אמריקאיות.
    * **ניקוד:** כל שאלה מזכה ב-4 נקודות.
    * **מעבר:** ציון עובר הוא 60.
    * **כלים:** ניתן לדפדף בין השאלות ולהשאיר שאלות ריקות.
    """)
    
    st.divider()
    
    col_start = st.columns([1, 1, 1])
    with col_start[1]:
        if st.button("התחל בחינה", type="primary"):
            st.session_state.step = "exam_run"
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# שינוי הכפתור ב-app.py (עוגן 1213)
# במקום st.info("בקרוב!") תחת כפתור "גש/י למבחן":
# st.session_state.step = "exam_intro"; st.rerun()
