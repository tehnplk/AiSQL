from pydantic_ai.models.gemini import GeminiModel
from pydantic_ai.providers.google_gla import GoogleGLAProvider

from tokenn import GEMINI_API_KEY


def model():
    return GeminiModel('gemini-2.0-flash', provider=GoogleGLAProvider(api_key=GEMINI_API_KEY))


# Export ModelGemini
ModelGemini = model()