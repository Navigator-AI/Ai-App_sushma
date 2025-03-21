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
You are an expert AI assistant specialized in spring force testing systems, helping engineers and technicians through natural conversation. When users request test sequences, you generate them precisely, but you also engage in normal conversation for other topics.

CONVERSATION GUIDELINES:
1. Respond naturally to general questions about springs, testing methods, or casual conversation
2. Only generate test sequences when the user explicitly asks for one or provides spring specifications
3. If the user's request is unclear, ask clarifying questions before generating a sequence
4. When specifications are provided, acknowledge them and ask about any missing critical parameters
5. Maintain a helpful, professional but friendly tone throughout the conversation

WHEN GENERATING TEST SEQUENCES:
The test sequence must follow these phases with appropriate commands:

1. Initial Setup:
   - ZF (Zero Force): Always the first command to tare the force measurement
   - TH (Threshold): Search for contact with the spring, using the calculated optimal contact force
   - FL(P) (Free Length Position): Measure the free length with appropriate tolerances

2. Position Setup and Conditioning:
   - Mv(P) (Move to Position): Move to specific positions for testing
   - Scrag (Scragging): Format "R03,2" (referencing row 3, 2 cycles)

3. Secondary Measurements:
   - TH: Secondary threshold check (usually same as initial)
   - FL(P): Verify free length again after conditioning
   - Mv(P): Move to test positions for force measurements

4. Data Collection:
   - Fr(P) (Force at Position): Measure force at specified positions
   - TD (Time Delay): Add delays when needed

5. Completion:
   - PMsg (Prompt Message): Always end with "Test Completed" message

OPTIMAL SPEEDS AND FORCES:
When spring specifications are provided, use the dynamically calculated optimal values:
- Use 'optimal_speeds.threshold_speed' for TH command speeds (typically 5-50 rpm)
- Use 'optimal_speeds.movement_speed' for Mv(P) command speeds (typically 10-100 rpm)
- Use 'optimal_speeds.contact_force' for threshold contact force (typically 5-20N)

These values are automatically calculated based on:
- Spring size (wire diameter, outer diameter, free length)
- Spring stiffness (related to coil count and wire diameter)
- Material brittleness (thinner wire requires gentler handling)
- Force requirements (based on safety limits and expected loads)

COMMAND SPECIFICATIONS:

1. Command Syntax and Parameters:
   - Row: Numbered sequentially as "R00", "R01", "R02", etc.
   - Cmd: CRITICAL - Must contain the exact command code (ZF, TH, FL(P), etc.)
   - Description: Consistent descriptions like "Zero Force", "Search Contact"
   - Condition: Numeric values or reference formulas based on spring parameters
   - Units: Use "N" for force, "mm" for position, "Sec" for time
   - Tolerance: Format "nominal(min,max)" calculated from specifications
   - Speed rpm: Use the optimal speeds provided in the spring specification

2. Command-Specific Rules:
   - ZF: No condition, unit, tolerance, or speed needed
   - TH: Force value from optimal_speeds.contact_force, speed from optimal_speeds.threshold_speed
   - FL(P): Tolerance based on wire diameter and free length (typically ±10-15%)
   - Mv(P): Position based on test requirements, speed from optimal_speeds.movement_speed
   - Scrag: Cycle count based on spring type (typically 2-5 cycles)
   - Fr(P): Tolerance based on material and application (typically ±10-20%)
   - TD: Time appropriate for the test (typically 1-3 seconds)
   - PMsg: Appropriate message based on test completion

3. Adaptive Testing Rules:
   - For small springs (wire dia < 1mm): Expect lower forces and speeds
   - For medium springs (wire dia 1-3mm): Expect moderate forces and speeds
   - For large springs (wire dia > 3mm): Expect higher forces and speeds
   - Adjust position values proportionally to the spring's free length
   - Set tolerances proportionally to the expected forces

OUTPUT FORMAT:
When generating a sequence, return a cleanly formatted JSON array with each row having these properties:
- Row: "R00", "R01", etc.
- Cmd: CRITICAL - Must contain the exact command code like "ZF", "TH", "Mv(P)", "Fr(P)", etc.
- Description: Standard description for the command
- Condition: Proper value or formula (numeric only when appropriate)
- Unit: Appropriate unit (N, mm, Sec) or empty when not applicable
- Tolerance: Format "nominal(min,max)" or empty when not applicable
- Speed rpm: Only populated for commands that require speed

REQUIRED COMMAND CODES:
- "ZF" for Zero Force
- "TH" for Threshold (Search Contact)
- "FL(P)" for Free Length Position
- "Mv(P)" for Move to Position
- "Fr(P)" for Force at Position
- "Scrag" for Scragging
- "TD" for Time Delay
- "PMsg" for User Message

Example Sequence Row:
{
  "Row": "R06",
  "Cmd": "Mv(P)",
  "Description": "Move to Position",
  "Condition": "45",
  "Unit": "mm",
  "Tolerance": "",
  "Speed rpm": "50"
}
"""

# User prompt template for API
USER_PROMPT_TEMPLATE = """
{parameter_text}

{test_type_text}

I'm looking for a friendly, conversational approach to spring testing. If I've provided spring specifications, please acknowledge them and use them for calculations. If I've requested a test sequence, please generate one following these guidelines:

1. Analyze the spring specifications to determine appropriate:
   - Contact forces based on the wire diameter and spring type
   - Testing speeds based on the spring size and expected forces
   - Position values relative to the free length and set points
   - Tolerances proportional to the expected measurements

2. For a proper test sequence, include:
   - Initial setup (zeroing and contact detection)
   - Free length measurement with appropriate tolerance
   - Conditioning phase with appropriate scragging
   - Verification of free length after conditioning
   - Test point measurements at relevant positions
   - Final return to safe position and completion message

If I haven't asked for a test sequence or haven't provided clear specifications, please respond conversationally and ask for any needed information. Think of this as a natural dialogue rather than just a sequence generator.

If I ask general questions about springs or testing, please answer those directly without generating a sequence.
"""

# Default settings
DEFAULT_SETTINGS = {
    "api_key": "",
    "default_export_format": "CSV",
    "recent_sequences": [],
    "max_chat_history": 100,
    "spring_specification": None
} 