def stream_ai_lesson(p):
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        m = genai.GenerativeModel('gemini-2.0-flash')
        # החזרת ההנחיה המפורטת כדי למנוע חומר דל
        full_p = (
            f"{p}. כתוב שיעור הכנה מעמיק ומפורט למבחן המתווכים. "
            f"חובה לפרט סעיפי חוק רלוונטיים, הסברים משפטיים ודוגמאות מעשיות."
        )
        response = m.generate_content(full_p, stream=True)
        placeholder = st.empty()
        full_text = ""
        for chunk in response:
            full_text += chunk.text
            placeholder.markdown(full_text + "▌")
        placeholder.markdown(full_text)
        return full_text
    except:
        return "⚠️ תקלה בטעינה."
