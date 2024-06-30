from ortools.sat.python import cp_model

subjects_list = ["sec_lec", "sec_td", "mf_lec", "mf_td", "anum_lec", "anum_td", "entre_lec", "ro2_lec",
                 "ro2_td", "diac_lec", "diac_td", "rx2_lec", "rx2_td", "rx2_tp", "ai_lec", "ai_td", "ai_tp"]
groups = ["g1", "g2", "g3", "g4", "g5", "g6"]

subjects = []
for subject in subjects_list:
    for group in groups:
        if "td" in subject or "tp" in subject:
            subjects.append(f"{subject}_{group}")
        elif not (subject in subjects):
            subjects.append(subject)

days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday"]
slots = ["Slot1", "Slot2", "Slot3", "Slot4", "Slot5"]

# Create the model
model = cp_model.CpModel()

# Create the variables
subject_to_slot = {}
for subject in subjects:
    subject_to_slot[subject] = model.NewIntVar(
        0, len(days) * len(slots) - 1, subject)
# ✅ Constraints to ensure no two lectures are in the same slot
lectures = [subject_to_slot[subject]
            for subject in subjects if "lec" in subject]
model.AddAllDifferent(lectures)
# ✅ this ensures that if there is lec in slot nothing should be there.
for lecture in lectures:
    for subject in subject_to_slot:
        if "lec" not in subject:
            model.Add(subject_to_slot[subject] != lecture)

# ✅  subjects with same group should not be in the same slot
counter = 0
for subject in subjects:
    # extract the same groups as subject
    if "lec" not in subject:
        if counter == 6:
            break
        group = subject.split('_')[-1]
        same_group = [subject_to_slot[subject]
                      for subject in subjects if group in subject]
        model.AddAllDifferent(same_group)
        counter = counter + 1
# ✅  Constraint: no more than 6 subjects in the same slot
for day in range(len(days)):
    for slot in range(len(slots)):
        slots_at_time = [
            model.NewBoolVar(f"{subject}_{day}_{slot}") for subject in subjects
        ]
        for idx, subject in enumerate(subjects):
            model.Add(subject_to_slot[subject] == day *
                      len(slots) + slot).OnlyEnforceIf(slots_at_time[idx])
            model.Add(subject_to_slot[subject] != day * len(slots) +
                      slot).OnlyEnforceIf(slots_at_time[idx].Not())
        model.Add(sum(slots_at_time) <= 6)
# ✅ Constraint: no two sessions (td/tp) of the same module in the same slot
module_dict = {}
for subject in subjects:
    base_module = "_".join(subject.split("_")[:-1])
    if base_module not in module_dict:
        module_dict[base_module] = []
    module_dict[base_module].append(subject)

for module, subs in module_dict.items():
    for i in range(len(subs)):
        for j in range(i + 1, len(subs)):
            model.Add(subject_to_slot[subs[i]] != subject_to_slot[subs[j]])

# ✅  constraint to make sure that tuesday have just 3 slots
subject_to_slot_sub = {}
for subject in subjects:
    subject_to_slot_sub[subject] = model.NewIntVar(
        13, 13, subject)
for subject in subjects:
    for subject2 in subjects:
        model.Add(subject_to_slot[subject] != subject_to_slot_sub[subject2])
for subject in subjects:
    subject_to_slot_sub[subject] = model.NewIntVar(
        14, 14, subject)
for subject in subjects:
    for subject2 in subjects:
        model.Add(subject_to_slot[subject] != subject_to_slot_sub[subject2])
# Create the solver and solve
solver = cp_model.CpSolver()
status = solver.Solve(model)
matrix = [
    [0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0]
]


def print_matrix():
    for i in range(len(matrix)):
        print(f"{days[i]} \t\n")
        for j in range(len(matrix)):
            print(f"{slots[j]} \t {matrix[i][j]}\t")
        print("\n\n")


if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    print("Solution:")
    for subject in subjects:
        slot = solver.Value(subject_to_slot[subject])
        day = slot // len(slots)
        slot_of_day = slot % len(slots)
        if (matrix[day][slot_of_day] == 0):
            matrix[day][slot_of_day] = str(subject)
        else:
            matrix[day][slot_of_day] = matrix[day][slot_of_day] + \
                " || " + str(subject)
    print_matrix()
else:
    print("No solution found.")

