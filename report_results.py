"""
report_results.py — per-cell TGC breakdown for a finished AppWorld run.

Reads the evaluation produced by:
    appworld evaluate $APPWORLD_EXPERIMENT <split>
i.e. experiments/outputs/<EXPERIMENT>/evaluations/<split>.json, and joins each task
to its (category, difficulty) so you can see WHERE the agent fails, not just the
aggregate Task Goal Completion (TGC).

  difficulty: taken from the eval record (it already includes it).
  category:   required_apps[0] from ground_truth (post-hoc reporting — allowed; the
              agent itself must never read ground_truth at solve time).

Run:  python report_results.py smoke            # uses $APPWORLD_EXPERIMENT
      python report_results.py testplan team_x  # explicit experiment
"""

import json
import os
import sys
from collections import defaultdict

from appworld.common.path_store import path_store

TASKS_DIR = os.path.join(path_store.data, "tasks")


def primary_app(task_id: str) -> str:
    path = os.path.join(TASKS_DIR, task_id, "ground_truth", "required_apps.json")
    try:
        apps = json.load(open(path))
        return apps[0] if apps else "?"
    except (FileNotFoundError, IndexError, json.JSONDecodeError):
        return "?"


def pct(passed: int, total: int) -> str:
    return f"{100.0 * passed / total:5.1f}%" if total else "   -- "


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit("usage: python report_results.py <split> [experiment]")
    split = sys.argv[1]
    experiment = sys.argv[2] if len(sys.argv) > 2 else os.environ.get("APPWORLD_EXPERIMENT", "team_demo")

    eval_path = os.path.join(
        "experiments", "outputs", experiment, "evaluations", f"{split}.json"
    )
    if not os.path.exists(eval_path):
        raise SystemExit(
            f"No eval file at {eval_path}.\n"
            f"Run:  appworld evaluate {experiment} {split}"
        )
    data = json.load(open(eval_path))
    individual = data.get("individual", {})
    aggregate = data.get("aggregate", {})

    # success/total per cell, per difficulty, per category
    cell = defaultdict(lambda: [0, 0])  # (app, diff) -> [passed, total]
    by_diff = defaultdict(lambda: [0, 0])
    by_app = defaultdict(lambda: [0, 0])
    overall = [0, 0]

    for task_id, rec in individual.items():
        ok = bool(rec.get("success"))
        diff = rec.get("difficulty", "?")
        app = primary_app(task_id)
        for bucket in (cell[(app, diff)], by_diff[diff], by_app[app], overall):
            bucket[0] += int(ok)
            bucket[1] += 1

    apps = sorted({a for a, _ in cell})
    diffs = sorted({d for _, d in cell}, key=lambda d: (d == "?", d))

    print(f"\n=== {experiment} / {split} — {overall[1]} tasks ===")
    print(f"TGC (overall): {pct(*overall)}   "
          f"[appworld aggregate: TGC {aggregate.get('task_goal_completion', '?')}, "
          f"SGC {aggregate.get('scenario_goal_completion', '?')}]")

    # cell matrix
    header = f"\n{'category':14s}" + "".join(f"   D{d}    " for d in diffs) + "   row"
    print(header)
    print("-" * len(header))
    for app in apps:
        row = [f"{app:14s}"]
        for d in diffs:
            p, t = cell.get((app, d), [0, 0])
            row.append(f"{pct(p, t)}({t})" if t else "    --   ")
        row.append(f"  {pct(*by_app[app])}")
        print(" ".join(row))
    foot = [f"{'col':14s}"]
    for d in diffs:
        foot.append(f"{pct(*by_diff[d])}({by_diff[d][1]})")
    foot.append(f"  {pct(*overall)}")
    print(" ".join(foot))

    # failed task ids (quick triage)
    failed = [tid for tid, rec in individual.items() if not rec.get("success")]
    if failed:
        print(f"\nFailed ({len(failed)}): {', '.join(sorted(failed))}")


if __name__ == "__main__":
    main()
