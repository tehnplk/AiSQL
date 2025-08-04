#!/usr/bin/env python3
"""
Simple test version of the SQL Editor to debug issues
"""
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel
from PyQt6.QtCore import Qt

class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SQL Editor Test")
        self.setGeometry(100, 100, 800, 600)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create layout
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        
        # Add test components
        self.label = QLabel("SQL Editor Test - Click button to test")
        self.button = QPushButton("Test Button")
        self.button.clicked.connect(self.test_function)
        
        layout.addWidget(self.label)
        layout.addWidget(self.button)
    
    def test_function(self):
        self.label.setText("Button clicked successfully!")
        print("Test function executed")

if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)
        app.setStyle("Fusion")
        
        window = TestWindow()
        window.show()
        
        print("Application starting...")
        sys.exit(app.exec())
        
    except Exception as e:
        print(f"Error starting application: {e}")
        import traceback
        traceback.print_exc()
