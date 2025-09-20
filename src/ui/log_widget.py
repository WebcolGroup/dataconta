"""
LogWidget - Specialized widget for log visualization and activity monitoring.

This module provides a specialized widget for displaying application logs with
professional styling and enhanced functionality following SOLID principles.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QGroupBox, QTextEdit, QHBoxLayout, 
    QPushButton, QLabel, QSizePolicy
)
from PySide6.QtCore import QTimer, Signal, Slot
from PySide6.QtGui import QFont
from datetime import datetime
import os


class LogWidget(QWidget):
    """
    Specialized widget for application log visualization and monitoring.
    
    Features:
    - Real-time log display with professional styling
    - Automatic log rotation and cleanup
    - Export functionality for log files
    - Clear and save operations
    - Signal-based communication with main application
    
    Signals:
        log_cleared: Emitted when logs are cleared
        log_exported: Emitted when logs are exported to file
    """
    
    # Signals for communication with main application
    log_cleared = Signal()
    log_exported = Signal(str)  # Emits file path
    
    def __init__(self, parent=None):
        """Initialize the LogWidget with professional styling."""
        super().__init__(parent)
        self.max_log_entries = 1000  # Prevent memory overflow
        self.log_entries_count = 0
        
        self.init_ui()
        self.setup_auto_cleanup()
    
    def init_ui(self):
        """Initialize the user interface components."""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create log area group
        self.log_group = QGroupBox("📝 Log de Actividades")
        self.log_group.setStyleSheet("""
            QGroupBox {
                font-size: 11px;
                font-weight: bold;
                color: #1976d2;
                border: 1px solid #1976d2;
                border-radius: 4px;
                margin-top: 20px;
                padding-top: 5px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        
        # Group layout
        group_layout = QVBoxLayout(self.log_group)
        
        # Create log text area
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setMinimumHeight(100)
        self.output_text.setMaximumHeight(150)
        self.output_text.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.output_text.setStyleSheet("""
            QTextEdit { 
                background-color: #2c3e50; 
                color: #ecf0f1; 
                font-family: 'Courier New', monospace; 
                font-size: 8pt; 
                border: 1px solid #1976d2;
                border-radius: 4px;
                padding: 8px;
            }
        """)
        
        # Create control buttons layout
        controls_layout = QHBoxLayout()
        
        # Status label
        self.status_label = QLabel("🔄 Sistema listo")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #4caf50;
                font-size: 10px;
                font-weight: bold;
            }
        """)
        
        # Clear button
        self.clear_btn = QPushButton("🗑️ Limpiar")
        self.clear_btn.setToolTip("Limpiar todos los logs del área de visualización")
        self.clear_btn.clicked.connect(self.clear_logs)
        self.clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff5722;
                color: white;
                border: none;
                padding: 5px 10px;
                border-radius: 3px;
                font-size: 9px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d84315;
            }
        """)
        
        # Export button
        self.export_btn = QPushButton("💾 Exportar")
        self.export_btn.setToolTip("Exportar logs a archivo de texto")
        self.export_btn.clicked.connect(self.export_logs)
        self.export_btn.setStyleSheet("""
            QPushButton {
                background-color: #4caf50;
                color: white;
                border: none;
                padding: 5px 10px;
                border-radius: 3px;
                font-size: 9px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #388e3c;
            }
        """)
        
        # Add controls to layout
        controls_layout.addWidget(self.status_label)
        controls_layout.addStretch()
        controls_layout.addWidget(self.clear_btn)
        controls_layout.addWidget(self.export_btn)
        
        # Add components to group layout
        group_layout.addWidget(self.output_text)
        group_layout.addLayout(controls_layout)
        
        # Add group to main layout
        main_layout.addWidget(self.log_group)
        
        # Initialize with welcome message
        self.log_message("✅ LogWidget inicializado correctamente")
    
    def setup_auto_cleanup(self):
        """Setup automatic log cleanup to prevent memory overflow."""
        self.cleanup_timer = QTimer()
        self.cleanup_timer.timeout.connect(self.auto_cleanup_logs)
        self.cleanup_timer.start(300000)  # Clean every 5 minutes
    
    @Slot(str)
    def log_message(self, message: str):
        """
        Add a message to the log area with timestamp.
        
        Args:
            message (str): The message to log
        """
        try:
            timestamp = datetime.now().strftime("%H:%M:%S")
            formatted_message = f"[{timestamp}] {message}"
            
            # Add to text area
            self.output_text.append(formatted_message)
            
            # Update counter
            self.log_entries_count += 1
            
            # Auto-scroll to bottom
            cursor = self.output_text.textCursor()
            cursor.movePosition(cursor.MoveOperation.End)
            self.output_text.setTextCursor(cursor)
            
            # Update status
            self.update_status(f"📝 {self.log_entries_count} entradas")
            
            # Auto cleanup if needed
            if self.log_entries_count > self.max_log_entries:
                self.auto_cleanup_logs()
                
        except Exception as e:
            print(f"Error in log_message: {e}")
    
    @Slot()
    def clear_logs(self):
        """Clear all log entries from the display."""
        try:
            self.output_text.clear()
            self.log_entries_count = 0
            self.update_status("🗑️ Logs limpiados")
            
            # Emit signal
            self.log_cleared.emit()
            
            # Add confirmation message
            self.log_message("🗑️ Logs limpiados por usuario")
            
        except Exception as e:
            self.log_message(f"❌ Error limpiando logs: {e}")
    
    @Slot()
    def export_logs(self):
        """Export current logs to a text file."""
        try:
            # Create logs directory if it doesn't exist
            logs_dir = "logs"
            if not os.path.exists(logs_dir):
                os.makedirs(logs_dir)
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"dataconta_logs_{timestamp}.txt"
            filepath = os.path.join(logs_dir, filename)
            
            # Get all log content
            log_content = self.output_text.toPlainText()
            
            # Write to file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"DataConta - Log Export\n")
                f.write(f"Exported: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Total Entries: {self.log_entries_count}\n")
                f.write("=" * 50 + "\n\n")
                f.write(log_content)
            
            # Update status and log
            self.update_status(f"💾 Exportado: {filename}")
            self.log_message(f"💾 Logs exportados a: {filepath}")
            
            # Emit signal with file path
            self.log_exported.emit(filepath)
            
        except Exception as e:
            self.log_message(f"❌ Error exportando logs: {e}")
    
    def auto_cleanup_logs(self):
        """Automatically clean old log entries to prevent memory overflow."""
        if self.log_entries_count > self.max_log_entries:
            try:
                # Keep only the last 500 entries
                all_text = self.output_text.toPlainText()
                lines = all_text.split('\n')
                
                if len(lines) > 500:
                    # Keep last 500 lines
                    cleaned_lines = lines[-500:]
                    cleaned_text = '\n'.join(cleaned_lines)
                    
                    self.output_text.clear()
                    self.output_text.setPlainText(cleaned_text)
                    
                    self.log_entries_count = 500
                    self.log_message("🔄 Auto-limpieza realizada (últimas 500 entradas)")
                    
            except Exception as e:
                print(f"Error in auto_cleanup_logs: {e}")
    
    def update_status(self, status_text: str):
        """
        Update the status label.
        
        Args:
            status_text (str): New status text
        """
        try:
            self.status_label.setText(status_text)
        except Exception as e:
            print(f"Error updating status: {e}")
    
    def get_log_count(self) -> int:
        """
        Get the current number of log entries.
        
        Returns:
            int: Number of log entries
        """
        return self.log_entries_count
    
    def set_max_entries(self, max_entries: int):
        """
        Set the maximum number of log entries before auto-cleanup.
        
        Args:
            max_entries (int): Maximum entries to keep
        """
        if max_entries > 0:
            self.max_log_entries = max_entries
            self.log_message(f"🔧 Límite de entradas establecido: {max_entries}")