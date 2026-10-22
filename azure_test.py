
import os
from dotenv import load_dotenv
from openai import OpenAI, APIStatusError

load_dotenv()

endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "").strip()
api_key = os.getenv("AZURE_OPENAI_API_KEY", "").strip()
model = os.getenv("AZURE_OPENAI_MODEL", "gpt4o").strip()

if not endpoint or not api_key:
    raise SystemExit("Missing endpoint or API key in .env")

print("Endpoint configured:", endpoint)
print("Deployment configured:", model)
print("API key loaded:", bool(api_key))

client = OpenAI(
    base_url=endpoint,
    api_key=api_key,
    timeout=30.0,
)

try:
    response = client.responses.create(
        model=model,
        input="Reply with exactly: Azure connection successful",
    )
    print("\nSUCCESS")
    print(response.output_text)

except APIStatusError as exc:
    print("\nAPI request failed")
    print("HTTP status:", exc.status_code)
    print("Request ID:", exc.response.headers.get("apim-request-id", "N/A"))
    print("Azure error details:", exc.response.text[:2000])
