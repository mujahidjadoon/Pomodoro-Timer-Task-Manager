import streamlit as st
import time
from datetime import timedelta
import random

# --- Configuration ---
WORK_TIME = 25 * 60
SHORT_BREAK = 5 * 60
LONG_BREAK = 15 * 60
POMODOROS_FOR_LONG_BREAK = 4

# --- State Initialization ---
if 'mode' not in st.session_state:
    st.session_state.mode = 'work'
if 'time_left' not in st.session_state:
    st.session_state.time_left = WORK_TIME
if 'is_running' not in st.session_state:
    st.session_state.is_running = False
if 'tasks' not in st.session_state:
    st.session_state.tasks = [
        {'id': 1, 'text': 'Complete project documentation', 'completed': False},
        {'id': 2, 'text': 'Review pull requests', 'completed': False}
    ]
if 'completed_pomodoros' not in st.session_state:
    st.session_state.completed_pomodoros = 0
if 'new_task_input' not in st.session_state:
    st.session_state.new_task_input = ""


# --- Timer Logic Functions ---

def get_mode_details(mode):
    """Returns duration and label for a given mode."""
    modes = {
        'work': {'duration': WORK_TIME, 'label': 'Focus Time'},
        'short_break': {'duration': SHORT_BREAK, 'label': 'Short Break'},
        'long_break': {'duration': LONG_BREAK, 'label': 'Long Break'}
    }
    return modes.get(mode, modes['work'])


def format_time(seconds):
    """Formats seconds into MM:SS string."""
    return str(timedelta(seconds=seconds))[2:]


def switch_mode(new_mode):
    """Switches the timer mode and resets the timer state."""
    st.session_state.mode = new_mode
    st.session_state.time_left = get_mode_details(new_mode)['duration']
    st.session_state.is_running = False


def switch_mode_callback(new_mode):
    """Callback for mode buttons: switches mode and stops timer."""
    switch_mode(new_mode)


def toggle_timer():
    """Starts or pauses the timer."""
    st.session_state.is_running = not st.session_state.is_running


def reset_timer():
    """Resets the timer to the current mode's default duration."""
    st.session_state.is_running = False
    st.session_state.time_left = get_mode_details(st.session_state.mode)['duration']


def run_timer(timer_placeholder):
    """Handles the main countdown logic."""

    # Core countdown logic
    if st.session_state.is_running and st.session_state.time_left > 0:
        st.session_state.time_left -= 1

        # Display the updated time in the placeholder
        with timer_placeholder.container():
            mode_info = get_mode_details(st.session_state.mode)
            progress_value = (mode_info['duration'] - st.session_state.time_left) / mode_info['duration']
            st.markdown(f"""
                <h1 style='font-size: 80px; text-align: center; margin: 0;'>{format_time(st.session_state.time_left)}</h1>
            """, unsafe_allow_html=True)
            st.progress(progress_value)

        time.sleep(1)  # Wait 1 second
        st.rerun()  # Rerun to continue the countdown

    # Mode switch logic when timer hits zero
    elif st.session_state.time_left <= 0 and st.session_state.is_running:
        st.session_state.is_running = False  # Stop the timer

        if st.session_state.mode == 'work':
            st.session_state.completed_pomodoros += 1

            if st.session_state.completed_pomodoros % POMODOROS_FOR_LONG_BREAK == 0:
                next_mode = 'long_break'
                st.toast("Time for a LONG Break! ☕", icon='🎉')
            else:
                next_mode = 'short_break'
                st.toast("Time for a Short Break! 🚶", icon='🔔')
        else:  # break is over
            next_mode = 'work'
            st.toast("Break is over! Back to work. 📚", icon='🔔')

        switch_mode(next_mode)
        st.rerun()  # Immediate re-run to update the Pomodoro counter and mode UI


# --- Task Management Functions ---

def add_task():
    """Adds a new task from the input box."""
    if st.session_state.new_task_input.strip():
        new_task = {
            'id': random.randint(1000, 9999),
            'text': st.session_state.new_task_input,
            'completed': False
        }
        st.session_state.tasks.append(new_task)
        st.session_state.new_task_input = ""  # Clear input


def toggle_task(task_id):
    """Toggles the completion status of a task."""
    for task in st.session_state.tasks:
        if task['id'] == task_id:
            task['completed'] = not task['completed']
            break


def delete_task(task_id):
    """Deletes a task by ID."""
    st.session_state.tasks = [task for task in st.session_state.tasks if task['id'] != task_id]


# --- Streamlit UI Layout ---

st.set_page_config(layout="wide", page_title="Pomodoro Focus Timer")

# Custom CSS for styling
st.markdown("""
<style>
.stApp {
    background-color: #0F172A;
    color: white;
}
h1 {
    color: white;
}
/* Style Streamlit buttons to be more circular/interactive */
.stButton>button {
    border-radius: 9999px !important; 
    border: none !important;
    background-color: #6D28D9;
    color: white;
    font-size: 18px;
    font-weight: bold;
    padding: 15px 30px;
    transition: all 0.2s;
}
.stButton>button:hover {
    background-color: #7C3AED;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}
.mode-button-style {
    color: white;
    font-weight: bold;
    border-radius: 8px;
    padding: 10px 15px;
    margin-right: 5px;
    cursor: pointer;
    transition: background-color 0.3s;
}
</style>
""", unsafe_allow_html=True)

st.title("⏱️ Pomodoro Focus Timer")
st.markdown("---")

col1, col2 = st.columns([1, 1])

# --- Timer Panel (Column 1) ---
with col1:
    current_mode = st.session_state.mode
    mode_info = get_mode_details(current_mode)

    # Dynamic Subheader
    st.markdown(f"## 🟢 {mode_info['label']}")

    # Mode Switch Buttons
    mode_cols = st.columns(3)

    mode_cols[0].button(
        "Work",
        on_click=switch_mode_callback,
        args=('work',),
        key='btn_work',
        type="primary" if current_mode == 'work' else "secondary",
        help="25 minutes focus",
    )
    mode_cols[1].button(
        "Short Break",
        on_click=switch_mode_callback,
        args=('short_break',),
        key='btn_short',
        type="primary" if current_mode == 'short_break' else "secondary",
        help="5 minutes break",
    )
    mode_cols[2].button(
        "Long Break",
        on_click=switch_mode_callback,
        args=('long_break',),
        key='btn_long',
        type="primary" if current_mode == 'long_break' else "secondary",
        help="15 minutes break",
    )

    st.markdown("---")

    # Placeholder for dynamic timer and progress updates
    timer_placeholder = st.empty()

    # --- FIX: Ensure Display Outside of Dynamic Loop When Paused ---
    if not st.session_state.is_running:
        with timer_placeholder.container():
            mode_info = get_mode_details(st.session_state.mode)
            progress_value = (mode_info['duration'] - st.session_state.time_left) / mode_info['duration']
            # FIX WAS HERE: Added closing parenthesis to st.markdown() call
            st.markdown(f"""
                <h1 style='font-size: 80px; text-align: center; margin: 0;'>{format_time(st.session_state.time_left)}</h1>
            """, unsafe_allow_html=True)
            st.progress(progress_value)

    # Control Buttons
    control_cols = st.columns(2)
    with control_cols[0]:
        st.button(
            '⏸️ PAUSE' if st.session_state.is_running else '▶️ START',
            on_click=toggle_timer,
            use_container_width=True,
            key='btn_toggle'
        )
    with control_cols[1]:
        st.button(
            '🔄 RESET',
            on_click=reset_timer,
            use_container_width=True,
            key='btn_reset'
        )

    st.markdown("---")
    st.metric(
        label="Pomodoros Completed Today 🍅",
        value=st.session_state.completed_pomodoros,
        delta_color="off"
    )

# --- Task Manager Panel (Column 2) ---
with col2:
    st.subheader("📋 Task Manager")

    # Add New Task Input
    st.text_input(
        "Add a new task:",
        key="new_task_input",
        on_change=add_task,
        placeholder="e.g., Finish Streamlit implementation"
    )

    st.markdown("---")

    # Task List
    if st.session_state.tasks:
        for task in st.session_state.tasks:
            task_container = st.container(border=False)
            task_col_check, task_col_text, task_col_del = task_container.columns([1, 6, 1])

            # Checkbox
            task_col_check.checkbox(
                label="",
                value=task['completed'],
                key=f"check_{task['id']}",
                on_change=toggle_task,
                args=(task['id'],),
                label_visibility="collapsed"
            )

            # Task Text
            text_style = "text-decoration: line-through; opacity: 0.6;" if task['completed'] else ""
            task_col_text.markdown(f"<span style='{text_style}'>{task['text']}</span>", unsafe_allow_html=True)

            # Delete Button
            task_col_del.button(
                '🗑️',
                key=f"del_{task['id']}",
                on_click=delete_task,
                args=(task['id'],),
                help="Delete Task"
            )
    else:
        st.info("No tasks yet. Add one to get started!")

# --- Run Timer Loop ---
run_timer(timer_placeholder)