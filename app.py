import streamlit as st
from pix2tex.cli import LatexOCR
from PIL import Image, ImageOps
import cv2
import numpy as np

st.set_page_config(page_title="MathInk2Text", page_icon="✏️", layout="wide")
st.title("✏️ MathInk2Text")
st.write("Upload a full page of handwritten equations — get LaTeX output line by line.")

@st.cache_resource(show_spinner="Loading model...")
def load_model():
    return LatexOCR()

model = load_model()

def split_into_lines(img, min_height=15, padding=8):
    gray = np.array(img.convert('L'))
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    h_proj = np.sum(thresh, axis=1)
    threshold = np.max(h_proj) * 0.04
    in_line = False
    starts, ends = [], []
    for i, val in enumerate(h_proj):
        if not in_line and val > threshold:
            in_line = True
            starts.append(i)
        elif in_line and val <= threshold:
            in_line = False
            ends.append(i)
    if in_line:
        ends.append(len(h_proj))
    lines = []
    for s, e in zip(starts, ends):
        if e - s < min_height:
            continue
        top = max(0, s - padding)
        bot = min(img.height, e + padding)
        lines.append(img.crop((0, top, img.width, bot)))
    return lines

# ── Step 1: Upload ──────────────────────────────────────────
st.markdown("### Step 1 — Upload image")
uploaded = st.file_uploader("", type=["png", "jpg", "jpeg"])

if uploaded:
    img = Image.open(uploaded).convert("RGB")

    # ── Step 2: Align ───────────────────────────────────────
    st.markdown("### Step 2 — Align & adjust")
    col1, col2 = st.columns([1, 1])

    with col1:
        rotation = st.slider("Rotate image", -30, 30, 0, 1)
        if rotation != 0:
            img = img.rotate(rotation, expand=True, fillcolor=(255, 255, 255))

        # Resize if too large
        max_size = 1500
        if max(img.size) > max_size:
            ratio = max_size / max(img.size)
            img = img.resize((int(img.width * ratio), int(img.height * ratio)), Image.LANCZOS)

        st.image(img, caption="Adjusted image", use_container_width=True)

    with col2:
        st.info("💡 Tips for best results:\n\n• Write equations on white paper\n\n• One equation per line\n\n• Use dark pen\n\n• Good lighting\n\n• Rotate until lines are horizontal")

    # ── Step 3: Split & Recognize ───────────────────────────
    st.markdown("### Step 3 — Line by line recognition")

    if st.button("Recognize equations", type="primary"):
        with st.spinner("Splitting into lines..."):
            lines = split_into_lines(img)

        if not lines:
            st.warning("No lines detected. Try adjusting the image.")
        else:
            st.success(f"Found {len(lines)} line(s)")
            full_latex = []

            for i, line_img in enumerate(lines):
                c1, c2 = st.columns([1, 2])
                with c1:
                    st.caption(f"Line {i+1}")
                    st.image(line_img, use_container_width=True)
                with c2:
                    with st.spinner(f"Reading line {i+1}..."):
                        try:
                            result = model(line_img)
                            full_latex.append(result)
                            st.caption("Rendered:")
                            st.latex(result)
                            st.caption("LaTeX:")
                            st.code(result, language="latex")
                        except Exception:
                            st.warning(f"Could not read line {i+1} — try a clearer image")
                st.divider()

            # ── Step 4: Combined output ──────────────────────
            if full_latex:
                st.markdown("### Step 4 — Combined LaTeX output")
                combined = " \\\\\n".join(full_latex)
                st.code(combined, language="latex")
                st.markdown("**Rendered combined:**")
                try:
                    st.latex(" \\\\ ".join(full_latex))
                except Exception:
                    st.info("Combined render unavailable — copy the LaTeX code above.")