import streamlit as st
from PIL import Image
import requests
import base64
import io
import json

st.set_page_config(page_title="MathInk2Text", page_icon="✏️", layout="wide")
st.title("✏️ MathInk2Text")
st.write("Upload handwritten math equations — get LaTeX output instantly.")

@st.cache_resource
def get_credentials():
    return st.secrets.get("MATHPIX_APP_ID", ""), st.secrets.get("MATHPIX_APP_KEY", "")

def recognize_math(img, app_id, app_key):
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    img_b64 = base64.b64encode(buffer.getvalue()).decode()
    
    response = requests.post(
        "https://api.mathpix.com/v3/text",
        headers={
            "app_id": app_id,
            "app_key": app_key,
            "Content-Type": "application/json"
        },
        json={
            "src": f"data:image/png;base64,{img_b64}",
            "formats": ["text", "latex_styled"],
            "math_inline_delimiters": ["$", "$"],
            "rm_spaces": True
        }
    )
    return response.json()

with st.sidebar:
    st.header("Configuration")
    app_id = st.text_input("Mathpix App ID", type="password")
    app_key = st.text_input("Mathpix App Key", type="password")
    st.markdown("[Get free credentials](https://mathpix.com)")

uploaded = st.file_uploader("Upload image", type=["png", "jpg", "jpeg"])

if uploaded:
    img = Image.open(uploaded).convert("RGB")
    
    # Resize if too large
    max_size = 1500
    if max(img.size) > max_size:
        ratio = max_size / max(img.size)
        img = img.resize((int(img.width * ratio), int(img.height * ratio)), Image.LANCZOS)

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("Input Image")
        rotation = st.slider("Rotate if needed", -30, 30, 0, 1)
        if rotation != 0:
            img = img.rotate(rotation, expand=True, fillcolor=(255, 255, 255))
        st.image(img, use_container_width=True)

    with col2:
        st.subheader("Recognized Output")
        if not app_id or not app_key:
            st.warning("Enter your Mathpix credentials in the sidebar.")
        else:
            with st.spinner("Recognizing..."):
                try:
                    result = recognize_math(img, app_id, app_key)
                    
                    if "latex_styled" in result:
                        latex = result["latex_styled"]
                        st.caption("Rendered math:")
                        st.latex(latex)
                        st.caption("LaTeX code:")
                        st.code(latex, language="latex")
                    
                    if "text" in result:
                        st.caption("Plain text:")
                        st.code(result["text"])
                        
                except Exception as e:
                    st.error(f"Error: {str(e)}")