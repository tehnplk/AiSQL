import os
import sys

# Standard library imports
from typing import Optional, List, Dict

# Third-party imports

# PyQt6 imports
from PyQt6.QtWidgets import (
    QDialog,
    QLabel,
    QLineEdit,
    QCheckBox,
    QVBoxLayout,
    QPushButton,
    QMessageBox,
    QHBoxLayout,
    QComboBox,
    QSplitter,
    QFrame,
    QSizePolicy,
    QScrollArea,
    QSpacerItem,
    QProgressBar,
    QFormLayout,
    QDialogButtonBox,
    QApplication,
    QTableWidgetItem,
    QTableWidget,
    QHeaderView,
    QTextEdit
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize, QTimer, QDate
from PyQt6.QtGui import (
    QIcon,
    QFont,
    QColor,
    QPixmap,
    QAction,
    QPainter,
    QKeySequence,
    QShortcut
)

class ColumnFilterDialog(QDialog):
    """Simple dialog for text-based column filtering"""

    def __init__(self, column_name, pandas_model, parent=None):
        super().__init__(parent)
        self.column_name = column_name
        self.pandas_model = pandas_model
        self.text_input = None
        self.case_sensitive_cb = None
        self.filter_action = None  # To distinguish between text and empty filter
        self.setup_ui()

    def setup_ui(self):
        """Setup the simple filter dialog UI"""
        self.setWindowTitle(f"ตัวกรองคอลัมน์: {self.column_name}")
        self.setMinimumWidth(350)
        self.setFixedHeight(250)

        layout = QVBoxLayout()

        # Title label
        title_label = QLabel(f"Filter data in column '{self.column_name}':")
        title_label.setStyleSheet("font-weight: bold; font-size: 12px;")
        layout.addWidget(title_label)

        # Help text
        help_label = QLabel(
            "Enter text to search. Use * for wildcards (e.g., John* will find John, Johnson)"
        )
        help_label.setStyleSheet("color: gray; font-size: 10px;")
        help_label.setWordWrap(True)
        layout.addWidget(help_label)

        # Show sample values from the column
        unique_values = self.pandas_model.get_unique_values(self.column_name)
        if unique_values:
            sample_values = unique_values[:5]  # Show first 5 unique values
            if len(unique_values) > 5:
                sample_text = f"Sample values: {', '.join(sample_values)}... ({len(unique_values)} total unique values)"
            else:
                sample_text = f"Available values: {', '.join(sample_values)}"
            
            sample_label = QLabel(sample_text)
            sample_label.setStyleSheet("color: blue; font-size: 9px; font-style: italic;")
            sample_label.setWordWrap(True)
            layout.addWidget(sample_label)

        # Text input
        self.text_input = QLineEdit()
        self.text_input.setPlaceholderText("Enter search text...")

        # Case sensitive checkbox
        self.case_sensitive_cb = QCheckBox("Case sensitive")

        # Load current filter if exists
        current_filter = self.pandas_model._filters.get(self.column_name)
        if isinstance(current_filter, dict) and current_filter.get("filter_type") == "text":
            self.text_input.setText(current_filter.get("text_filter", ""))
            self.case_sensitive_cb.setChecked(
                current_filter.get("case_sensitive", False)
            )

        layout.addWidget(self.text_input)
        layout.addWidget(self.case_sensitive_cb)

        # Spacer
        layout.addStretch()

        # Buttons
        button_layout = QHBoxLayout()

        filter_empty_button = QPushButton("กรองค่าว่าง")
        filter_empty_button.clicked.connect(self.accept_empty_filter)
        button_layout.addWidget(filter_empty_button)

        button_layout.addStretch()

        ok_button = QPushButton("ตกลง")
        ok_button.clicked.connect(self.accept_text_filter)
        ok_button.setDefault(True)  # Make this the default button
        button_layout.addWidget(ok_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

        # Set focus to text input and connect Enter key to text filter
        self.text_input.setFocus()
        self.text_input.returnPressed.connect(self.accept_text_filter)

    def accept_text_filter(self):
        """Set action for text filter and accept the dialog."""
        self.filter_action = "text"
        self.accept()

    def accept_empty_filter(self):
        """Set action for empty filter and accept the dialog."""
        self.filter_action = "empty"
        self.accept()

    def get_filter_value(self):
        """Get the filter value based on the user's action."""
        if self.filter_action == "text":
            text_pattern = self.text_input.text().strip()
            if text_pattern:
                return {
                    "filter_type": "text",
                    "text_filter": text_pattern,
                    "case_sensitive": self.case_sensitive_cb.isChecked(),
                }
        elif self.filter_action == "empty":
            return {"filter_type": "empty"}
        else:
            # Default to text filter if no action is set (e.g., when Enter is pressed)
            text_pattern = self.text_input.text().strip()
            if text_pattern:
                return {
                    "filter_type": "text",
                    "text_filter": text_pattern,
                    "case_sensitive": self.case_sensitive_cb.isChecked(),
                }
        return None


if __name__ == "__main__":
    app = QApplication(sys.argv)
    dialog = ColumnFilterDialog(None, None)
    dialog.show()
    sys.exit(app.exec_())
