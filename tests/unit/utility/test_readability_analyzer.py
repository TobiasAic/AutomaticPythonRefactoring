from utility.readability_analyzer import ReadabilityAnalyzer, ReadabilityMetrics

SAMPLE_CODE = (
    "def add(a, b):\n"
    "    # adds two numbers\n"
    "    return a + b\n"
)


def test_analyze_code_returns_populated_metrics():
    metrics = ReadabilityAnalyzer.analyze_code(SAMPLE_CODE)

    assert isinstance(metrics, ReadabilityMetrics)
    assert metrics.cyclomatic_complexity >= 1
    assert metrics.loc == len(SAMPLE_CODE.splitlines())
    assert metrics.comments == 1


def test_analyze_file_reads_and_analyzes_a_file(tmp_path):
    file_path = tmp_path / "sample.py"
    file_path.write_text(SAMPLE_CODE)

    metrics = ReadabilityAnalyzer.analyze_file(str(file_path))

    assert metrics.loc == len(SAMPLE_CODE.splitlines())


def test_metrics_to_dict_and_from_dict_round_trip():
    metrics = ReadabilityAnalyzer.analyze_code(SAMPLE_CODE)

    restored = ReadabilityMetrics.from_dict(metrics.to_dict())

    assert restored == metrics


def test_get_string_improvements_lists_only_changed_fields():
    before = ReadabilityAnalyzer.analyze_code("def f():\n    return 1\n")
    after = ReadabilityAnalyzer.analyze_code(SAMPLE_CODE)

    improvements = before.get_string_improvements(after)

    assert "comments: 0 -> 1" in improvements
    assert "loc:" in improvements


def test_record_metrics_appends_to_history_for_file(tmp_path):
    file_path = tmp_path / "sample.py"
    file_path.write_text(SAMPLE_CODE)
    analyzer = ReadabilityAnalyzer()

    analyzer.record_metrics(str(file_path))
    analyzer.record_metrics(str(file_path))

    assert len(analyzer.metrics[str(file_path)]) == 2


def test_save_and_load_round_trip(tmp_path):
    file_path = tmp_path / "sample.py"
    file_path.write_text(SAMPLE_CODE)
    analyzer = ReadabilityAnalyzer()
    analyzer.record_metrics(str(file_path))
    metrics_path = tmp_path / "metrics.json"

    analyzer.save(str(metrics_path))

    loaded = ReadabilityAnalyzer()
    loaded.load(str(metrics_path))

    assert loaded.metrics[str(file_path)] == analyzer.metrics[str(file_path)]
