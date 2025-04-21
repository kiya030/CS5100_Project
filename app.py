import streamlit as st
import pandas as pd
import plotly.express as px
from ver3 import load_schedule_data, solve_schedule  # Import backend functions

# -------------------------- 1) FRONT-END STRUCTURE --------------------------
st.set_page_config(page_title="Course Scheduling System", layout="wide")

# Sidebar: Data Input
with st.sidebar:
    st.header("📥 Data Input")
    uploaded_file = st.file_uploader("Upload your CSV file here")
    if uploaded_file:
        try:
            df = pd.read_csv(uploaded_file)
            st.success("File uploaded successfully!")
        except Exception as e:
            st.error(f"Error reading the uploaded file: {e}")
            df = None

# Main Page: Constraint Configuration
st.title("Course Scheduling System")
with st.expander("⚙️ Advanced Constraint Configuration"):
    tab1, tab2 = st.tabs(["Hard Constraints", "Soft Constraints"])
    
    # Hard Constraints
    with tab1:
        prevent_teacher_conflicts = st.checkbox("Prevent Teacher Time Conflicts", True, help="A teacher cannot teach two courses at the same time.")
        room_time_conflicts = st.checkbox("No Two Courses in the Same Room at the Same Time", True, help="Ensure no two courses are scheduled in the same room at the same time.")
        room_capacity_limit = st.checkbox("Room Capacity Constraint", True, help="Ensure the number of students does not exceed the room capacity.")
        teacher_availability = st.checkbox("Teacher Availability", True, help="Ensure courses are scheduled during the teacher's available times.")
        course_preferred_times = st.checkbox("Course Preferred Times", True, help="Ensure courses are scheduled during their preferred time slots.")
        department_course_match = st.checkbox("Teacher–Department Match", True, help="Ensure courses are taught by teachers from the same department.")

    # Soft Constraints
    with tab2:
        gap_weight = st.slider(
            "Minimize Gaps Between Classes",
            min_value=0,
            max_value=5,
            value=2,
            help=(
                "Controls how strongly the scheduler avoids long gaps between classes for each group.\n\n"
                "0 = No preference for compact schedules.\n"
                "5 = Very strong preference for compact, back-to-back classes."
            )
        )

# Optimization Execution
if st.button("Run Optimization Model"):
    st.write("### Running the Model...")
    if uploaded_file and df is not None:
        constraints = {
            "prevent_teacher_conflicts": prevent_teacher_conflicts,
            "room_time_conflicts": room_time_conflicts,
            "room_capacity_limit": room_capacity_limit,
            "teacher_availability": teacher_availability,
            "course_preferred_times": course_preferred_times,
            "department_course_match": department_course_match,
            "gap_weight": gap_weight
        }
        courses, teachers, rooms, time_slots, assignments = solve_schedule(df, constraints)
        if assignments:
            st.success("A feasible schedule has been found!")
            st.write("### Final Schedule")
            st.dataframe(pd.DataFrame(assignments))

            # Visualization: Bar Charts
            st.write("#### Number of Courses per Timeslot")
            slot_counts = pd.DataFrame(assignments)["Start"].value_counts().sort_index()
            st.bar_chart(slot_counts)

            st.write("#### Number of Courses per Room")
            room_counts = pd.DataFrame(assignments)["Room"].value_counts()
            st.bar_chart(room_counts)
        else:
            st.error("No feasible schedule could be generated.")
    else:
        st.error("No valid file uploaded. Please upload a valid CSV file.")