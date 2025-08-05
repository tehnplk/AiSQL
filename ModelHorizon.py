from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openrouter import OpenRouterProvider

from tokenn import OPENROUTER_API_KEY


def model():
    return OpenAIModel('openrouter/horizon-beta', provider=OpenRouterProvider(api_key=OPENROUTER_API_KEY))


# Export ModelHorizon
ModelHorizon = model()