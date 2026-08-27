# AI-generated

from utility.cli import CLI


def test_print_debug_silent_when_debug_mode_disabled(capsys):
    CLI.set_debug_mode(False)

    CLI.print_debug("hidden message")

    assert capsys.readouterr().out == ""


def test_print_debug_prints_when_debug_mode_enabled(capsys):
    CLI.set_debug_mode(True)
    try:
        CLI.print_debug("visible message")
        output = capsys.readouterr().out
    finally:
        CLI.set_debug_mode(False)

    assert "DEBUG" in output
    assert "visible message" in output


def test_print_debug_includes_caller_class_name(capsys):
    class Caller:
        def report(self):
            CLI.print_debug("from a method")

    CLI.set_debug_mode(True)
    try:
        Caller().report()
        output = capsys.readouterr().out
    finally:
        CLI.set_debug_mode(False)

    assert "Caller" in output


def test_print_error_always_prints_regardless_of_debug_mode(capsys):
    CLI.set_debug_mode(False)

    CLI.print_error("something went wrong")

    output = capsys.readouterr().out
    assert "ERROR" in output
    assert "something went wrong" in output


def test_print_banner_wraps_message_with_symbols(capsys):
    CLI.print_banner("hello", symbol="*", empty_line_count=0)

    output = capsys.readouterr().out
    assert output.startswith("*" * CLI.banner_width)
    assert "hello" in output
    assert output.strip().endswith("*" * CLI.banner_width)
