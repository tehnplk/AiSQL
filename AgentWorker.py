from PyQt6.QtCore import QThread, pyqtSignal
import asyncio


class AgentWorker(QThread):
    signal_finished = pyqtSignal(str)  # SQL result
    signal_error = pyqtSignal(str)
    signal_progress = pyqtSignal(str)
    signal_message_history = pyqtSignal(list)

    def __init__(self, agent, user_input, message_history):
        super().__init__()
        self.agent = agent
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
                if result.output.sql:
                    self.signal_finished.emit(result.output.sql)
                else:
                    self.signal_finished.emit(result.output.explanation)

        except Exception as e:
            self.signal_error.emit(str(e))

    def run(self):
        asyncio.run(self.chat())
