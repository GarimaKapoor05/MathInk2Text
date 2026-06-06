import streamlit as st
import google.generativeai as genai
from PIL import Image
import io

st.set_page_config(page_title="MathInk2Text", page_icon="✏️")
st.title("✏️ MathInk2Text")
st.write("Upload a photo of a handwritten math expression to convert it to text.")

with st.sidebar:
    st.header("Configuration")
    api_key = st.text_input("Google Gemini API Key (free)", type="password",
                             help="Get free key at aistudio.google.com")
    st.markdown("[Get Free Key](https://aistudio.google.com)")

uploaded = st.file_uploader("Upload image", type=["png", "jpg", "jpeg"])

if uploaded:
    img = Image.open(uploaded).convert("RGB")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Input Image")
        st.image(img, use_column_width=True)

    with col2:
        st.subheader("Recognized Expression")
        if not api_key:
            st.warning("Please enter your Gemini API key in the sidebar.")
        else:
            with st.spinner("Recognizing..."):
                try:
                    genai.configure(api_key=api_key)
                    model = genai.GenerativeModel("gemini-1.5-flash")
                    
                    buffer = io.BytesIO()
                    img.save(buffer, format="PNG")
                    buffer.seek(0)
                    
                    response = model.generate_content([
                        "This image contains a handwritten mathematical expression. Extract and return ONLY the math expression as plain text. Use standard symbols: + - * / for operators, ^ for powers. Return nothing else.",
                        Image.open(buffer)
                    ])
                    text = response.text.strip()
                    st.success(text)
                    st.code(text)
                except Exception as e:
                    st.error(f"Error: {str(e)}")