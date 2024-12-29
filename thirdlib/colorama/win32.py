# Copyright Jonathan Hartley 2013. BSD 3-Clause license, see LICENSE file.

"""
Enhanced Win32 Console Utilities for managing text attributes, cursor positions, and console titles.
Provides extended functionality for advanced console interactions with improved performance and maintainability.
"""

import os
import logging

# Define Standard Output and Error constants
STDOUT = -11
STDERR = -12

# Attempt to import necessary ctypes libraries for Windows API calls
try:
    import ctypes
    from ctypes import wintypes, byref, Structure, POINTER, c_char
    windll = ctypes.LibraryLoader(ctypes.WinDLL)
except ImportError:
    windll = None
    def SetConsoleTextAttribute(*args): pass
    def SetConsoleCursorPosition(*args): pass
    def winapi_test(*args): return False
else:
    # Define COORD structure
    class COORD(ctypes.Structure):
        _fields_ = [("X", wintypes.SHORT), ("Y", wintypes.SHORT)]

    # Define CONSOLE_SCREEN_BUFFER_INFO structure
    class CONSOLE_SCREEN_BUFFER_INFO(Structure):
        _fields_ = [
            ("dwSize", COORD),
            ("dwCursorPosition", COORD),
            ("wAttributes", wintypes.WORD),
            ("srWindow", wintypes.SMALL_RECT),
            ("dwMaximumWindowSize", COORD),
        ]

    # Get standard handle for console
    _GetStdHandle = windll.kernel32.GetStdHandle
    _GetStdHandle.argtypes = [wintypes.DWORD]
    _GetStdHandle.restype = wintypes.HANDLE

    # Get console screen buffer info
    _GetConsoleScreenBufferInfo = windll.kernel32.GetConsoleScreenBufferInfo
    _GetConsoleScreenBufferInfo.argtypes = [wintypes.HANDLE, POINTER(CONSOLE_SCREEN_BUFFER_INFO)]
    _GetConsoleScreenBufferInfo.restype = wintypes.BOOL

    # Set console text attributes
    _SetConsoleTextAttribute = windll.kernel32.SetConsoleTextAttribute
    _SetConsoleTextAttribute.argtypes = [wintypes.HANDLE, wintypes.WORD]
    _SetConsoleTextAttribute.restype = wintypes.BOOL

    # Set console cursor position
    _SetConsoleCursorPosition = windll.kernel32.SetConsoleCursorPosition
    _SetConsoleCursorPosition.argtypes = [wintypes.HANDLE, COORD]
    _SetConsoleCursorPosition.restype = wintypes.BOOL

    # Set console title
    _SetConsoleTitleW = windll.kernel32.SetConsoleTitleW
    _SetConsoleTitleW.argtypes = [wintypes.LPCWSTR]
    _SetConsoleTitleW.restype = wintypes.BOOL

    def winapi_test():
        """Check if WinAPI calls are supported on this console."""
        handle = _GetStdHandle(STDOUT)
        csbi = CONSOLE_SCREEN_BUFFER_INFO()
        success = _GetConsoleScreenBufferInfo(handle, byref(csbi))
        return bool(success)

    def SetConsoleTextAttribute(handle, attributes):
        """Set text attributes such as color and style."""
        if not _SetConsoleTextAttribute(handle, attributes):
            raise RuntimeError("Failed to set text attributes.")

    def SetConsoleCursorPosition(handle, position):
        """Set the cursor position in the console."""
        coord = COORD(position[0], position[1])
        if not _SetConsoleCursorPosition(handle, coord):
            raise RuntimeError("Failed to set cursor position.")

    def SetConsoleTitle(title):
        """Set the console title."""
        if not _SetConsoleTitleW(title):
            raise RuntimeError("Failed to set console title.")

    def GetConsoleScreenBufferInfo():
        """Retrieve information about the console screen buffer."""
        handle = _GetStdHandle(STDOUT)
        csbi = CONSOLE_SCREEN_BUFFER_INFO()
        if not _GetConsoleScreenBufferInfo(handle, byref(csbi)):
            raise RuntimeError("Failed to get console screen buffer info.")
        return csbi

    def ClearConsole():
        """Clear the console screen."""
        csbi = GetConsoleScreenBufferInfo()
        console_size = csbi.dwSize.X * csbi.dwSize.Y
        handle = _GetStdHandle(STDOUT)
        coord_screen = COORD(0, 0)
        chars_written = wintypes.DWORD(0)
        windll.kernel32.FillConsoleOutputCharacterA(
            handle, c_char(b' '), console_size, coord_screen, byref(chars_written)
        )
        windll.kernel32.FillConsoleOutputAttribute(
            handle, csbi.wAttributes, console_size, coord_screen, byref(chars_written)
        )
        SetConsoleCursorPosition(handle, (0, 0))

# Logging setup for debugging and error tracking
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(message)s")

def log_action(action):
    """Log a console action for debugging purposes."""
    logging.debug(f"Action: {action}")

# Enhanced functionality: progress bars
def show_progress_bar(completed, total, length=50):
    """Display a progress bar in the console."""
    percent = int((completed / total) * 100)
    bar_length = int((completed / total) * length)
    bar = f"[{'#' * bar_length}{'.' * (length - bar_length)}] {percent}%"
    print(bar, end="\r")

# Enhanced functionality: loading spinner
import itertools
import time

def loading_spinner(message="Loading"):
    """Display a loading spinner in the console."""
    spinner = itertools.cycle(["|", "/", "-", "\\"])
    for _ in range(20):  # Simulate 20 iterations of loading
        sys.stdout.write(f"\r{message} {next(spinner)}")
        sys.stdout.flush()
        time.sleep(0.1)
    print("\r", end="")

# Example usage of all features
if __name__ == "__main__":
    try:
        SetConsoleTitle("Enhanced Console")
        log_action("Console title set.")

        SetConsoleTextAttribute(_GetStdHandle(STDOUT), 7)  # Default text attributes
        log_action("Console text attributes set to default.")

        print("Welcome to the Enhanced Console!")
        log_action("Displayed welcome message.")

        # Show progress bar
        for i in range(101):
            show_progress_bar(i, 100)
            time.sleep(0.05)
        print()  # Newline after progress bar

        # Show loading spinner
        loading_spinner("Processing")
        print("Done!")

        # Clear console
        ClearConsole()
        log_action("Console cleared.")

    except Exception as e:
        logging.error(f"An error occurred: {e}")

