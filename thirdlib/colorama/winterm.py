# Enhanced WinTerm Class with Extended Functionality

from . import win32


# Terminal Colors Constants
class WinColor:
    BLACK = 0
    BLUE = 1
    GREEN = 2
    CYAN = 3
    RED = 4
    MAGENTA = 5
    YELLOW = 6
    GREY = 7


# Text Style Constants
class WinStyle:
    NORMAL = 0x00  # Dim text, dim background
    BRIGHT = 0x08  # Bright text, dim background
    BRIGHT_BACKGROUND = 0x80  # Dim text, bright background


class WinTerm:
    """Enhanced Terminal Management Class with Color, Style, and Cursor Control."""

    def __init__(self):
        # Initialize terminal attributes
        self._default_attrs = win32.GetConsoleScreenBufferInfo(win32.STDOUT).wAttributes
        self._reset_attributes()
        self._light_mode = 0  # Light mode for extended colors

    def _reset_attributes(self):
        """Reset console attributes to default."""
        self._fore = self._default_attrs & 7
        self._back = (self._default_attrs >> 4) & 7
        self._style = self._default_attrs & (WinStyle.BRIGHT | WinStyle.BRIGHT_BACKGROUND)

    def set_console_attrs(self, attrs=None, on_stderr=False):
        """Apply the current attributes to the console."""
        if attrs is None:
            attrs = self.get_attrs()
        handle = win32.STDOUT if not on_stderr else win32.STDERR
        win32.SetConsoleTextAttribute(handle, attrs)

    def get_attrs(self):
        """Combine foreground, background, and style into a single attribute value."""
        return self._fore + (self._back * 16) + (self._style | self._light_mode)

    def reset_all(self, on_stderr=False):
        """Reset all attributes and styles to default."""
        self._reset_attributes()
        self.set_console_attrs(on_stderr=on_stderr)

    def set_foreground(self, color=WinColor.GREY, light=False, on_stderr=False):
        """Set the foreground color."""
        self._fore = color
        self._light_mode = WinStyle.BRIGHT if light else 0
        self.set_console_attrs(on_stderr=on_stderr)

    def set_background(self, color=WinColor.BLACK, light=False, on_stderr=False):
        """Set the background color."""
        self._back = color
        self._light_mode = WinStyle.BRIGHT_BACKGROUND if light else 0
        self.set_console_attrs(on_stderr=on_stderr)

    def move_cursor(self, x=0, y=0, on_stderr=False):
        """Move the cursor to a relative position."""
        handle = win32.STDOUT if not on_stderr else win32.STDERR
        current_pos = win32.GetConsoleScreenBufferInfo(handle).dwCursorPosition
        new_pos = (current_pos.X + x, current_pos.Y + y)
        win32.SetConsoleCursorPosition(handle, new_pos)

    def clear_screen(self, mode=2, on_stderr=False):
        """Clear the screen using the specified mode."""
        handle = win32.STDOUT if not on_stderr else win32.STDERR
        csbi = win32.GetConsoleScreenBufferInfo(handle)
        cells_to_clear = csbi.dwSize.X * csbi.dwSize.Y if mode == 2 else csbi.dwSize.X
        start_coord = win32.COORD(0, 0) if mode == 2 else csbi.dwCursorPosition
        win32.FillConsoleOutputCharacter(handle, ' ', cells_to_clear, start_coord)
        win32.FillConsoleOutputAttribute(handle, self.get_attrs(), cells_to_clear, start_coord)
        if mode == 2:
            win32.SetConsoleCursorPosition(handle, (1, 1))

    def erase_line(self, mode=2, on_stderr=False):
        """Erase a single line based on the specified mode."""
        handle = win32.STDOUT if not on_stderr else win32.STDERR
        csbi = win32.GetConsoleScreenBufferInfo(handle)
        line_length = csbi.dwSize.X
        start_coord = win32.COORD(0, csbi.dwCursorPosition.Y)
        win32.FillConsoleOutputCharacter(handle, ' ', line_length, start_coord)
        win32.FillConsoleOutputAttribute(handle, self.get_attrs(), line_length, start_coord)

    def set_title(self, title):
        """Set the console window title."""
        win32.SetConsoleTitle(title)

    def display_progress_bar(self, progress, total=100, bar_length=50):
        """Display a dynamic progress bar in the console."""
        percent = int((progress / total) * 100)
        filled_length = int(bar_length * progress // total)
        bar = '=' * filled_length + '-' * (bar_length - filled_length)
        print(f"\r|{bar}| {percent}%", end='', flush=True)
        if progress == total:
            print()

    def print_styled(self, text, fore_color=None, back_color=None, style=None, on_stderr=False):
        """Print styled text to the console."""
        if fore_color is not None:
            self.set_foreground(fore_color, on_stderr=on_stderr)
        if back_color is not None:
            self.set_background(back_color, on_stderr=on_stderr)
        if style is not None:
            self._style = style
            self.set_console_attrs(on_stderr=on_stderr)
        print(text)
        self.reset_all(on_stderr=on_stderr)

    def animate_spinner(self, message="Loading", duration=5):
        """Display a spinner animation for the given duration."""
        import itertools, time
        spinner = itertools.cycle(['|', '/', '-', '\\'])
        end_time = time.time() + duration
        while time.time() < end_time:
            print(f"\r{message} {next(spinner)}", end='', flush=True)
            time.sleep(0.1)
        print("\r" + " " * len(message), end='', flush=True)


# Example Usage
if __name__ == "__main__":
    term = WinTerm()

    # Set a title
    term.set_title("Enhanced Terminal")

    # Print styled text
    term.print_styled("Hello, World!", fore_color=WinColor.RED, style=WinStyle.BRIGHT)

    # Display a progress bar
    for i in range(101):
        term.display_progress_bar(i)
        import time
        time.sleep(0.02)

    # Spinner animation
    term.animate_spinner()

    # Clear the screen
    term.clear_screen()

