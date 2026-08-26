from utility.compiler import Compiler


def test_try_compile_code_returns_true_for_valid_code():
    assert Compiler.try_compile_code("x = 1\nprint(x)\n") is True


def test_try_compile_code_returns_false_for_syntax_error():
    assert Compiler.try_compile_code("def foo(:\n") is False


def test_try_compile_file_reads_and_compiles_file(tmp_path):
    file_path = tmp_path / "valid.py"
    file_path.write_text("x = 1\n")

    assert Compiler.try_compile_file(str(file_path)) is True


def test_try_compile_file_returns_false_for_invalid_file(tmp_path):
    file_path = tmp_path / "invalid.py"
    file_path.write_text("def foo(:\n")

    assert Compiler.try_compile_file(str(file_path)) is False
