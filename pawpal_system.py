from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Any, Literal, Optional

Frequency = Optional[Literal["daily", "weekly"]]

PRIORITY_EMOJI: dict[str, str] = {"high": "🔴", "medium": "🟡", "low": "🟢"}

TASK_TYPE_EMOJI: dict[str, str] = {
    "walk": "🚶",
    "feed": "🍽️",
    "play": "🎾",
    "groom": "✂️",
    "medication": "💊",
    "vet": "🏥",
    "train": "🎓",
    "bath": "🛁",
}


def task_type_icon(title: str) -> str:
    """Return an emoji for well-known task titles, or a generic paw."""
    return TASK_TYPE_EMOJI.get(title.lower().strip(), "🐾")


def _parse_hh_mm(time_str: str) -> tuple[int, int]:
    """Parse 'HH:MM' into (hour, minute). Raises ValueError if invalid."""
    parts = time_str.strip().split(":")
    if len(parts) != 2:
        raise ValueError(f"Time must be HH:MM, got {time_str!r}")
    h, m = int(parts[0]), int(parts[1])
    if not (0 <= h <= 23 and 0 <= m <= 59):
        raise ValueError(f"Invalid time values: {time_str!r}")
    return h, m


def _time_sort_key_optional(time_window: Optional[str]) -> tuple[int, int]:
    """Sort key for clock time; missing window sorts last within a day."""
    if time_window is None:
        return (24, 0)
    return _parse_hh_mm(time_window)


@dataclass
class Task:
    """
    A care task (matches design: title, description, duration, priority,
    optional time_window, completed). ``occurrence_date`` and ``frequency``
    support daily views and recurrence without changing the public UML shape.
    """

    title: str
    description: str
    duration: int
    priority: str
    time_window: Optional[str] = None
    completed: bool = False
    occurrence_date: date = field(default_factory=date.today)
    frequency: Frequency = None

    def mark_complete(self) -> None:
        """Set the task as done."""
        self.completed = True

    def is_due(self, on_date: date) -> bool:
        """Check if the task is due on a given date (this instance's day)."""
        return self.occurrence_date == on_date

    def __str__(self) -> str:
        """Readable representation of the task."""
        tw = self.time_window or "unspecified time"
        freq = self.frequency or "one-off"
        status = "✅ done" if self.completed else "⏳ pending"
        emoji = PRIORITY_EMOJI.get(self.priority.lower(), "")
        icon = task_type_icon(self.title)
        return (
            f"{icon} {self.title}: {self.description} @ {tw} on {self.occurrence_date.isoformat()} "
            f"({emoji} {self.priority}, {freq}, {status})"
        )


@dataclass
class Pet:
    """A pet with name, species, image, and assigned tasks."""

    name: str
    animal: str
    image: str
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Assign a new task to this pet."""
        self.tasks.append(task)

    def get_tasks(self) -> list[Task]:
        """Retrieve all tasks for this pet."""
        return list(self.tasks)

    def get_daily_tasks(self, on_date: date) -> list[Task]:
        """Get tasks specific to a certain day."""
        return [t for t in self.tasks if t.is_due(on_date)]


@dataclass
class Owner:
    """An owner with pets and scheduling preferences."""

    name: str
    pets: list[Pet] = field(default_factory=list)
    preferences: dict[str, Any] = field(default_factory=dict)

    def add_pet(self, pet: Pet) -> None:
        """Add a new pet to the owner profile."""
        self.pets.append(pet)

    def get_pets(self) -> list[Pet]:
        """Retrieve a list of all owned pets."""
        return list(self.pets)

    def set_preferences(self, preferences: dict[str, Any]) -> None:
        """Update owner scheduling or task preferences."""
        self.preferences = dict(preferences)

    def get_all_tasks(self) -> list[Task]:
        """Return every task from every pet (handy for scheduling)."""
        out: list[Task] = []
        for pet in self.pets:
            out.extend(pet.get_tasks())
        return out


class Scheduler:
    """
    Uses an Owner's pets/tasks and preferences. Exposes UML fields
    ``tasks`` (aggregated), ``constraints``, and ``schedule``.
    """

    def __init__(self, owner: Owner) -> None:
        """Attach an owner and initialize empty constraints and schedule."""
        self._owner = owner
        self.constraints: dict[str, Any] = {}
        self.schedule: dict[str, Any] = {}

    @property
    def tasks(self) -> list[Task]:
        """All tasks needing to be scheduled (across pets)."""
        return self._owner.get_all_tasks()

    def generate_daily_plan(self, on_date: date) -> None:
        """Build a prioritized daily plan from pet tasks and store it in ``schedule``."""
        day_tasks: list[Task] = []
        for pet in self._owner.pets:
            day_tasks.extend(pet.get_daily_tasks(on_date))
        ordered = sorted(
            day_tasks,
            key=lambda t: (
                _priority_rank(t.priority),
                t.occurrence_date,
                _time_sort_key_optional(t.time_window),
            ),
        )
        self.schedule = {
            "date": on_date.isoformat(),
            "tasks": ordered,
            "owner_preferences": dict(self._owner.preferences),
            "constraints": dict(self.constraints),
        }

    def explain_plan(self) -> str:
        """Provide a rationale or explanation for the generated schedule."""
        if not self.schedule:
            return "No plan yet. Call generate_daily_plan(date) first."
        lines: list[str] = [f"Plan for {self.schedule.get('date', '?')}:"]
        for t in self.schedule.get("tasks", []):
            tw = t.time_window or "unspecified"
            lines.append(
                f"  • {t.title} — {tw} — {t.priority} priority ({t.duration} min)"
            )
        return "\n".join(lines)

    def update_constraints(self, new_constraints: dict[str, Any]) -> None:
        """Modify scheduling parameters (e.g., owner's available time)."""
        self.constraints.update(new_constraints)

    def reschedule_task(self, task: Task, new_time: Any) -> None:
        """Change the timing of a given task (updates ``time_window``)."""
        task.time_window = str(new_time) if not isinstance(new_time, str) else new_time

    def get_all_tasks(self) -> list[Task]:
        """Retrieve all tasks from the owner (all pets)."""
        return self._owner.get_all_tasks()

    def sort_by_time(self, tasks: list[Task]) -> list[Task]:
        """
        Sort tasks chronologically by date and time.

        Uses Python's sorted() with a tuple key: (occurrence_date, parsed time).
        Tasks without a time_window are placed at the end of their day.
        """
        return sorted(
            tasks,
            key=lambda t: (t.occurrence_date, _time_sort_key_optional(t.time_window)),
        )

    def sort_by_priority(self, tasks: list[Task]) -> list[Task]:
        """
        Sort tasks by priority first (High > Medium > Low), then by time.

        This is the advanced scheduling strategy: urgent tasks surface to the
        top regardless of their scheduled time, with time as a tiebreaker
        within the same priority level.
        """
        return sorted(
            tasks,
            key=lambda t: (
                _priority_rank(t.priority),
                t.occurrence_date,
                _time_sort_key_optional(t.time_window),
            ),
        )

    def filter_tasks(
        self,
        tasks: list[Task],
        completed: Optional[bool] = None,
        pet_name: Optional[str] = None,
    ) -> list[Task]:
        """
        Filter tasks by completion status and/or pet name.

        Args:
            tasks: List of tasks to filter.
            completed: If True, keep only completed; if False, only incomplete.
            pet_name: If provided, keep only tasks belonging to that pet.

        Both filters can be combined. Returns a new filtered list.
        """
        result = list(tasks)
        if completed is not None:
            result = [t for t in result if t.completed is completed]
        if pet_name is not None:
            allowed = self._tasks_for_pet_named(pet_name)
            result = [t for t in result if t in allowed]
        return result

    def _tasks_for_pet_named(self, pet_name: str) -> list[Task]:
        """Return tasks for the pet named ``pet_name``, or an empty list if not found."""
        for pet in self._owner.pets:
            if pet.name == pet_name:
                return list(pet.tasks)
        return []

    def detect_conflicts(self, tasks: list[Task]) -> list[list[Task]]:
        """
        Detect scheduling conflicts (exact time match).

        Groups tasks by (date, time_window) and returns groups with 2+ tasks.
        This is a lightweight approach: only exact time matches are flagged,
        not overlapping durations.
        """
        buckets: dict[tuple[date, str], list[Task]] = {}
        for task in tasks:
            if task.time_window is None:
                continue
            key = (task.occurrence_date, task.time_window)
            buckets.setdefault(key, []).append(task)
        return [group for group in buckets.values() if len(group) >= 2]

    def mark_task_complete(self, task: Task) -> None:
        """
        Mark a task complete and handle recurrence.

        If the task has frequency "daily" or "weekly", a new Task is created
        for the next occurrence (using timedelta) and added to the same pet.
        Only one future task is created per completion to avoid infinite chains.
        """
        pet = self._find_pet_containing(task)
        if pet is None:
            return

        task.mark_complete()

        if task.frequency not in ("daily", "weekly"):
            return

        if task.frequency == "daily":
            next_day = task.occurrence_date + timedelta(days=1)
        else:
            next_day = task.occurrence_date + timedelta(weeks=1)

        successor = Task(
            title=task.title,
            description=task.description,
            duration=task.duration,
            priority=task.priority,
            time_window=task.time_window,
            completed=False,
            occurrence_date=next_day,
            frequency=task.frequency,
        )
        pet.add_task(successor)

    def _find_pet_containing(self, task: Task) -> Optional[Pet]:
        """Return the pet whose task list includes ``task``, or None."""
        for pet in self._owner.pets:
            if task in pet.tasks:
                return pet
        return None


def _priority_rank(priority: str) -> int:
    """Lower number = higher priority for sorting (simple default)."""
    order = {"high": 0, "medium": 1, "low": 2}
    return order.get(priority.lower().strip(), 3)
