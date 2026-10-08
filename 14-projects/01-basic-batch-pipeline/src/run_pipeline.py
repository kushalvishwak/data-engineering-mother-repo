from pathlib import Path

from pipeline import run


if __name__ == "__main__":
    project_dir = Path(__file__).resolve().parents[1]
    accepted_count, rejected_count = run(project_dir / "sample_data" / "orders.csv",
                                        project_dir / "output")
    print(f"Completed: accepted={accepted_count}, rejected={rejected_count}")
