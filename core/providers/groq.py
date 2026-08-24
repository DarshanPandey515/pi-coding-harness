from groq import Groq


def generate(api_key: str, model: str, messages: list):
    client = Groq(api_key=api_key)

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": m["role"], "content": m["content"]}
            for m in messages
        ],
    )

    return response.choices[0].message.content
