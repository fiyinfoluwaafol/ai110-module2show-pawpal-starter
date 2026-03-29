"""
PawPal+ demo: builds sample owner/pets/tasks and prints today's schedule via Scheduler.
"""

from datetime import date

from pawpal_system import Owner, Pet, Scheduler, Task


def find_pet_for_task(owner: Owner, task: Task) -> Pet:
    """Resolve which pet a task belongs to (for labeling lines in the schedule)."""
    for pet in owner.pets:
        if task in pet.tasks:
            return pet
    raise ValueError("Task is not attached to any of the owner's pets.")


def main() -> None:
    # Use one calendar day so daily/weekly tasks line up with "today's" view.
    today = date.today()

    # Create an owner and register pets (different species).
    owner = Owner(name="Jordan Rivera")
    max_dog = Pet(name="Max", animal="Dog", image="max.png")
    luna_cat = Pet(name="Luna", animal="Cat", image="luna.png")
    owner.add_pet(max_dog)
    owner.add_pet(luna_cat)

    # Attach tasks across pets with varied HH:MM times and care types.
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
    luna_cat.add_task(
        Task(
            title="Medication",
            description="Thyroid pill with food",
            duration=5,
            priority="high",
            time_window="09:00",
            occurrence_date=today,
            frequency="daily",
        )
    )
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
    # Intentional overlap at 12:00 to demonstrate conflict detection (same time, same day).
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
    luna_cat.add_task(
        Task(
            title="Play",
            description="Laser pointer session",
            duration=15,
            priority="low",
            time_window="12:00",
            occurrence_date=today,
        )
    )
    # Recurring weekly task (grooming) — still shown on today's list when due today.
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

    # Demo: mark one task completed so the schedule shows both states.
    max_dog.tasks[0].mark_complete()

    # Scheduler aggregates the owner's tasks and provides sorting / conflict checks.
    scheduler = Scheduler(owner)
    all_tasks = scheduler.get_all_tasks()
    ordered = scheduler.sort_by_time(all_tasks)

    # Surface scheduling conflicts (same date + same time_window).
    conflict_groups = scheduler.detect_conflicts(ordered)
    if conflict_groups:
        print("*** Warning: time conflicts detected (multiple tasks at the same slot). ***")
        for group in conflict_groups:
            labels = [f"{find_pet_for_task(owner, t).name}: {t.description}" for t in group]
            print(f"    Overlap at {group[0].time_window}: {', '.join(labels)}")
        print()

    # Human-readable schedule lines.
    print("--- Today's Schedule ---")
    for task in ordered:
        pet = find_pet_for_task(owner, task)
        time_str = task.time_window or "???"
        status = "Completed" if task.completed else "Incomplete"
        print(
            f"{time_str} - {pet.name} ({pet.animal}): {task.description} [{status}]"
        )


if __name__ == "__main__":
    main()
