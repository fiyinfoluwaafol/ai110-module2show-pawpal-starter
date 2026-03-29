from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Any, Optional


@dataclass
class Task:
    title: str
    description: str
    duration: int
    priority: str
    time_window: Optional[str] = None
    completed: bool = False

    def mark_complete(self) -> None:
        pass

    def is_due(self, on_date: date) -> bool:
        pass


@dataclass
class Pet:
    name: str
    animal: str
    image: str
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        pass

    def get_tasks(self) -> list[Task]:
        pass

    def get_daily_tasks(self, on_date: date) -> list[Task]:
        pass


@dataclass
class Owner:
    name: str
    pets: list[Pet] = field(default_factory=list)
    preferences: dict[str, Any] = field(default_factory=dict)

    def add_pet(self, pet: Pet) -> None:
        pass

    def get_pets(self) -> list[Pet]:
        pass

    def set_preferences(self, preferences: dict[str, Any]) -> None:
        pass


@dataclass
class Scheduler:
    tasks: list[Task] = field(default_factory=list)
    constraints: dict[str, Any] = field(default_factory=dict)
    schedule: dict[str, Any] = field(default_factory=dict)

    def generate_daily_plan(self, on_date: date) -> None:
        pass

    def explain_plan(self) -> str:
        pass

    def update_constraints(self, new_constraints: dict[str, Any]) -> None:
        pass

    def reschedule_task(self, task: Task, new_time: Any) -> None:
        pass
