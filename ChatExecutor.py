
from PyQt6.QtCore import QThread, pyqtSignal
import asyncio
from AgentData import AgentData

class ChatExecutor(QThread):
    """Background thread for executing chat queries."""

    signal_finished = pyqtSignal(str)  # SQL result
    signal_error = pyqtSignal(str)
    signal_progress = pyqtSignal(str)
    signal_message_history = pyqtSignal(list)

    def __init__(self, model,user_prompt, message_history):
        super().__init__()
        self.user_prompt = user_prompt
        self.message_history = message_history
        self.model = model

    def run(self):
        """Execute the chat query in background."""
        try:
            self.signal_progress.emit("Thinking...")

            agent = AgentData(model=self.model)
            result = asyncio.run(
                agent.chat(self.user_prompt, message_history=self.message_history)
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
