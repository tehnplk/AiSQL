import os
import sys

# Standard library imports
from typing import Any, Optional
import re
import datetime
import numpy as np

# Third-party imports
import pandas as pd

# PyQt6 imports
from PyQt6.QtCore import (
    QAbstractTableModel,
    QModelIndex,
    Qt,
    pyqtSignal,
    QSortFilterProxyModel,
    QVariant,
    QSize,
    QTimer,
    QDate
)
from PyQt6.QtWidgets import (
    QMessageBox,
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QFileDialog,
    QComboBox,
    QLineEdit,
    QSplitter,
    QFrame,
    QSizePolicy,
    QScrollArea,
    QSpacerItem,
    QProgressBar,
    QFormLayout,
    QDialogButtonBox
)
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

# Imports from project root with fallback
try:
    from AppSetting import settings
except ImportError:
    # Fallback to direct import if relative import fails
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    from AppSetting import settings


class PandasModel(QAbstractTableModel):
    """A model to interface a Qt view with pandas dataframe"""

    def __init__(self, data=None, parent=None):
        QAbstractTableModel.__init__(self, parent)
        self._original_data = data if data is not None else pd.DataFrame()
        self._data = self._original_data.copy()
        self._filters = {}  # Dictionary to store active filters: {column_name: filter_value}

    def rowCount(self, parent=None):
        return len(self._data.index)

    def columnCount(self, parent=None):
        return len(self._data.columns)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if index.isValid() and role == Qt.ItemDataRole.DisplayRole:
            value = self._data.iloc[index.row(), index.column()]
            # Handle NaN, None, and empty values - display as empty instead of "nan"
            if pd.isna(value) or value is None or str(value).strip() == "":
                return ""  # Return empty string instead of "nan"
            return str(value)
        return QVariant()

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return str(self._data.columns[section])
            else:
                return str(self._data.index[section])
        return QVariant()

    def update_data(self, data):
        """Update the model with new data"""
        self.beginResetModel()
        self._original_data = data.copy()
        self._data = data.copy()
        self._filters = {}  # Reset filters when data is updated
        # Ensure all data types are properly set for filtering
        for col in self._data.columns:
            if self._data[col].dtype == 'object':
                # Convert object columns to string for better filtering
                self._data[col] = self._data[col].astype(str)
                self._original_data[col] = self._original_data[col].astype(str)
        self.endResetModel()
        
    def apply_filter(self, column_name, filter_value):
        """Apply a filter to the specified column"""
        if column_name not in self._original_data.columns:
            print(f"Error: Column '{column_name}' not found for filtering.")
            return False
            
        # Debug: Print filter criteria
        print(f"\n=== FILTER CRITERIA DEBUG ===")
        print(f"Column: {column_name}")
        print(f"Filter Value: {filter_value}")
        print(f"Filter Type: {type(filter_value)}")
        
        # Show user's raw input if it's a text filter
        if isinstance(filter_value, dict):
            if filter_value.get('filter_type') == 'text':
                user_text = filter_value.get('text_filter', '')
                case_sensitive = filter_value.get('case_sensitive', False)
                print(f"User Input Text: '{user_text}'")
                print(f"Case Sensitive: {case_sensitive}")
            elif filter_value.get('filter_type') == 'empty':
                print(f"User Action: Filter for empty values")
        else:
            print(f"User Input (legacy format): '{filter_value}'")
        
        print(f"Original Data Shape: {self._original_data.shape}")
        print(f"Current Data Shape (before): {self._data.shape}")
        print(f"Active Filters (before): {self._filters}")
        
        # Store the filter
        self._filters[column_name] = filter_value
        print(f"Active Filters (after adding): {self._filters}")
        
        # Apply all filters
        self._apply_all_filters()
        
        print(f"Final Data Shape (after): {self._data.shape}")
        print(f"Filter Applied Successfully: True")
        print("============================\n")
        
        return True
        
    def clear_filter(self, column_name):
        """Clear the filter for a specific column"""
        print(f"\n=== CLEARING FILTER ===")
        print(f"Column: {column_name}")
        print(f"Active Filters (before): {self._filters}")
        print(f"Current Data Shape (before): {self._data.shape}")
        
        if column_name in self._filters:
            del self._filters[column_name]
            print(f"Active Filters (after removal): {self._filters}")
            self._apply_all_filters()
            print(f"Final Data Shape (after): {self._data.shape}")
            print("Filter cleared successfully")
            print("======================\n")
            return True
        else:
            print(f"No filter found for column '{column_name}'")
            print("======================\n")
        return False
        
    def clear_all_filters(self):
        """Clear all filters"""
        print(f"\n=== CLEARING ALL FILTERS ===")
        print(f"Active Filters (before): {self._filters}")
        print(f"Current Data Shape (before): {self._data.shape}")
        print(f"Original Data Shape: {self._original_data.shape}")
        
        if self._filters:
            self._filters = {}
            self.beginResetModel()
            self._data = self._original_data.copy()
            self.endResetModel()
            print(f"Final Data Shape (after): {self._data.shape}")
            print("All filters cleared successfully")
            print("============================\n")
            return True
        else:
            print("No filters to clear")
            print("============================\n")
        return False
        
    def _apply_all_filters(self):
        """Apply all active filters to the data"""
        print(f"\n=== APPLYING ALL FILTERS ===")
        print(f"Total Filters to Apply: {len(self._filters)}")
        
        self.beginResetModel()
        
        # Start with the original data
        filtered_data = self._original_data.copy()
        initial_rows = len(filtered_data)
        print(f"Starting with {initial_rows} rows")
        
        # Apply each filter
        for column_name, filter_value in self._filters.items():
            rows_before = len(filtered_data)
            print(f"\nApplying filter on column '{column_name}':")
            print(f"  Rows before this filter: {rows_before}")
            print(f"  Filter value: {filter_value}")
            
            # Show user input details
            if isinstance(filter_value, dict):
                if filter_value.get('filter_type') == 'text':
                    user_text = filter_value.get('text_filter', '')
                    case_sensitive = filter_value.get('case_sensitive', False)
                    print(f"  User typed: '{user_text}' (Case sensitive: {case_sensitive})")
                elif filter_value.get('filter_type') == 'empty':
                    print(f"  User chose: Filter for empty values")
            else:
                print(f"  User input (legacy format): '{filter_value}'")
            
            if column_name in filtered_data.columns:
                if isinstance(filter_value, dict):
                    filter_type = filter_value.get('filter_type')
                    print(f"  Filter type: {filter_type}")
                    
                    if filter_type == 'empty':
                        # Filter for empty values (NaN, None, empty string)
                        filtered_data = filtered_data[
                            filtered_data[column_name].isna() | 
                            (filtered_data[column_name].astype(str).str.strip() == '')
                        ]
                        print(f"  Applied empty filter")
                    elif filter_type == 'text':
                        # Text filter with case sensitivity option
                        text_filter = filter_value.get('text_filter', '')
                        case_sensitive = filter_value.get('case_sensitive', False)
                        print(f"  Text filter: '{text_filter}', Case sensitive: {case_sensitive}")
                        
                        if text_filter:
                            # Convert to string and handle case sensitivity
                            col_data = filtered_data[column_name].fillna('').astype(str)
                            original_filter = text_filter
                            
                            if not case_sensitive:
                                col_data = col_data.str.lower()
                                text_filter = text_filter.lower()
                            
                            # Handle wildcard patterns
                            if '*' in text_filter:
                                # Convert SQL-like wildcards to regex
                                import re
                                pattern = text_filter.replace('*', '.*')
                                print(f"  Using wildcard pattern: '{pattern}'")
                                try:
                                    mask = col_data.str.contains(pattern, regex=True, na=False)
                                    filtered_data = filtered_data[mask]
                                    print(f"  Wildcard filter applied successfully")
                                except Exception as e:
                                    print(f"  Wildcard filter failed: {e}")
                                    # Fallback to simple contains if regex fails
                                    clean_filter = text_filter.replace('*', '')
                                    if clean_filter:  # Only apply if there's actual text after removing *
                                        mask = col_data.str.contains(clean_filter, na=False)
                                        filtered_data = filtered_data[mask]
                                        print(f"  Fallback to simple contains: '{clean_filter}'")
                            else:
                                # Simple substring search (default behavior - like LIKE '%text%')
                                mask = col_data.str.contains(text_filter, na=False)
                                filtered_data = filtered_data[mask]
                                print(f"  Applied substring filter")
                    elif filter_value.get('empty_only', False):
                        # Legacy empty filter format
                        filtered_data = filtered_data[
                            filtered_data[column_name].isna() | 
                            (filtered_data[column_name].astype(str).str.strip() == '')
                        ]
                        print(f"  Applied legacy empty filter")
                    elif filter_value.get('not_empty', False):
                        # Legacy non-empty filter format
                        filtered_data = filtered_data[
                            filtered_data[column_name].notna() & 
                            (filtered_data[column_name].astype(str).str.strip() != '')
                        ]
                        print(f"  Applied legacy not-empty filter")
                elif filter_value:  # Regular text filter
                    # Make sure column is treated as string for filtering
                    try:
                        # Convert column to string and ensure filter_value is a string
                        filter_str = str(filter_value)
                        print(f"  Regular text filter: '{filter_str}'")
                        # Use pandas str.contains for substring matching
                        mask = filtered_data[column_name].fillna('').astype(str).str.lower().str.contains(filter_str.lower())
                        filtered_data = filtered_data[mask]
                        print(f"  Applied text filter on {column_name}: '{filter_str}', matching {mask.sum()} rows")
                    except Exception as e:
                        print(f"  Error filtering column {column_name}: {e}")
                        # Fall back to simple equality check if string operations fail
                        try:
                            filtered_data = filtered_data[
                                filtered_data[column_name].astype(str) == str(filter_value)
                            ]
                            print(f"  Applied fallback equality filter")
                        except:
                            print(f"  Even fallback filtering failed for column {column_name}")
                            pass
            
            rows_after = len(filtered_data)
            print(f"  Rows after this filter: {rows_after}")
            
        print(f"\nFinal result: {len(filtered_data)} rows from original {initial_rows}")
        print("============================\n")
        
        self._data = filtered_data
        self.endResetModel()
        
    def get_unique_values(self, column_name):
        """Get unique values for a column to populate filter dropdown"""
        if column_name in self._original_data.columns:
            # Get unique values, handle NaN values, and sort
            values = self._original_data[column_name].dropna().unique().tolist()
            values = [str(val) for val in values]  # Convert all values to strings
            values.sort()
            return values
        return []
        
    def is_column_filtered(self, column_name):
        """Check if a column has an active filter"""
        return column_name in self._filters
        
    def get_filter_info(self):
        """Get information about active filters"""
        return self._filters.copy()


    def sort(self, column, order):
        """Sort table by given column number"""
        self.layoutAboutToBeChanged.emit()

        if len(self._data.columns) > column >= 0:
            # Get column name
            col_name = self._data.columns[column]

            # Determine sort order
            ascending = order == Qt.SortOrder.AscendingOrder

            # Sort the dataframe
            try:
                self._data = self._data.sort_values(by=col_name, ascending=ascending)
                # Reset index to maintain row numbers
                self._data = self._data.reset_index(drop=True)
            except Exception as e:
                print(f"Error sorting column '{col_name}': {str(e)}")

        self.layoutChanged.emit()

    def flags(self, index):
        """Return item flags for the given index"""
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags
        return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable

    def update_his_data(
        self, identifier_column_name, identifier_value, his_data, refresh_model=True
    ):
        """
        Update a row with data fetched from HIS. Adds new columns if they don't exist.
        If refresh_model is False, _apply_all_filters() will not be called.
        """
        if identifier_column_name not in self._original_data.columns:
            print(f"Error: Identifier column '{identifier_column_name}' not found.")
            return

        # Define the order of new columns to be added to the left
        new_columns_ordered = ["pid_found", "cid_found", "fname_found", "lname_found"]

        # Check which new columns need to be added
        cols_to_add = [
            col for col in new_columns_ordered if col not in self._original_data.columns
        ]

        # Insert new columns at the beginning of the DataFrame if they don't exist
        if cols_to_add:
            # Insert in reverse order to maintain the desired final order at the front
            for col_name in reversed(cols_to_add):
                self._original_data.insert(0, col_name, pd.NA)
        # Find the index of the row to update in the original, unfiltered data
        target_indices = self._original_data[
            self._original_data[identifier_column_name] == identifier_value
        ].index

        if not target_indices.empty:
            target_row_index = target_indices[0]

            # Update the row with the new data
            for col, val in his_data.items():
                if col in self._original_data.columns:
                    self._original_data.loc[target_row_index, col] = val

            if refresh_model:
                # Refresh the model to reflect changes
                if self._filters:
                    # If filters are active, reapply them
                    self._apply_all_filters()
                else:
                    # Otherwise just reset with the original data
                    self.beginResetModel()
                    self._data = self._original_data.copy()
                    self.endResetModel()
        else:
            print(
                f"Warning: Could not find row with {identifier_column_name} = {identifier_value} in original data."
            )
