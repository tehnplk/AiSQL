import sys
import re
import pandas as pd
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QMessageBox,
    QFileDialog,
    QMenu
)
from PyQt6.QtCore import (
    Qt,
    QSettings,
)
from PyQt6.QtGui import (
    QStandardItemModel,
    QStandardItem,
)
from main_ui import main_ui
from db_setting_dlg import DbSettingsDialog


# Import MySQLFormatter for SQL formatting
from SQLFormatter import MySQLFormatter

from ChatExecutor import ChatExecutor

from QueryExecutor import QueryExecutor

from PandasTableModel import PandasTableModel

import traceback
import os

import logfire
from tokenn import LOGFIRE_KEY
logfire.configure(token=LOGFIRE_KEY)
logfire.instrument_pydantic_ai()


class main(QMainWindow, main_ui):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        # Initialize instance variables
        self.query_executor = None
        self.chat_executor = None
        self.pandas_model = None
        self.results_data = []
        self.columns_data = []
        self.message_history = []
        # Initialize MySQL formatter
        self.mysql_formatter = MySQLFormatter()


        # Setup table context menu
        self.setup_table_context_menu()

        # Connect button signals
        self.run_button.clicked.connect(self.run_query)
        self.clear_button.clicked.connect(self.clear_editor)
        self.format_button.clicked.connect(self.format_sql)
        self.export_button.clicked.connect(self.export_to_excel)
        self.chat_button.clicked.connect(self.btn_chat)
        self.save_button.clicked.connect(self.save_sql)

        # Connect menu actions
        self.settings_action.triggered.connect(self.show_settings)
        if hasattr(self, 'open_action'):
            self.open_action.triggered.connect(self.open_sql)

        # Connect run action from Query menu
        if hasattr(self, "run_action"):
            self.run_action.triggered.connect(self.run_query)


    def btn_chat(self):
        """Execute chat query using background thread."""
        try:
            user_prompt = self.chat_text.toPlainText().strip()
            if not user_prompt:
                return

            # Clear SQL editor
            self.sql_editor.setPlainText("")

            # Disable chat button during processing
            if hasattr(self, "chat_button"):
                self.chat_button.setEnabled(False)
                self.chat_button.setText("Thinking...")

            # Start background chat execution with selected model
            selected_model = self.model_combo.currentText()
            self.chat_executor = ChatExecutor(
                selected_model, user_prompt, self.message_history
            )
            self.chat_executor.signal_finished.connect(self.on_chat_finished)
            self.chat_executor.signal_error.connect(self.on_chat_error)
            self.chat_executor.signal_progress.connect(self.on_progress_update)
            self.chat_executor.signal_message_history.connect(self.on_message_history)
            self.chat_executor.start()

        except Exception as e:
            # Catch-all exception handler
            error_msg = f"เกิดข้อผิดพลาด: {str(e)}"
            print(f"DEBUG: {error_msg}")
            traceback.print_exc()

            # Restore button state
            if hasattr(self, "chat_button"):
                self.chat_button.setEnabled(True)
                self.chat_button.setText("Chat")

    def on_message_history(self, message_history):
        """Handle message history update."""
        self.message_history = message_history

    def on_chat_finished(self, sql_result):
        """Handle successful chat completion."""
        # Restore button state
        if hasattr(self, "chat_button"):
            self.chat_button.setEnabled(True)
            self.chat_button.setText("Chat")

        # Set SQL result in editor
        self.sql_editor.setPlainText(sql_result)

        # Format the SQL
        self.format_sql()

    def on_chat_error(self, error_message):
        """Handle chat error."""
        # Restore button state
        if hasattr(self, "chat_button"):
            self.chat_button.setEnabled(True)
            self.chat_button.setText("Chat")

        self.statusbar.showMessage("เกิดข้อผิดพลาด: Error occurred during chat processing")
        print(f"ERROR: {error_message}")

        # Show error in a message box
        QMessageBox.critical(self, "เกิดข้อผิดพลาด", f"{error_message}\n กรุณาดำเนินการใหม่อีกครั้ง")

    def run_query(self):
        """Execute SQL query using background thread and pandas model."""
        try:
            query = self.sql_editor.toPlainText().strip()
            if not query:
                print("No query to run")
                return

            print(f"\n=== Executing Query ===")
            print(f"Query: {query}")

            # Load database settings
            try:
                settings = QSettings("AiSQL", "DatabaseSettings")
                db_config = {
                    "host": str(settings.value("host", "localhost")),
                    "port": int(settings.value("port", 3306)),
                    "user": str(settings.value("user", "")),
                    "password": str(settings.value("password", "")),
                    "database": str(settings.value("database", "")),
                }
                print(
                    f"Database config: {db_config['user']}@{db_config['host']}:{db_config['port']}/{db_config['database']}"
                )
            except Exception as e:
                error_msg = f"เกิดข้อผิดพลาด: {str(e)}"
                self._show_error(error_msg)
                print(f"ERROR: {error_msg}")
                return

            # Check if required settings are present
            if not all([db_config["user"], db_config["database"]]):
                print("Database not configured - showing demo data")
                self._show_demo_data()
                return

            # Prevent execution of modifying queries
            forbidden_keywords = [
                "INSERT",
                "UPDATE",
                "DELETE",
                "ALTER",
                "CREATE",
                "DROP",
                "TRUNCATE",
            ]
            if any(keyword in query.upper() for keyword in forbidden_keywords):
                error_message = "Not allowed to execute SQL commands that modify data or database structure"
                self._show_error(error_message)
                print(f"ERROR: {error_message}")
                return

            # Disable run button and show progress
            self.run_button.setEnabled(False)
            self.run_button.setText("Processing...")

            # Clear previous results
            self.results_area.setModel(None)

            # Start background query execution
            self.query_executor = QueryExecutor(query, db_config)
            self.query_executor.finished.connect(self.on_query_finished)
            self.query_executor.error.connect(self.on_query_error)
            self.query_executor.progress.connect(self.on_progress_update)
            self.query_executor.start()

        except Exception as e:
            # Catch-all exception handler to prevent application crash
            error_msg = f"เกิดข้อผิดพลาด: {str(e)}"
            self._show_error(error_msg)
            print(f"DEBUG: {error_msg}")
            import traceback

            traceback.print_exc()

            # Restore button state
            self.run_button.setEnabled(True)
            self.run_button.setText("Run Query")

    def on_progress_update(self, message):
        """Update progress display."""
        print(f"Progress: {message}")

    def on_query_finished(self, results, columns):
        """Handle successful query completion."""
        # Restore button state
        self.run_button.setEnabled(True)
        self.run_button.setText("Run Query")

        print(f"\n=== Query Results ===")
        print(f"Columns: {columns}")
        print(f"Rows returned: {len(results)}")

        if not results:
            self.statusbar.showMessage("ไม่พบข้อมูล")
            # Show no data message
            model = QStandardItemModel(1, 1)
            model.setHorizontalHeaderLabels(["Result"])
            item = QStandardItem("ไม่พบข้อมูลที่ตรงตามเงื่อนไข")
            item.setEditable(False)
            model.setItem(0, 0, item)
            self.results_area.setModel(model)
            self.pandas_model = None
            return

        # Print first few rows to console
        for i, row in enumerate(results[:10]):
            print(f"Row {i+1}: {row}")
        if len(results) > 10:
            print(f"... and {len(results) - 10} more rows")

        # Convert results to pandas DataFrame
        df = pd.DataFrame(results, columns=columns)

        # Create pandas model
        self.pandas_model = PandasTableModel(df)

        # Set model to table and enable sorting
        self.results_area.setModel(self.pandas_model)
        self.results_area.setSortingEnabled(True)
        self.results_area.sortByColumn(0, Qt.SortOrder.AscendingOrder)
        self.results_area.resizeColumnsToContents()

        # Update status
        self.results_data = results
        self.columns_data = columns

        # Enable export button
        self.export_button.setEnabled(True)

    def on_query_error(self, error_message):
        """Handle query error."""
        # Restore button state
        self.run_button.setEnabled(True)
        self.run_button.setText("Run Query")

        print(f"ERROR: {error_message}")

        # Show error in a message box
        QMessageBox.critical(self, "Error", error_message)
        self.results_area.setModel(None)

    def setup_table_context_menu(self):
        """Setup context menu for table headers."""
        if hasattr(self, "results_area"):
            header = self.results_area.horizontalHeader()
            header.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            header.customContextMenuRequested.connect(self.show_header_context_menu)

    def show_header_context_menu(self, position):
        """Show context menu on header right-click."""
        if self.pandas_model is None:
            return

        header = self.results_area.horizontalHeader()
        logical_index = header.logicalIndexAt(position)

        if logical_index < 0:
            return

        column_name = self.pandas_model.headerData(
            logical_index, Qt.Orientation.Horizontal, Qt.ItemDataRole.DisplayRole
        )

        menu = QMenu(self)

        # Filter action
        filter_action = menu.addAction(f"Filter column '{column_name}'")
        filter_action.triggered.connect(lambda: self.show_filter_dialog(column_name))

        # Clear filter action (only if filter exists)
        if column_name in self.pandas_model.column_filters:
            clear_action = menu.addAction(f"Clear filter for '{column_name}'")
            clear_action.triggered.connect(
                lambda: self.clear_column_filter(column_name)
            )

        # Clear all filters action (only if any filters exist)
        if self.pandas_model.column_filters:
            menu.addSeparator()
            clear_all_action = menu.addAction("Clear all filters")
            clear_all_action.triggered.connect(self.clear_all_filters)

        menu.exec(header.mapToGlobal(position))

    def show_filter_dialog(self, column_name):
        """Show simple filter dialog for a column."""
        if not hasattr(self, "pandas_model") or not self.pandas_model:
            return

        # Get current filter text if exists
        current_filter = self.pandas_model.column_filters.get(column_name, "")

        # Simple input dialog
        from PyQt6.QtWidgets import QInputDialog

        text, ok = QInputDialog.getText(
            self,
            "Filter Column",
            f"Enter filter text for '{column_name}':",
            text=current_filter,
        )

        if ok:
            self.pandas_model.set_column_filter(column_name, text.strip())
            self.update_status_after_filter()

    def clear_column_filter(self, column_name):
        """Clear filter for a specific column."""
        if self.pandas_model and column_name in self.pandas_model.column_filters:
            del self.pandas_model.column_filters[column_name]
            self.pandas_model.apply_filters()
            self.update_status_after_filter()

    def clear_all_filters(self):
        """Clear all column filters."""
        if self.pandas_model:
            self.pandas_model.column_filters.clear()
            self.pandas_model.apply_filters()
            self.update_status_after_filter()

    def update_status_after_filter(self):
        """Update status label after filtering."""
        if self.pandas_model:
            filtered_count = self.pandas_model.rowCount()
            total_count = len(self.pandas_model._original_dataframe)

            if filtered_count == total_count:
                self.statusbar.showMessage(f"Found {total_count} records")
            else:
                self.statusbar.showMessage(
                    f"Showing {filtered_count} of {total_count} records (filtered)"
                )

    def _show_error(self, error_message):
        """Helper method to display error messages in the results area"""
        self.statusbar.showMessage(error_message)
        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(["Error"])
        model.appendRow([QStandardItem(error_message)])
        self.results_area.setModel(model)

    def export_to_excel(self):
        """Export results to Excel file."""
        try:
            from datetime import datetime

            if not self.results_data:
                QMessageBox.warning(self, "Warning", "No data to export")
                return

            # Get save location
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            default_filename = f"query_results_{timestamp}.xlsx"

            filename, _ = QFileDialog.getSaveFileName(
                self,
                "Save File",
                default_filename,
                "Excel Files (*.xlsx);;All Files (*)",
            )

            if filename:
                # Export filtered data if available, otherwise export original data
                if self.pandas_model and hasattr(self.pandas_model, "_dataframe"):
                    df = self.pandas_model._dataframe
                else:
                    df = pd.DataFrame(self.results_data, columns=self.columns_data)

                # Save to Excel
                df.to_excel(filename, index=False, engine="openpyxl")

                QMessageBox.information(
                    self,
                    "Success",
                    f"Data exported successfully\n{filename}\nRows: {len(df)}",
                )
                print(f"Data exported to: {filename}")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Cannot export data: {str(e)}")
            print(f"Export error: {e}")

    def _show_demo_data(self):
        """Show demo data when database is not configured"""
        self.status_label.setText(
            "Database not configured. Showing demo data. Configure database in File > Settings."
        )
        print("\n=== Demo Data (Database not configured) ===")

        # Create demo data
        headers = ["ID", "Name", "Email", "Department", "Salary"]
        demo_rows = [
            [1, "John Doe", "john@example.com", "Engineering", 75000],
            [2, "Jane Smith", "jane@example.com", "Marketing", 65000],
            [3, "Bob Johnson", "bob@example.com", "Sales", 55000],
            [4, "Alice Brown", "alice@example.com", "HR", 60000],
            [5, "Charlie Wilson", "charlie@example.com", "Engineering", 80000],
        ]

        # Print to console
        print(f"Columns: {headers}")
        for i, row in enumerate(demo_rows):
            print(f"Row {i+1}: {row}")

        # Create pandas DataFrame for demo data
        df = pd.DataFrame(demo_rows, columns=headers)
        self.pandas_model = PandasTableModel(df)

        # Set model to table and enable sorting
        self.results_area.setModel(self.pandas_model)
        self.results_area.setSortingEnabled(True)
        self.results_area.resizeColumnsToContents()

        # Store demo data for export
        self.results_data = demo_rows
        self.columns_data = headers

        # Enable export button for demo data
        self.export_button.setEnabled(True)

    def validate_query(self, query):
        # Basic SQL validation (simplified)
        query_upper = query.upper().strip()
        valid_starts = [
            "SELECT",
            "INSERT",
            "UPDATE",
            "DELETE",
            "CREATE",
            "DROP",
            "ALTER",
            "WITH",
        ]
        return any(query_upper.startswith(start) for start in valid_starts)

    def clear_editor(self):
        self.sql_editor.clear()
        self.chat_text.clear()
        model = QStandardItemModel()
        self.results_area.setModel(model)

        # Clear data and disable export
        self.results_data = []
        self.columns_data = []
        self.pandas_model = None
        self.export_button.setEnabled(False)

    def format_sql(self):
        # Format SQL using MySQLFormatter
        query = self.sql_editor.toPlainText()
        if not query.strip():
            return

        try:
            # Use MySQLFormatter to format the SQL query
            formatted = self.mysql_formatter.format_sql(
                sql=query,
                keyword_case="upper",
                identifier_case="lower",
                reindent=True,
                indent_width=4,
                use_space_around_operators=True,
            )
            self.sql_editor.setPlainText(formatted)
        except Exception as e:
            # Fallback to simple formatting if MySQLFormatter fails
            formatted = query
            formatted = re.sub(
                r"\bSELECT\b", "\nSELECT", formatted, flags=re.IGNORECASE
            )
            formatted = re.sub(r"\bFROM\b", "\nFROM", formatted, flags=re.IGNORECASE)
            formatted = re.sub(r"\bWHERE\b", "\nWHERE", formatted, flags=re.IGNORECASE)
            formatted = re.sub(
                r"\bORDER BY\b", "\nORDER BY", formatted, flags=re.IGNORECASE
            )
            formatted = re.sub(
                r"\bGROUP BY\b", "\nGROUP BY", formatted, flags=re.IGNORECASE
            )
            formatted = re.sub(r";\s*$", ";\n", formatted, flags=re.MULTILINE)
            self.sql_editor.setPlainText(formatted)

    def show_settings(self):
        """Show the database settings dialog."""
        dialog = DbSettingsDialog(self)
        dialog.exec()

    def save_sql(self):
        """Save the current SQL query to /sql directory only."""
        try:
            # Get the current SQL query
            sql_query = self.sql_editor.toPlainText().strip()
            
            if not sql_query:
                QMessageBox.warning(self, "Warning", "No SQL query to save")
                return

            # Force save to /sql directory
            sql_dir = os.path.join(os.getcwd(), 'sql')
            
            # Create sql directory if it doesn't exist
            os.makedirs(sql_dir, exist_ok=True)

            # Get filename only (without path)
            filename, _ = QFileDialog.getSaveFileName(
                self,
                "Save SQL Query to /sql directory",
                os.path.join(sql_dir, "query.sql"),
                "SQL Files (*.sql)",
            )

            if filename:
                # Ensure the file is saved in /sql directory
                basename = os.path.basename(filename)
                forced_path = os.path.join(sql_dir, basename)
                
                # Save to forced /sql directory
                with open(forced_path, 'w', encoding='utf-8') as file:
                    file.write(sql_query)

                QMessageBox.information(
                    self,
                    "Success",
                    f"SQL query saved to /sql directory\n{forced_path}",
                )
                print(f"SQL saved to: {forced_path}")
                self.statusbar.showMessage(f"SQL saved to: {forced_path}")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Cannot save SQL: {str(e)}")
            print(f"Save error: {e}")
            self.statusbar.showMessage(f"Save error: {str(e)}")

    def open_sql(self):
        """Open SQL file from /sql directory by default."""
        try:
            # Set default directory to /sql
            sql_dir = os.path.join(os.getcwd(), 'sql')
            
            # Create sql directory if it doesn't exist
            os.makedirs(sql_dir, exist_ok=True)

            # Get file to open from /sql directory
            filename, _ = QFileDialog.getOpenFileName(
                self,
                "Open SQL File from /sql directory",
                sql_dir,
                "SQL Files (*.sql);;Text Files (*.txt);;All Files (*)",
            )

            if filename:
                # Read file content
                with open(filename, 'r', encoding='utf-8') as file:
                    sql_content = file.read()

                # Load into SQL editor
                self.sql_editor.setPlainText(sql_content)

                QMessageBox.information(
                    self,
                    "Success",
                    f"SQL file loaded successfully\n{filename}",
                )
                print(f"SQL loaded from: {filename}")
                self.statusbar.showMessage(f"SQL loaded from: {filename}")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Cannot open SQL file: {str(e)}")
            print(f"Open error: {e}")
            self.statusbar.showMessage(f"Open error: {str(e)}")


if __name__ == "__main__":
    try:
        print("Starting application...")
        app = QApplication(sys.argv)
        app.setStyle("Fusion")

        print("Creating main window...")
        editor = main()
        print("Showing window...")
        editor.show()

        print("Starting event loop...")
        sys.exit(app.exec())

    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback

        traceback.print_exc()
