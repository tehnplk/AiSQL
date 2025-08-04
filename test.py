from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openrouter import OpenRouterProvider

OPENROUTER_API_KEY = "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"
model = OpenAIModel(
    'openrouter/horizon-beta',
    provider=OpenRouterProvider(api_key=OPENROUTER_API_KEY),
)
agent = Agent(model)

import asyncio
result = asyncio.run(agent.run('Hello, how are you?'))
print(result.output)