import argparse
from pathlib import Path
import logging

from config import load_from_toml
from refactoring_system import RefactoringSystem
from logging_setup import setup_logging


if __name__ == '__main__':
    setup_logging(level=logging.DEBUG)
    parser = argparse.ArgumentParser(description='Automatic Python Refactoring Tool')
    parser.add_argument('config_path', help='Path to config file')
    args = parser.parse_args()

    full_config_path = Path(args.config_path).absolute().resolve()
    config = load_from_toml(full_config_path)

    print("Running the refactoring system with the following parameters:")
    print(str(config))

    refactoring_system = RefactoringSystem(config)
    refactoring_system.run()