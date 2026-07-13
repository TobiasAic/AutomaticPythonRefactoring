import json
from radon.complexity import cc_visit
from radon.metrics import mi_visit, h_visit   
from radon.raw import analyze as raw_analyze
from dataclasses import dataclass, asdict
import matplotlib.pyplot as plt

@dataclass
class ReadabilityMetrics:
    cyclomatic_complexity: int
    loc: int
    lloc: int
    sloc: int
    comments: int
    comment_blocks: int
    blank_lines: int
    single_comments: int
    halstead_h1: int
    halstead_h2: int
    halstead_n1: int
    halstead_n2: int
    halstead_vocabulary: int
    halstead_length: int
    halstead_calculated_length: float
    halstead_volume: float
    halstead_difficulty: float
    halstead_effort: float
    halstead_time: float
    halstead_bugs: float
    maintainability_index: float

    def print_metrics(self):
        print(f"Cyclomatic Complexity: {self.cyclomatic_complexity}")
        print(f"Lines of Code (LOC): {self.loc}")
        print(f"Logical Lines of Code (LLOC): {self.lloc}")
        print(f"Source Lines of Code (SLOC): {self.sloc}")
        print(f"Comments: {self.comments}")
        print(f"Comment Blocks: {self.comment_blocks}")
        print(f"Blank Lines: {self.blank_lines}")
        print(f"Single Comments: {self.single_comments}")
        print(f"Distinct Operators (H1): {self.halstead_h1}")
        print(f"Distinct Operands (H2): {self.halstead_h2}")
        print(f"Total Number of Operators (N1): {self.halstead_n1}")
        print(f"Total Number of Operands (N2): {self.halstead_n2}")
        print(f"Vocabulary: {self.halstead_vocabulary}")
        print(f"Length: {self.halstead_length}")
        print(f"Calculated Length: {self.halstead_calculated_length}")
        print(f"Volume: {self.halstead_volume}")
        print(f"Difficulty: {self.halstead_difficulty}")
        print(f"Effort: {self.halstead_effort}")
        print(f"Time: {self.halstead_time} seconds")
        print(f"Bugs: {self.halstead_bugs}")
        print(f"Maintainability Index (MI): {self.maintainability_index}")

    def get_string_improvements(self, other: 'ReadabilityMetrics') -> str:
        improvements = []
        for field in self.__dataclass_fields__:
            old_value = getattr(self, field)
            new_value = getattr(other, field)
            if old_value != new_value:
                improvements.append(f"{field}: {old_value} -> {new_value}")
        return "\n".join(improvements)

class ReadabilityAnalyzer:
    def __init__(self):
        self.metrics = dict()

    def record_metrics(self, filepath: str):
        metrics = ReadabilityAnalyzer.analyze_file(filepath)
        if self.metrics.get(filepath) is None:
            self.metrics[filepath] = []
        self.metrics[filepath].append(metrics)

    def analyze_file(filepath: str) -> ReadabilityMetrics:
        code = ""
        with open(filepath, 'r') as file:
            code = file.read()
        return ReadabilityAnalyzer.analyze_code(code)

    def analyze_code(code: str) -> ReadabilityMetrics:
        # Get Cyclomatic Complexity results
        cc_results = cc_visit(code)
        # Get raw metrics (including LOC)
        raw_results = raw_analyze(code)
        # Get Maintainability Index results
        mi_results = mi_visit(code, multi=True)
        # Halstead metrics
        halstead_results = h_visit(code)

        return ReadabilityMetrics(
            cyclomatic_complexity=cc_results[0].complexity if cc_results else 1,
            loc=raw_results.loc,
            lloc=raw_results.lloc,
            sloc=raw_results.sloc,
            comments=raw_results.comments,
            comment_blocks=raw_results.multi,
            blank_lines=raw_results.blank,
            single_comments=raw_results.single_comments,
            halstead_h1=halstead_results.total.h1,
            halstead_h2=halstead_results.total.h2,
            halstead_n1=halstead_results.total.N1,
            halstead_n2=halstead_results.total.N2,
            halstead_vocabulary=halstead_results.total.vocabulary,
            halstead_length=halstead_results.total.length,
            halstead_calculated_length=round(halstead_results.total.calculated_length, 2),
            halstead_volume=round(halstead_results.total.volume, 2),
            halstead_difficulty=round(halstead_results.total.difficulty, 2),
            halstead_effort=round(halstead_results.total.effort, 2),
            halstead_time=round(halstead_results.total.time, 2),
            halstead_bugs=round(halstead_results.total.bugs, 2),
            maintainability_index=round(mi_results, 2)
        )
    
    def save(self, filepath: str):
        with open(filepath, 'w') as file:
            serializable_metrics = {
                path: [asdict(metric) for metric in metrics_list]
                for path, metrics_list in self.metrics.items()
            }
            json.dump(serializable_metrics, file)

    def load(self, filepath: str):
        with open(filepath, 'r') as file:
            loaded_metrics = json.load(file)

        self.metrics = {
            path: [ReadabilityMetrics(**metric_data) for metric_data in metrics_list]
            for path, metrics_list in loaded_metrics.items()
        }

    def plot_percentage_change(self, filepath: str, output_path: str = None):
        if len(self.metrics[filepath]) < 2:
            print("Not enough data to plot percentage change.")
            return
        
        figure, axes = plt.subplots(4, 1, sharex=True, figsize=(12, 14))

        self.plot_metric_group(filepath, ['cyclomatic_complexity', 'maintainability_index'], axes[0]) 
        self.plot_metric_group(filepath, ['loc', 'lloc', 'sloc', 'comments', 'comment_blocks', 'blank_lines', 'single_comments'], axes[1])
        self.plot_metric_group(filepath, ['halstead_h1', 'halstead_h2', 'halstead_n1', 'halstead_n2'], axes[2])
        self.plot_metric_group(filepath, ['halstead_vocabulary', 'halstead_length', 'halstead_calculated_length', 'halstead_volume', 'halstead_difficulty', 'halstead_effort', 'halstead_time', 'halstead_bugs'], axes[3])
        
        figure.suptitle(f'Percentage Change in Metrics for {filepath}')
        axes[-1].set_xlabel('Iteration')
        figure.tight_layout(rect=[0, 0.03, 1, 0.97])

        if output_path:
            figure.savefig(output_path)
        else:
            figure.show()

    def plot_metric_group(self, filepath: str, metric_group: list[str], axis: plt.Axes):
        for metric in metric_group:
            self.plot_metric(filepath, metric, axis)

            axis.set_ylabel('Percentage Change (%)')
            axis.grid(True)
            axis.legend()

    def plot_metric(self, filepath: str, metric: str, axis: plt.Axes):
        values = [getattr(readability_metrics, metric) for readability_metrics in self.metrics[filepath]]
        percentage_changes = [(values[i] - values[i-1]) / values[i-1] * 100 for i in range(1, len(values))]
        axis.plot(range(1, len(values)), percentage_changes, marker='o', label=metric)
