"""
PawPal+ Phase 4 Demo: Algorithmic Layer

Demonstrates sorting, filtering, conflict detection, recurring tasks,
priority-based scheduling, and professional CLI formatting (tabulate).
"""

from datetime import date

from tabulate import tabulate

from pawpal_system import (
    PRIORITY_EMOJI,
    Owner,
    Pet,
    Scheduler,
    Task,
    task_type_icon,
)

ANSI_BOLD = "\033[1m"
ANSI_RED = "\033[91m"
ANSI_YELLOW = "\033[93m"
ANSI_GREEN = "\033[92m"
ANSI_CYAN = "\033[96m"
ANSI_DIM = "\033[2m"
ANSI_RESET = "\033[0m"

PRIORITY_COLOR: dict[str, str] = {
    "high": ANSI_RED,
    "medium": ANSI_YELLOW,
    "low": ANSI_GREEN,
}


def find_pet_for_task(owner: Owner, task: Task) -> Pet:
    """Resolve which pet a task belongs to (for labeling in output)."""
    for pet in owner.pets:
        if task in pet.tasks:
            return pet
    raise ValueError("Task is not attached to any of the owner's pets.")


def _banner(title: str) -> None:
    """Print a styled section banner."""
    print(f"\n{ANSI_BOLD}{'═' * 62}{ANSI_RESET}")
    print(f"{ANSI_BOLD}  {title}{ANSI_RESET}")
    print(f"{ANSI_BOLD}{'═' * 62}{ANSI_RESET}")


def _task_rows(tasks: list[Task], owner: Owner) -> list[list[str]]:
    """Build tabulate rows from a task list."""
    rows: list[list[str]] = []
    for t in tasks:
        pet = find_pet_for_task(owner, t)
        icon = task_type_icon(t.title)
        pri_emoji = PRIORITY_EMOJI.get(t.priority.lower(), "")
        color = PRIORITY_COLOR.get(t.priority.lower(), "")
        pri_label = f"{color}{pri_emoji} {t.priority.capitalize()}{ANSI_RESET}"
        status = f"{ANSI_DIM}✅ done{ANSI_RESET}" if t.completed else "⏳ pending"
        tw = t.time_window or "—"
        freq = f"🔁 {t.frequency}" if t.frequency else ""
        rows.append([tw, f"{icon} {t.title}", pet.name, t.description, pri_label, status, freq])
    return rows


TABLE_HEADERS = ["Time", "Task", "Pet", "Details", "Priority", "Status", "Repeat"]


def print_task_table(tasks: list[Task], owner: Owner, title: str) -> None:
    """Print a formatted task table with a title."""
    print(f"\n{ANSI_BOLD}{title}{ANSI_RESET}")
    if not tasks:
        print(f"  {ANSI_DIM}(no tasks){ANSI_RESET}")
        return
    rows = _task_rows(tasks, owner)
    print(tabulate(rows, headers=TABLE_HEADERS, tablefmt="rounded_outline"))


def main() -> None:
    today = date.today()

    owner = Owner(name="Jordan Rivera")
    max_dog = Pet(name="Max", animal="Dog", image="max.png")
    luna_cat = Pet(name="Luna", animal="Cat", image="luna.png")
    owner.add_pet(max_dog)
    owner.add_pet(luna_cat)

    max_dog.add_task(
        Task(title="Feed", description="Dinner", duration=15, priority="medium",
             time_window="18:00", occurrence_date=today)
    )
    max_dog.add_task(
        Task(title="Walk", description="Midday stroll", duration=20, priority="low",
             time_window="12:00", occurrence_date=today)
    )
    max_dog.add_task(
        Task(title="Walk", description="Morning walk", duration=30, priority="high",
             time_window="08:00", occurrence_date=today)
    )
    max_dog.add_task(
        Task(title="Groom", description="Brush and nail trim", duration=45,
             priority="medium", time_window="17:00", occurrence_date=today, frequency="weekly")
    )

    luna_cat.add_task(
        Task(title="Play", description="Laser pointer session", duration=15,
             priority="low", time_window="12:00", occurrence_date=today)
    )
    luna_cat.add_task(
        Task(title="Feed", description="Breakfast", duration=10, priority="medium",
             time_window="09:00", occurrence_date=today)
    )
    luna_cat.add_task(
        Task(title="Medication", description="Thyroid pill", duration=5,
             priority="high", time_window="09:00", occurrence_date=today, frequency="daily")
    )

    scheduler = Scheduler(owner)
    all_tasks = scheduler.get_all_tasks()

    # ── Demo 1: Unsorted → Sorted by Time → Sorted by Priority ──────
    _banner("SORTING DEMO")

    print_task_table(all_tasks, owner, "📋 Unsorted Tasks (insertion order)")

    sorted_by_time = scheduler.sort_by_time(all_tasks)
    print_task_table(sorted_by_time, owner, "⏰ Sorted by Time")

    sorted_by_pri = scheduler.sort_by_priority(all_tasks)
    print_task_table(sorted_by_pri, owner, "🔴 Sorted by Priority (then time)")

    # ── Demo 2: Conflict Detection ───────────────────────────────────
    _banner("CONFLICT DETECTION")

    conflict_groups = scheduler.detect_conflicts(all_tasks)
    if conflict_groups:
        for group in conflict_groups:
            slot = group[0].time_window
            print(f"\n  {ANSI_YELLOW}⚠️  Overlap at {slot}:{ANSI_RESET}")
            for task in group:
                pet = find_pet_for_task(owner, task)
                icon = task_type_icon(task.title)
                print(f"     {icon}  {pet.name}'s {task.title} — {task.description}")
    else:
        print(f"\n  {ANSI_GREEN}No conflicts detected.{ANSI_RESET}")

    # ── Demo 3: Filtering ────────────────────────────────────────────
    _banner("FILTERING EXAMPLES")

    luna_tasks = scheduler.filter_tasks(all_tasks, pet_name="Luna")
    print_task_table(luna_tasks, owner, "🐱 Filter: Luna's tasks only")

    pending_tasks = scheduler.filter_tasks(all_tasks, completed=False)
    print(f"\n  {ANSI_CYAN}Pending tasks count: {len(pending_tasks)}{ANSI_RESET}")

    max_pending = scheduler.filter_tasks(all_tasks, completed=False, pet_name="Max")
    print_task_table(max_pending, owner, "🐶 Filter: Max's pending tasks")

    # ── Demo 4: Recurring Tasks ──────────────────────────────────────
    _banner("RECURRING TASK DEMO")

    med_task = next(t for t in luna_cat.tasks if t.title == "Medication")
    print(f"\n  Before completion: Luna has {len(luna_cat.tasks)} tasks")
    print(f"  💊 Medication task date: {med_task.occurrence_date}")

    scheduler.mark_task_complete(med_task)
    new_med = next(t for t in luna_cat.tasks if t.title == "Medication" and not t.completed)
    print(f"\n  {ANSI_GREEN}✅ Medication marked complete{ANSI_RESET}")
    print(f"  Luna now has {len(luna_cat.tasks)} tasks")
    print(f"  🔁 New occurrence created for: {new_med.occurrence_date}")

    groom_task = next(t for t in max_dog.tasks if t.title == "Groom")
    scheduler.mark_task_complete(groom_task)
    new_groom = next(t for t in max_dog.tasks if t.title == "Groom" and not t.completed)
    print(f"\n  {ANSI_GREEN}✅ Max's weekly Groom marked complete{ANSI_RESET}")
    print(f"  🔁 Next grooming scheduled for: {new_groom.occurrence_date}")

    # ── Final schedule ───────────────────────────────────────────────
    _banner("FINAL SCHEDULE (after completions)")

    updated = scheduler.sort_by_priority(scheduler.get_all_tasks())
    print_task_table(updated, owner, f"📅 All tasks for {today} and beyond (priority order)")


if __name__ == "__main__":
    main()
