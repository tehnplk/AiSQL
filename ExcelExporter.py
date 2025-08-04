import os
import sys

# Standard library imports

# Third-party imports
import pandas as pd
import openpyxl

# PyQt6 imports
from PyQt6.QtCore import QObject, pyqtSignal, QThread
from PyQt6.QtWidgets import QMessageBox, QFileDialog, QProgressBar

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

class ExcelExporter(QObject):
    """Worker thread for exporting data to an Excel file without freezing the UI."""
    finished = pyqtSignal()
    error = pyqtSignal(str)
    progress = pyqtSignal(str)

    def __init__(self, data, file_path):
        super().__init__()
        self.data = data
        self.file_path = file_path

    def export_to_excel(self):
        """Exports the DataFrame to the specified file (Excel or CSV)."""
        try:
            self.progress.emit("Exporting data, please wait...")
            
            # Check file extension and export accordingly
            if self.file_path.lower().endswith('.csv'):
                self.data.to_csv(self.file_path, index=False)
            else:
                # Default to Excel format
                self.data.to_excel(self.file_path, index=False, engine='openpyxl')
                
            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))
