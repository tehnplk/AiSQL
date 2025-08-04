#!/usr/bin/env python3
"""
Minimal version of SQL Editor to test functionality step by step
"""
import sys
import re
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                            QWidget, QPushButton, QLabel, QMessageBox, QFileDialog,
                            QHeaderView, QTableView, QDialog)
from PyQt6.QtCore import Qt, QSize, QSettings
from PyQt6.QtGui import (QTextCursor, QKeySequence, QAction, 
                         QStandardItemModel, QStandardItem)

# Test importing main_ui
try:
    from main_ui import main_ui
    print("✓ main_ui imported successfully")
except Exception as e:
    print(f"✗ Error importing main_ui: {e}")
    sys.exit(1)

# Test importing database dialog
try:
    from db_setting_dlg import DbSettingsDialog
    print("✓ db_setting_dlg imported successfully")
except Exception as e:
    print(f"✗ Error importing db_setting_dlg: {e}")
    sys.exit(1)

# Test importing pandas and sqlalchemy
try:
    import pandas as pd
    print("✓ pandas imported successfully")
except Exception as e:
    print(f"✗ Error importing pandas: {e}")

try:
    import pymysql
    print("✓ pymysql imported successfully")
except Exception as e:
    print(f"✗ Error importing pymysql: {e}")

try:
    from sqlalchemy import create_engine, text
    print("✓ sqlalchemy imported successfully")
except Exception as e:
    print(f"✗ Error importing sqlalchemy: {e}")

class MinimalMain(QMainWindow, main_ui):
    def __init__(self, parent=None):
        super().__init__(parent)
        print("Initializing UI...")
        self.setupUi(self)
        print("UI setup complete")
        
        # Connect basic signals
        print("Connecting signals...")
        self.run_button.clicked.connect(self.test_run_query)
        self.clear_button.clicked.connect(self.clear_editor)
        self.format_button.clicked.connect(self.format_sql)
        
        # Connect menu actions
        if hasattr(self, 'settings_action'):
            self.settings_action.triggered.connect(self.show_settings)
        
        print("Initialization complete")

    def test_run_query(self):
        """Simple test query function"""
        try:
            print("Test run query called")
            self.status_label.setText("Test query executed")
            
            # Create simple test data
            model = QStandardItemModel()
            model.setHorizontalHeaderLabels(["Test Column 1", "Test Column 2"])
            model.appendRow([QStandardItem("Test Data 1"), QStandardItem("Test Data 2")])
            model.appendRow([QStandardItem("Test Data 3"), QStandardItem("Test Data 4")])
            
            self.results_area.setModel(model)
            print("Test data displayed successfully")
            
        except Exception as e:
            print(f"Error in test_run_query: {e}")
            import traceback
            traceback.print_exc()

    def clear_editor(self):
        try:
            self.sql_editor.clear()
            model = QStandardItemModel()
            self.results_area.setModel(model)
            self.status_label.setText("Editor cleared")
        except Exception as e:
            print(f"Error in clear_editor: {e}")

    def format_sql(self):
        try:
            query = self.sql_editor.toPlainText()
            if not query.strip():
                return
            
            # Simple formatting
            formatted = re.sub(r'\\bSELECT\\b', '\\nSELECT', query, flags=re.IGNORECASE)
            self.sql_editor.setPlainText(formatted)
            self.status_label.setText("SQL formatted")
        except Exception as e:
            print(f"Error in format_sql: {e}")

    def show_settings(self):
        try:
            dialog = DbSettingsDialog(self)
            dialog.exec()
        except Exception as e:
            print(f"Error showing settings: {e}")

if __name__ == "__main__":
    try:
        print("Starting application...")
        app = QApplication(sys.argv)
        app.setStyle("Fusion")
        
        print("Creating main window...")
        editor = MinimalMain()
        editor.show()
        
        print("Application ready")
        sys.exit(app.exec())
        
    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
