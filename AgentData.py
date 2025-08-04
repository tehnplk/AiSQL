from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStdio

from pydantic_ai.models.gemini import GeminiModel
from pydantic_ai.providers.google_gla import GoogleGLAProvider


from pydantic import BaseModel, Field

from tokenn import GEMINI_API_KEY


from sandbox import read_db_config


# model llm


class AgentData:
    class OutputType(BaseModel):
        sql: str = Field(
            description="SQL query if use alias name need to cover by `` and remove limit clause at end of command,if no sql return empty string"
        )
        csv: str = Field(description="The result of the agent in csv format")
        explanation: str = Field(
            description="The explanation of the result or result value not in tabular or markdown format , Limit in 200 words."
        )

    # Read database configuration from sandbox.txt

    mcp_mysql = MCPServerStdio(
        "uvx",
        ["--from", "mysql-mcp-server", "mysql_mcp_server"],
        read_db_config(),
    )

    def __init__(self, model="gemini-2.5-flash"):

        self.model = GeminiModel(
            model, provider=GoogleGLAProvider(api_key=GEMINI_API_KEY)
        )

        self.agent = Agent(
            model=self.model,
            system_prompt=open("sys_prompt.txt", "r", encoding="utf-8").read(),
            retries=3,
            output_type=self.OutputType,
            toolsets=[self.mcp_mysql],
        )

    async def chat(self, query: str, message_history=[]):
        async with self.agent:
            result = await self.agent.run(query, message_history=message_history)
        return result