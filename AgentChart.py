from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStdio

from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openrouter import OpenRouterProvider

from pydantic import BaseModel, Field

from tokenn import OPENROUTER_API_KEY

class AgentChart:
    class OutputType(BaseModel):
        chart: str = Field(description="The chart url in markdown format")
        explanation: str = Field(description="The conclusion of the chart")

    mcp_chart = MCPServerStdio("npx", ["-y", "@antv/mcp-server-chart"])
    # mcp_chart = MCPServerStdio("npx", ["-y", "@gongrzhe/quickchart-mcp-server"])

    def __init__(self, model="openrouter/horizon-beta"):

        self.model = OpenAIModel(
            model,
            provider=OpenRouterProvider(api_key=OPENROUTER_API_KEY),
        )

        self.agent = Agent(
            model=self.model,
            system_prompt="สร้างแผนภูมิจากข้อมูล CSV ที่ได้รับ และแสดงผลลัพธ์ที่ได้ในรูปแบบ markdown",
            retries=3,
            output_type=self.OutputType,
            toolsets=[self.mcp_chart],
        )

    async def chat(self, query: str, data: str, message_history=[]):
        async with self.agent:
            result = await self.agent.run(
                f"{query} \n\n {data}", message_history=message_history
            )

        return result
