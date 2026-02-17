import asyncio
from openai import AsyncOpenAI
from app.config import settings

async def test_gemini():
    client = AsyncOpenAI(
        api_key=settings.gemini_api_key,
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
    )

    try:
        response = await client.chat.completions.create(
            model="models/gemini-2.0-flash",
            messages=[{"role": "user", "content": "Say hi"}]
        )
        print("Success:", response.choices[0].message.content)
        return True
    except Exception as e:
        print("Error:", str(e))
        return False

if __name__ == "__main__":
    asyncio.run(test_gemini())
