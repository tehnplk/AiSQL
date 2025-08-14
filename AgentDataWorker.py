import os
from PyQt6.QtCore import QThread, pyqtSignal

from pydantic_ai import Agent
from pydantic import BaseModel, Field
from pydantic_ai.mcp import MCPServerStreamableHTTP,MCPServerSSE
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openrouter import OpenRouterProvider

from dotenv import load_dotenv

load_dotenv()



import logfire
logfire.configure(token=os.getenv("LOGFIRE_TOKEN"))
logfire.instrument_pydantic_ai()


sys_prompt = open("sys_prompt.txt", "r", encoding="utf-8").read()


class OutputType(BaseModel):
    sql: str = Field(
        description="The SQL query that agent used. If use alias name need to cover by `` and remove limit clause at end of command. If no sql return empty string"
    )
    answer: str = Field(
        description="The answer of the agent when user ask question not related to database. If no answer return empty string"
    )


class AgentDataWorker(QThread):
    signal_finished = pyqtSignal(str)
    signal_error = pyqtSignal(str)
    signal_progress = pyqtSignal(str)
    signal_message_history = pyqtSignal(list)

    def __init__(self, llm_model, user_input, message_history):
        super().__init__()

        if llm_model == "openai/gpt-oss-20b":
            llm_model = OpenAIModel(
                model_name="openai/gpt-oss-20b",
                provider=OpenRouterProvider(api_key=os.getenv("OPENROUTER_API_KEY")),
            )

        # ควรใช้ MCPServerSSE แทน MCPServerStdio เพื่อหลีกเลี่ยง error TaskGroup
        self.mcp_mysql = MCPServerSSE(url=os.getenv("MCP_DB_SANDBOX"))

        self.agent = Agent(
            model=llm_model,
            system_prompt=sys_prompt,
            instructions="คุณชื่อ 'มะเฟือง' เป็นผู้หญิงที่มีความเชี่ยวชาญด้านฐานข้อมูลและการเขียนคำสั่ง SQL เวลาตอบคำถามให้ลงท้ายด้วย 'ค่ะ' เสมอ",
            output_type=OutputType,
            toolsets=[self.mcp_mysql],
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
                    self.signal_finished.emit(result.output.answer)

        except Exception as e:
            # Re-raise so run() catches it and logs
            # raise
            self.signal_error.emit(str(e))
            print(f"Ai agent run chat error : {str(e)}")

    def run(self):
        import traceback, logging, asyncio
        # asyncio.run(self.chat())

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
                loop.close()
