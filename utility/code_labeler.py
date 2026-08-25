import libcst as cst
from libcst.metadata import MetadataWrapper, PositionProvider


class CodeLabeler:
    """Assigns each source line a label describing which top-level statement
    group, class, or function it belongs to (and, for nested code, the full
    path down to it), so callers can group and split lines by structure.
    """

    def compute_labels(self, source: str) -> dict[int, tuple[str, ...]]:
        module = cst.parse_module(source)
        wrapper = MetadataWrapper(module)
        module = wrapper.module
        positions = wrapper.resolve(PositionProvider)

        labels = [None] * (len(source.splitlines()))

        def visit_body(body, path):
            for stmt in body:
                pos = positions[stmt]
                # leading_lines holds the blank/comment lines directly above
                # this statement - libcst already attaches them to whatever
                # follows, not to the statement before, so starting the label
                # range there keeps a comment (or decorator, similarly
                # excluded from pos itself) with the thing it's attached to
                # instead of leaking it into the enclosing block's own label.
                # Small statements sharing a single-line body (e.g. the
                # `return 1` in `def foo(): return 1`) have no leading_lines
                # of their own, since trivia attaches at the line level.
                leading_lines = getattr(stmt, "leading_lines", None)
                start_line = positions[leading_lines[0]].start.line if leading_lines else pos.start.line

                if isinstance(stmt, cst.ClassDef):
                    new_path = (*path, f"c({stmt.name.value})")

                    for line in range(start_line, pos.end.line + 1):
                        labels[line-1] = new_path

                    visit_body(stmt.body.body, new_path)

                elif isinstance(stmt, cst.FunctionDef):
                    new_path = (*path, f"f({stmt.name.value})")

                    for line in range(start_line, pos.end.line + 1):
                        labels[line-1] = new_path

                    visit_body(stmt.body.body, new_path)

                else:
                    for line in range(start_line, pos.end.line + 1):
                        labels[line-1] = path or ("s",)

        visit_body(module.body, ())

        def fill_missing_labels():
            next_label = None
            for i in reversed(range(len(labels))):
                if source.splitlines()[i].strip() == "":
                    labels[i] = "e"
                elif labels[i] is not None:
                    next_label = labels[i]
                elif next_label is not None:
                    labels[i] = next_label
                elif next_label is None:
                    raise ValueError(
                        f"Line {i+1} has no label and no subsequent label to inherit from.")

        fill_missing_labels()
        return labels

    def key_at_depth(self, label: tuple[str] | str, depth: int):
        """The grouping key for one line's label at a given nesting depth.

        `label` is either "e" (blank line) or a tuple such as ("c(Foo)",) or
        ("c(Foo)", "f(bar)"). At `depth`, a line is keyed by the name of
        whichever class/function it directly belongs to at that level, or by
        None if the line is content of the container itself (e.g. the "class
        Foo:" line, or a field/statement directly in its body) rather than
        belonging to a nested class or function.
        """
        return label[depth] if len(label) > depth else None

    def print_labels_with_source(self, source: str, labels):
        lines = source.splitlines()

        label_strings = [
            ".".join(label) if isinstance(label, tuple) else label
            for label in labels
        ]

        line_number_width = len(str(len(lines)))
        label_width = max(len(label) for label in label_strings)

        for i, line in enumerate(lines):
            label = label_strings[i]

            print(
                f"{i + 1:>{line_number_width}}: "
                f"{label:<{label_width}} | "
                f"{line}"
            )
