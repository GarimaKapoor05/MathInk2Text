import streamlit as st
from pix2tex.cli import LatexOCR
from PIL import Image
import cv2
import numpy as np

st.set_page_config(page_title="MathInk2Text", page_icon="✏️")
st.title("✏️ MathInk2Text")
st.write("Upload a photo of a handwritten math expression to get LaTeX output.")

@st.cache_resource(show_spinner="Loading model...")
def load_model():
    return LatexOCR()

model = load_model()

def split_into_lines(img):
    # Convert to grayscale
    gray = np.array(img.convert('L'))
    
    # Threshold
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    
    # Find horizontal projection (sum of pixels per row)
    h_proj = np.sum(thresh, axis=1)
    
    # Find line boundaries
    in_line = False
    line_starts = []
    line_ends = []
    threshold = np.max(h_proj) * 0.05  # 5% of max as threshold
    
    for i, val in enumerate(h_proj):
        if not in_line and val > threshold:
            in_line = True
            line_starts.append(i)
        elif in_line and val <= threshold:
            in_line = False
            line_ends.append(i)
    
    if in_line:
        line_ends.append(len(h_proj))
    
    # Crop each line with padding
    lines = []
    padding = 10
    for start, end in zip(line_starts, line_ends):
        if end - start < 10:  # skip tiny lines
            continue
        top = max(0, start - padding)
        bottom = min(img.height, end + padding)
        line_img = img.crop((0, top, img.width, bottom))
        lines.append(line_img)
    
    return lines

uploaded = st.file_uploader("Upload image", type=["png", "jpg", "jpeg"])

if uploaded:
    img = Image.open(uploaded).convert("RGB")
    
    # Resize if too large
    max_size = 1500
    if max(img.size) > max_size:
        ratio = max_size / max(img.size)
        new_size = (int(img.width * ratio), int(img.height * ratio))
        img = img.resize(new_size, Image.LANCZOS)

    st.subheader("Input Image")
    st.image(img, width=600)
    
    st.divider()
    
    with st.spinner("Splitting into lines..."):
        lines = split_into_lines(img)
    
    st.success(f"Found {len(lines)} line(s) — recognizing each...")
    st.divider()

    full_latex = []

    for i, line_img in enumerate(lines):
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.caption(f"Line {i+1}")
            st.image(line_img, width=300)
        
        with col2:
            with st.spinner(f"Reading line {i+1}..."):
                try:
                    result = model(line_img)
                    full_latex.append(result)
                    st.caption("Rendered:")
                    st.latex(result)
                    st.caption("LaTeX:")
                    st.code(result, language="latex")
                except Exception as e:
                    st.warning(f"Could not read line {i+1}")
        
        st.divider()
    
    if full_latex:
        st.subheader("Complete LaTeX Output:")
        combined = " \\\\ ".join(full_latex)
        st.code(combined, language="latex")