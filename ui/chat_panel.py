"""
Chat panel module for the Spring Test App.
Contains the chat interface components.
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, 
                           QPushButton, QMessageBox, QProgressBar, QSplitter, QFrame,
                           QSizePolicy)
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot, QTimer, QSize
from PyQt5.QtGui import QFont, QTextCursor, QIcon, QMovie

from utils.text_parser import extract_parameters
from models.data_models import TestSequence, ChatMessage
from utils.constants import USER_ICON, ASSISTANT_ICON


class ChatPanel(QWidget):
    """Chat panel widget for the Spring Test App."""
    
    # Define signals
    sequence_generated = pyqtSignal(object)  # TestSequence object
    
    def __init__(self, chat_service, sequence_generator):
        """Initialize the chat panel.
        
        Args:
            chat_service: Chat service.
            sequence_generator: Sequence generator service.
        """
        super().__init__()
        
        # Store services
        self.chat_service = chat_service
        self.sequence_generator = sequence_generator
        
        # State variables
        self.is_generating = False
        
        # Set up the UI
        self.init_ui()
        
        # Connect signals
        self.connect_signals()
        
        # Load chat history
        self.refresh_chat_display()
    
    def init_ui(self):
        """Initialize the UI."""
        # Main layout
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Chat panel title
        title_label = QLabel("Spring Test Chat Assistant")
        title_label.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(title_label)
        
        # Chat display
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setMinimumHeight(300)
        layout.addWidget(self.chat_display, 1)  # Give it stretch factor 1
        
        # Progress section frame - wrap in a fixed-height frame
        progress_frame = QFrame()
        progress_frame.setFrameShape(QFrame.StyledPanel)
        progress_frame.setFixedHeight(50)  # Set a fixed height
        progress_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        progress_layout = QHBoxLayout(progress_frame)
        progress_layout.setContentsMargins(5, 5, 5, 5)
        progress_layout.setSpacing(5)
        
        # Progress bar 
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("%p% - %v")
        progress_layout.addWidget(self.progress_bar, 1)
        
        # Loading animation
        self.loading_label = QLabel()
        self.loading_movie = QMovie("resources/loading.gif")
        self.loading_movie.setScaledSize(QSize(24, 24))
        self.loading_label.setMovie(self.loading_movie)
        self.loading_label.setFixedSize(24, 24)
        progress_layout.addWidget(self.loading_label)
        
        # Status label
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: gray; font-style: italic;")
        self.status_label.setMinimumWidth(100)
        progress_layout.addWidget(self.status_label, 2)
        
        # Cancel button
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.on_cancel_clicked)
        self.cancel_btn.setFixedWidth(80)
        progress_layout.addWidget(self.cancel_btn)
        
        # Initially hide progress components but keep the frame
        self.progress_bar.hide()
        self.loading_label.hide()
        self.cancel_btn.hide()
        
        # Add progress frame to main layout
        layout.addWidget(progress_frame, 0)  # No stretch factor
        
        # Input area
        input_label = QLabel("Enter your request:")
        layout.addWidget(input_label, 0)  # No stretch factor
        
        self.user_input = QTextEdit()
        self.user_input.setPlaceholderText("Example: Generate a test sequence for a compression spring with free length 50mm, wire diameter 2mm, and spring rate 5 N/mm.")
        self.user_input.setMinimumHeight(100)
        self.user_input.setMaximumHeight(150)
        layout.addWidget(self.user_input, 0)  # No stretch factor
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        self.generate_btn = QPushButton("Generate Sequence")
        self.generate_btn.clicked.connect(self.on_generate_clicked)
        self.generate_btn.setMinimumHeight(30)
        button_layout.addWidget(self.generate_btn)
        
        self.clear_input_btn = QPushButton("Clear Input")
        self.clear_input_btn.clicked.connect(self.on_clear_input_clicked)
        self.clear_input_btn.setMinimumHeight(30)
        button_layout.addWidget(self.clear_input_btn)
        
        layout.addLayout(button_layout, 0)  # No stretch factor
        
        # Set the layout
        self.setLayout(layout)
    
    def connect_signals(self):
        """Connect signals from the sequence generator."""
        self.sequence_generator.sequence_generated.connect(self.on_sequence_generated_async)
        self.sequence_generator.progress_updated.connect(self.on_progress_updated)
        self.sequence_generator.status_updated.connect(self.on_status_updated)
    
    def refresh_chat_display(self):
        """Refresh the chat display with current history."""
        self.chat_display.clear()
        
        # Get chat history
        history = self.chat_service.get_history()
        
        # Display each message
        for message in history:
            if message.role == "user":
                self.chat_display.append(f"<b>{USER_ICON} You:</b>")
                self.chat_display.append(message.content)
                self.chat_display.append("")
            else:
                self.chat_display.append(f"<b>{ASSISTANT_ICON} Assistant:</b>")
                self.chat_display.append(message.content)
                self.chat_display.append("")
        
        # Scroll to bottom
        cursor = self.chat_display.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.chat_display.setTextCursor(cursor)
    
    def on_generate_clicked(self):
        """Handle generate button clicks."""
        # Get user input
        user_input = self.user_input.toPlainText()
        
        # Check if input is empty
        if not user_input:
            QMessageBox.warning(self, "Missing Input", "Please enter your request.")
            return
        
        # Check if generation is already in progress
        if self.is_generating:
            QMessageBox.warning(self, "Generation in Progress", "Please wait for the current generation to complete.")
            return
        
        # Add user message to chat history
        self.chat_service.add_message("user", user_input)
        
        # Refresh chat display
        self.refresh_chat_display()
        
        # Extract parameters from user input
        parameters = extract_parameters(user_input)
        
        # Start generation
        self.start_generation(parameters)
    
    def on_cancel_clicked(self):
        """Handle cancel button clicks."""
        if self.is_generating:
            # Cancel the operation
            self.sequence_generator.cancel_current_operation()
            
            # Update UI
            self.on_status_updated("Operation cancelled")
            self.on_progress_updated(0)
            
            # Add cancellation message to chat
            self.chat_service.add_message(
                "assistant", 
                "I've cancelled the sequence generation as requested."
            )
            self.refresh_chat_display()
            
            # Reset generating state
            self.set_generating_state(False)
    
    def on_clear_input_clicked(self):
        """Handle clear input button clicks."""
        self.user_input.clear()
    
    def start_generation(self, parameters):
        """Start sequence generation.
        
        Args:
            parameters: Dictionary of spring parameters.
        """
        # Set generating state
        self.set_generating_state(True)
        
        # Reset progress and status
        self.progress_bar.setValue(0)
        self.status_label.setText("Starting generation...")
        
        # Start async generation
        self.sequence_generator.generate_sequence_async(parameters)
    
    def set_generating_state(self, is_generating):
        """Set the generating state and update UI accordingly.
        
        Args:
            is_generating: Whether generation is in progress.
        """
        self.is_generating = is_generating
        
        # Update UI based on state
        self.generate_btn.setEnabled(not is_generating)
        self.user_input.setReadOnly(is_generating)
        
        if is_generating:
            # Show progress indicators
            self.progress_bar.show()
            self.loading_label.show()
            self.loading_movie.start()
            self.cancel_btn.show()
        else:
            # Hide progress indicators
            self.progress_bar.hide()
            self.loading_label.hide()
            self.loading_movie.stop()
            self.cancel_btn.hide()
            self.status_label.setText("Ready")
    
    def on_sequence_generated_async(self, sequence, error_msg):
        """Handle sequence generation completion from async operation.
        
        Args:
            sequence: Generated sequence or None if failed.
            error_msg: Error message if generation failed.
        """
        # Reset generating state
        self.set_generating_state(False)
        
        # Check for errors
        if not sequence:
            # Add error message to chat history
            self.chat_service.add_message("assistant", f"I couldn't generate a valid test sequence: {error_msg}")
            self.refresh_chat_display()
            return
        
        # Add success message to chat history
        self.chat_service.add_message(
            "assistant", 
            "I've generated a test sequence based on your specifications. "
            "You can see the results in the right panel."
        )
        
        # Refresh chat display
        self.refresh_chat_display()
        
        # Emit signal to show sequence in results panel
        self.sequence_generated.emit(sequence)
    
    def on_progress_updated(self, progress):
        """Handle progress updates.
        
        Args:
            progress: Progress percentage (0-100).
        """
        self.progress_bar.setValue(progress)
    
    def on_status_updated(self, status):
        """Handle status updates.
        
        Args:
            status: Status message.
        """
        self.status_label.setText(status)
    
    def validate_api_key(self):
        """Validate the API key."""
        # Get the API key from the sequence generator
        api_key = self.sequence_generator.api_client.api_key
        
        # Check if API key is empty
        if not api_key:
            # Add message to chat history
            self.chat_service.add_message(
                "assistant", 
                "Please enter an API key in the sidebar to use the chat."
            )
            self.refresh_chat_display()
            return
        
        # Set generating state
        self.set_generating_state(True)
        self.status_label.setText("Validating API key...")
        
        # Use a timer to validate in the background
        QTimer.singleShot(100, self._validate_api_key_async)
    
    def _validate_api_key_async(self):
        """Perform API key validation in the background."""
        try:
            # Validate the API key
            valid, message = self.sequence_generator.api_client.validate_api_key()
            
            if not valid:
                # Add error message to chat history
                self.chat_service.add_message(
                    "assistant", 
                    f"API key validation failed: {message}"
                )
                self.refresh_chat_display()
            else:
                # Add success message to chat history
                self.chat_service.add_message(
                    "assistant", 
                    "API key is valid. You can now generate sequences."
                )
                self.refresh_chat_display()
        finally:
            # Reset generating state
            self.set_generating_state(False) 