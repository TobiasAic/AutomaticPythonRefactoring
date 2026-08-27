import argparse
import random
from pathlib import Path

from llm.llm_presets import qwen3_7_plus_config
from llm.openai_llm import OpenAILLM
from llm.parallel_llm import ParallelLLM
from llm.retrying_llm import RetryingLLM
from refactoring_system import RefactoringSystem
from utility.cli import CLI
from utility.config import load_from_toml

if __name__ == '__main__':
    CLI.set_debug_mode(True)
    parser = argparse.ArgumentParser(
        description='Automatic Python Refactoring Tool')
    parser.add_argument('config_path', help='Path to config file')
    parser.add_argument('--seed', type=int, default=42,
                         help='Random seed for category selection (default: 42)')
    args = parser.parse_args()

    random.seed(args.seed)

    full_config_path = Path(args.config_path).absolute().resolve()
    config = load_from_toml(full_config_path)

    print("Running the refactoring system with the following parameters:")
    print(str(config))
    print(f"Random seed: {args.seed}")

    llm = ParallelLLM(RetryingLLM(OpenAILLM(qwen3_7_plus_config),
                      max_retries=3, delay_seconds=10.0))
    refactoring_idea_count = 3  # Number of refactoring ideas to generate per segment
    category_attempt_count = 3  # Number of attempts to generate refactorings for each category

    refactoring_system = RefactoringSystem(
        config, llm, refactoring_idea_count, category_attempt_count)
    refactoring_system.run()
