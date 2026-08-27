import inspect
import time
from datetime import timedelta


class CLI:
    in_debug_mode = False
    banner_width = 30

    @staticmethod
    def set_debug_mode(enabled: bool):
        """Enable or disable debug mode. This controls wether debug output is shown.

        Args:
            enabled (bool): True to enable debug mode, False to disable it. 
        """
        CLI.in_debug_mode = enabled

    @staticmethod
    def print_debug(message: str):
        """Only print if debug mode enabled.

        Args:
            message (str): The debug message to be printed. 
        """
        if CLI.in_debug_mode:
            frame = inspect.currentframe().f_back
            CLI.__print_with_caller_info("DEBUG", message, frame) 

    @staticmethod
    def print_error(message: str):
        """Print an error message.

        Args:
            message (str): The error message to be printed. 
        """
        frame = inspect.currentframe().f_back
        CLI.__print_with_caller_info("ERROR", message, frame) 

    @staticmethod
    def print_banner(message: str, symbol: str = "=", empty_line_count: int = 1):
        """Print a message with symbols in front and behind it, to make it stand out.
        Args:
            message (str): The message to be printed in the banner.
            symbol (str, optional): The symbol to be used for the banner. Defaults to "=".
            empty_line_count (int, optional): The number of empty lines to print before the banner. Defaults to 1.
        """
        banner = '\n' * empty_line_count + symbol * CLI.banner_width + f" {message} " + symbol * CLI.banner_width
        print(banner)

    @staticmethod
    def __print_with_caller_info(prefix: str, message: str, frame):
        line_no = frame.f_lineno
        class_name = CLI.__get_class_name(frame)
        if class_name:
            print(f"{prefix}:{class_name}:{line_no}: {message}")
        else:
            print(f"{prefix}: {message}")

    @staticmethod
    def __get_class_name(frame):
        self_obj = frame.f_locals.get("self")
        return type(self_obj).__name__ if self_obj else None

    @staticmethod
    def print_with_duration(message: str):
        start = time.time()
        yield
        print(f"{message} This took {CLI._format_timespan(time.time() - start)}.")

    def _format_timespan(seconds: float) -> str:
        return str(timedelta(seconds=seconds))