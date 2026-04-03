import asyncio
import os
from openai import AsyncOpenAI
from dotenv import load_dotenv

async def test_ollama():
    load_dotenv()
    url = os.getenv("OLLAMA_URL", "http://localhost:11434")
    model = os.getenv("OLLAMA_MODEL", "qwen3:4b")
    print(f"Testing Ollama at {url} with model {model}...")
    
    client = AsyncOpenAI(base_url=f"{url}/v1", api_key="ollama")
    
    try:
        response = await client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": "say hello"}],
            response_format={"type": "json_object"}
        )
        print("Success:", response.choices[0].message.content)
    except Exception as e:
        print("Error:", str(e))

if __name__ == "__main__":
    asyncio.run(test_ollama())
