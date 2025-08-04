import os
import sys

# Standard library imports

# Third-party imports
import pandas as pd
import openpyxl

# PyQt6 imports
from PyQt6.QtCore import QObject, pyqtSignal, QThread, Qt
from PyQt6.QtWidgets import (
    QApplication,
    QFileDialog,
    QMessageBox,
    QWidget,
    QProgressBar
)

# Handle imports with robust fallback
try:
    # First try relative imports (works when part of package)
    from .PandasModel import PandasModel as PandasTableModel
except ImportError:
    # Fallback to direct import if relative import fails
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    from PandasModel import PandasModel as PandasTableModel

try:
    # Imports from project root with fallback
    from AppSetting import settings
except ImportError:
    # Fallback to direct import if relative import fails
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    from AppSetting import settings


class ExcelLoader(QObject):
    """Worker thread for loading Excel files without freezing the UI."""
    finished = pyqtSignal(object)  # Emits the loaded DataFrame
    error = pyqtSignal(str)
    progress = pyqtSignal(str)

    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path

    def load_excel(self):
        """Loads the excel file and emits signals on completion or error."""
        try:
            self.progress.emit("Loading Excel file, please wait...")
            if not os.path.exists(self.file_path):
                raise FileNotFoundError(f"File not found: {self.file_path}")
            if not self.file_path.lower().endswith(('.xlsx', '.xls')):
                raise ValueError("Please select a valid Excel file (.xlsx or .xls)")
            
            df = pd.read_excel(self.file_path, header=0, engine='openpyxl')
            self.finished.emit(df)
        except Exception as e:
            self.error.emit(str(e))
