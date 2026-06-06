"""
make_test_plan.py — build balanced AppWorld test splits for fast iteration.

Samples tasks across (category x difficulty) so we can measure the agent per cell
instead of a single aggregate number. Writes two custom split files that work with
both `load_task_ids(<name>)` and `appworld evaluate $EXPERIMENT <name>`:

  data/datasets/smoke.txt     K=1 per cell  (~12 tasks, fast inner loop)
  data/datasets/testplan.txt  K=2 per cell  (~30 tasks, fuller signal)

Category = required_apps[0]; difficulty = ground_truth/metadata.json["difficulty"].
NOTE: reading ground_truth here is fine — this script only *selects* tasks, it does
not solve them. The agent (agent.py) must NEVER read ground_truth at solve time.

Built from dev + train only (test_normal's ground truth is withheld locally, so it
can't be self-evaluated and has no difficulty/category to balance on).

Run:  python make_test_plan.py
"""

import json
import os
from collections import defaultdict

from appworld import load_task_ids
from appworld.common.path_store import path_store
from appworld.task import task_id_to_generator_id

DATA = path_store.data
TASKS_DIR = os.path.join(DATA, "tasks")
DATASETS_DIR = os.path.join(DATA, "datasets")

# Splits that ship with ground truth locally. dev first so it's preferred when a
# cell is available in both (dev is the standard, faster iteration split).
SOURCE_SPLITS = ["dev", "train"]


def task_cell(task_id: str) -> tuple[str, int] | None:
    """Return (primary_app, difficulty) from ground truth, or None if unavailable."""
    gt = os.path.join(TASKS_DIR, task_id, "ground_truth")
    try:
        difficulty = json.load(open(os.path.join(gt, "metadata.json")))["difficulty"]
        apps = json.load(open(os.path.join(gt, "required_apps.json")))
    except (FileNotFoundError, KeyError, json.JSONDecodeError):
        return None
    if not apps:
        return None
    return apps[0], difficulty


def collect_cells() -> dict[tuple[str, int], list[str]]:
    """Map (app, difficulty) -> ordered candidate task ids (dev preferred)."""
    cells: dict[tuple[str, int], list[str]] = defaultdict(list)
    for split in SOURCE_SPLITS:
        for task_id in load_task_ids(split):
            cell = task_cell(task_id)
            if cell is not None:
                cells[cell].append(task_id)
    return cells


def pick(candidates: list[str], k: int) -> list[str]:
    """Pick up to k tasks from distinct generators (avoid near-duplicate _1/_2/_3)."""
    chosen: list[str] = []
    seen_generators: set[str] = set()
    for task_id in candidates:
        gen = task_id_to_generator_id(task_id)
        if gen in seen_generators:
            continue
        seen_generators.add(gen)
        chosen.append(task_id)
        if len(chosen) >= k:
            break
    # Fall back to remaining candidates if there weren't k distinct generators.
    if len(chosen) < k:
        for task_id in candidates:
            if task_id not in chosen:
                chosen.append(task_id)
            if len(chosen) >= k:
                break
    return chosen


def write_split(name: str, task_ids: list[str]) -> str:
    path = os.path.join(DATASETS_DIR, name + ".txt")
    with open(path, "w") as f:
        f.write("\n".join(task_ids) + "\n")
    return path


def print_matrix(cells: dict[tuple[str, int], list[str]], chosen: dict[str, list[str]]) -> None:
    apps = sorted({app for app, _ in cells})
    diffs = [1, 2, 3]
    chosen_set = {name: set(ids) for name, ids in chosen.items()}
    print(f"\n{'category':14s} " + "  ".join(f"D{d}" for d in diffs) + "   (n available)")
    print("-" * 52)
    for app in apps:
        row = [f"{app:14s}"]
        for d in diffs:
            avail = cells.get((app, d), [])
            if not avail:
                row.append(" - ")
            else:
                marks = "".join(
                    "*" for ids in chosen_set.values() if set(avail) & ids
                )
                row.append(f"{len(avail):>2d}{marks or ' '}")
        print("  ".join(row))
    print("\n  '*' per suite that drew from a cell (left=smoke, right=testplan).")


def main() -> None:
    cells = collect_cells()
    if not cells:
        raise SystemExit("No cells found — is the AppWorld data downloaded?")

    smoke: list[str] = []
    testplan: list[str] = []
    for cell in sorted(cells):
        candidates = cells[cell]
        smoke.extend(pick(candidates, 1))
        testplan.extend(pick(candidates, 2))

    smoke_path = write_split("smoke", smoke)
    testplan_path = write_split("testplan", testplan)

    print_matrix(cells, {"smoke": smoke, "testplan": testplan})
    print(f"\nWrote {len(smoke):2d} tasks -> {smoke_path}")
    print(f"Wrote {len(testplan):2d} tasks -> {testplan_path}")
    print("\nNext:")
    print("  export APPWORLD_DATASET=smoke MAX_TASKS=0 && python agent.py")
    print("  appworld evaluate $APPWORLD_EXPERIMENT smoke && python report_results.py smoke")


if __name__ == "__main__":
    main()
