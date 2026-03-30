import streamlit as st
from datetime import date

from pawpal_system import Owner, Pet, Scheduler, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

# ── Custom CSS ────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
/* Streamlit 1.47+ uses Material Symbols Rounded for UI icons (expanders, etc.) */
@import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@24,400,0,0');
@import url('https://fonts.googleapis.com/icon?family=Material+Icons');

:root {
    --accent: #6C5CE7;
    --accent-light: #A29BFE;
    --success: #00B894;
    --warning: #FDCB6E;
    --danger: #E17055;
    --bg: #FAFAFA;
    --card-bg: #FFFFFF;
    --text: #2D3436;
    --text-muted: #636E72;
    --border: #E8E8E8;
    --shadow: 0 1px 3px rgba(0,0,0,0.04), 0 1px 2px rgba(0,0,0,0.06);
}

/*
 * Scope Inter to app text only. Do NOT use [class*="st-"] — it matches
 * Streamlit's "st-emotion-cache-*" classes on icon spans and forces Inter,
 * which breaks ligatures (you see "keyboard_arrow_down" as plain text).
 */
.stApp .main .block-container,
.stApp [data-testid="stSidebar"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

/* Streamlit's built-in icons (expander chevrons, etc.) — theme uses Material Symbols Rounded */
[data-testid="stIconMaterial"] {
    font-family: "Material Symbols Rounded", sans-serif !important;
    font-variation-settings: "FILL" 0, "wght" 400, "GRAD" 0, "opsz" 24 !important;
    font-style: normal !important;
    font-weight: 400 !important;
    letter-spacing: normal !important;
    text-transform: none !important;
    white-space: nowrap !important;
    -webkit-font-smoothing: antialiased !important;
}

.material-icons {
    font-family: "Material Icons", sans-serif !important;
}
.material-symbols-outlined,
.material-symbols-rounded,
[class*="material-symbols"] {
    font-family: "Material Symbols Rounded", sans-serif !important;
    font-variation-settings: "FILL" 0, "wght" 400, "GRAD" 0, "opsz" 24 !important;
}

.block-container {
    max-width: 740px !important;
    padding-top: 2rem !important;
}

/* Header */
.hero-header {
    text-align: center;
    padding: 1.5rem 0 0.5rem;
}
.hero-header h1 {
    font-size: 2.2rem;
    font-weight: 700;
    color: var(--text);
    margin: 0;
    letter-spacing: -0.5px;
}
.hero-header p {
    color: var(--text-muted);
    font-size: 0.95rem;
    margin-top: 0.3rem;
}

/* Section headers */
.section-header {
    font-size: 1.1rem;
    font-weight: 600;
    color: var(--text);
    margin: 1.5rem 0 0.6rem;
    padding-bottom: 0.4rem;
    border-bottom: 2px solid var(--accent-light);
    display: inline-block;
}

/* Pet cards */
.pet-grid {
    display: flex;
    flex-wrap: wrap;
    gap: 0.75rem;
    margin: 0.5rem 0 1rem;
}
.pet-card {
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 0.8rem 1rem;
    display: flex;
    align-items: center;
    gap: 0.6rem;
    box-shadow: var(--shadow);
    min-width: 140px;
    transition: transform 0.15s ease, box-shadow 0.15s ease;
}
.pet-card:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
}
.pet-card .pet-emoji {
    font-size: 1.8rem;
    line-height: 1;
}
.pet-card .pet-info {
    display: flex;
    flex-direction: column;
}
.pet-card .pet-name {
    font-weight: 600;
    font-size: 0.95rem;
    color: var(--text);
}
.pet-card .pet-species {
    font-size: 0.78rem;
    color: var(--text-muted);
    text-transform: capitalize;
}

/* Task cards */
.task-card {
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 0.85rem 1rem;
    margin-bottom: 0.5rem;
    box-shadow: var(--shadow);
    display: flex;
    align-items: flex-start;
    gap: 0.75rem;
    transition: transform 0.15s ease;
}
.task-card:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
}
.task-card.done {
    opacity: 0.55;
}
.task-time {
    background: #F0EFFF;
    color: var(--accent);
    font-weight: 600;
    font-size: 0.8rem;
    padding: 0.25rem 0.5rem;
    border-radius: 6px;
    white-space: nowrap;
    min-width: 50px;
    text-align: center;
    margin-top: 2px;
}
.task-body {
    flex: 1;
    min-width: 0;
}
.task-title {
    font-weight: 600;
    font-size: 0.9rem;
    color: var(--text);
    margin-bottom: 0.15rem;
}
.task-desc {
    font-size: 0.82rem;
    color: var(--text-muted);
    margin-bottom: 0.35rem;
}
.task-meta {
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
    align-items: center;
}

/* Badges */
.badge {
    font-size: 0.7rem;
    font-weight: 600;
    padding: 0.15rem 0.45rem;
    border-radius: 4px;
    text-transform: uppercase;
    letter-spacing: 0.3px;
}
.badge-high { background: #FFEAEA; color: #C0392B; }
.badge-medium { background: #FFF5E0; color: #E67E22; }
.badge-low { background: #E8F8F0; color: #27AE60; }
.badge-pet { background: #F0EFFF; color: var(--accent); }
.badge-freq { background: #E8F4FD; color: #2980B9; }
.badge-done { background: #E8F8F0; color: var(--success); }
.badge-pending { background: #FFF5E0; color: #E67E22; }

/* Progress bar */
.progress-wrap {
    margin: 0.75rem 0;
}
.progress-bar-bg {
    background: var(--border);
    border-radius: 6px;
    height: 8px;
    overflow: hidden;
}
.progress-bar-fill {
    background: linear-gradient(90deg, var(--accent), var(--accent-light));
    height: 100%;
    border-radius: 6px;
    transition: width 0.4s ease;
}
.progress-label {
    font-size: 0.8rem;
    color: var(--text-muted);
    margin-top: 0.25rem;
}

/* Conflict banner */
.conflict-banner {
    background: #FFF8E1;
    border: 1px solid #FFE082;
    border-left: 4px solid #FFA000;
    border-radius: 8px;
    padding: 0.7rem 1rem;
    margin-bottom: 0.5rem;
    font-size: 0.85rem;
    color: #5D4037;
}

/* Empty state */
.empty-state {
    text-align: center;
    padding: 2rem 1rem;
    color: var(--text-muted);
}
.empty-state .empty-icon {
    font-size: 2.5rem;
    margin-bottom: 0.5rem;
}
.empty-state p {
    font-size: 0.9rem;
    margin: 0;
}

/* Sidebar polish */
section[data-testid="stSidebar"] {
    background: #FAFAFF;
    border-right: 1px solid var(--border);
}
section[data-testid="stSidebar"] .block-container {
    padding-top: 1.5rem;
}

/* Form / input overrides */
.stTextInput > div > div > input,
.stSelectbox > div > div,
.stTextArea textarea {
    border-radius: 8px !important;
    border: 1px solid var(--border) !important;
    font-size: 0.9rem !important;
}
.stTextInput > div > div > input:focus,
.stTextArea textarea:focus {
    border-color: var(--accent-light) !important;
    box-shadow: 0 0 0 2px rgba(108,92,231,0.12) !important;
}

/* Buttons */
.stButton > button {
    border-radius: 8px;
    font-weight: 600;
    font-size: 0.85rem;
    padding: 0.45rem 1.2rem;
    transition: all 0.15s ease;
}
button[kind="primaryFormSubmit"], .stButton > button[kind="primary"] {
    background: var(--accent) !important;
    border: none !important;
    color: #fff !important;
}

/* Hide default Streamlit decoration */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* Expander polish */
.streamlit-expanderHeader {
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    color: var(--text) !important;
}

/* Dividers */
hr {
    border: none;
    border-top: 1px solid var(--border);
    margin: 1rem 0;
}
</style>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────
if "owner" not in st.session_state:
    st.session_state.owner = Owner("User")

owner: Owner = st.session_state.owner
scheduler = Scheduler(owner)

# ── Sidebar ───────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("#### 👤 Owner Profile")
    owner_name = st.text_input(
        "Your name", value=owner.name, key="owner_name_input",
        label_visibility="collapsed", placeholder="Enter your name…"
    )
    if owner_name != owner.name:
        owner.name = owner_name

    st.markdown("---")

    pets = owner.get_pets()
    st.markdown(f"**🐾 Your Pets** ({len(pets)})")
    if pets:
        for p in pets:
            st.markdown(f"&ensp;{p.image}&ensp; **{p.name}** · {p.animal}")
    else:
        st.caption("No pets yet — add one below!")

    st.markdown("---")

    all_tasks_sidebar = scheduler.get_all_tasks()
    done_count = sum(1 for t in all_tasks_sidebar if t.completed)
    total_count = len(all_tasks_sidebar)
    st.markdown(f"**📋 Tasks** {done_count}/{total_count} done")
    if total_count > 0:
        pct = int(done_count / total_count * 100)
        st.markdown(f"""
        <div class="progress-wrap">
            <div class="progress-bar-bg"><div class="progress-bar-fill" style="width:{pct}%"></div></div>
            <div class="progress-label">{pct}% complete</div>
        </div>
        """, unsafe_allow_html=True)

# ── Hero header ───────────────────────────────────────────────────────
st.markdown("""
<div class="hero-header">
    <h1>🐾 PawPal+</h1>
    <p>Keep your pets happy, healthy, and on schedule.</p>
</div>
""", unsafe_allow_html=True)

# ── Pet gallery ───────────────────────────────────────────────────────
pets = owner.get_pets()
if pets:
    cards_html = "".join(
        f"""<div class="pet-card">
            <span class="pet-emoji">{p.image}</span>
            <div class="pet-info">
                <span class="pet-name">{p.name}</span>
                <span class="pet-species">{p.animal} · {len(p.get_tasks())} tasks</span>
            </div>
        </div>"""
        for p in pets
    )
    st.markdown(f'<div class="pet-grid">{cards_html}</div>', unsafe_allow_html=True)

# ── Add a pet ─────────────────────────────────────────────────────────
with st.expander("➕ Add a Pet", expanded=not pets):
    with st.form("add_pet_form"):
        c1, c2 = st.columns([2, 1])
        with c1:
            pet_name = st.text_input("Pet name", placeholder="e.g. Buddy")
        with c2:
            species = st.selectbox("Species", ["dog", "cat", "other"])
        pet_image = st.text_input("Icon (emoji or URL)", value="🐾")
        add_pet_submitted = st.form_submit_button("Add pet", use_container_width=True)

    if add_pet_submitted:
        if not pet_name.strip():
            st.error("Please enter a pet name.")
        else:
            owner.add_pet(
                Pet(name=pet_name.strip(), animal=species, image=pet_image or "🐾")
            )
            st.rerun()

# ── Add a task ────────────────────────────────────────────────────────
with st.expander("➕ Add a Task", expanded=False):
    pets = owner.get_pets()
    if not pets:
        st.caption("Add a pet first, then you can assign tasks.")
    else:
        pet_labels = {p.name: p for p in pets}
        with st.form("add_task_form"):
            row1_c1, row1_c2 = st.columns(2)
            with row1_c1:
                selected_pet_name = st.selectbox("Pet", list(pet_labels.keys()))
            with row1_c2:
                task_title = st.text_input("Task title", placeholder="e.g. Walk")
            task_description = st.text_area("Description", height=68, placeholder="Optional details…")
            row2_c1, row2_c2, row2_c3 = st.columns(3)
            with row2_c1:
                time_str = st.text_input("Time (HH:MM)", value="09:00")
            with row2_c2:
                duration = st.number_input("Minutes", min_value=1, max_value=240, value=20)
            with row2_c3:
                priority = st.selectbox("Priority", ["high", "medium", "low"], index=1)
            frequency = st.selectbox(
                "Frequency",
                ["one-off", "daily", "weekly"],
                format_func=lambda x: {"one-off": "One-off", "daily": "Daily", "weekly": "Weekly"}[x],
            )
            freq_value = None if frequency == "one-off" else frequency
            add_task_submitted = st.form_submit_button("Add task", use_container_width=True)

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

st.markdown("---")

# ── Task Schedule ─────────────────────────────────────────────────────
st.markdown('<div class="section-header">📅 Task Schedule</div>', unsafe_allow_html=True)

all_tasks = scheduler.get_all_tasks()

if not all_tasks:
    st.markdown("""
    <div class="empty-state">
        <div class="empty-icon">📭</div>
        <p>No tasks yet. Add a pet and some tasks to get started.</p>
    </div>
    """, unsafe_allow_html=True)
else:
    _task_pet: dict[int, str] = {}
    for p in owner.get_pets():
        for t in p.get_tasks():
            _task_pet[id(t)] = p.name

    conflicts = scheduler.detect_conflicts(all_tasks)
    if conflicts:
        for group in conflicts:
            slot = group[0].time_window
            day = group[0].occurrence_date.strftime("%b %d, %Y")
            details = ", ".join(
                f"<b>{_task_pet.get(id(t), '?')}</b>'s {t.title}" for t in group
            )
            st.markdown(
                f'<div class="conflict-banner">⚠️ Overlap at <b>{slot}</b> on {day} — {details}. Consider rescheduling.</div>',
                unsafe_allow_html=True,
            )

    col1, col2 = st.columns(2)
    pet_names = ["All Pets"] + [p.name for p in owner.get_pets()]
    with col1:
        filter_pet = st.selectbox("Filter by pet", pet_names, key="filter_pet", label_visibility="collapsed")
    with col2:
        filter_status = st.selectbox(
            "Filter by status",
            ["All", "Incomplete", "Completed"],
            key="filter_status",
            label_visibility="collapsed",
        )

    pet_arg = None if filter_pet == "All Pets" else filter_pet
    completed_arg = (
        None if filter_status == "All" else (filter_status == "Completed")
    )

    visible_tasks = scheduler.filter_tasks(all_tasks, completed=completed_arg, pet_name=pet_arg)
    visible_tasks = scheduler.sort_by_time(visible_tasks)

    if not visible_tasks:
        st.caption("No tasks match the current filters.")
    else:
        done = sum(1 for t in visible_tasks if t.completed)
        total = len(visible_tasks)
        pct = int(done / total * 100) if total else 0
        st.markdown(f"""
        <div class="progress-wrap">
            <div class="progress-bar-bg"><div class="progress-bar-fill" style="width:{pct}%"></div></div>
            <div class="progress-label">{done} of {total} tasks complete ({pct}%)</div>
        </div>
        """, unsafe_allow_html=True)

        for t in visible_tasks:
            pet_name_for_task = _task_pet.get(id(t), "Unknown")
            done_class = " done" if t.completed else ""
            time_display = t.time_window or "—"
            priority_class = f"badge-{t.priority}"
            status_badge = (
                '<span class="badge badge-done">✓ Done</span>'
                if t.completed
                else '<span class="badge badge-pending">Pending</span>'
            )
            freq_badge = (
                f'<span class="badge badge-freq">{t.frequency}</span>'
                if t.frequency
                else ""
            )
            st.markdown(f"""
            <div class="task-card{done_class}">
                <div class="task-time">{time_display}</div>
                <div class="task-body">
                    <div class="task-title">{t.title}</div>
                    <div class="task-desc">{t.description}</div>
                    <div class="task-meta">
                        <span class="badge badge-pet">{pet_name_for_task}</span>
                        <span class="badge {priority_class}">{t.priority}</span>
                        {status_badge}
                        {freq_badge}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    # ── Mark a task complete ──────────────────────────────────────────
    st.markdown('<div class="section-header">✅ Mark Complete</div>', unsafe_allow_html=True)
    pending = [t for t in visible_tasks if not t.completed] if visible_tasks else []
    if not pending:
        st.caption("All caught up — no pending tasks!")
    else:
        task_options = {
            f"{_task_pet.get(id(t), '?')} — {t.title} @ {t.time_window or 'no time'}": t
            for t in pending
        }
        chosen = st.selectbox(
            "Select a task", list(task_options.keys()), key="complete_task",
            label_visibility="collapsed",
        )
        if st.button("Mark complete", use_container_width=True):
            scheduler.mark_task_complete(task_options[chosen])
            st.rerun()

st.markdown("---")

# ── Daily Plan ────────────────────────────────────────────────────────
with st.expander("🗓️ Daily Plan"):
    plan_date = st.date_input("Date", value=date.today())
    if st.button("Generate daily plan", use_container_width=True):
        scheduler.generate_daily_plan(plan_date)
        plan_text = scheduler.explain_plan()
        if "No plan" in plan_text:
            st.caption("No tasks scheduled for this date.")
        else:
            st.code(plan_text, language=None)
