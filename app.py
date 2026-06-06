import streamlit as st
import easyocr
import numpy as np
import re
from PIL import Image

st.set_page_config(page_title="Handwritten Math Recognition", page_icon="✏️")
st.title("✏️ Handwritten Math Expression Recognition")
st.write("Upload a photo of a handwritten math expression to convert it to text.")

@st.cache_resource
def load_model():
    return easyocr.Reader(['en'])

reader = load_model()

def normalize(text):
    text = re.sub(r'\s*=.*$', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    replacements = {
        'X': '*', 'x': '*', ':': '÷', '_': '÷',
        'I': '1', 'l': '1', 'O': '0', 'z': '2',
        'Z': '2', '~': '-', '>': '2', "'": '1',
    }
    for wrong, correct in replacements.items():
        text = text.replace(wrong, correct)
    text = re.sub(r'\s+\d$', '', text).strip()
    return text

uploaded = st.file_uploader("Upload image", type=["png", "jpg", "jpeg"])

if uploaded:
    img = Image.open(uploaded).convert("RGB")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Input Image")
        st.image(img, use_column_width=True)
    
    with col2:
        st.subheader("Recognized Expression")
        with st.spinner("Reading..."):
            result = reader.readtext(np.array(img), detail=0)
            text = normalize(" ".join(result))
        st.success(text)
        st.code(text)