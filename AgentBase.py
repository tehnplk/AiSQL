from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStdio

from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openrouter import OpenRouterProvider

from pydantic_ai.models.gemini import GeminiModel
from pydantic_ai.providers.google_gla import GoogleGLAProvider


from pydantic import BaseModel, Field

from tokenn import LOGFIRE_KEY, OPENROUTER_API_KEY, GEMINI_API_KEY
import logfire

logfire.configure(token=LOGFIRE_KEY)
logfire.instrument_pydantic_ai()

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

    def __init__(self, model="gemini-2.5-flash-lite"):

        self.model = None

        model_horizon = OpenAIModel(
            "openrouter/horizon-beta",
            provider=OpenRouterProvider(api_key=OPENROUTER_API_KEY),
        )

        model_gemini = GeminiModel(
            model, provider=GoogleGLAProvider(api_key=GEMINI_API_KEY)
        )

        if model == "horizon-beta":
            self.model = model_horizon
        else:
            self.model = model_gemini

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


class AgentChart:
    class OutputType(BaseModel):
        chart: str = Field(description="The chart url in markdown format")
        explanation: str = Field(description="The conclusion of the chart")

    mcp_chart = MCPServerStdio("npx", ["-y", "@antv/mcp-server-chart"])
    # mcp_chart = MCPServerStdio("npx", ["-y", "@gongrzhe/quickchart-mcp-server"])

    def __init__(self, model="horizon-beta"):

        self.model = None

        model_horizon = OpenAIModel(
            "openrouter/horizon-beta",
            provider=OpenRouterProvider(api_key=OPENROUTER_API_KEY),
        )

        model_gemini = GeminiModel(
            model, provider=GoogleGLAProvider(api_key=GEMINI_API_KEY)
        )

        if model == "horizon-beta":
            self.model = model_horizon
        else:
            self.model = model_gemini

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


if __name__ == "__main__":

    import asyncio
    agent_data = AgentData(model="gemini-2.5-flash")
    result_data = asyncio.run(
        agent_data.chat("ใช้ mcp tool execute_sql นับจำนวนประชากรทั้งหมด แยกรายหมู่บ้าน"),
    )
    print(result_data.output)

    agent_chart = AgentChart(model="horizon-beta")
    result_chart = asyncio.run(
        agent_chart.chat(
            "แสดงกราฟแท่ง",
            """ หมู่ที่,จำนวนหลังคาเรือน
                01,191
                02,111
                03,101
                04,81
                05,102
                06,173 """,
        )
    )
    print(result_chart.output)
