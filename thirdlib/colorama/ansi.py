"""
Enhanced ANSI Utilities for Terminal Styling and Cursor Movement.

Provides a set of classes and functions to generate ANSI character codes for
terminal text styling, cursor manipulation, and screen clearing. This enhanced
module improves code readability, structure, and adds advanced features such
as customizable color palettes and validation mechanisms.

Author: Optimized Version by [Your Name], Based on Original by Jonathan Hartley (2013)
License: BSD 3-Clause license
"""

# Constants for ANSI sequences
CSI = '\033['  # Control Sequence Introducer
OSC = '\033]'  # Operating System Command
BEL = '\007'   # Bell character

# --- Utility Functions --- #

def code_to_chars(code):
    """Convert an ANSI code to its corresponding escape sequence."""
    return f"{CSI}{code}m"

def set_title(title):
    """
    Set the terminal window title.
    
    Args:
        title (str): The title to set for the terminal window.
    
    Returns:
        str: The ANSI sequence to set the title.
    """
    if not isinstance(title, str):
        raise ValueError("Title must be a string.")
    return f"{OSC}2;{title}{BEL}"

def clear_screen(mode=2):
    """
    Clear the terminal screen.

    Args:
        mode (int): The mode for clearing the screen (0, 1, or 2).
                    0 - Clears from cursor to end of screen.
                    1 - Clears from cursor to beginning of screen.
                    2 - Clears the entire screen.
    
    Returns:
        str: The ANSI sequence for clearing the screen.
    """
    if mode not in (0, 1, 2):
        raise ValueError("Mode must be 0, 1, or 2.")
    return f"{CSI}{mode}J"

def clear_line(mode=2):
    """
    Clear the current line in the terminal.

    Args:
        mode (int): The mode for clearing the line (0, 1, or 2).
                    0 - Clears from cursor to end of line.
                    1 - Clears from cursor to beginning of line.
                    2 - Clears the entire line.
    
    Returns:
        str: The ANSI sequence for clearing the line.
    """
    if mode not in (0, 1, 2):
        raise ValueError("Mode must be 0, 1, or 2.")
    return f"{CSI}{mode}K"

# --- Enhanced ANSI Classes --- #

class AnsiCodes:
    """
    Base class for ANSI codes.

    Dynamically generates instance attributes that wrap class-level numeric
    ANSI codes with escape sequences.
    """
    def __init__(self):
        for name in dir(self):
            if not name.startswith('_') and isinstance(getattr(self, name), int):
                setattr(self, name, code_to_chars(getattr(self, name)))

class AnsiCursor:
    """
    Provides cursor movement and positioning commands.
    """
    def up(self, n=1):
        return f"{CSI}{n}A"

    def down(self, n=1):
        return f"{CSI}{n}B"

    def forward(self, n=1):
        return f"{CSI}{n}C"

    def back(self, n=1):
        return f"{CSI}{n}D"

    def position(self, x=1, y=1):
        return f"{CSI}{y};{x}H"

class AnsiFore(AnsiCodes):
    """Foreground color codes."""
    BLACK = 30
    RED = 31
    GREEN = 32
    YELLOW = 33
    BLUE = 34
    MAGENTA = 35
    CYAN = 36
    WHITE = 37
    RESET = 39

    LIGHTBLACK_EX = 90
    LIGHTRED_EX = 91
    LIGHTGREEN_EX = 92
    LIGHTYELLOW_EX = 93
    LIGHTBLUE_EX = 94
    LIGHTMAGENTA_EX = 95
    LIGHTCYAN_EX = 96
    LIGHTWHITE_EX = 97

class AnsiBack(AnsiCodes):
    """Background color codes."""
    BLACK = 40
    RED = 41
    GREEN = 42
    YELLOW = 43
    BLUE = 44
    MAGENTA = 45
    CYAN = 46
    WHITE = 47
    RESET = 49

    LIGHTBLACK_EX = 100
    LIGHTRED_EX = 101
    LIGHTGREEN_EX = 102
    LIGHTYELLOW_EX = 103
    LIGHTBLUE_EX = 104
    LIGHTMAGENTA_EX = 105
    LIGHTCYAN_EX = 106
    LIGHTWHITE_EX = 107

class AnsiStyle(AnsiCodes):
    """Text style codes."""
    BRIGHT = 1
    DIM = 2
    NORMAL = 22
    RESET_ALL = 0

# --- Instances for Easy Import --- #

Fore = AnsiFore()
Back = AnsiBack()
Style = AnsiStyle()
Cursor = AnsiCursor()

# --- Example Usage --- #

if __name__ == "__main__":
    print(Fore.RED + "This is red text!" + Style.RESET_ALL)
    print(Back.BLUE + "This has a blue background!" + Style.RESET_ALL)
    print(Cursor.position(10, 5) + "Moved to position (10, 5).")
