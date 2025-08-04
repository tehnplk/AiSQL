from PyQt6.QtCore import QAbstractTableModel, Qt
import pandas as pd

class PandasTableModel(QAbstractTableModel):
    """Table model for pandas DataFrame with filtering and sorting support."""

    def __init__(self, dataframe=None):
        super().__init__()
        self._dataframe = dataframe if dataframe is not None else pd.DataFrame()
        self._original_dataframe = self._dataframe.copy()
        self.column_filters = {}  # Store filters for each column
        self._sort_column = None
        self._sort_order = Qt.SortOrder.AscendingOrder

    def rowCount(self, parent=None):
        return len(self._dataframe)

    def columnCount(self, parent=None):
        return len(self._dataframe.columns)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None

        if role == Qt.ItemDataRole.DisplayRole:
            value = self._dataframe.iloc[index.row(), index.column()]
            return str(value) if pd.notna(value) else ""

        return None

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                # Add sort indicator to column header
                header = str(self._dataframe.columns[section])
                if section == self._sort_column:
                    sort_indicator = (
                        " ↑"
                        if self._sort_order == Qt.SortOrder.AscendingOrder
                        else " ↓"
                    )
                    header += sort_indicator
                return header
            else:
                return str(section + 1)
        return None

    def sort(self, column, order):
        """Sort table by given column number."""
        self.layoutAboutToBeChanged.emit()

        column_name = self._dataframe.columns[column]
        ascending = order == Qt.SortOrder.AscendingOrder

        # Sort the dataframe
        self._dataframe = self._dataframe.sort_values(
            by=column_name,
            ascending=ascending,
            na_position="last",
            key=lambda col: col.astype(str).str.lower(),
        )

        # Store sort state
        self._sort_column = column
        self._sort_order = order

        self.layoutChanged.emit()
        self.headerDataChanged.emit(
            Qt.Orientation.Horizontal, 0, self.columnCount() - 1
        )

    def set_dataframe(self, dataframe):
        """Set new dataframe data."""
        self.beginResetModel()
        self._dataframe = dataframe.copy()
        self._original_dataframe = dataframe.copy()
        self.column_filters = {}
        self.endResetModel()

    def apply_filters(self):
        """Apply all column filters to the dataframe using 'contains' method."""
        self.beginResetModel()

        filtered_df = self._original_dataframe.copy()

        for column, filter_text in self.column_filters.items():
            if column in filtered_df.columns and filter_text:
                # Convert column to string and apply contains filter (case-insensitive)
                filtered_df = filtered_df[
                    filtered_df[column]
                    .astype(str)
                    .str.contains(filter_text, case=False, na=False, regex=False)
                ]

        self._dataframe = filtered_df
        self.endResetModel()

    def set_column_filter(self, column, filter_text):
        """Set filter for a specific column using 'contains' method."""
        if filter_text:
            self.column_filters[column] = filter_text
        else:
            self.column_filters.pop(column, None)
        self.apply_filters()

