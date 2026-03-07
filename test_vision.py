import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
client = Groq()

models = [
    'llama-3.3-70b-versatile',
    'qwen/qwen3-32b',
    'meta-llama/llama-4-scout-17b-16e-instruct',
    'meta-llama/llama-4-maverick-17b-128e-instruct',
    'moonshotai/kimi-k2-instruct',
    'openai/gpt-oss-20b',
]

print("Testing Vision Support on Groq Models:")
for m in models:
    try:
        response = client.chat.completions.create(
            model=m,
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": "What's in this image?"},
                    {"type": "image_url", "image_url": {"url": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="}}
                ]
            }]
        )
        print(f"{m}: SUCCESS")
    except Exception as e:
        print(f"{m}: FAILED - {type(e).__name__}")
