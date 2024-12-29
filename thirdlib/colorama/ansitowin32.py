# Optimized ANSI to Win32 Conversion with Extended Features
# License: BSD 3-Clause License

import re
import sys
import os
import logging
from datetime import datetime

# Import ANSI codes and Windows Terminal API
from .ansi import AnsiFore, AnsiBack, AnsiStyle, Style
from .winterm import WinTerm, WinColor, WinStyle
from .win32 import windll, winapi_test

# Initialize logging for debugging
logging.basicConfig(
    filename=f"ansi_to_win32_{datetime.now().strftime('%Y%m%d%H%M%S')}.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# Initialize Windows terminal support
winterm = WinTerm() if windll is not None else None


class StreamWrapper:
    """
    Wraps an output stream to intercept and process 'write()' calls.
    Provides compatibility for ANSI-to-Win32 conversion and supports debug logging.
    """

    def __init__(self, wrapped, converter, debug=False):
        self.__wrapped = wrapped
        self.__converter = converter
        self.__debug = debug

    def __getattr__(self, name):
        return getattr(self.__wrapped, name)

    def __enter__(self, *args, **kwargs):
        return self.__wrapped.__enter__(*args, **kwargs)

    def __exit__(self, *args, **kwargs):
        return self.__wrapped.__exit__(*args, **kwargs)

    def write(self, text):
        if self.__debug:
            logging.debug(f"Writing text: {text}")
        self.__converter.write(text)

    def isatty(self):
        if 'PYCHARM_HOSTED' in os.environ:
            return self.__wrapped in [sys.__stdout__, sys.__stderr__]
        return getattr(self.__wrapped, 'isatty', lambda: False)()

    @property
    def closed(self):
        return getattr(self.__wrapped, 'closed', True)


class AnsiToWin32:
    """
    Converts ANSI escape sequences to equivalent Win32 API calls.
    Handles both stripping and conversion of ANSI codes for Windows terminals.
    """
    ANSI_CSI_RE = re.compile(r'\033\[([0-9;]*)m')  # Match ANSI Control Sequence Introducer
    ANSI_OSC_RE = re.compile(r'\033\](.*?)(\x07)')  # Match ANSI Operating System Command

    def __init__(self, wrapped, convert=None, strip=None, autoreset=False, debug=False):
        self.wrapped = wrapped
        self.autoreset = autoreset
        self.debug = debug
        self.stream = StreamWrapper(wrapped, self, debug=debug)

        self.convert = convert if convert is not None else self.default_conversion()
        self.strip = strip if strip is not None else not self.convert
        self.win32_calls = self.get_win32_calls()

        if self.debug:
            logging.debug(f"Initialized AnsiToWin32 with convert={self.convert}, strip={self.strip}")

    def default_conversion(self):
        on_windows = os.name == 'nt'
        return on_windows and winapi_test() and self.stream.isatty()

    def get_win32_calls(self):
        if not (self.convert and winterm):
            return {}
        return {
            AnsiStyle.RESET_ALL: (winterm.reset_all,),
            AnsiStyle.BRIGHT: (winterm.style, WinStyle.BRIGHT),
            AnsiStyle.DIM: (winterm.style, WinStyle.NORMAL),
            AnsiFore.RED: (winterm.fore, WinColor.RED),
            AnsiBack.BLUE: (winterm.back, WinColor.BLUE),
            # Add more mappings as needed
        }

    def write(self, text):
        if self.debug:
            logging.debug(f"Processing text: {text}")
        if self.strip or self.convert:
            self.process_text(text)
        else:
            self.wrapped.write(text)
        if self.autoreset:
            self.reset_all()

    def process_text(self, text):
        """
        Process text to strip or convert ANSI sequences.
        """
        cursor = 0
        text = self.convert_osc(text)
        for match in self.ANSI_CSI_RE.finditer(text):
            start, end = match.span()
            self.write_plain_text(text, cursor, start)
            self.handle_ansi_sequence(*match.groups())
            cursor = end
        self.write_plain_text(text, cursor, len(text))

    def handle_ansi_sequence(self, paramstring):
        params = [int(p) for p in paramstring.split(';') if p.isdigit()]
        for param in params:
            if param in self.win32_calls:
                func, *args = self.win32_calls[param]
                func(*args)
        if self.debug:
            logging.debug(f"Handled ANSI sequence: {paramstring}")

    def reset_all(self):
        if self.convert:
            self.handle_ansi_sequence('0')
        elif not self.strip and not self.stream.closed:
            self.wrapped.write(Style.RESET_ALL)

    def write_plain_text(self, text, start, end):
        if start < end:
            self.wrapped.write(text[start:end])
            self.wrapped.flush()

    def convert_osc(self, text):
        for match in self.ANSI_OSC_RE.finditer(text):
            start, end = match.span()
            text = text[:start] + text[end:]
            paramstring, command = match.groups()
            if command == '\x07':  # BEL
                params = paramstring.split(";")
                if params[0] in '02':  # Title or icon change
                    winterm.set_title(params[1])
        return text


# Utility Functions
def log_debug_message(message):
    """
    Log debug messages if debugging is enabled.
    """
    logging.debug(message)


# Example usage with extended features
if __name__ == "__main__":
    # Initialize AnsiToWin32 for stdout
    converter = AnsiToWin32(sys.stdout, autoreset=True, debug=True)
    stream = converter.stream

    # Print styled text
    stream.write(f"{AnsiFore.RED}This is red text.{Style.RESET_ALL}\n")
    stream.write(f"{AnsiBack.BLUE}This has a blue background.{Style.RESET_ALL}\n")
    stream.write(f"{Style.BRIGHT}{AnsiFore.GREEN}This is bright green text.{Style.RESET_ALL}\n")
    stream.write("Plain text without styling.\n")

