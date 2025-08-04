import sys
from PyQt6.QtWidgets import (QApplication, QDialog, QVBoxLayout, QFormLayout, 
                            QLineEdit, QDialogButtonBox, QMessageBox, QCheckBox, 
                            QComboBox)
from PyQt6.QtCore import Qt, QSettings
import pymysql

class DbSettingsDialog(QDialog):
    """
    Database Settings Dialog for configuring MySQL database connections.
    Saves settings using QSettings and tests connections using PyMySQL.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Database Settings")
        self.setMinimumWidth(400)
        
        # Initialize UI
        self.setup_ui()
        
        # Load saved settings
        self.load_settings()
    
    def setup_ui(self):
        """Set up the user interface components."""
        layout = QVBoxLayout()
        form_layout = QFormLayout()
        
        # Database Type
        self.db_type_combo = QComboBox()
        self.db_type_combo.addItems(["MySQL", "PostgreSQL", "SQLite"])
        form_layout.addRow("Database Type:", self.db_type_combo)
        
        # Connection parameters
        self.host_edit = QLineEdit()
        self.host_edit.setPlaceholderText("localhost")
        
        self.port_edit = QLineEdit()
        self.port_edit.setPlaceholderText("3306")
        self.port_edit.setMaximumWidth(80)
        
        self.user_edit = QLineEdit()
        self.user_edit.setPlaceholderText("username")
        
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_edit.setPlaceholderText("password")
        
        self.database_edit = QLineEdit()
        self.database_edit.setPlaceholderText("database_name")
        
        # SSL Options
        self.ssl_check = QCheckBox("Use SSL")
        self.ssl_check.stateChanged.connect(self.toggle_ssl_options)
        
        self.ssl_ca_edit = QLineEdit()
        self.ssl_ca_edit.setPlaceholderText("CA certificate path")
        self.ssl_ca_edit.setEnabled(False)
        
        # Add widgets to form layout
        form_layout.addRow("Host:", self.host_edit)
        form_layout.addRow("Port:", self.port_edit)
        form_layout.addRow("Username:", self.user_edit)
        form_layout.addRow("Password:", self.password_edit)
        form_layout.addRow("Database:", self.database_edit)
        form_layout.addRow(self.ssl_check)
        form_layout.addRow("CA Cert:", self.ssl_ca_edit)
        
        # Buttons
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel |
            QDialogButtonBox.StandardButton.Apply
        )
        
        # Add test connection button
        test_btn = self.button_box.addButton(
            "Test Connection", 
            QDialogButtonBox.ButtonRole.ActionRole
        )
        
        # Connect signals
        self.button_box.accepted.connect(self.on_accept)
        self.button_box.rejected.connect(self.reject)
        test_btn.clicked.connect(self.test_connection)
        
        # Connect Apply button
        apply_btn = self.button_box.button(QDialogButtonBox.StandardButton.Apply)
        apply_btn.clicked.connect(self.save_settings)
        
        # Add widgets to main layout
        layout.addLayout(form_layout)
        layout.addWidget(self.button_box)
        self.setLayout(layout)
    
    def toggle_ssl_options(self, state):
        """Enable/disable SSL options based on checkbox state."""
        enabled = state == Qt.CheckState.Checked.value
        self.ssl_ca_edit.setEnabled(enabled)
    
    def get_connection_params(self):
        """Get connection parameters from form fields."""
        params = {
            'host': self.host_edit.text() or 'localhost',
            'port': int(self.port_edit.text() or '3306'),
            'user': self.user_edit.text() or '',
            'password': self.password_edit.text() or '',
            'database': self.database_edit.text() or ''
        }
        
        # Add SSL parameters if enabled
        if self.ssl_check.isChecked() and self.ssl_ca_edit.text():
            params['ssl'] = {
                'ca': self.ssl_ca_edit.text(),
                'check_hostname': True
            }
        
        return params
    
    def save_settings(self):
        """Save settings to QSettings."""
        settings = QSettings("AiSQL", "DatabaseSettings")
        params = self.get_connection_params()
        
        # Save connection parameters
        for key, value in params.items():
            if key != 'ssl':  # Handle SSL separately
                settings.setValue(key, value)
        
        # Save SSL settings
        settings.setValue('use_ssl', self.ssl_check.isChecked())
        if 'ssl' in params and 'ca' in params['ssl']:
            settings.setValue('ssl_ca', params['ssl']['ca'])
        
        settings.sync()
    
    def load_settings(self):
        """Load settings from QSettings."""
        settings = QSettings("AiSQL", "DatabaseSettings")
        
        # Load connection parameters
        self.host_edit.setText(str(settings.value("host", "localhost")))
        self.port_edit.setText(str(settings.value("port", "3306")))
        self.user_edit.setText(str(settings.value("user", "")))
        self.password_edit.setText(str(settings.value("password", "")))
        self.database_edit.setText(str(settings.value("database", "")))
        
        # Load SSL settings
        use_ssl = settings.value("use_ssl", "false").lower() == 'true'
        self.ssl_check.setChecked(use_ssl)
        self.ssl_ca_edit.setText(str(settings.value("ssl_ca", "")))
        self.ssl_ca_edit.setEnabled(use_ssl)
    
    def on_accept(self):
        """Handle OK button click - save settings and close dialog."""
        if self.test_connection():
            self.save_settings()
            self.accept()
    
    def test_connection(self):
        """Test the database connection with current settings."""
        params = self.get_connection_params()
        
        if not all([params['user'], params['database']]):
            QMessageBox.warning(
                self, 
                "Incomplete Settings", 
                "Please fill in all required fields (username and database)."
            )
            return False
        
        try:
            # Test connection
            connection = pymysql.connect(**params)
            info = connection.get_server_info()
            connection.close()
            
            QMessageBox.information(
                self, 
                "Connection Successful", 
                f"Successfully connected to MySQL server (v{info})."
            )
            return True
            
        except pymysql.Error as e:
            QMessageBox.critical(
                self, 
                "Connection Failed", 
                f"Failed to connect to database: {str(e)}"
            )
            return False
        except Exception as e:
            QMessageBox.critical(
                self, 
                "Error", 
                f"An unexpected error occurred: {str(e)}"
            )
            return False

if __name__ == "__main__":
    app = QApplication(sys.argv)
    dialog = DbSettingsDialog()
    dialog.show()
    sys.exit(app.exec())