from ortools.sat.python import cp_model
import pandas as pd

# -------------------------- 1) DATA SETUP -----------------------------------
# courses = [
#     {"id": "CS101", "department": "CS",      "group": "GroupA", "preferred_times": [8, 9],         "num_students": 45},
#     {"id": "CS102", "department": "CS",      "group": "GroupA", "preferred_times": [10, 11],       "num_students": 40},
#     {"id": "MA202", "department": "Math",    "group": "GroupB", "preferred_times": [9, 11],        "num_students": 35},
#     {"id": "MA203", "department": "Math",    "group": "GroupB", "preferred_times": [13, 14],       "num_students": 28},
#     {"id": "PH303", "department": "Physics", "group": "GroupC", "preferred_times": [10, 12, 14],   "num_students": 20},
#     {"id": "PH304", "department": "Physics", "group": "GroupC", "preferred_times": [8, 10, 14],    "num_students": 15},
#     {"id": "CS201", "department": "CS",      "group": "GroupD", "preferred_times": [8, 14],        "num_students": 50},
#     {"id": "MA301", "department": "Math",    "group": "GroupE", "preferred_times": [9, 15],        "num_students": 25},
#     {"id": "PH401", "department": "Physics", "group": "GroupF", "preferred_times": [12, 14, 16],   "num_students": 10},
#     {"id": "PH402", "department": "Physics", "group": "GroupG", "preferred_times": [14, 15],       "num_students": 10},
# ]
#
# teachers = [
#     {"name": "Dr. X", "department": "CS",      "available_times": [8, 9, 10, 11, 13, 14]},
#     {"name": "Dr. Y", "department": "Math",    "available_times": [9, 11, 13, 14, 15]},
#     {"name": "Dr. Z", "department": "Physics", "available_times": [8, 10, 12, 14, 15, 16]},
#     {"name": "Dr. W", "department": "Physics", "available_times": [8, 10, 12, 14, 15, 16]},
# ]
#
# rooms = [
#     {"id": "Room101", "capacity": 50},
#     {"id": "Room102", "capacity": 40},
#     {"id": "Lab201",  "capacity": 30},
#     {"id": "Lab202",  "capacity": 20},
# ]
#
# time_slots = [8, 9, 10, 11, 12, 13, 14, 15, 16]  # 8 AM through 4 PM

def load_schedule_data(file):
    """Load schedule data from a CSV file or DataFrame."""
    if isinstance(file, str):  # If file is a path
        df = pd.read_csv(file)
    elif isinstance(file, pd.DataFrame):  # If file is already a DataFrame
        df = file
    else:
        raise ValueError("Input must be a file path or a Pandas DataFrame.")

    courses, teachers, rooms, time_slots = [], [], [], []

    for _, row in df.iterrows():
        if row["type"] == "course":
            courses.append({
                "id": row["id"],
                "department": row["department"],
                "group": row["group"],
                "preferred_times": list(map(int, row["preferred_times"].split(','))),
                "num_students": int(row["num_students"])
            })
        elif row["type"] == "teacher":
            teachers.append({
                "name": row["name"],
                "department": row["department"],
                "available_times": list(map(int, row["available_times"].split(',')))
            })
        elif row["type"] == "room":
            rooms.append({
                "id": row["id"],
                "capacity": int(row["capacity"])
            })
        elif row["type"] == "time_slot":
            time_slots.append(int(row["id"]))

    return courses, teachers, rooms, time_slots

# -------------------------- 2) CREATE THE MODEL -----------------------------
def solve_schedule(file, constraints):
    """Solve the scheduling problem using the provided data and constraints."""
    courses, teachers, rooms, time_slots = load_schedule_data(file)

    model = cp_model.CpModel()
    num_courses = len(courses)
    num_teachers = len(teachers)
    num_rooms = len(rooms)
    num_time_slots = len(time_slots)

    # 4D decision variables
    course_assignment = {}
    for i in range(num_courses):
        for j in range(num_teachers):
            for t in range(num_time_slots):
                for r in range(num_rooms):
                    var_name = f"assign_c{i}_T{j}_t{t}_r{r}"
                    course_assignment[(i, j, t, r)] = model.NewBoolVar(var_name)

# -------------------------- 3) HARD CONSTRAINTS -----------------------------
    # (A) Each course assigned exactly once
    for i in range(num_courses):
        model.Add(
            sum(
                course_assignment[(i, j, t, r)]
                for j in range(num_teachers)
                for t in range(num_time_slots)
                for r in range(num_rooms)
            ) == 1
        )

    # Apply constraints dynamically based on user input
    # (B) A teacher cannot teach two courses at the same time
    if constraints.get("prevent_teacher_conflicts", True):
        for j in range(num_teachers):
            for t in range(num_time_slots):
                model.Add(
                    sum(
                        course_assignment[(i, j, t, r)]
                        for i in range(num_courses)
                        for r in range(num_rooms)
                    ) <= 1
                )

    # (C) No two courses in the same room at the same time
    if constraints.get("room_time_conflicts", True):
        for t in range(num_time_slots):
            for r in range(num_rooms):
                model.Add(
                    sum(
                        course_assignment[(i, j, t, r)]
                        for i in range(num_courses)
                        for j in range(num_teachers)
                    ) <= 1
                )

    # (D) Room capacity constraint
    # If a course has more students than the room capacity, disallow assignment
    if constraints.get("room_capacity_limit", True):
        for i, c_info in enumerate(courses):
            n_students = c_info["num_students"]
            for r, room_info in enumerate(rooms):
                if n_students > room_info["capacity"]:
                    for j in range(num_teachers):
                        for t in range(num_time_slots):
                            model.Add(course_assignment[(i, j, t, r)] == 0)

    # (E) Teacher availability
    if constraints.get("teacher_availability", True):
        for j, t_info in enumerate(teachers):
            avail = set(t_info["available_times"])
            for t_idx, slot_val in enumerate(time_slots):
                if slot_val not in avail:
                    for i in range(num_courses):
                        for r in range(num_rooms):
                            model.Add(course_assignment[(i, j, t_idx, r)] == 0)

    # (F) Course’s preferred times
    if constraints.get("course_preferred_times", True):
        for i, c_info in enumerate(courses):
            pref_set = set(c_info["preferred_times"])
            for t_idx, slot_val in enumerate(time_slots):
                if slot_val not in pref_set:
                    for j in range(num_teachers):
                        for r in range(num_rooms):
                            model.Add(course_assignment[(i, j, t_idx, r)] == 0)

    # (G) Teacher–department match
    if constraints.get("department_course_match", True):
        for i, c_info in enumerate(courses):
            c_dept = c_info["department"]
            for j, t_info in enumerate(teachers):
                t_dept = t_info["department"]
                if t_dept != c_dept:
                    for t_idx in range(num_time_slots):
                        for r in range(num_rooms):
                            model.Add(course_assignment[(i, j, t_idx, r)] == 0)

# -------------------------- 4) SOFT CONSTRAINTS (Large Gap Minimization) ----

    # We'll minimize the "spread" for each group's courses.
    # Minimize gaps if the gap_weight is greater than 0
    gap_weight = constraints.get("gap_weight", 0)
    if gap_weight > 0:
        all_groups = list({c["group"] for c in courses})
        group_course_map = {g: [] for g in all_groups}
        for i, c_info in enumerate(courses):
            group_course_map[c_info["group"]].append(i)

        min_slot = min(time_slots)
        max_slot = max(time_slots)

        # Create start_time[g] and end_time[g] for each group
        start_time = {}
        end_time = {}

        for g in all_groups:
            start_time[g] = model.NewIntVar(min_slot, max_slot, f"start_{g}")
            end_time[g] = model.NewIntVar(min_slot, max_slot, f"end_{g}")
            model.Add(start_time[g] <= end_time[g])

            # Link each course's assignment to start/end times
            for i_course in group_course_map[g]:
                for j in range(len(teachers)):
                    for t_idx, slot_val in enumerate(time_slots):
                        for r in range(len(rooms)):
                            boolvar = course_assignment[(i_course, j, t_idx, r)]
                            model.Add(start_time[g] <= slot_val).OnlyEnforceIf(boolvar)
                            model.Add(end_time[g] >= slot_val).OnlyEnforceIf(boolvar)

        # For each group g, define a gap variable
        gap_penalties = []
        for g in all_groups:
            num_cg = len(group_course_map[g])
            gap_var = model.NewIntVar(0, max_slot - min_slot, f"gap_{g}")
            # gap_var >= end_time[g] - start_time[g] - (num_cg - 1)
            # => end_time[g] - start_time[g] - gap_var <= num_cg - 1
            model.Add(end_time[g] - start_time[g] - gap_var <= (num_cg - 1))
            gap_penalties.append(gap_var)

        # Minimizing sum of gap variables => more compact schedules for each group
        model.Minimize(gap_weight * sum(gap_penalties))

# -------------------------- 5) SOLVE THE MODEL ------------------------------
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    assignments = []
    if status in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
        for i in range(num_courses):
            for j in range(num_teachers):
                for t in range(num_time_slots):
                    for r in range(num_rooms):
                        if solver.Value(course_assignment[(i, j, t, r)]) == 1:
                            course_id = courses[i]["id"]
                            teacher = teachers[j]["name"]
                            time_val = time_slots[t]
                            room_id = rooms[r]["id"]
                            assignments.append({
                                "Course": course_id,
                                "Teacher": teacher,
                                "Start": time_val,
                                "End": time_val + 1,  # Assume each course is 1-hour long
                                "Room": room_id
                            })

    return courses, teachers, rooms, time_slots, assignments
