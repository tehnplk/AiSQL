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

        self.effect_keywords = [
            "INSERT",
            "UPDATE",
            "DELETE",
            "ALTER",
            "CREATE",
            "DROP",
            "TRUNCATE",
        ]

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

            self.progress.emit("กำลังดำเนินการ...")
            # check sql_command in effect_keywords
            # do execute and commit only
            if any(
                keyword in self.sql_command.upper() for keyword in self.effect_keywords
            ):
                with connection.cursor() as cursor:
                    cursor.execute(self.sql_command)
                    connection.commit()
                    #หาจำนวน effect rows
                    effect_rows = cursor.rowcount
                self.progress.emit(f"ปรับปรุงฐานข้อมูลสำเร็จ")
                self.finished.emit([effect_rows], ["effect"])
                return

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
                self.progress.emit("ดึงข้อมูลสำเร็จ")
                self.finished.emit(results, columns)
            else:
                self.finished.emit([], [])

        except Exception as e:
            self.error.emit(f"เกิดข้อผิดพลาด: {str(e)}")
