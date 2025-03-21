import sys
import pandas as pd
import requests
import json
import re
import io
import time
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QLineEdit, QPushButton, QTextEdit, QTableView, 
                            QHeaderView, QFileDialog, QTabWidget, QSplitter, QMessageBox,
                            QGroupBox)
from PyQt5.QtCore import Qt, QAbstractTableModel, QModelIndex
from PyQt5.QtGui import QFont, QColor, QTextCursor

# Core commands for spring testing with detailed descriptions
COMMANDS = {
    "ZF": "Zero Force", 
    "ZD": "Zero Displacement", 
    "TH": "Threshold (Search Contact)",
    "LP": "Loop", 
    "Mv(P)": "Move to Position", 
    "Calc": "Formula Calculation",
    "TD": "Time Delay", 
    "PMsg": "User Message", 
    "Fr(P)": "Force at Position",
    "FL(P)": "Measure Free Length", 
    "Scrag": "Scragging", 
    "SR": "Spring Rate",
    "PkF": "Measure Peak Force", 
    "PkP": "Measure Peak Position", 
    "Po(F)": "Position at Force",
    "Po(PkF)": "Position at Peak Force", 
    "Mv(F)": "Move to Force", 
    "PUi": "User Input"
}

# Standard speed values for different command types
STANDARD_SPEEDS = {
    "ZF": "50",         # Zero Force - slow speed for accuracy
    "ZD": "50",         # Zero Displacement - slow speed for accuracy
    "TH": "50",         # Threshold - slow speed for precision
    "Mv(P)": "200",     # Move to Position - moderate to fast speed
    "TD": "",           # Time Delay - no speed needed
    "PMsg": "",         # User Message - no speed needed
    "Fr(P)": "100",     # Force at Position - moderate speed
    "FL(P)": "100",     # Free Length - moderate speed
    "Scrag": "300",     # Scragging - fast speed for cycling
    "SR": "100",        # Spring Rate - moderate speed
    "PkF": "100",       # Peak Force - moderate speed
    "PkP": "100",       # Peak Position - moderate speed
    "Po(F)": "100",     # Position at Force - moderate speed
    "Mv(F)": "200",     # Move to Force - moderate to fast speed
    "default": "100"    # Default moderate speed
}

class PandasModel(QAbstractTableModel):
    """Model for displaying pandas DataFrame in QTableView"""
    def __init__(self, data):
        super().__init__()
        self._data = data

    def rowCount(self, parent=None):
        return self._data.shape[0]

    def columnCount(self, parent=None):
        return self._data.shape[1]

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid():
            if role == Qt.DisplayRole:
                return str(self._data.iloc[index.row(), index.column()])
            if role == Qt.TextAlignmentRole:
                return Qt.AlignCenter
        return None

    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._data.columns[section]
        if orientation == Qt.Vertical and role == Qt.DisplayRole:
            return str(section + 1)
        return None

class CommandTableModel(QAbstractTableModel):
    """Model for displaying command reference"""
    def __init__(self, commands):
        super().__init__()
        self.commands = [(k, v) for k, v in commands.items()]
        self.headers = ["Command", "Description"]

    def rowCount(self, parent=None):
        return len(self.commands)

    def columnCount(self, parent=None):
        return len(self.headers)

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid():
            if role == Qt.DisplayRole:
                return self.commands[index.row()][index.column()]
            if role == Qt.TextAlignmentRole:
                return Qt.AlignCenter
        return None

    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.headers[section]
        return None

class ChatMessage:
    def __init__(self, role, content):
        self.role = role
        self.content = content

class SpringTestApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Spring Test Sequence Generator")
        self.setGeometry(100, 100, 1200, 800)
        
        # Initialize variables similar to session state
        self.chat_history = []
        self.current_sequence = None
        self.chat_memory = []
        self.last_raw_response = ""
        
        self.initUI()
        
    def initUI(self):
        # Main widget and layout
        main_widget = QWidget()
        main_layout = QHBoxLayout()
        
        # Create sidebar and main content splitter
        splitter = QSplitter(Qt.Horizontal)
        
        # Sidebar for API key and command reference
        sidebar = QWidget()
        sidebar_layout = QVBoxLayout()
        
        # API key input
        api_key_label = QLabel("Enter API Key:")
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.Password)
        
        # Command reference table
        cmd_label = QLabel("Command Reference")
        cmd_label.setFont(QFont("Arial", 12, QFont.Bold))
        
        self.cmd_table = QTableView()
        cmd_model = CommandTableModel(COMMANDS)
        self.cmd_table.setModel(cmd_model)
        self.cmd_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        # Clear chat button
        clear_chat_btn = QPushButton("Clear Chat")
        clear_chat_btn.clicked.connect(self.clear_chat)
        
        # Add widgets to sidebar
        sidebar_layout.addWidget(api_key_label)
        sidebar_layout.addWidget(self.api_key_input)
        sidebar_layout.addWidget(cmd_label)
        sidebar_layout.addWidget(self.cmd_table)
        sidebar_layout.addWidget(clear_chat_btn)
        sidebar_layout.addStretch()
        
        sidebar.setLayout(sidebar_layout)
        sidebar.setMaximumWidth(300)
        
        # Main content
        main_content = QWidget()
        content_layout = QHBoxLayout()
        
        # Left column - Chat interface
        chat_widget = QWidget()
        chat_layout = QVBoxLayout()
        
        chat_label = QLabel("Spring Test Chat Assistant")
        chat_label.setFont(QFont("Arial", 12, QFont.Bold))
        
        # Chat history display
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        
        # User input
        input_label = QLabel("Enter your request:")
        self.user_input = QTextEdit()
        self.user_input.setPlaceholderText("Example: Generate a test sequence for a compression spring with free length 50mm, wire diameter 2mm, and spring rate 5 N/mm.")
        self.user_input.setMaximumHeight(150)
        
        # Generate button
        generate_btn = QPushButton("Generate Sequence")
        generate_btn.clicked.connect(self.generate_sequence)
        
        # Add widgets to chat layout
        chat_layout.addWidget(chat_label)
        chat_layout.addWidget(self.chat_display)
        chat_layout.addWidget(input_label)
        chat_layout.addWidget(self.user_input)
        chat_layout.addWidget(generate_btn)
        
        chat_widget.setLayout(chat_layout)
        
        # Right column - Results
        results_widget = QWidget()
        results_layout = QVBoxLayout()
        
        results_label = QLabel("Generated Test Sequence")
        results_label.setFont(QFont("Arial", 12, QFont.Bold))
        
        # Results table
        self.results_table = QTableView()
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        # Download buttons
        download_label = QLabel("Download Options")
        download_label.setFont(QFont("Arial", 12, QFont.Bold))
        
        download_layout = QHBoxLayout()
        download_csv_btn = QPushButton("Download CSV")
        download_csv_btn.clicked.connect(self.download_csv)
        download_json_btn = QPushButton("Download JSON")
        download_json_btn.clicked.connect(self.download_json)
        
        download_layout.addWidget(download_csv_btn)
        download_layout.addWidget(download_json_btn)
        
        # Add widgets to results layout
        results_layout.addWidget(results_label)
        results_layout.addWidget(self.results_table)
        results_layout.addWidget(download_label)
        results_layout.addLayout(download_layout)
        
        results_widget.setLayout(results_layout)
        
        # Add left and right columns to content layout
        content_layout.addWidget(chat_widget)
        content_layout.addWidget(results_widget)
        
        main_content.setLayout(content_layout)
        
        # Add widgets to splitter
        splitter.addWidget(sidebar)
        splitter.addWidget(main_content)
        splitter.setSizes([300, 900])  # Default sizes
        
        # Add splitter to main layout
        main_layout.addWidget(splitter)
        
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
    
    def clear_chat(self):
        """Clear chat history and current sequence"""
        self.chat_history = []
        self.current_sequence = None
        self.chat_display.clear()
        self.results_table.setModel(None)
    
    def add_chat_message(self, role, content):
        """Add a message to the chat history"""
        self.chat_history.append(ChatMessage(role, content))
        self.update_chat_display()
    
    def update_chat_display(self):
        """Update the chat display with current history"""
        self.chat_display.clear()
        
        for message in self.chat_history:
            if message.role == "user":
                self.chat_display.append("<b>You:</b>")
                self.chat_display.append(message.content)
                self.chat_display.append("")
            else:
                self.chat_display.append("<b>Assistant:</b>")
                self.chat_display.append(message.content)
                self.chat_display.append("")
                
        # Scroll to bottom - fixed
        cursor = self.chat_display.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.chat_display.setTextCursor(cursor)
    
    def generate_sequence(self):
        """Generate test sequence based on user input"""
        user_input = self.user_input.toPlainText()
        api_key = self.api_key_input.text()
        
        if not api_key:
            QMessageBox.warning(self, "Missing API Key", "Please enter an API key.")
            return
        
        if not user_input:
            QMessageBox.warning(self, "Missing Input", "Please enter your request.")
            return
        
        # Add user message to chat history
        self.add_chat_message("user", user_input)
        
        # Extract parameters from natural language input
        parameters = self.extract_parameters(user_input)
        
        try:
            # Show loading message
            QApplication.setOverrideCursor(Qt.WaitCursor)
            
            # Generate test sequence
            df = self.call_api(parameters, api_key)
            
            QApplication.restoreOverrideCursor()
            
            if not df.empty:
                self.current_sequence = df
                # Display the sequence in the table
                model = PandasModel(df)
                self.results_table.setModel(model)
                self.results_table.resizeColumnsToContents()
                response = "I've generated a test sequence based on your specifications. You can see the results in the right panel."
            else:
                response = "I couldn't generate a valid test sequence. Please provide more specific spring details."
            
            self.add_chat_message("assistant", response)
            
        except Exception as e:
            QApplication.restoreOverrideCursor()
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")
    
    def call_api(self, parameters, api_key):
        """Call the API to generate test sequence"""
        url = "https://chat01.ai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        # Enhanced system prompt with more precise industry specifications
        system_prompt = """
        You are an expert AI in spring force testing systems. Generate test sequences exactly matching this format:

        COMMAND SEQUENCE:
        1. Initial Setup:
           - ZF: Tare force (no condition needed)
           - TH: Threshold at 5N exactly
           - FL(P): Free length measurement with tolerance (e.g., 120(119,121))
           
        2. Position Setup:
           - Mv(P): Move to calculated position =(FreeLength-24.3)
           - Mv(P): Home position (absolute value)
           
        3. Conditioning:
           - Scrag: Format "R03,2" for 2 cycles
           - TH: Search contact at 5N
           - FL(P): Verify free length
           
        4. Test Points:
           - Mv(P): L1 position =(R07-14.3)
           - Fr(P): F1 measurement with tolerance
           - TD: 3 second delay
           - Mv(P): L2 position =(R07-24.3)

        EXACT FORMAT RULES:
        1. Conditions:
           - TH: Always use 5N
           - Mv(P): Use formulas like =(R02-24.3)
           - Scrag: Use format R03,2
           - TD: Use exact seconds (3)
           
        2. Units:
           - Force: N
           - Position: mm
           - Time: Sec
           
        3. Tolerances:
           - Length: nominal(min,max) e.g., 120(119,121)
           - Force: nominal(min,max) e.g., 2799(2659,2939)
           
        4. Speeds:
           - TH: 50 rpm
           - FL(P): 100 rpm
           - Mv(P): 200 rpm for home, 100 rpm for test
           - Fr(P): 100 rpm

        OUTPUT FORMAT:
        Return JSON array with:
        - Row: "R00", "R01", etc.
        - CMD: Exact command from list
        - Description: Match example descriptions
        - Condition: Exact formula or value
        - Unit: N, mm, or Sec only
        - Tolerance: nominal(min,max) format
        - Speed rpm: Match example speeds
        """

        # Format parameter text for prompt
        parameter_text = "\n".join([f"{k}: {v}" for k, v in parameters.items()])
        
        # Include previous context if available
        context = ""
        if self.chat_memory:
            context = "\n\nPrevious context:\n" + "\n".join(self.chat_memory[-3:])
        
        # Enhanced user prompt with simpler, command-focused requirements
        user_prompt = f"""
        Generate a spring test sequence using these commands in order:
        1. Setup: ZF, ZD, TH
        2. Initial Check: FL(P)
        3. Conditioning: Scrag, TD (2 seconds)
        4. Main Test: Mv(P), Fr(P), SR
        5. Final Check: FL(P), PMsg

        Spring Parameters:
        {parameter_text}

        Rules:
        - Start with zeroing (ZF, ZD)
        - Use TH at 10N for contact
        - Include 3 Scrag cycles
        - Use proper speeds:
          * 50 rpm for zeroing
          * 100 rpm for measurements
          * 200 rpm for movement
          * 300 rpm for scragging
        - Add 2-second TD after movements
        - End with final length check

        Return a JSON array with Row, CMD, Description, Condition, Unit, Tolerance, and Speed rpm.
        """

        payload = {
            "model": "gpt-4o",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.1  # Lower temperature for more consistent output
        }

        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            response_json = response.json()
            
            message = response_json['choices'][0].get('message', {})
            raw_content = message.get('content', '')
            
            # Save context for continuity
            self.chat_memory.append(parameter_text)
            if len(self.chat_memory) > 10:  # Keep memory limited
                self.chat_memory = self.chat_memory[-10:]
            
            # Extract JSON from the response, handling potential code blocks
            json_match = re.search(r'```json\n(.*?)\n```|(\[.*\])', raw_content, re.DOTALL)
            if json_match:
                json_content = json_match.group(1) or json_match.group(2)
            else:
                json_content = raw_content
                
            # Clean up any remaining markdown or text
            json_content = re.sub(r'^```.*|```$', '', json_content, flags=re.MULTILINE).strip()
            
            # Save raw response for debugging
            self.last_raw_response = raw_content
            
            # Handle JSON parsing errors safely
            try:
                data = json.loads(json_content)
            except json.JSONDecodeError:
                # If JSON parsing fails, try to extract just the array part
                array_match = re.search(r'\[(.*)\]', json_content, re.DOTALL)
                if array_match:
                    cleaned_json = '[' + array_match.group(1) + ']'
                    data = json.loads(cleaned_json)
                else:
                    QMessageBox.warning(self, "API Response Error", "Could not parse API response as JSON.")
                    return pd.DataFrame()
            
            # Ensure all required columns are present
            required_columns = ["Row", "CMD", "Description", "Condition", "Unit", "Tolerance", "Speed rpm"]
            df = pd.DataFrame(data)
            
            # Rename any mismatched columns
            if "Speed" in df.columns and "Speed rpm" not in df.columns:
                df = df.rename(columns={"Speed": "Speed rpm"})
                
            # Add any missing columns
            for col in required_columns:
                if col not in df.columns:
                    df[col] = ""
                    
            # Reorder columns to match required format
            for col in required_columns:
                if col not in df.columns:
                    # If a required column is completely missing, add it
                    df[col] = ""
            
            # Ensure we only have the columns we want in the right order
            df = df[required_columns]
                
            return df
        except Exception as e:
            QMessageBox.critical(self, "API Error", f"API Error: {str(e)}")
            return pd.DataFrame()
    
    def extract_parameters(self, text):
        """Extract spring parameters from natural language text with improved pattern matching"""
        parameters = {}
        
        # Enhanced parameter extraction patterns
        patterns = {
            "Free Length": r'free\s*length\s*(?:[=:]|is|of)?\s*(\d+\.?\d*)\s*(?:mm)?',
            "Part Number": r'part\s*(?:number|#|no\.?)?\s*(?:[=:]|is)?\s*([A-Za-z0-9-_]+)',
            "Model Number": r'model\s*(?:number|#|no\.?)?\s*(?:[=:]|is)?\s*([A-Za-z0-9-_]+)',
            "Wire Diameter": r'wire\s*(?:diameter|thickness)?\s*(?:[=:]|is)?\s*(\d+\.?\d*)\s*(?:mm)?',
            "Outer Diameter": r'(?:outer|outside)\s*diameter\s*(?:[=:]|is)?\s*(\d+\.?\d*)\s*(?:mm)?',
            "Inner Diameter": r'(?:inner|inside)\s*diameter\s*(?:[=:]|is)?\s*(\d+\.?\d*)\s*(?:mm)?',
            "Spring Rate": r'(?:spring|target)\s*rate\s*(?:[=:]|is)?\s*(\d+\.?\d*)',
            "Test Load": r'(?:test|target)\s*load\s*(?:[=:]|is)?\s*(\d+\.?\d*)',
            "Deflection": r'deflection\s*(?:[=:]|is)?\s*(\d+\.?\d*)',
            "Working Length": r'working\s*length\s*(?:[=:]|is)?\s*(\d+\.?\d*)',
            "Customer ID": r'customer\s*(?:id|number)?\s*(?:[=:]|is)?\s*([A-Za-z0-9\s]+)',
        }
        
        # Extract test type
        if re.search(r'\b(?:compress|compression)\b', text, re.IGNORECASE):
            parameters["Test Type"] = "Compression"
        elif re.search(r'\b(?:tens|tension|extension|extend)\b', text, re.IGNORECASE):
            parameters["Test Type"] = "Tension"
        else:
            # Default to compression if not specified
            parameters["Test Type"] = "Compression"
        
        # Extract parameters based on patterns
        for param, pattern in patterns.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                value = match.group(1).strip()
                # Convert to float if it's a numeric value
                if param not in ["Part Number", "Model Number", "Customer ID"]:
                    try:
                        parameters[param] = float(value)
                    except ValueError:
                        parameters[param] = value
                else:
                    parameters[param] = value
        
        # Add timestamp to parameters
        parameters["Timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        return parameters
    
    def download_csv(self):
        """Download the current sequence as CSV"""
        if self.current_sequence is None:
            QMessageBox.warning(self, "No Data", "No test sequence available to download.")
            return
        
        fileName, _ = QFileDialog.getSaveFileName(self, "Save CSV", "", "CSV Files (*.csv)")
        if fileName:
            if not fileName.endswith('.csv'):
                fileName += '.csv'
            try:
                self.current_sequence.to_csv(fileName, index=False)
                QMessageBox.information(self, "Success", f"Saved to {fileName}")
            except Exception as e:
                QMessageBox.critical(self, "Save Error", f"Error saving file: {str(e)}")
    
    def download_json(self):
        """Download the current sequence as JSON"""
        if self.current_sequence is None:
            QMessageBox.warning(self, "No Data", "No test sequence available to download.")
            return
        
        fileName, _ = QFileDialog.getSaveFileName(self, "Save JSON", "", "JSON Files (*.json)")
        if fileName:
            if not fileName.endswith('.json'):
                fileName += '.json'
            try:
                self.current_sequence.to_json(fileName, orient="records", indent=2)
                QMessageBox.information(self, "Success", f"Saved to {fileName}")
            except Exception as e:
                QMessageBox.critical(self, "Save Error", f"Error saving file: {str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SpringTestApp()
    window.show()
    sys.exit(app.exec_())