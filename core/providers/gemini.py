from google import genai


def generate(api_key:str, model:str, messages:str):
    
    client = genai.Client(
        api_key=api_key
    )
    
    response = client.models.generate_content(
        model=model,
        contents=messages
    )
    
    
    return response.text