import pytest
from pawpal_system import Task, Pet

def test_task_mark_complete_changes_status():
    task = Task(
        title="Test walk",
        description="A simple walk",
        duration=20,
        priority="high"
    )
    assert not task.completed
    task.mark_complete()
    assert task.completed

def test_adding_task_to_pet_increases_task_count():
    pet = Pet(name="Buddy", animal="Dog", image="buddy.png")
    initial_count = len(pet.tasks)
    task = Task(
        title="Feed",
        description="Dinner time",
        duration=10,
        priority="medium"
    )
    pet.add_task(task)
    assert len(pet.tasks) == initial_count + 1
    assert pet.tasks[-1] is task