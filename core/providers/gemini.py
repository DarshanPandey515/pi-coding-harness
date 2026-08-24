from google import genai


def generate(api_key: str, model: str, messages: list):
    client = genai.Client(api_key=api_key)

    contents = []
    for m in messages:
        role = "user" if m["role"] == "user" else "model"
        contents.append({"role": role, "parts": [{"text": m["content"]}]})

    response = client.models.generate_content(
        model=model,
        contents=contents
    )

    return response.text
