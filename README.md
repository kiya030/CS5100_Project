# Course Scheduling Solver

## Overview
This project implements a **Course Scheduling Solver** using **Constraint Programming (CP)** techniques, specifically leveraging **Google OR-Tools' CP-SAT solver**. The goal is to assign courses to time slots and rooms while satisfying various constraints, such as avoiding schedule conflicts and optimizing resource usage.

## Features
- Uses **Constraint Programming (CP)** to efficiently assign courses.
- Avoids scheduling conflicts between courses with common students or instructors.
- Ensures **room capacity constraints** are met.
- Supports **time slot constraints** (e.g., avoiding overlapping courses).
- Implements **heuristic search** and optimization techniques to improve scheduling efficiency.
- Uses **CP-SAT (a state-of-the-art SAT-based constraint solver)** to solve the problem effectively.

## Technologies Used
- **Python**
- **Google OR-Tools (CP-SAT Solver)**
- **Constraint Programming (CP)**
- **CSP (Constraint Satisfaction Problem) methodology**
- **Streamlit** (for front-end interface)

## Installation
Ensure you have Python installed (version 3.7+ recommended). Then, install the required dependencies:

```sh
pip install ortools streamlit plotly pandas
```

## How to Run
1. Clone this repository:
   ```sh
   git clone https://github.com/kiya030/CS5100_Project
   ```
2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
3. Run the Streamlit front-end interface:
   ```sh
   streamlit run app.py
   ```
4. Upload a CSV file containing course, teacher, and room data.
5. Configure hard and soft constraints through the sidebar.
6. Click the "Run Optimization Model" button to generate the course schedule.

## Constraints Considered
### Hard Constraints
- **No instructor can teach two courses at the same time.**
- **No student can attend two courses scheduled at the same time.**
- **Room capacity cannot be exceeded.**
- **Specific courses require specific time slots or rooms.**
- **A teacher can only teach a course during their available times.**
- **No two courses can be scheduled in the same room at the same time.**

### Soft Constraints
- **Minimize gaps between classes** (Allows setting a preference for compact schedules).

## Example CSV Format
The uploaded CSV file should contain data for courses, teachers, rooms, and time slots in the following format, or you can just try the "data.csv" file already been given in the folder:

| type      | id        | department | group   | preferred_times    | num_students | available_times    | capacity |
|-----------|-----------|------------|---------|--------------------|--------------|--------------------|----------|
| course    | CS101     | CS         | GroupA  | 8,9                | 45           |                    |          |
| teacher   | Dr. X     | CS         |         |                    |              | 8,9,10,11           |          |
| room      | Room101   |            |         |                    |              |                    | 50       |
| time_slot | 8         |            |         |                    |              |                    |          |
| time_slot | 9         |            |         |                    |              |                    |          |

## Example Output
```sh
Course  Group Department Teacher  Time    Room  Students
 CS101 GroupA         CS   Dr. X     8   HallB        45
 CS201 GroupB         CS   Dr. X     9 Room101        50
...
```

## Future Improvements
- Add **soft constraints** (e.g., preferred time slots for instructors).
- Support **multi-campus scheduling**.
- Optimize for **minimum gaps between courses**.

## Authors
- **Yuxin Qin**
- **Zihan Zhan**
- **(Kristen) Yang Wang**

## License
This project is licensed under the MIT License.

