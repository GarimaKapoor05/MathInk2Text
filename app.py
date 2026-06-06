import streamlit as st
import easyocr
import numpy as np
import re
from PIL import Image

st.set_page_config(page_title="MathInk2Text", page_icon="✏️")
st.title("✏️ MathInk2Text")
st.write("Upload a photo of a handwritten math expression to convert it to text.")

@st.cache_resource(show_spinner="Loading OCR model...")
def load_model():
    return easyocr.Reader(['en'], gpu=False, download_enabled=True)

def normalize(text):
    text = re.sub(r'\s*=.*$', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    replacements = {
        'X': '*', 'x': '*', ':': '÷',
        'I': '1', 'l': '1', 'O': '0',
        'z': '2', 'Z': '2', '~': '-',
    }
    for wrong, correct in replacements.items():
        text = text.replace(wrong, correct)
    text = re.sub(r'\s+\d$', '', text).strip()
    return text

reader = load_model()

uploaded = st.file_uploader("Upload image", type=["png", "jpg", "jpeg"])

if uploaded:
    img = Image.open(uploaded).convert("RGB")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Input Image")
        st.image(img, use_column_width=True)

    with col2:
        st.subheader("Recognized Expression")
        with st.spinner("Recognizing..."):
            result = reader.readtext(np.array(img), detail=0)
            text = normalize(" ".join(result))

        if text:
            st.success(text)
            st.code(text)
        else:
            st.warning("Could not recognize. Try a clearer image.")