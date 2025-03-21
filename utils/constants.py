"""
Constants module for the Spring Test App.
Contains all application-wide constants and configuration.
"""

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

# API Configurations
API_ENDPOINT = "https://chat01.ai/v1/chat/completions"
DEFAULT_MODEL = "gpt-4o"
DEFAULT_TEMPERATURE = 0.1

# UI Constants
APP_TITLE = "Spring Test Sequence Generator"
APP_VERSION = "1.0.0"
APP_WINDOW_SIZE = (1200, 800)
SIDEBAR_WIDTH = 300
MAX_CHAT_HISTORY = 100
USER_ICON = "👤"
ASSISTANT_ICON = "🤖"

# File Export Options
FILE_FORMATS = {
    "CSV": ".csv",
    "JSON": ".json",
    "Excel": ".xlsx"
}

# Parameter Patterns for text extraction
PARAMETER_PATTERNS = {
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

# System prompt template for API
SYSTEM_PROMPT_TEMPLATE = """
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

# User prompt template for API
USER_PROMPT_TEMPLATE = """
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