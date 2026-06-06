import streamlit as st
import pytesseract
import numpy as np
import re
from PIL import Image, ImageFilter, ImageEnhance

st.set_page_config(page_title="MathInk2Text", page_icon="✏️")
st.title("✏️ MathInk2Text")
st.write("Upload a photo of a handwritten math expression to convert it to text.")

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

def preprocess(img):
    img = img.convert('L')  # grayscale
    img = ImageEnhance.Contrast(img).enhance(2.0)
    img = img.filter(ImageFilter.SHARPEN)
    return img

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
            processed = preprocess(img)
            config = '--psm 7 --oem 3 -c tessedit_char_whitelist=0123456789+-*/÷×()=. '
            text = pytesseract.image_to_string(processed, config=config).strip()
            text = normalize(text)
        if text:
            st.success(text)
            st.code(text)
        else:
            st.warning("Could not recognize expression. Try a clearer image.")