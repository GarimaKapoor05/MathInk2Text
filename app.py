import streamlit as st
import requests
import re
from PIL import Image
import io

st.set_page_config(page_title="MathInk2Text", page_icon="✏️")
st.title("✏️ MathInk2Text")
st.write("Upload a photo of a handwritten math expression to convert it to text.")

HF_API_URL = "https://api-inference.huggingface.co/models/microsoft/trocr-base-handwritten"

def query(img, hf_token):
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    data = buffer.getvalue()
    headers = {"Authorization": f"Bearer {hf_token}"}
    response = requests.post(HF_API_URL, headers=headers, data=data)
    return response.json()

def normalize(text):
    text = re.sub(r'\s*=.*$', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    replacements = {
        'X': '*', 'x': '*', ':': '÷',
        'I': '1', 'l': '1', 'O': '0',
    }
    for wrong, correct in replacements.items():
        text = text.replace(wrong, correct)
    return text

with st.sidebar:
    st.header("Configuration")
    hf_token = st.text_input("HuggingFace Token (free)", type="password",
                              help="Get free token at huggingface.co/settings/tokens")
    st.markdown("[Get Free Token](https://huggingface.co/settings/tokens)")

uploaded = st.file_uploader("Upload image", type=["png", "jpg", "jpeg"])

if uploaded:
    img = Image.open(uploaded).convert("RGB")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Input Image")
        st.image(img, use_column_width=True)

    with col2:
        st.subheader("Recognized Expression")
        if not hf_token:
            st.warning("Please enter your HuggingFace token in the sidebar.")
        else:
            with st.spinner("Recognizing..."):
                try:
                    result = query(img, hf_token)
                    if isinstance(result, list):
                        text = normalize(result[0].get('generated_text', ''))
                    else:
                        text = str(result)
                    st.success(text)
                    st.code(text)
                except Exception as e:
                    st.error(f"Error: {str(e)}")