"""
PawPal+ Phase 4 Demo: Algorithmic Layer

Demonstrates sorting, filtering, conflict detection, and recurring tasks.
"""

from datetime import date

from pawpal_system import Owner, Pet, Scheduler, Task


def find_pet_for_task(owner: Owner, task: Task) -> Pet:
    """Resolve which pet a task belongs to (for labeling in output)."""
    for pet in owner.pets:
        if task in pet.tasks:
            return pet
    raise ValueError("Task is not attached to any of the owner's pets.")


def print_task_list(tasks: list[Task], owner: Owner, title: str) -> None:
    """Helper to print a labeled list of tasks."""
    print(f"\n{title}")
    print("-" * len(title))
    if not tasks:
        print("  (no tasks)")
        return
    for task in tasks:
        pet = find_pet_for_task(owner, task)
        time_str = task.time_window or "no time"
        status = "done" if task.completed else "pending"
        freq = f" [{task.frequency}]" if task.frequency else ""
        print(f"  {time_str} | {pet.name}: {task.title} - {task.description} ({status}){freq}")


def main() -> None:
    today = date.today()

    # --- Setup: Owner and Pets ---
    owner = Owner(name="Jordan Rivera")
    max_dog = Pet(name="Max", animal="Dog", image="max.png")
    luna_cat = Pet(name="Luna", animal="Cat", image="luna.png")
    owner.add_pet(max_dog)
    owner.add_pet(luna_cat)

    # --- Add tasks INTENTIONALLY OUT OF ORDER to demonstrate sorting ---
    # Evening task added first
    max_dog.add_task(
        Task(
            title="Feed",
            description="Dinner",
            duration=15,
            priority="medium",
            time_window="18:00",
            occurrence_date=today,
        )
    )
    # Midday task (will conflict with Luna's Play)
    max_dog.add_task(
        Task(
            title="Walk",
            description="Midday stroll",
            duration=20,
            priority="low",
            time_window="12:00",
            occurrence_date=today,
        )
    )
    # Morning task added later
    max_dog.add_task(
        Task(
            title="Walk",
            description="Morning walk",
            duration=30,
            priority="high",
            time_window="08:00",
            occurrence_date=today,
        )
    )
    # Weekly recurring task
    max_dog.add_task(
        Task(
            title="Groom",
            description="Brush and nail trim",
            duration=45,
            priority="medium",
            time_window="17:00",
            occurrence_date=today,
            frequency="weekly",
        )
    )

    # Luna's tasks (also out of order)
    luna_cat.add_task(
        Task(
            title="Play",
            description="Laser pointer session",
            duration=15,
            priority="low",
            time_window="12:00",  # Same time as Max's midday walk = conflict
            occurrence_date=today,
        )
    )
    luna_cat.add_task(
        Task(
            title="Feed",
            description="Breakfast",
            duration=10,
            priority="medium",
            time_window="09:00",
            occurrence_date=today,
        )
    )
    # Daily recurring task
    luna_cat.add_task(
        Task(
            title="Medication",
            description="Thyroid pill",
            duration=5,
            priority="high",
            time_window="09:00",
            occurrence_date=today,
            frequency="daily",
        )
    )

    # --- Create Scheduler ---
    scheduler = Scheduler(owner)
    all_tasks = scheduler.get_all_tasks()

    # =====================================================================
    # DEMO 1: Unsorted vs Sorted Tasks
    # =====================================================================
    print("=" * 60)
    print("PHASE 4 DEMO: Algorithmic Layer")
    print("=" * 60)

    print_task_list(all_tasks, owner, "UNSORTED TASKS (order added)")

    sorted_tasks = scheduler.sort_by_time(all_tasks)
    print_task_list(sorted_tasks, owner, "SORTED TASKS (by time)")

    # =====================================================================
    # DEMO 2: Conflict Detection
    # =====================================================================
    print("\n" + "=" * 60)
    print("CONFLICT DETECTION")
    print("=" * 60)

    conflict_groups = scheduler.detect_conflicts(all_tasks)
    if conflict_groups:
        print("\nWarning: The following tasks are scheduled at the same time:\n")
        for group in conflict_groups:
            time_slot = group[0].time_window
            print(f"  Conflict at {time_slot}:")
            for task in group:
                pet = find_pet_for_task(owner, task)
                print(f"    - {pet.name}: {task.title} ({task.description})")
    else:
        print("\nNo conflicts detected.")

    # =====================================================================
    # DEMO 3: Filtering
    # =====================================================================
    print("\n" + "=" * 60)
    print("FILTERING EXAMPLES")
    print("=" * 60)

    # Filter by pet name
    luna_tasks = scheduler.filter_tasks(all_tasks, pet_name="Luna")
    print_task_list(luna_tasks, owner, "Filter: Luna's tasks only")

    # Filter by completion status (all are pending initially)
    pending_tasks = scheduler.filter_tasks(all_tasks, completed=False)
    print(f"\nFilter: Pending tasks count = {len(pending_tasks)}")

    # Combined filter: Max's pending tasks
    max_pending = scheduler.filter_tasks(all_tasks, completed=False, pet_name="Max")
    print_task_list(max_pending, owner, "Filter: Max's pending tasks")

    # =====================================================================
    # DEMO 4: Recurring Tasks
    # =====================================================================
    print("\n" + "=" * 60)
    print("RECURRING TASK DEMO")
    print("=" * 60)

    # Find Luna's daily medication task
    med_task = next(t for t in luna_cat.tasks if t.title == "Medication")
    print(f"\nBefore completion:")
    print(f"  Luna has {len(luna_cat.tasks)} tasks")
    print(f"  Medication task date: {med_task.occurrence_date}")

    # Mark it complete via scheduler (triggers recurrence)
    scheduler.mark_task_complete(med_task)

    print(f"\nAfter marking Medication complete:")
    print(f"  Luna now has {len(luna_cat.tasks)} tasks")
    print(f"  Original task completed: {med_task.completed}")

    # Show the new recurring task that was created
    new_med = next(t for t in luna_cat.tasks if t.title == "Medication" and not t.completed)
    print(f"  New task created for: {new_med.occurrence_date}")

    # Also demonstrate weekly recurrence with Max's grooming
    groom_task = next(t for t in max_dog.tasks if t.title == "Groom")
    scheduler.mark_task_complete(groom_task)
    new_groom = next(t for t in max_dog.tasks if t.title == "Groom" and not t.completed)
    print(f"\n  Max's weekly Groom task completed.")
    print(f"  Next grooming scheduled for: {new_groom.occurrence_date}")

    # =====================================================================
    # FINAL: Updated Schedule View
    # =====================================================================
    print("\n" + "=" * 60)
    print("FINAL SCHEDULE (after completions)")
    print("=" * 60)

    # Get fresh task list and sort
    updated_tasks = scheduler.sort_by_time(scheduler.get_all_tasks())
    print_task_list(updated_tasks, owner, f"All tasks for {today} and beyond")


if __name__ == "__main__":
    main()
