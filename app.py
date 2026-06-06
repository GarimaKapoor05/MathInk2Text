import streamlit as st
import boto3
import re
from PIL import Image
import io

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

with st.sidebar:
    st.header("AWS Configuration")
    aws_access_key = st.text_input("AWS Access Key ID", type="password")
    aws_secret_key = st.text_input("AWS Secret Access Key", type="password")
    aws_region = st.selectbox("Region", ["us-east-1", "us-west-2", "eu-west-1", "ap-south-1"])

uploaded = st.file_uploader("Upload image", type=["png", "jpg", "jpeg"])

if uploaded:
    img = Image.open(uploaded).convert("RGB")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Input Image")
        st.image(img, use_column_width=True)

    with col2:
        st.subheader("Recognized Expression")
        if not aws_access_key or not aws_secret_key:
            st.warning("Please enter your AWS credentials in the sidebar.")
        else:
            with st.spinner("Recognizing..."):
                try:
                    # Convert image to bytes
                    buffer = io.BytesIO()
                    img.save(buffer, format="PNG")
                    img_bytes = buffer.getvalue()

                    # Call AWS Textract
                    client = boto3.client(
                        'textract',
                        aws_access_key_id=aws_access_key,
                        aws_secret_access_key=aws_secret_key,
                        region_name=aws_region
                    )
                    response = client.detect_document_text(
                        Document={'Bytes': img_bytes}
                    )

                    # Extract text blocks
                    lines = [
                        block['Text']
                        for block in response['Blocks']
                        if block['BlockType'] == 'LINE'
                    ]
                    raw_text = " ".join(lines)
                    text = normalize(raw_text)

                    if text:
                        st.success(text)
                        st.code(text)
                    else:
                        st.warning("Could not recognize. Try a clearer image.")

                except Exception as e:
                    st.error(f"Error: {str(e)}")