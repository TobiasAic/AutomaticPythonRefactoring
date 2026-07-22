class Compiler:
    @staticmethod
    def try_compile_file(file_path: str) -> bool:
        """Try to compile a Python file.

        Args:
            file_path (str): The path to the Python file to be compiled. 

        Returns:
            bool: True if the file compiled successfully, False otherwise.
        """
        with open(file_path, 'r') as f:
            code = f.read()

        return Compiler.try_compile_code(code)

    @staticmethod
    def try_compile_code(code: str) -> bool:
        """Try to compile a Python code segment.

        Args:
            code (str): The Python code to be compiled.

        Returns:
            bool: True if the code compiled successfully, False otherwise.
        """
        try:
            compile(code, '', 'exec')
        except SyntaxError as e:
            return False 
        
        return True