# AI-generated

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
