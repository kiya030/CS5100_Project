import streamlit as st
import pandas as pd
import plotly.express as px
from ver3 import solve_schedule  # Backend functions

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

# Main Page
st.title("Course Scheduling System")

with st.expander("⚙️ Advanced Constraint Configuration"):
    tab1, tab2 = st.tabs(["Hard Constraints", "Soft Constraints"])

    with tab1:
        prevent_teacher_conflicts = st.checkbox("Prevent Teacher Time Conflicts", True)
        room_time_conflicts = st.checkbox("No Two Courses in the Same Room at the Same Time", True)
        room_capacity_limit = st.checkbox("Room Capacity Constraint", True)
        teacher_availability = st.checkbox("Teacher Availability", True)
        course_preferred_times = st.checkbox("Course Preferred Times", True)
        department_course_match = st.checkbox("Teacher–Department Match", True)

    with tab2:
        gap_weight = st.slider(
            "Minimize Gaps Between Classes", 0, 5, 2
        )

# Run Solver
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

            df_assign = pd.DataFrame(assignments)
            course_dept_map = {course['id']: course['department'] for course in courses}
            df_assign['Department'] = df_assign['Course'].map(course_dept_map)
            st.write("### Final Schedule")
            st.dataframe(df_assign)

            # ========== Charts ==========

            # Bar Chart: Courses per Timeslot
            st.subheader("📊 Number of Courses per Timeslot")
            timeslot_counts = df_assign["Start"].astype(int).value_counts().sort_index()
            st.bar_chart(timeslot_counts)

            # Bar Chart: Courses per Room
            st.subheader("🏫 Number of Courses per Room")
            room_counts = df_assign["Room"].value_counts()
            st.bar_chart(room_counts)

            # Stacked Bar Chart: Courses by Department over Time
            st.subheader("📚 Departmental Distribution per Time Slot")
            dept_time = df_assign.groupby(["Start", "Department"]).size().unstack(fill_value=0)
            fig_stack = px.bar(
                dept_time,
                x=dept_time.index,
                y=dept_time.columns,
                title="Courses by Department per Time Slot",
                labels={"value": "Number of Courses", "Start": "Time Slot"},
            )
            st.plotly_chart(fig_stack, use_container_width=True)

            # Pie Chart: Room Usage Distribution
            st.subheader("🧩 Room Usage Distribution")
            pie_data = df_assign["Room"].value_counts().reset_index()
            pie_data.columns = ["Room", "Count"]
            fig_pie = px.pie(pie_data, names="Room", values="Count", title="Room Usage Distribution")
            st.plotly_chart(fig_pie, use_container_width=True)

            # Gantt Chart: Course Timeline
            st.subheader("🗓️ Gantt Chart of Courses")
            gantt_df = df_assign.copy()
            gantt_df["Start_Time"] = gantt_df["Start"].astype(int).apply(lambda x: f"{int(x):02d}:00")
            gantt_df["End_Time"] = gantt_df["Start"].astype(int).apply(lambda x: f"{int(x) + 1:02d}:00")
            gantt_df["Start"] = pd.to_datetime(gantt_df["Start_Time"], format="%H:%M")
            gantt_df["End"] = pd.to_datetime(gantt_df["End_Time"], format="%H:%M")

            fig_gantt = px.timeline(
                gantt_df,
                x_start="Start",
                x_end="End",
                y="Course",
                color="Course",
                hover_data=["Teacher", "Room"],
                title="Course Schedule"
            )
            fig_gantt.update_yaxes(autorange="reversed")
            st.plotly_chart(fig_gantt, use_container_width=True)

        else:
            st.error("❌ No feasible schedule could be generated.")
    else:
        st.error("Please upload a valid CSV file.")