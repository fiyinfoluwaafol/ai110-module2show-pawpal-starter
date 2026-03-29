import streamlit as st
from datetime import date

from pawpal_system import Owner, Pet, Scheduler, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

if "owner" not in st.session_state:
    st.session_state.owner = Owner("User")

owner = st.session_state.owner

st.sidebar.subheader("Owner")
owner_name = st.sidebar.text_input("Owner name", value=owner.name, key="owner_name_input")
if owner_name != owner.name:
    owner.name = owner_name
    st.session_state.owner = owner

st.divider()

st.subheader("Add a pet")
with st.form("add_pet_form"):
    pet_name = st.text_input("Pet name")
    species = st.selectbox("Species", ["dog", "cat", "other"])
    pet_image = st.text_input("Image (URL or emoji)", value="🐾")
    add_pet_submitted = st.form_submit_button("Add pet")

if add_pet_submitted:
    if not pet_name.strip():
        st.error("Please enter a pet name.")
    else:
        pet = Pet(name=pet_name.strip(), animal=species, image=pet_image or "🐾")
        owner.add_pet(pet)
        st.session_state.owner = owner
        st.rerun()

st.subheader("Add a task")
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
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
        priority = st.selectbox("Priority", ["high", "medium", "low"], index=1)
        frequency = st.selectbox(
            "Frequency",
            ["one-off", "daily", "weekly"],
            format_func=lambda x: {"one-off": "One-off (none)", "daily": "Daily", "weekly": "Weekly"}[x],
        )
        freq_value = None if frequency == "one-off" else frequency
        add_task_submitted = st.form_submit_button("Add task")

    if add_task_submitted:
        pet = pet_labels[selected_pet_name]
        task = Task(
            title=task_title.strip() or "Task",
            description=task_description.strip() or task_title.strip() or "—",
            duration=int(duration),
            priority=priority,
            time_window=time_str.strip() or None,
            completed=False,
            occurrence_date=date.today(),
            frequency=freq_value,
        )
        pet.add_task(task)
        st.session_state.owner = owner
        st.rerun()

st.divider()

st.subheader("All tasks")
scheduler = Scheduler(owner)
all_tasks = scheduler.get_all_tasks()
conflicts = scheduler.detect_conflicts(all_tasks)
if conflicts:
    st.warning(
        "Scheduling conflict: two or more tasks share the same date and time. "
        "Review the table below."
    )

if not all_tasks:
    st.info("No tasks yet.")
else:
    rows = []
    for p in owner.get_pets():
        for t in p.get_tasks():
            rows.append(
                {
                    "Pet": p.name,
                    "Time": t.time_window or "—",
                    "Title": t.title,
                    "Description": t.description,
                    "Done": "Yes" if t.completed else "No",
                    "Priority": t.priority,
                    "Frequency": t.frequency or "one-off",
                }
            )
    rows.sort(key=lambda r: (r["Time"] == "—", r["Time"]))
    st.dataframe(rows, use_container_width=True, hide_index=True)

st.divider()

st.subheader("Daily plan")
plan_date = st.date_input("Date", value=date.today())
if st.button("Generate daily plan"):
    scheduler.generate_daily_plan(plan_date)
    st.session_state.owner = owner
    st.text(scheduler.explain_plan())
