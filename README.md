# AI Image Understanding & SVG Generation

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/UI-Streamlit-FF4B4B.svg)](https://streamlit.io/)
[![Azure AI](https://img.shields.io/badge/AI-Azure%20OpenAI-0078D4.svg)](https://azure.microsoft.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

An AI-powered application built with Python, Streamlit, and Azure OpenAI that helps users understand images and generate vector illustrations from natural-language prompts.

## Features

- **Image Understanding:** Upload an image and request a natural-language description.
- **Visual Question Answering:** Ask questions about objects, visible text, scenes, and image details.
- **SVG Generation:** Generate vector illustrations from text prompts using an LLM.
- **SVG Preview:** Preview generated vector artwork in the application.
- **SVG Download:** Download generated illustrations as `.svg` files.
- **Secure Configuration:** Load Azure endpoint and authentication settings from environment variables.
- **Input Validation:** Validate uploaded image files and apply basic SVG sanitization.

## Technology Stack

- Python
- Streamlit
- Azure AI Foundry / Azure OpenAI-compatible API
- OpenAI Python SDK
- Pillow
- python-dotenv
- SVG and XML processing

## Project Structure

```text
Image_classification_generation/
├── app.py
├── imageGenerate.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
└── LICENSE
```

## Prerequisites

- Python 3.12 or a compatible supported version
- An Azure AI resource with an appropriate deployed model
- Valid credentials and permissions for the configured endpoint
- Git

## Installation

Clone the repository:

```bash
git clone https://github.com/javedbajwa/Image_classification_generation.git
cd Image_classification_generation
```

Create and activate a virtual environment.

Windows PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Configuration

Create a local `.env` file using `.env.example` as a template.

Configure the required Azure endpoint, API key, and deployment name. Use the exact deployment name shown in your Azure portal.

Never commit `.env` or expose API keys in source code, logs, screenshots, or public repositories.

## Run the Applications

Image understanding:

```bash
streamlit run app.py
```

SVG generation:

```bash
streamlit run imageGenerate.py
```

Streamlit will display a local URL where you can access each application.

## How It Works

### Image Understanding

1. The user uploads an image.
2. The application validates the file.
3. The image is encoded for the model request.
4. The configured Azure model processes the image and question.
5. The application displays the generated response.

### SVG Generation

1. The user describes the desired illustration.
2. The language model generates SVG markup.
3. The application validates and sanitizes the markup.
4. The SVG is previewed and made available for download.

Note: SVG generation uses language-model-generated vector markup. It is not equivalent to photorealistic image generation using a dedicated image-generation model.

## Security Considerations

- Keep credentials in environment variables or a suitable secrets manager.
- Rotate any credentials that have been exposed.
- Validate uploaded files and generated SVG content.
- Apply appropriate access controls, rate limits, and monitoring before production deployment.
- Do not upload confidential images without appropriate authorization.

## Future Enhancements

- Conversational image analysis
- Image analysis history
- Structured JSON responses
- Automated unit and integration tests
- FastAPI backend
- PostgreSQL persistence
- Azure deployment and monitoring
- Managed identity authentication where supported

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
