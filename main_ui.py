import sys
import re
from PyQt6.QtWidgets import (QApplication, QMainWindow, QTextEdit, QVBoxLayout, 
                             QHBoxLayout, QWidget, QPushButton, QSplitter, 
                             QLabel, QCompleter, QTextBrowser, QTableView, QHeaderView, QComboBox)
from PyQt6.QtCore import Qt, QStringListModel, QRect, QAbstractTableModel
from PyQt6.QtGui import (QSyntaxHighlighter, QTextCharFormat, QColor, QFont, 
                         QTextCursor, QKeySequence, QAction, QStandardItemModel, QStandardItem)


class SQLSyntaxHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Define SQL keywords
        self.sql_keywords = [
            'SELECT', 'FROM', 'WHERE', 'INSERT', 'UPDATE', 'DELETE', 'CREATE', 
            'DROP', 'ALTER', 'TABLE', 'INDEX', 'VIEW', 'DATABASE', 'SCHEMA',
            'JOIN', 'INNER', 'LEFT', 'RIGHT', 'FULL', 'OUTER', 'ON', 'USING',
            'GROUP', 'BY', 'ORDER', 'HAVING', 'DISTINCT', 'UNION', 'ALL',
            'AS', 'AND', 'OR', 'NOT', 'IN', 'EXISTS', 'BETWEEN', 'LIKE',
            'IS', 'NULL', 'TRUE', 'FALSE', 'CASE', 'WHEN', 'THEN', 'ELSE', 'END',
            'IF', 'IFNULL', 'COALESCE', 'COUNT', 'SUM', 'AVG', 'MIN', 'MAX',
            'VARCHAR', 'INT', 'INTEGER', 'DECIMAL', 'FLOAT', 'DOUBLE', 'DATE',
            'DATETIME', 'TIMESTAMP', 'TEXT', 'BLOB', 'PRIMARY', 'KEY', 'FOREIGN',
            'REFERENCES', 'UNIQUE', 'NOT', 'NULL', 'DEFAULT', 'AUTO_INCREMENT',
            'CONSTRAINT', 'CHECK', 'TRIGGER', 'PROCEDURE', 'FUNCTION'
        ]
        
        # Define highlighting rules
        self.highlighting_rules = []
        
        # Keywords format
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor(86, 156, 214))  # Blue
        keyword_format.setFontWeight(QFont.Weight.Bold)
        
        for keyword in self.sql_keywords:
            pattern = f'\\b{keyword}\\b'
            self.highlighting_rules.append((re.compile(pattern, re.IGNORECASE), keyword_format))
        
        # String literals format
        string_format = QTextCharFormat()
        string_format.setForeground(QColor(206, 145, 120))  # Orange
        self.highlighting_rules.append((re.compile(r"'[^']*'"), string_format))
        self.highlighting_rules.append((re.compile(r'"[^"]*"'), string_format))
        
        # Numbers format
        number_format = QTextCharFormat()
        number_format.setForeground(QColor(181, 206, 168))  # Green
        self.highlighting_rules.append((re.compile(r'\b\d+\.?\d*\b'), number_format))
        
        # Comments format
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor(106, 153, 85))  # Dark green
        comment_format.setFontItalic(True)
        self.highlighting_rules.append((re.compile(r'--[^\n]*'), comment_format))
        self.highlighting_rules.append((re.compile(r'/\*.*?\*/', re.DOTALL), comment_format))
        
        # Operators format
        operator_format = QTextCharFormat()
        operator_format.setForeground(QColor(212, 212, 212))  # Light gray
        operator_format.setFontWeight(QFont.Weight.Bold)
        operators = ['=', '!=', '<>', '<', '>', '<=', '>=', '+', '-', '*', '/', '%']
        for op in operators:
            self.highlighting_rules.append((re.compile(re.escape(op)), operator_format))
    
    def highlightBlock(self, text):
        for pattern, format in self.highlighting_rules:
            for match in pattern.finditer(text):
                start, end = match.span()
                self.setFormat(start, end - start, format)


class SQLTextEdit(QTextEdit):
    def __init__(self):
        super().__init__()
        
        # Set font
        font = QFont("Consolas", 11)
        if not font.exactMatch():
            font = QFont("Courier New", 11)
        self.setFont(font)
        
        # Set tab width
        self.setTabStopDistance(40)
        
        # Apply syntax highlighter
        self.highlighter = SQLSyntaxHighlighter(self.document())
        
        # Setup auto-completion
        self.setup_completer()
        
        # Set placeholder text
        self.setPlaceholderText("-- Enter your SQL query here\nSELECT * FROM table_name;")
    
    def setup_completer(self):
        # SQL keywords and common functions for auto-completion
        sql_completions = [
            'SELECT', 'FROM', 'WHERE', 'INSERT INTO', 'UPDATE', 'DELETE FROM',
            'CREATE TABLE', 'DROP TABLE', 'ALTER TABLE', 'CREATE INDEX',
            'JOIN', 'INNER JOIN', 'LEFT JOIN', 'RIGHT JOIN', 'FULL OUTER JOIN',
            'GROUP BY', 'ORDER BY', 'HAVING', 'DISTINCT', 'UNION', 'UNION ALL',
            'AND', 'OR', 'NOT', 'IN', 'EXISTS', 'BETWEEN', 'LIKE', 'IS NULL',
            'IS NOT NULL', 'CASE WHEN', 'COUNT(*)', 'COUNT(DISTINCT', 'SUM(',
            'AVG(', 'MIN(', 'MAX(', 'COALESCE(', 'IFNULL(', 'SUBSTRING(',
            'UPPER(', 'LOWER(', 'TRIM(', 'LENGTH(', 'CONCAT(', 'DATE(',
            'NOW()', 'CURRENT_DATE', 'CURRENT_TIME', 'CURRENT_TIMESTAMP'
        ]
        
        self.completer = QCompleter(sql_completions)
        self.completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.completer.setWidget(self)
        self.completer.activated.connect(self.insert_completion)
    
    def insert_completion(self, completion):
        cursor = self.textCursor()
        extra = len(completion) - len(self.completer.completionPrefix())
        cursor.movePosition(QTextCursor.MoveOperation.Left)
        cursor.movePosition(QTextCursor.MoveOperation.EndOfWord)
        cursor.insertText(completion[-extra:])
        self.setTextCursor(cursor)
    
    def keyPressEvent(self, event):
        if self.completer.popup().isVisible():
            if event.key() in (Qt.Key.Key_Enter, Qt.Key.Key_Return, Qt.Key.Key_Escape, Qt.Key.Key_Tab, Qt.Key.Key_Backtab):
                event.ignore()
                return
        
        super().keyPressEvent(event)
        
        # Trigger auto-completion
        cursor = self.textCursor()
        cursor.select(QTextCursor.SelectionType.WordUnderCursor)
        word = cursor.selectedText()
        
        if len(word) >= 2:
            self.completer.setCompletionPrefix(word.upper())
            popup = self.completer.popup()
            popup.setCurrentIndex(self.completer.completionModel().index(0, 0))
            
            cursor_rect = self.cursorRect()
            cursor_rect.setWidth(popup.sizeHintForColumn(0) + popup.verticalScrollBar().sizeHint().width())
            self.completer.complete(cursor_rect)
        else:
            self.completer.popup().hide()


class main_ui(object):
    def setupUi(self,main_ui):
        self.setWindowTitle("AiSQL")
        self.setGeometry(100, 100, 1000, 700)
        self.showMaximized()
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create layout
        layout = QVBoxLayout(central_widget)
        
        # Create toolbar
        toolbar_layout = QHBoxLayout()
        
        # Buttons
        self.run_button = QPushButton("▶️ Run Query")
        self.run_button.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
        """)
        
        self.clear_button = QPushButton("Clear")
        
        self.format_button = QPushButton("Format SQL")
        
        self.export_button = QPushButton("📤 Export to Excel")
        
        # Model selection combo box
        self.model_combo = QComboBox()
        self.model_combo.addItems([
            "gemini-2.0-flash-lite",
            "gemini-2.0-flash",
            "gemini-2.5-flash-lite",
            "gemini-2.5-flash",
            "horizon-beta"
        ])
        self.model_combo.setCurrentText("gemini-2.5-flash")
        self.model_combo.setStyleSheet("""
            QComboBox {
                background-color: #6c757d;
                color: #ffffff;
                border: 1px solid #5a6268;
                padding: 6px 16px;
                border-radius: 4px;
                font-weight: 600;
                min-width: 180px;
                font-size: 13px;
            }
            QComboBox:hover {
                background-color: #5a6268;
                border-color: #4e555b;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
                width: 0;
                height: 0;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 5px solid #ffffff;
            }
            QComboBox QAbstractItemView {
                background: #6c757d;
                color: #ffffff;
                selection-background-color: #5a6268;
                selection-color: #ffffff;
                border: 1px solid #5a6268;
                padding: 4px;
                outline: none;
            }
        """)
        self.export_button.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            QPushButton:disabled {
                background-color: #6c757d;
                color: #ffffff;
            }
        """)
        self.export_button.setEnabled(False)  # Initially disabled
        
        self.save_button = QPushButton("💾 Save SQL")
        self.save_button.setStyleSheet("""
            QPushButton {
                background-color: #17a2b8;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #138496;
            }
        """)
        
        toolbar_layout.addWidget(self.format_button)
        toolbar_layout.addWidget(self.clear_button)
        toolbar_layout.addWidget(self.save_button)
        toolbar_layout.addWidget(self.export_button)
        toolbar_layout.addStretch()
        toolbar_layout.addWidget(self.run_button)
        toolbar_layout.addWidget(self.model_combo)
        
        layout.addLayout(toolbar_layout)
        
        # Create horizontal layout for chat text and button
        chat_layout = QHBoxLayout()
        
        # Add 2-row text edit above SQL area
        self.chat_text = QTextEdit()
        self.chat_text.setMaximumHeight(60)  # Approximately 2 rows
        self.chat_text.setPlaceholderText("สอบถามข้อมูลด้วย AI")
        self.chat_text.setStyleSheet("""
            QTextEdit {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                padding: 8px;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 10pt;
                color: #495057;
            }
            QTextEdit:focus {
                border-color: #0078d4;
                background-color: #ffffff;
            }
        """)
        
        # Add chat button
        self.chat_button = QPushButton("Chat")
        self.chat_button.setMaximumHeight(60)  # Same height as chat_text
        self.chat_button.setFixedWidth(120)  # Set fixed width to 120px
        self.chat_button.setStyleSheet("""
            QPushButton {
                background-color: #28a745;  /* Green color */
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #218838;  /* Darker green on hover */
            }
            QPushButton:pressed {
                background-color: #1e7e34;  /* Even darker green when pressed */
            }
        """)
        
        # Add widgets to horizontal layout
        chat_layout.addWidget(self.chat_text)
        chat_layout.addWidget(self.chat_button)
        
        # Add the horizontal layout to main layout
        layout.addLayout(chat_layout)
        
        # Create splitter for editor and results
        splitter = QSplitter(Qt.Orientation.Vertical)
        
        # SQL text editor
        self.sql_editor = SQLTextEdit()
        
        # Results area - TableView
        self.results_area = QTableView()
        self.results_area.setMinimumHeight(100)  # Minimum height when collapsed
        self.results_area.setStyleSheet("""
            QTableView {
                background-color: white;
                color: black;
                border: 1px solid #cccccc;
                gridline-color: #e0e0e0;
                font-family: 'Consolas', monospace;
            }
            QHeaderView::section {
                background-color: #f0f0f0;
                color: black;
                padding: 4px;
                border: 1px solid #cccccc;
                font-weight: bold;
            }
        """)
        
        # Add widgets to splitter
        splitter.addWidget(self.sql_editor)
        splitter.addWidget(self.results_area)
        
        # Initialize empty model
        self.results_model = QStandardItemModel()
        self.results_area.setModel(self.results_model)
        
        # Add status bar
        self.statusbar = self.statusBar()
        self.statusbar.setStyleSheet("""
            QStatusBar {
                background-color: #2d2d30;
                color: #ffffff;
                border-top: 1px solid #3e3e42;
            }
        """)
        self.statusbar.showMessage("Ready")
        
        # Set splitter stretch factors and initial sizes
        splitter.setStretchFactor(0, 3)  # Editor gets 3/4 of the space
        splitter.setStretchFactor(1, 1)  # Results get 1/4 of the space
        
        # Set minimum sizes for the splitter handles
        splitter.setHandleWidth(8)  # Make the splitter handle more visible
        splitter.setChildrenCollapsible(False)  # Prevent either widget from being collapsed completely
        
        layout.addWidget(splitter)
        
        # Set dark theme
        self.set_dark_theme()
        
        # Create menu bar
        self.create_menu_bar()
    
    def create_menu_bar(self):
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('File')
        
        new_action = QAction('New', self)
        new_action.setShortcut(QKeySequence.StandardKey.New)
        new_action.triggered.connect(self.clear_editor)
        file_menu.addAction(new_action)
        
        open_action = QAction('Open...', self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        file_menu.addAction(open_action)
        self.open_action = open_action
        
        # Add Settings submenu
        settings_action = QAction('Settings', self)
        settings_action.setShortcut('Ctrl+,')
        file_menu.addAction(settings_action)
        
        # Store reference to settings action for later connection
        self.settings_action = settings_action
        
        # Edit menu
        edit_menu = menubar.addMenu('Edit')
        
        copy_action = QAction('Copy', self)
        copy_action.setShortcut(QKeySequence.StandardKey.Copy)
        copy_action.triggered.connect(self.sql_editor.copy)
        edit_menu.addAction(copy_action)
        
        paste_action = QAction('Paste', self)
        paste_action.setShortcut(QKeySequence.StandardKey.Paste)
        paste_action.triggered.connect(self.sql_editor.paste)
        edit_menu.addAction(paste_action)
        
        # Query menu
        query_menu = menubar.addMenu('Query')
        
        run_action = QAction('Run Query', self)
        run_action.setShortcut('F5')
        # Signal connection will be handled in main class
        query_menu.addAction(run_action)
        
        # Store reference for main class to connect
        self.run_action = run_action
    
    def set_dark_theme(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
                color: #ffffff;
            }
            QTextEdit {
                background-color: #2d2d30;
                color: #ffffff;
                border: 1px solid #3e3e42;
                border-radius: 4px;
                padding: 8px;
                selection-background-color: #094771;
            }
            QTextBrowser {
                background-color: #252526;
                color: #cccccc;
                border: 1px solid #3e3e42;
                border-radius: 4px;
                padding: 8px;
            }
            QPushButton {
                background-color: #3c3c3c;
                color: #ffffff;
                border: 1px solid #5a5a5a;
                padding: 6px 12px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #4a4a4a;
            }
            QMenuBar {
                background-color: #2d2d30;
                color: #ffffff;
                border-bottom: 1px solid #3e3e42;
            }
            QMenuBar::item {
                padding: 6px 12px;
            }
            QMenuBar::item:selected {
                background-color: #3e3e42;
            }
            QMenu {
                background-color: #2d2d30;
                color: #ffffff;
                border: 1px solid #3e3e42;
            }
            QMenu::item:selected {
                background-color: #094771;
            }
        """)
    

