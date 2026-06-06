import streamlit as st
import anthropic
import base64
import re
from PIL import Image
import io

st.set_page_config(page_title="MathInk2Text", page_icon="✏️")
st.title("✏️ MathInk2Text")
st.write("Upload a photo of a handwritten math expression to convert it to text.")

def image_to_base64(img):
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode()

def recognize_math(img, api_key):
    client = anthropic.Anthropic(api_key=api_key)
    img_b64 = image_to_base64(img)
    
    message = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=500,
        messages=[{
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/png",
                        "data": img_b64
                    }
                },
                {
                    "type": "text",
                    "text": "This image contains a handwritten mathematical expression. Extract and return ONLY the mathematical expression as plain text. Use standard symbols: + - * / for operators, ^ for powers, sqrt() for square roots. Return nothing else — just the expression itself."
                }
            ]
        }]
    )
    return message.content[0].text.strip()

# Sidebar for API key
with st.sidebar:
    st.header("Configuration")
    api_key = st.text_input("Anthropic API Key", type="password", 
                             help="Get your key at console.anthropic.com")
    st.markdown("[Get API Key](https://console.anthropic.com)")

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
            st.warning("Please enter your Anthropic API key in the sidebar.")
        else:
            with st.spinner("Recognizing..."):
                try:
                    result = recognize_math(img, api_key)
                    st.success(result)
                    st.code(result)
                except Exception as e:
                    st.error(f"Error: {str(e)}")