elif st.session_state.step == "exam_mode":
    # CSS ייעודי לסטריפ דק והצמדת ה-iframe למעלה
    st.markdown("""
        <style>
        /* ביטול פאדינג של הקונטיינר הראשי */
        .block-container { padding-top: 0rem !important; }
        
        /* צמצום גובה הסטריפ */
        [data-testid="column"] { padding: 0px !important; }
        
        /* הצמדת ה-iframe לתקרה */
        iframe { margin-top: -30px !important; }
        
        /* עיצוב שם המשתמש למניעת גובה מיותר */
        .user-name { 
            font-size: 1.2rem; 
            font-weight: bold; 
            margin-top: 5px;
        }
        </style>
    """, unsafe_allow_html=True)

    # הסטריפ - שורה אחת בלבד מתחת לתקרה
    with st.container():
        # שימוש ב-gap קטן למניעת מרווחים בין העמודות
        c1, c2, c3 = st.columns([1.5, 2, 1], gap="small")
        
        with c1:
            # לוגו ושם מימין
            st.markdown("### 🏠 מתווך בקליק")
            
        with c2:
            # שם המשתמש במרכז - ללא כותרת h3 שתופסת מקום
            st.markdown(f'<div class="user-name" style="text-align:center;">👤 {st.session_state.user}</div>', 
                        unsafe_allow_html=True)
            
        with c3:
            # כפתור חזרה משמאל
            if st.button("↩️ לתפריט הראשי"):
                st.session_state.step = "menu"
                st.rerun()

    # טעינת המבחן - עם גובה מלא והצמדה לסטריפ
    ex_url = "https://fullrealestatebroker-yevuzewxde4obgrpgacrpc.streamlit.app/?embedded=true"
    components.iframe(ex_url, height=1000, scrolling=True)
