import inspect

class CLI:
    in_debug_mode = False

    @staticmethod
    def set_debug_mode(enabled: bool):
        CLI.in_debug_mode = enabled

    @staticmethod
    def print_debug(message: str):
        if CLI.in_debug_mode:
            frame = inspect.currentframe().f_back
            CLI.print_with_caller_info("DEBUG", message, frame) 

    @staticmethod
    def print_error(message: str):
        frame = inspect.currentframe().f_back
        CLI.print_with_caller_info("ERROR", message, frame) 

    def print_with_caller_info(prefix: str, message: str, frame):
        line_no = frame.f_lineno
        class_name = CLI.get_class_name(frame)
        if class_name:
            print(f"{prefix}:{class_name}:{line_no}: {message}")
        else:
            print(f"{prefix}: {message}")

    @staticmethod
    def get_class_name(frame):
        self_obj = frame.f_locals.get("self")
        return type(self_obj).__name__ if self_obj else None