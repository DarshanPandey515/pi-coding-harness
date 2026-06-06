from google import genai


def generate(api_key:str, model:str, prompt:str):
    client = genai.Client(
        api_key=api_key
    )
    
    response = client.models.generate_content(
        model=model,
        contents=prompt
    )
    
    
    return response.text