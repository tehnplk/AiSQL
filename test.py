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