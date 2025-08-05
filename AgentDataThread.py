from PyQt6.QtCore import QThread, pyqtSignal
import asyncio
from pydantic_ai import Agent
from pydantic import BaseModel, Field
from pydantic_ai.mcp import MCPServerStdio
from pydantic_ai.models.gemini import GeminiModel
from pydantic_ai.providers.google_gla import GoogleGLAProvider

from tokenn import GEMINI_API_KEY

from sandbox import read_db_config


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
    read_db_config(),
)


class AgentDataThread(QThread):
    """Background thread for executing chat queries."""

    signal_finished = pyqtSignal(str)  # SQL result
    signal_error = pyqtSignal(str)
    signal_progress = pyqtSignal(str)
    signal_message_history = pyqtSignal(list)

    def __init__(self, model, user_prompt, message_history):
        super().__init__()
        self.user_prompt = user_prompt
        self.message_history = message_history
        self.model = GeminiModel(
            model, provider=GoogleGLAProvider(api_key=GEMINI_API_KEY)
        )

    def run(self):
        """Execute the chat query in background."""
        try:
            self.signal_progress.emit("Thinking...")

            self.agent = Agent(
                model=self.model,
                system_prompt=open("sys_prompt.txt", "r", encoding="utf-8").read(),
                retries=3,
                output_type=OutputType,
                toolsets=[mcp_mysql],
            )
            result = asyncio.run(
                self.agent.run(self.user_prompt, message_history=self.message_history)
            )
            new_message_history = result.all_messages()
            self.signal_message_history.emit(new_message_history)

            self.signal_progress.emit("สำเร็จ")
            if result.output.sql:
                self.signal_finished.emit(result.output.sql)
            else:
                self.signal_finished.emit(result.output.explanation)

        except Exception as e:
            self.signal_error.emit(f"เกิดข้อผิดพลาด: {str(e)}")
