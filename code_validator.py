import subprocess
from typing import Enum
import logging

class ValidationResult(Enum):
    SUCCESS = "Success"
    SYNTAX_ERROR = "Syntax Error"
    TEST_FAILURE = "Test Failure"

class CodeValidator:
    """ Checks if a python file compiles and if the tests pass. """
    def validate_code(code: str, test_file_path: str) -> ValidationResult:
        if not CodeValidator.try_compile(code):
            return ValidationResult.SYNTAX_ERROR
        if not CodeValidator.run_tests(test_file_path):
            return ValidationResult.TEST_FAILURE
        return ValidationResult.SUCCESS

    def try_compile(code: str) -> bool:
        try:
            compile(code, '', 'exec')
        except SyntaxError as e:
            return False 
        
        return True

    def run_tests(test_file_path: str) -> bool:
        result = subprocess.run(['pytest', test_file_path], capture_output=True, text=True)
        logger = logging.getLogger(__name__)
        logger.debug(f"Pytest stdout: {result.stdout}")
        logger.debug(f"Pytest stderr: {result.stderr}")
        return result.returncode == 0