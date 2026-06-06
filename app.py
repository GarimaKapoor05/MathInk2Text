import streamlit as st
from pix2tex.cli import LatexOCR
from PIL import Image

st.set_page_config(page_title="MathInk2Text", page_icon="✏️")
st.title("✏️ MathInk2Text")
st.write("Upload a photo of a handwritten math expression to get LaTeX output.")

@st.cache_resource(show_spinner="Loading model...")
def load_model():
    return LatexOCR()

model = load_model()

uploaded = st.file_uploader("Upload image", type=["png", "jpg", "jpeg"])

if uploaded:
    img = Image.open(uploaded).convert("RGB")
    
    # Resize if too large
    max_size = 1000
    if max(img.size) > max_size:
        ratio = max_size / max(img.size)
        new_size = (int(img.width * ratio), int(img.height * ratio))
        img = img.resize(new_size, Image.LANCZOS)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Input Image")
        st.image(img, width=400)

    with col2:
        st.subheader("Recognized Expression")
        with st.spinner("Recognizing..."):
            result = model(img)

        st.subheader("Rendered Math:")
        st.latex(result)

        st.subheader("LaTeX Code:")
        st.code(result, language="latex")