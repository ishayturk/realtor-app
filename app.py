elif st.session_state.step == "menu":
    st.subheader(f"👤 שלום, {st.session_state.user}")
    c1, c2 = st.columns(2)
    
    with c1:
        # כפתור לימוד - מעביר לשלב ה-study באפליקציה הזו
        if st.button("📚 לימוד לפי נושאים"):
            st.session_state.step = "study"
            st.rerun()
            
    with c2:
        # כפתור מבחן - שומר על העיצוב המקורי ושולח לאפליקציה השנייה
        if st.button("⏱️ גש/י למבחן"):
            user_name = st.session_state.user.replace(" ", "%20")
            exam_url = f"https://fullrealestatebroker-yevuzewxde4obgrpgacrpc.streamlit.app/?user={user_name}"
            # הרצת הלינק באותו חלון בלי לשנות את מראה הכפתור
            st.components.v1.html(f"""
                <script>
                    window.parent.location.href = "{exam_url}";
                </script>
            """, height=0)
