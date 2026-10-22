
import os
import re
import xml.etree.ElementTree as ET

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI, APIError

load_dotenv()

st.set_page_config(
    page_title="AI SVG Image Generator",
    page_icon="🎨",
    layout="wide",
)

st.title("AI SVG Image Generator")
st.write("Describe an illustration and generate downloadable SVG artwork.")

SVG_NS = "http://www.w3.org/2000/svg"

ALLOWED_TAGS = {
    "svg", "g", "rect", "circle", "ellipse", "line",
    "polyline", "polygon", "path", "text", "tspan",
    "defs", "linearGradient", "radialGradient", "stop",
    "clipPath",
}

ALLOWED_ATTRIBUTES = {
    "xmlns", "width", "height", "viewBox", "version",
    "x", "y", "x1", "y1", "x2", "y2", "cx", "cy",
    "r", "rx", "ry", "d", "points", "fill", "stroke",
    "stroke-width", "stroke-linecap", "stroke-linejoin",
    "opacity", "fill-opacity", "stroke-opacity",
    "transform", "font-size", "font-family", "font-weight",
    "text-anchor", "dominant-baseline", "offset",
    "stop-color", "stop-opacity", "id", "clip-path",
    "gradientUnits", "gradientTransform",
}

SYSTEM_PROMPT = """
You are an SVG illustration designer.

Create a complete, valid, self-contained SVG illustration
based on the user's description.

Requirements:
- Return only SVG markup, without Markdown fences.
- Start with an <svg> root element.
- Use a viewBox of 0 0 512 512.
- Use vector shapes, paths, gradients, and text as appropriate.
- Do not use JavaScript, event handlers, foreignObject,
  external URLs, external images, or embedded HTML.
- Make the artwork visually attractive and well composed.
- Keep the SVG reasonably compact.
"""


def extract_svg(text):
    """Extract SVG markup if the model adds surrounding text."""
    match = re.search(
        r"<svg\b[\s\S]*?</svg\s*>",
        text,
        flags=re.IGNORECASE,
    )

    if not match:
        raise ValueError("The model did not return valid SVG markup.")

    return match.group(0)


def sanitize_svg(svg_text):
    """Allow only basic SVG elements and safe attributes."""
    try:
        root = ET.fromstring(svg_text)
    except ET.ParseError as exc:
        raise ValueError("The generated SVG is not valid XML.") from exc

    root_name = root.tag.split("}")[-1]

    if root_name != "svg":
        raise ValueError("The SVG root element is missing.")

    def clean(element):
        tag = element.tag.split("}")[-1]

        if tag not in ALLOWED_TAGS:
            raise ValueError(f"Unsupported SVG element: {tag}")

        # Remove non-whitelisted attributes, including event handlers.
        for attribute in list(element.attrib):
            name = attribute.split("}")[-1]

            if name not in ALLOWED_ATTRIBUTES:
                del element.attrib[attribute]
                continue

            value = element.attrib[attribute].strip()

            if (
                re.search(r"javascript\s*:", value, re.IGNORECASE)
                or re.search(r"data\s*:", value, re.IGNORECASE)
                or re.search(r"url\s*\(\s*['\"]?\s*https?:", value,
                             re.IGNORECASE)
                or re.search(r"expression\s*\(", value, re.IGNORECASE)
            ):
                del element.attrib[attribute]

        for child in list(element):
            child_name = child.tag.split("}")[-1]

            if child_name not in ALLOWED_TAGS:
                element.remove(child)
            else:
                clean(child)

    clean(root)

    # Ensure the SVG namespace is present.
    root.set("xmlns", SVG_NS)

    return ET.tostring(root, encoding="unicode")


def generate_svg(prompt):
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "").strip()
    api_key = os.getenv("AZURE_OPENAI_API_KEY", "").strip()
    deployment = os.getenv("AZURE_OPENAI_MODEL", "").strip()

    if not endpoint or not api_key or not deployment:
        raise ValueError(
            "Configure AZURE_OPENAI_ENDPOINT, "
            "AZURE_OPENAI_API_KEY, and AZURE_OPENAI_MODEL in .env."
        )

    client = OpenAI(
        base_url=endpoint,
        api_key=api_key,
        timeout=120.0,
        max_retries=2,
    )

    response = client.responses.create(
        model=deployment,
        input=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": (
                    "Create an SVG illustration for this prompt:\n"
                    + prompt
                ),
            },
        ],
    )

    return sanitize_svg(extract_svg(response.output_text or ""))


prompt = st.text_area(
    "Describe the image you want",
    placeholder=(
        "Example: Create a minimalist blue and purple "
        "mountain landscape with a sunset and pine trees."
    ),
    height=120,
)

if st.button("Generate SVG", type="primary"):
    if not prompt.strip():
        st.warning("Please enter an image description.")
    elif len(prompt) > 2000:
        st.warning("Keep your prompt under 2,000 characters.")
    else:
        try:
            with st.spinner("Generating vector artwork..."):
                svg_result = generate_svg(prompt.strip())

            st.session_state["generated_svg"] = svg_result
            st.success("SVG artwork generated!")

        except ValueError as exc:
            st.error(str(exc))

        except APIError as exc:
            st.error(
                f"Azure API error: HTTP {exc.status_code}. "
                "Check the endpoint, key, and deployment name."
            )

        except Exception:
            st.error(
                "Generation failed. Check the application "
                "configuration and terminal logs."
            )

if st.session_state.get("generated_svg"):
    svg_result = st.session_state["generated_svg"]

    st.subheader("Generated artwork")

    # Display the sanitized vector image.
    st.components.v1.html(
        svg_result,
        height=540,
        scrolling=False,
    )

    st.download_button(
        "Download SVG",
        data=svg_result.encode("utf-8"),
        file_name="generated_image.svg",
        mime="image/svg+xml",
    )

    with st.expander("View SVG source code"):
        st.code(svg_result, language="xml")
