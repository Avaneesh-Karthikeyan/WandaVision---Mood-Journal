import json
from groq import AsyncGroq
from .config import settings

client = AsyncGroq(api_key=settings.groq_api_key)

VALID_MOODS = ["happy", "sad", "anxious", "stressed", "neutral", "angry", "excited", "grateful", "overwhelmed", "calm"]

SYSTEM_PROMPT = """You are an empathetic mood analysis assistant.
Analyze the emotional tone of the journal entry and respond ONLY with valid JSON in this exact format:
{
  "mood": "<one of: happy, sad, anxious, stressed, neutral, angry, excited, grateful, overwhelmed, calm>",
  "reflection": "<a single warm, supportive sentence acknowledging the writer's feelings>"
}
Do not include any text outside the JSON object."""


async def analyze_sentiment(text: str) -> dict:
    """
    Analyze the sentiment of a journal entry using the Groq API (free tier).
    Returns a dict with 'mood' and 'reflection' keys.
    """
    try:
        response = await client.chat.completions.create(
            model=settings.groq_model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Journal entry:\n\n{text}"},
            ],
            temperature=0.4,
            max_tokens=150,
            response_format={"type": "json_object"},
        )

        raw = response.choices[0].message.content.strip()
        result = json.loads(raw)

        mood = result.get("mood", "neutral").lower()
        if mood not in VALID_MOODS:
            mood = "neutral"

        reflection = result.get("reflection", "Thank you for sharing your thoughts today.")

        return {"mood": mood, "reflection": reflection}

    except json.JSONDecodeError:
        return {
            "mood": "neutral",
            "reflection": "Thank you for taking the time to write today.",
        }
    except Exception as e:
        raise RuntimeError(f"Sentiment analysis failed: {str(e)}") from e
