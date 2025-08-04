from PyQt6.QtCore import QThread, pyqtSignal
import pymysql
class QueryExecutor(QThread):
    """Background thread for executing SQL queries."""

    finished = pyqtSignal(list, list)  # results, columns
    error = pyqtSignal(str)
    progress = pyqtSignal(str)

    def __init__(self, sql_command, db_config):
        super().__init__()
        self.sql_command = sql_command
        self.db_config = db_config

    def run(self):
        """Execute the SQL query in background."""
        try:
            self.progress.emit("กำลังเชื่อมต่อฐานข้อมูล...")

            # Connect to database
            connection = pymysql.connect(
                host=self.db_config["host"],
                port=self.db_config["port"],
                user=self.db_config["user"],
                password=self.db_config["password"],
                database=self.db_config["database"],
                charset="utf8mb4",
            )

            self.progress.emit("กำลังดำเนินการคิวรี...")

            with connection.cursor() as cursor:
                cursor.execute(self.sql_command)
                results = cursor.fetchall()
                columns = (
                    [desc[0] for desc in cursor.description]
                    if cursor.description
                    else []
                )

            connection.close()

            if results:
                self.progress.emit("สำเร็จ")
                self.finished.emit(results, columns)
            else:
                self.finished.emit([], [])

        except Exception as e:
            self.error.emit(f"เกิดข้อผิดพลาด: {str(e)}")
