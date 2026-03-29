import streamlit as st
from datetime import date

from pawpal_system import Owner, Pet, Scheduler, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

# ── Session state ────────────────────────────────────────────────────
if "owner" not in st.session_state:
    st.session_state.owner = Owner("User")

owner: Owner = st.session_state.owner
scheduler = Scheduler(owner)

# ── Sidebar: owner name ─────────────────────────────────────────────
st.sidebar.subheader("Owner")
owner_name = st.sidebar.text_input(
    "Owner name", value=owner.name, key="owner_name_input"
)
if owner_name != owner.name:
    owner.name = owner_name

st.divider()

# ── Add a pet ────────────────────────────────────────────────────────
st.subheader("Add a Pet")
with st.form("add_pet_form"):
    pet_name = st.text_input("Pet name")
    species = st.selectbox("Species", ["dog", "cat", "other"])
    pet_image = st.text_input("Image (URL or emoji)", value="🐾")
    add_pet_submitted = st.form_submit_button("Add pet")

if add_pet_submitted:
    if not pet_name.strip():
        st.error("Please enter a pet name.")
    else:
        owner.add_pet(
            Pet(name=pet_name.strip(), animal=species, image=pet_image or "🐾")
        )
        st.rerun()

# ── Add a task ───────────────────────────────────────────────────────
st.subheader("Add a Task")
pets = owner.get_pets()
if not pets:
    st.info("Add a pet first, then you can assign tasks.")
else:
    pet_labels = {p.name: p for p in pets}
    with st.form("add_task_form"):
        selected_pet_name = st.selectbox("Pet", list(pet_labels.keys()))
        task_title = st.text_input("Task title", value="Care task")
        task_description = st.text_area("Description", value="")
        time_str = st.text_input("Time (HH:MM)", value="09:00")
        duration = st.number_input(
            "Duration (minutes)", min_value=1, max_value=240, value=20
        )
        priority = st.selectbox("Priority", ["high", "medium", "low"], index=1)
        frequency = st.selectbox(
            "Frequency",
            ["one-off", "daily", "weekly"],
            format_func=lambda x: {
                "one-off": "One-off",
                "daily": "Daily",
                "weekly": "Weekly",
            }[x],
        )
        freq_value = None if frequency == "one-off" else frequency
        add_task_submitted = st.form_submit_button("Add task")

    if add_task_submitted:
        pet = pet_labels[selected_pet_name]
        pet.add_task(
            Task(
                title=task_title.strip() or "Task",
                description=task_description.strip() or task_title.strip() or "—",
                duration=int(duration),
                priority=priority,
                time_window=time_str.strip() or None,
                completed=False,
                occurrence_date=date.today(),
                frequency=freq_value,
            )
        )
        st.rerun()

st.divider()

# ── Task Schedule (Scheduler-driven) ────────────────────────────────
st.subheader("Task Schedule")

all_tasks = scheduler.get_all_tasks()

if not all_tasks:
    st.info("No tasks yet. Add a pet and some tasks to get started.")
else:
    # Build a task → pet-name lookup so every display row can show the pet
    _task_pet: dict[int, str] = {}
    for p in owner.get_pets():
        for t in p.get_tasks():
            _task_pet[id(t)] = p.name

    # ── Conflict detection (runs on the full unfiltered set) ─────
    conflicts = scheduler.detect_conflicts(all_tasks)
    if conflicts:
        for group in conflicts:
            slot = group[0].time_window
            day = group[0].occurrence_date.strftime("%b %d, %Y")
            details = ", ".join(
                f"{_task_pet.get(id(t), '?')}'s {t.title}" for t in group
            )
            st.warning(
                f"You have overlapping tasks at **{slot}** on {day} — {details}. "
                "Consider rescheduling one of them."
            )

    # ── Filter controls ──────────────────────────────────────────
    col1, col2 = st.columns(2)
    pet_names = ["All Pets"] + [p.name for p in owner.get_pets()]
    with col1:
        filter_pet = st.selectbox("Filter by pet", pet_names, key="filter_pet")
    with col2:
        filter_status = st.selectbox(
            "Filter by status",
            ["All", "Incomplete", "Completed"],
            key="filter_status",
        )

    # Translate UI selections into Scheduler.filter_tasks() args
    pet_arg = None if filter_pet == "All Pets" else filter_pet
    completed_arg = (
        None
        if filter_status == "All"
        else (filter_status == "Completed")
    )

    # Filter then sort — both via Scheduler methods
    visible_tasks = scheduler.filter_tasks(
        all_tasks, completed=completed_arg, pet_name=pet_arg
    )
    visible_tasks = scheduler.sort_by_time(visible_tasks)

    if not visible_tasks:
        st.caption("No tasks match the current filters.")
    else:
        rows = [
            {
                "Time": t.time_window or "—",
                "Pet": _task_pet.get(id(t), "Unknown"),
                "Task": f"{t.title}: {t.description}",
                "Priority": t.priority.capitalize(),
                "Status": "✅ Done" if t.completed else "⏳ Pending",
                "Frequency": (t.frequency or "one-off").capitalize(),
            }
            for t in visible_tasks
        ]
        st.dataframe(rows, use_container_width=True, hide_index=True)

        # Completion summary
        done = sum(1 for t in visible_tasks if t.completed)
        total = len(visible_tasks)
        if done == total:
            st.success(f"All {total} task(s) completed!")
        elif done > 0:
            st.info(f"{done} of {total} task(s) completed.")

    # ── Mark a task complete (supports recurring via Scheduler) ──
    st.divider()
    st.subheader("Mark a Task Complete")
    pending = [t for t in visible_tasks if not t.completed] if visible_tasks else []
    if not pending:
        st.caption("No pending tasks to mark complete.")
    else:
        task_options = {
            f"{_task_pet.get(id(t), '?')} — {t.title} @ {t.time_window or 'no time'}": t
            for t in pending
        }
        chosen = st.selectbox(
            "Select a task", list(task_options.keys()), key="complete_task"
        )
        if st.button("Mark complete"):
            scheduler.mark_task_complete(task_options[chosen])
            st.rerun()

st.divider()

# ── Daily Plan ───────────────────────────────────────────────────────
st.subheader("Daily Plan")
plan_date = st.date_input("Date", value=date.today())
if st.button("Generate daily plan"):
    scheduler.generate_daily_plan(plan_date)
    plan_text = scheduler.explain_plan()
    if "No plan" in plan_text:
        st.caption("No tasks scheduled for this date.")
    else:
        st.text(plan_text)
