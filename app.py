elif st.session_state.step == "exam_mode":
    # סטריפ עליון - פריים 1
    # רקע אפור בהיר, צמוד לתקרה
    st.markdown("""
        <style>
        .exam-strip {
            background-color: #f0f2f6;
            padding: 10px 20px;
            border-radius: 10px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 5px;
        }
        </style>
    """, unsafe_allow_html=True)

    with st.container():
        # חלוקה ל-3 טורים בתוך הסטריפ
        c1, c2, c3 = st.columns([2, 2, 1])
        
        with c1:
            # לוגו ושם אפליקציה בצד ימין
            st.markdown("### 🏠 מתווך בקליק")
            
        with c2:
            # שם המשתמש במרכז
            st.markdown(f"<center><h3>👤 {st.session_state.user}</h3></center>", 
                        unsafe_allow_html=True)
            
        with c3:
            # כפתור חזרה בצד שמאל
            if st.button("↩️ לתפריט הראשי"):
                st.session_state.step = "menu"
                st.rerun()

    # פריים תחתון - האפליקציה השנייה (דף ההסבר)
    # גובה מותאם אישית כדי למנוע גלילה מיותרת
    exam_link = "https://fullrealestatebroker-yevuzewxde4obgrpgacrpc.streamlit.app/?embedded=true"
    components.iframe(exam_link, height=850, scrolling=True)
