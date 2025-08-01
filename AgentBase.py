from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStdio, MCPServerSSE
from pydantic import BaseModel, Field
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openrouter import OpenRouterProvider
from pydantic_ai.providers.openai import OpenAIProvider
import asyncio
import os

from dotenv import load_dotenv
load_dotenv()

import logfire
logfire.configure(token=os.getenv("LOGFIRE_TOKEN"))

local_model = OpenAIModel(
    model_name="aliafshar/gemma3-it-qat-tools:1b",
    provider=OpenAIProvider(base_url="http://localhost:11434/v1"),
)

cloud_model = OpenAIModel(
    model_name="openrouter/horizon-alpha",
    provider=OpenRouterProvider(api_key=os.getenv("OPENROUTER_API_KEY")),
)

custom_model = 'google-gla:gemini-2.5-flash'

class AgentData:
    class OutputType(BaseModel):
        sql: str = Field(
            description="SQL query if use alias name need to cover by `` and remove limit clause at end of command,if no sql return empty string"
        )
        csv: str = Field(description="The result of the agent in csv format")
        explanation: str = Field(
            description="The explanation of the result or result value not in tabular or markdown format , Limit in 200 words."
        )

    mcp_mysql = MCPServerStdio(
        "uvx",
        ["--from", "mysql-mcp-server", "mysql_mcp_server"],
        {
            "MYSQL_HOST": os.getenv("MYSQL_HOST"),
            "MYSQL_PORT": os.getenv("MYSQL_PORT"),
            "MYSQL_USER": os.getenv("MYSQL_USER"),
            "MYSQL_PASSWORD": os.getenv("MYSQL_PASSWORD"),
            "MYSQL_DATABASE": os.getenv("MYSQL_DATABASE"),
        },
    )

    def __init__(self, model=custom_model):
        self.agent = Agent(
            model=model,
            system_prompt=open("sys_prompt2.txt", "r", encoding="utf-8").read(),
            instrument=True,
            mcp_servers=[self.mcp_mysql],
            retries=3,
            output_type=self.OutputType,
        )

    async def run(self, query: str, message_history=[]):
        async with self.agent.run_mcp_servers():
            result = await self.agent.run(query, message_history=message_history)
        return result


class AgentChart:
    class OutputType(BaseModel):
        chart: str = Field(
            description="The chart url in markdown format"
        )
        explanation: str = Field(description="The conclusion of the chart")

    mcp_chart = MCPServerStdio("npx", ["-y", "@antv/mcp-server-chart"])
    # mcp_chart = MCPServerStdio("npx", ["-y", "@gongrzhe/quickchart-mcp-server"])

    def __init__(self, model=cloud_model):
        self.agent = Agent(
            model=model,
            system_prompt="สร้างแผนภูมิจากข้อมูล CSV ที่ได้รับ และแสดงผลลัพธ์ที่ได้ในรูปแบบ markdown",
            instrument=True,
            mcp_servers=[self.mcp_chart],
            retries=3,
            output_type=self.OutputType,
        )

    async def run(self, query: str, data: str,message_history=[]):
        async with self.agent.run_mcp_servers():
            result = await self.agent.run(f"{query} \n\n {data}",message_history=message_history)
        return result


if __name__ == "__main__":

    agent_data = AgentData()
    result_data = asyncio.run(
        agent_data.run("ใช้ mcp tool execute_sql นับจำนวนประชากรทั้งหมด แยกรายหมู่บ้าน"),
    )
    print(result_data.output)

    agent_chart = AgentChart()
    result_chart = asyncio.run(
        agent_chart.run(
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
