from utility.code_labeler import CodeLabeler


def test_compute_labels_for_simple_statements_and_function():
    source = (
        "import os\n"
        "\n"
        "def foo():\n"
        "    return 1\n"
    )

    labels = CodeLabeler().compute_labels(source)

    assert labels[0] == ("s",)
    assert labels[1] == "e"
    assert labels[2] == ("f(foo)",)
    assert labels[3] == ("f(foo)",)


def test_compute_labels_for_nested_class_and_method():
    source = (
        "class Foo:\n"
        "    def bar(self):\n"
        "        return 1\n"
    )

    labels = CodeLabeler().compute_labels(source)

    assert labels[0] == ("c(Foo)",)
    assert labels[1] == ("c(Foo)", "f(bar)")
    assert labels[2] == ("c(Foo)", "f(bar)")


def test_compute_labels_attaches_leading_blank_and_comment_lines_to_following_statement():
    source = (
        "x = 1\n"
        "\n"
        "# a comment\n"
        "def foo():\n"
        "    return x\n"
    )

    labels = CodeLabeler().compute_labels(source)

    assert labels[0] == ("s",)
    assert labels[1] == "e"
    assert labels[2] == ("f(foo)",)
    assert labels[3] == ("f(foo)",)
    assert labels[4] == ("f(foo)",)


def test_compute_labels_for_trailing_blank_lines_inherits_previous_label():
    source = (
        "def foo():\n"
        "    return 1\n"
        "\n"
    )

    labels = CodeLabeler().compute_labels(source)

    assert labels[0] == ("f(foo)",)
    assert labels[1] == ("f(foo)",)
    assert labels[2] == "e"


def test_key_at_depth_returns_none_beyond_label_length():
    labeler = CodeLabeler()

    assert labeler.key_at_depth(("c(Foo)",), 0) == "c(Foo)"
    assert labeler.key_at_depth(("c(Foo)",), 1) is None
    assert labeler.key_at_depth(("c(Foo)", "f(bar)"), 1) == "f(bar)"
