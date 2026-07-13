class Compiler:
    @staticmethod
    def try_compile_file(file_path: str) -> bool:
        with open(file_path, 'r') as f:
            code = f.read()

        return Compiler.try_compile_code(code)

    @staticmethod
    def try_compile_code(code: str) -> bool:
        try:
            compile(code, '', 'exec')
        except SyntaxError as e:
            return False 
        
        return True