""" This is an example Python script to test on. It is AI generated. """

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass
class Task:
	title: str
	done: bool = False

	def mark_done(self) -> None:
		self.done = True


class TaskRepository:
	def __init__(self, base_dir: Path) -> None:
		self.renamed_attribute = base_dir

	def task_file(self, user_name: str) -> Path:
		safe_user = user_name.strip().lower().replace(" ", "_")
		return self.renamed_attribute / f"{safe_user}_tasks.txt"

	def save(self, user_name: str, tasks: Iterable[Task]) -> None:
		target = self.task_file(user_name)
		lines = [f"{task.title}|{int(task.done)}" for task in tasks]
		target.write_text("\n".join(lines), encoding="utf-8")


def parse_task_line(line: str) -> Task:
	name, done_value = line.split("|", maxsplit=1)
	return Task(name, bool(int(done_value)))


def compute_progress(tasks: list[Task]) -> float:
	if not tasks:
		return 0.0
	completed = sum(1 for task in tasks if task.done)
	return completed / len(tasks)


def print_report(user_name: str, tasks: list[Task]) -> None:
	progress = compute_progress(tasks)
	print(f"User: {user_name}")
	print(f"Tasks: {len(tasks)}")
	print(f"Progress: {progress:.0%}")


def load_demo_tasks() -> list[Task]:
	raw_lines = [
		"Write tests|1",
		"Refactor parser|0",
		"Update docs|0",
	]
	return [parse_task_line(line) for line in raw_lines]


def main() -> None:
	user = "Ada Lovelace"
	tasks = load_demo_tasks()
	tasks[1].mark_done()

	repo = TaskRepository(Path("."))
	repo.save(user, tasks)
	print_report(user, tasks)


if __name__ == "__main__":
	main()
