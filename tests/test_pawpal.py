"""
PawPal+ Test Suite - Phase 5: Testing and Verification

Tests core system behaviors including sorting, recurrence, conflict detection,
and basic CRUD operations on Task, Pet, Owner, and Scheduler classes.
"""

import pytest
from datetime import date, timedelta

from pawpal_system import Task, Pet, Owner, Scheduler, PRIORITY_EMOJI, task_type_icon


# =============================================================================
# FIXTURE: Reusable test data
# =============================================================================

@pytest.fixture
def sample_owner_with_pets():
    """Create an owner with two pets and sample tasks for testing."""
    owner = Owner(name="Test Owner")
    
    dog = Pet(name="Buddy", animal="Dog", image="buddy.png")
    cat = Pet(name="Whiskers", animal="Cat", image="whiskers.png")
    
    owner.add_pet(dog)
    owner.add_pet(cat)
    
    return owner, dog, cat


# =============================================================================
# TEST: Task.mark_complete changes status
# =============================================================================

def test_task_mark_complete_changes_status():
    """Verify that mark_complete() sets completed to True."""
    # Arrange
    task = Task(
        title="Test walk",
        description="A simple walk",
        duration=20,
        priority="high"
    )
    
    # Act & Assert (before)
    assert not task.completed
    
    # Act
    task.mark_complete()
    
    # Assert (after)
    assert task.completed


# =============================================================================
# TEST: Adding task to pet increases task count
# =============================================================================

def test_adding_task_to_pet_increases_task_count():
    """Verify that add_task() appends the task to the pet's task list."""
    # Arrange
    pet = Pet(name="Buddy", animal="Dog", image="buddy.png")
    initial_count = len(pet.tasks)
    task = Task(
        title="Feed",
        description="Dinner time",
        duration=10,
        priority="medium"
    )
    
    # Act
    pet.add_task(task)
    
    # Assert
    assert len(pet.tasks) == initial_count + 1
    assert pet.tasks[-1] is task


# =============================================================================
# TEST: Sorting Correctness (Required)
# =============================================================================

def test_sort_by_time_returns_chronological_order():
    """
    Verify that tasks are returned in chronological order by date and time.
    
    Tasks added out of order should be sorted by:
    1. occurrence_date (ascending)
    2. time_window (ascending, with None sorted last)
    """
    # Arrange
    owner = Owner(name="Test Owner")
    pet = Pet(name="Max", animal="Dog", image="max.png")
    owner.add_pet(pet)
    
    today = date.today()
    
    # Add tasks intentionally OUT OF ORDER
    task_evening = Task(
        title="Evening Feed",
        description="Dinner",
        duration=15,
        priority="medium",
        time_window="18:00",
        occurrence_date=today,
    )
    task_morning = Task(
        title="Morning Walk",
        description="Early walk",
        duration=30,
        priority="high",
        time_window="08:00",
        occurrence_date=today,
    )
    task_noon = Task(
        title="Midday Play",
        description="Play session",
        duration=20,
        priority="low",
        time_window="12:00",
        occurrence_date=today,
    )
    
    pet.add_task(task_evening)  # Added first, but should sort third
    pet.add_task(task_morning)  # Added second, but should sort first
    pet.add_task(task_noon)     # Added third, but should sort second
    
    scheduler = Scheduler(owner)
    
    # Act
    sorted_tasks = scheduler.sort_by_time(scheduler.get_all_tasks())
    
    # Assert
    assert len(sorted_tasks) == 3
    assert sorted_tasks[0] is task_morning  # 08:00
    assert sorted_tasks[1] is task_noon     # 12:00
    assert sorted_tasks[2] is task_evening  # 18:00


def test_sort_by_time_tasks_without_time_window_sort_last():
    """Verify that tasks with no time_window are placed at the end of their day."""
    # Arrange
    owner = Owner(name="Test Owner")
    pet = Pet(name="Max", animal="Dog", image="max.png")
    owner.add_pet(pet)
    
    today = date.today()
    
    task_no_time = Task(
        title="Flexible Task",
        description="No specific time",
        duration=15,
        priority="low",
        time_window=None,  # No time specified
        occurrence_date=today,
    )
    task_with_time = Task(
        title="Scheduled Task",
        description="Specific time",
        duration=15,
        priority="low",
        time_window="10:00",
        occurrence_date=today,
    )
    
    pet.add_task(task_no_time)
    pet.add_task(task_with_time)
    
    scheduler = Scheduler(owner)
    
    # Act
    sorted_tasks = scheduler.sort_by_time(scheduler.get_all_tasks())
    
    # Assert
    assert sorted_tasks[0] is task_with_time  # 10:00 comes first
    assert sorted_tasks[1] is task_no_time    # None comes last


def test_sort_by_time_across_multiple_dates():
    """Verify sorting works correctly across different dates."""
    # Arrange
    owner = Owner(name="Test Owner")
    pet = Pet(name="Max", animal="Dog", image="max.png")
    owner.add_pet(pet)
    
    today = date.today()
    tomorrow = today + timedelta(days=1)
    
    task_tomorrow_early = Task(
        title="Tomorrow Early",
        description="Task",
        duration=15,
        priority="low",
        time_window="06:00",
        occurrence_date=tomorrow,
    )
    task_today_late = Task(
        title="Today Late",
        description="Task",
        duration=15,
        priority="low",
        time_window="22:00",
        occurrence_date=today,
    )
    
    pet.add_task(task_tomorrow_early)
    pet.add_task(task_today_late)
    
    scheduler = Scheduler(owner)
    
    # Act
    sorted_tasks = scheduler.sort_by_time(scheduler.get_all_tasks())
    
    # Assert: Today's late task should come before tomorrow's early task
    assert sorted_tasks[0] is task_today_late
    assert sorted_tasks[1] is task_tomorrow_early


# =============================================================================
# TEST: Recurrence Logic (Required)
# =============================================================================

def test_mark_task_complete_daily_creates_next_day_task():
    """
    Verify that completing a daily recurring task creates a new task
    for the following day.
    """
    # Arrange
    owner = Owner(name="Test Owner")
    pet = Pet(name="Luna", animal="Cat", image="luna.png")
    owner.add_pet(pet)
    
    today = date.today()
    tomorrow = today + timedelta(days=1)
    
    daily_task = Task(
        title="Medication",
        description="Daily pill",
        duration=5,
        priority="high",
        time_window="09:00",
        occurrence_date=today,
        frequency="daily",
    )
    pet.add_task(daily_task)
    
    scheduler = Scheduler(owner)
    initial_task_count = len(pet.tasks)
    
    # Act
    scheduler.mark_task_complete(daily_task)
    
    # Assert
    assert daily_task.completed is True
    assert len(pet.tasks) == initial_task_count + 1
    
    # Find the new task (the one that's not completed)
    new_task = next(t for t in pet.tasks if t.title == "Medication" and not t.completed)
    assert new_task.occurrence_date == tomorrow
    assert new_task.frequency == "daily"
    assert new_task.time_window == "09:00"


def test_mark_task_complete_weekly_creates_next_week_task():
    """
    Verify that completing a weekly recurring task creates a new task
    for the following week.
    """
    # Arrange
    owner = Owner(name="Test Owner")
    pet = Pet(name="Max", animal="Dog", image="max.png")
    owner.add_pet(pet)
    
    today = date.today()
    next_week = today + timedelta(weeks=1)
    
    weekly_task = Task(
        title="Grooming",
        description="Weekly brush",
        duration=45,
        priority="medium",
        time_window="14:00",
        occurrence_date=today,
        frequency="weekly",
    )
    pet.add_task(weekly_task)
    
    scheduler = Scheduler(owner)
    
    # Act
    scheduler.mark_task_complete(weekly_task)
    
    # Assert
    assert weekly_task.completed is True
    
    new_task = next(t for t in pet.tasks if t.title == "Grooming" and not t.completed)
    assert new_task.occurrence_date == next_week
    assert new_task.frequency == "weekly"


def test_mark_task_complete_one_off_does_not_create_new_task():
    """
    Verify that completing a one-off task (no frequency) does NOT
    create a new recurring task.
    """
    # Arrange
    owner = Owner(name="Test Owner")
    pet = Pet(name="Max", animal="Dog", image="max.png")
    owner.add_pet(pet)
    
    one_off_task = Task(
        title="Vet Visit",
        description="Annual checkup",
        duration=60,
        priority="high",
        time_window="10:00",
        occurrence_date=date.today(),
        frequency=None,  # One-off task
    )
    pet.add_task(one_off_task)
    
    scheduler = Scheduler(owner)
    initial_task_count = len(pet.tasks)
    
    # Act
    scheduler.mark_task_complete(one_off_task)
    
    # Assert
    assert one_off_task.completed is True
    assert len(pet.tasks) == initial_task_count  # No new task created


# =============================================================================
# TEST: Conflict Detection (Required)
# =============================================================================

def test_detect_conflicts_flags_duplicate_times():
    """
    Verify that tasks scheduled at the exact same date and time
    are detected as conflicts.
    """
    # Arrange
    owner = Owner(name="Test Owner")
    dog = Pet(name="Max", animal="Dog", image="max.png")
    cat = Pet(name="Luna", animal="Cat", image="luna.png")
    owner.add_pet(dog)
    owner.add_pet(cat)
    
    today = date.today()
    
    # Two tasks at the same time (conflict!)
    dog_task = Task(
        title="Walk Max",
        description="Dog walk",
        duration=30,
        priority="high",
        time_window="12:00",
        occurrence_date=today,
    )
    cat_task = Task(
        title="Play with Luna",
        description="Cat play",
        duration=15,
        priority="low",
        time_window="12:00",  # Same time as dog_task
        occurrence_date=today,
    )
    
    dog.add_task(dog_task)
    cat.add_task(cat_task)
    
    scheduler = Scheduler(owner)
    
    # Act
    conflicts = scheduler.detect_conflicts(scheduler.get_all_tasks())
    
    # Assert
    assert len(conflicts) == 1  # One conflict group
    assert len(conflicts[0]) == 2  # Two tasks in conflict
    assert dog_task in conflicts[0]
    assert cat_task in conflicts[0]


def test_detect_conflicts_no_conflicts_when_times_differ():
    """Verify that tasks at different times do not trigger conflicts."""
    # Arrange
    owner = Owner(name="Test Owner")
    pet = Pet(name="Max", animal="Dog", image="max.png")
    owner.add_pet(pet)
    
    today = date.today()
    
    task_morning = Task(
        title="Morning Walk",
        description="Walk",
        duration=30,
        priority="high",
        time_window="08:00",
        occurrence_date=today,
    )
    task_evening = Task(
        title="Evening Feed",
        description="Dinner",
        duration=15,
        priority="medium",
        time_window="18:00",
        occurrence_date=today,
    )
    
    pet.add_task(task_morning)
    pet.add_task(task_evening)
    
    scheduler = Scheduler(owner)
    
    # Act
    conflicts = scheduler.detect_conflicts(scheduler.get_all_tasks())
    
    # Assert
    assert len(conflicts) == 0


def test_detect_conflicts_ignores_tasks_without_time_window():
    """Verify that tasks with no time_window are not included in conflicts."""
    # Arrange
    owner = Owner(name="Test Owner")
    pet = Pet(name="Max", animal="Dog", image="max.png")
    owner.add_pet(pet)
    
    today = date.today()
    
    task_no_time_1 = Task(
        title="Flexible Task 1",
        description="No time",
        duration=15,
        priority="low",
        time_window=None,
        occurrence_date=today,
    )
    task_no_time_2 = Task(
        title="Flexible Task 2",
        description="Also no time",
        duration=15,
        priority="low",
        time_window=None,
        occurrence_date=today,
    )
    
    pet.add_task(task_no_time_1)
    pet.add_task(task_no_time_2)
    
    scheduler = Scheduler(owner)
    
    # Act
    conflicts = scheduler.detect_conflicts(scheduler.get_all_tasks())
    
    # Assert: No conflicts because time_window is None
    assert len(conflicts) == 0


# =============================================================================
# TEST: Filtering by pet name and completion status
# =============================================================================

def test_filter_tasks_by_pet_name(sample_owner_with_pets):
    """Verify filtering tasks by pet name returns only that pet's tasks."""
    # Arrange
    owner, dog, cat = sample_owner_with_pets
    
    dog_task = Task(title="Walk", description="Dog walk", duration=30, priority="high")
    cat_task = Task(title="Feed", description="Cat food", duration=10, priority="medium")
    
    dog.add_task(dog_task)
    cat.add_task(cat_task)
    
    scheduler = Scheduler(owner)
    all_tasks = scheduler.get_all_tasks()
    
    # Act
    dog_tasks = scheduler.filter_tasks(all_tasks, pet_name="Buddy")
    
    # Assert
    assert len(dog_tasks) == 1
    assert dog_tasks[0] is dog_task


def test_filter_tasks_by_completion_status(sample_owner_with_pets):
    """Verify filtering by completion status works correctly."""
    # Arrange
    owner, dog, _ = sample_owner_with_pets
    
    completed_task = Task(title="Done Task", description="Completed", duration=10, priority="low")
    pending_task = Task(title="Pending Task", description="Not done", duration=10, priority="low")
    
    completed_task.mark_complete()
    
    dog.add_task(completed_task)
    dog.add_task(pending_task)
    
    scheduler = Scheduler(owner)
    all_tasks = scheduler.get_all_tasks()
    
    # Act
    only_pending = scheduler.filter_tasks(all_tasks, completed=False)
    only_completed = scheduler.filter_tasks(all_tasks, completed=True)
    
    # Assert
    assert len(only_pending) == 1
    assert only_pending[0] is pending_task
    assert len(only_completed) == 1
    assert only_completed[0] is completed_task


# =============================================================================
# TEST: Edge case - Pet with no tasks
# =============================================================================

def test_pet_with_no_tasks_does_not_break_scheduler():
    """Verify that an owner with a pet that has no tasks doesn't cause errors."""
    # Arrange
    owner = Owner(name="Test Owner")
    empty_pet = Pet(name="NewPet", animal="Hamster", image="hamster.png")
    owner.add_pet(empty_pet)
    
    scheduler = Scheduler(owner)
    
    # Act & Assert: These operations should not raise exceptions
    all_tasks = scheduler.get_all_tasks()
    assert all_tasks == []
    
    sorted_tasks = scheduler.sort_by_time(all_tasks)
    assert sorted_tasks == []
    
    conflicts = scheduler.detect_conflicts(all_tasks)
    assert conflicts == []
    
    filtered = scheduler.filter_tasks(all_tasks, pet_name="NewPet")
    assert filtered == []


# =============================================================================
# TEST: Priority-Based Scheduling (Challenge 3)
# =============================================================================

def test_sort_by_priority_high_before_medium_before_low():
    """Verify tasks are ordered High > Medium > Low, with time as tiebreaker."""
    owner = Owner(name="Test Owner")
    pet = Pet(name="Max", animal="Dog", image="max.png")
    owner.add_pet(pet)

    today = date.today()

    task_low = Task(
        title="Play", description="Ball", duration=15,
        priority="low", time_window="08:00", occurrence_date=today,
    )
    task_high = Task(
        title="Medication", description="Pill", duration=5,
        priority="high", time_window="12:00", occurrence_date=today,
    )
    task_medium = Task(
        title="Feed", description="Lunch", duration=10,
        priority="medium", time_window="10:00", occurrence_date=today,
    )

    pet.add_task(task_low)
    pet.add_task(task_high)
    pet.add_task(task_medium)

    scheduler = Scheduler(owner)
    result = scheduler.sort_by_priority(scheduler.get_all_tasks())

    assert result[0] is task_high
    assert result[1] is task_medium
    assert result[2] is task_low


def test_sort_by_priority_same_priority_sorts_by_time():
    """Within the same priority level, earlier times come first."""
    owner = Owner(name="Test Owner")
    pet = Pet(name="Max", animal="Dog", image="max.png")
    owner.add_pet(pet)

    today = date.today()

    task_late = Task(
        title="Walk", description="Evening", duration=30,
        priority="high", time_window="18:00", occurrence_date=today,
    )
    task_early = Task(
        title="Medication", description="Morning pill", duration=5,
        priority="high", time_window="07:00", occurrence_date=today,
    )

    pet.add_task(task_late)
    pet.add_task(task_early)

    scheduler = Scheduler(owner)
    result = scheduler.sort_by_priority(scheduler.get_all_tasks())

    assert result[0] is task_early
    assert result[1] is task_late


# =============================================================================
# TEST: Priority emojis and task-type icons (Challenge 3 / 4)
# =============================================================================

def test_priority_emoji_mapping():
    """Verify the PRIORITY_EMOJI dict contains the expected symbols."""
    assert PRIORITY_EMOJI["high"] == "🔴"
    assert PRIORITY_EMOJI["medium"] == "🟡"
    assert PRIORITY_EMOJI["low"] == "🟢"


def test_task_type_icon_known_titles():
    """Known task titles should return their specific emoji."""
    assert task_type_icon("Walk") == "🚶"
    assert task_type_icon("feed") == "🍽️"
    assert task_type_icon("MEDICATION") == "💊"
    assert task_type_icon("Groom") == "✂️"
    assert task_type_icon("Play") == "🎾"


def test_task_type_icon_unknown_title_returns_paw():
    """Unknown task titles should fall back to the paw emoji."""
    assert task_type_icon("CustomStuff") == "🐾"


# =============================================================================
# TEST: Daily tasks by date
# =============================================================================

def test_get_daily_tasks_returns_only_tasks_for_specified_date():
    """Verify that get_daily_tasks filters by the correct date."""
    # Arrange
    pet = Pet(name="Max", animal="Dog", image="max.png")
    
    today = date.today()
    tomorrow = today + timedelta(days=1)
    
    today_task = Task(
        title="Today Task",
        description="Due today",
        duration=15,
        priority="high",
        occurrence_date=today,
    )
    tomorrow_task = Task(
        title="Tomorrow Task",
        description="Due tomorrow",
        duration=15,
        priority="high",
        occurrence_date=tomorrow,
    )
    
    pet.add_task(today_task)
    pet.add_task(tomorrow_task)
    
    # Act
    daily_tasks = pet.get_daily_tasks(today)
    
    # Assert
    assert len(daily_tasks) == 1
    assert daily_tasks[0] is today_task
