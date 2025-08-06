import os
from PyQt6.QtCore import QThread, pyqtSignal
from dotenv import load_dotenv

load_dotenv()

from pydantic_ai import Agent
from pydantic import BaseModel, Field
from pydantic_ai.mcp import MCPServerStdio
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openrouter import OpenRouterProvider

from sandbox import read_db_config

import asyncio

# import logfire
# logfire.configure(token=os.getenv("LOGFIRE_TOKEN"))
# logfire.instrument_pydantic_ai()


class OutputType(BaseModel):
    sql: str = Field(
        description="SQL query if use alias name need to cover by `` and remove limit clause at end of command,if no sql return empty string"
    )
    csv: str = Field(description="The result of the agent in csv format")
    explanation: str = Field(
        description="The explanation of the result or result value not in tabular or markdown format , Limit in 200 words."
    )


class AgentDataWorker(QThread):
    signal_finished = pyqtSignal(str)
    signal_error = pyqtSignal(str)
    signal_progress = pyqtSignal(str)
    signal_message_history = pyqtSignal(list)

    def __init__(self, llm_model, user_input, message_history):
        super().__init__()

        if llm_model == "openrouter/horizon-beta":
            llm_model = OpenAIModel(
                model_name="openrouter/horizon-beta",
                provider=OpenRouterProvider(api_key=os.getenv("OPENROUTER_API_KEY")),
            )

        mcp_mysql = MCPServerStdio(
            "uvx",
            ["--from", "mysql-mcp-server", "mysql_mcp_server"],
            read_db_config(),
        )
        system_prompt = open("sys_prompt.txt", "r", encoding="utf-8").read()
        self.agent = Agent(
            model=llm_model,
            system_prompt=system_prompt,
            instructions="คุณชื่อ 'สาระแนน' เป็นผู้หญิงที่เชี่ยวชาญด้านฐานข้อมูลและการเขียนคำสั่ง SQL เวลาตอบคำถามให้ลงท้ายด้วย 'ค่ะ' เสมอ",
            output_type=OutputType,
            toolsets=[mcp_mysql],
        )

        self.user_input = user_input
        self.message_history = message_history
        self.new_message_history = []

    async def chat(self):
        try:
            async with self.agent:
                result = await self.agent.run(
                    self.user_input, message_history=self.message_history
                )
                self.new_message_history = result.all_messages()
                self.signal_message_history.emit(self.new_message_history)

                self.signal_progress.emit("สำเร็จ")
                if getattr(result.output, "sql", None):
                    self.signal_finished.emit(result.output.sql)
                else:
                    self.signal_finished.emit(getattr(result.output, "explanation", ""))
        except Exception as e:
            # Re-raise so run() catches it and logs
            # raise
            self.signal_error.emit(str(e))

    def run(self):
        asyncio.run(self.chat())

        """import traceback, logging, asyncio

        loop = asyncio.new_event_loop()
        loop.set_exception_handler(
            lambda l, c: logging.error(
                f"Asyncio exception: {c.get('message')}", exc_info=c.get("exception")
            )
        )
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self.chat())
        except Exception as e:
            self.signal_error.emit(f"{e}\n{traceback.format_exc()}")
        finally:
            try:
                pending = asyncio.all_tasks(loop)
                for task in pending:
                    task.cancel()
                if pending:
                    loop.run_until_complete(
                        asyncio.gather(*pending, return_exceptions=True)
                    )
            finally:
                loop.close()"""
