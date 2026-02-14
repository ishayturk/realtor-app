try:
            # ניסיון ראשון עם דור 3
            model = genai.GenerativeModel('gemini-3-flash-preview')
            responses = model.generate_content(
                f"כתוב שיעור קצר וממוקד על {topic} למבחן המתווכים. השתמש בכותרות ונקודות.",
                stream=True
            )
            for chunk in responses:
                full_response += chunk.text
                placeholder.markdown(f'<div dir="rtl">{full_response}</div>', unsafe_allow_html=True)
                
        except Exception as e:
            if "503" in str(e):
                st.warning("Gemini 3 עמוס כרגע, עובר אוטומטית ל-Gemini 2.5 המהיר...")
                # גיבוי למודל 2.5 (שורה 0 ברשימה שלך)
                model_backup = genai.GenerativeModel('gemini-2.5-flash')
                response = model_backup.generate_content(f"כתוב שיעור על {topic}")
                placeholder.markdown(f'<div dir="rtl">{response.text}</div>', unsafe_allow_html=True)
            else:
                st.error(f"תקלה: {e}")
