import argparse
from pathlib import Path

from llm.llm_presets import qwen3_7_plus_config
from llm.openai_llm import OpenAILLM
from refactoring_system import RefactoringSystem
from utility.cli import CLI
from utility.config import load_from_toml

if __name__ == '__main__':
    CLI.set_debug_mode(True)
    parser = argparse.ArgumentParser(description='Automatic Python Refactoring Tool')
    parser.add_argument('config_path', help='Path to config file')
    args = parser.parse_args()

    full_config_path = Path(args.config_path).absolute().resolve()
    config = load_from_toml(full_config_path)

    print("Running the refactoring system with the following parameters:")
    print(str(config))

    llm = OpenAILLM(qwen3_7_plus_config)

    refactoring_system = RefactoringSystem(config, llm, 2)
    refactoring_system.run()