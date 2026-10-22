
import os
import base64
from io import BytesIO

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI, APIError
from PIL import Image, UnidentifiedImageError

load_dotenv()

st.set_page_config(
    page_title="AI Image Understanding",
    page_icon="🔎",
    layout="wide",
)

st.title("AI Image Understanding System")
st.write("Powered by your Azure GPT-4o deployment")

endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
api_key = os.getenv("AZURE_OPENAI_API_KEY")
model = os.getenv("AZURE_OPENAI_MODEL", "gpt4o")


@st.cache_resource
def get_client(endpoint, api_key):
    return OpenAI(
        base_url=endpoint,
        api_key=api_key,
        timeout=60.0,
        max_retries=2,
    )


def encode_image(uploaded_file):
    raw = uploaded_file.getvalue()

    if not raw or len(raw) > 10 * 1024 * 1024:
        raise ValueError("Choose a non-empty image under 10 MB.")

    try:
        with Image.open(BytesIO(raw)) as img:
            img.verify()

        with Image.open(BytesIO(raw)) as img:
            fmt = img.format
    except (UnidentifiedImageError, OSError, ValueError):
        raise ValueError("The uploaded file is not a valid image.")

    mime_types = {
        "JPEG": "image/jpeg",
        "PNG": "image/png",
        "WEBP": "image/webp",
    }

    if fmt not in mime_types:
        raise ValueError("Use a JPEG, PNG, or WEBP image.")

    encoded = base64.b64encode(raw).decode("utf-8")
    return f"data:{mime_types[fmt]};base64,{encoded}"


uploaded = st.file_uploader(
    "Upload an image",
    type=["jpg", "jpeg", "png", "webp"],
)

question = st.text_area(
    "Ask a question about your image",
    value="Describe this image and identify its main objects and details.",
)

if uploaded:
    st.image(uploaded, caption="Uploaded image", width="stretch")

if st.button("Analyze image", type="primary", disabled=uploaded is None):
    if not endpoint or not api_key:
        st.error("Configure the endpoint and API key in your .env file.")
    elif not question.strip():
        st.warning("Enter a question about the image.")
    else:
        try:
            image_url = encode_image(uploaded)
            client = get_client(endpoint, api_key)

            with st.spinner("Analyzing image with GPT-4o..."):
                response = client.responses.create(
                    model=model,
                    input=[
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "input_text",
                                    "text": question,
                                },
                                {
                                    "type": "input_image",
                                    "image_url": image_url,
                                    "detail": "auto",
                                },
                            ],
                        }
                    ],
                )

            st.subheader("Analysis")
            st.markdown(response.output_text or "No text was returned.")

        except ValueError as exc:
            st.error(str(exc))
        except APIError as exc:
            st.error(
                f"Azure API request failed (HTTP {exc.status_code}). "
                "Check your key, endpoint, deployment, and permissions."
            )
        except Exception:
            st.error(
                "The request failed. Check your local terminal logs "
                "and Azure configuration."
            )
