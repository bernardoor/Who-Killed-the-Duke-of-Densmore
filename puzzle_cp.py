from ortools.sat.python import cp_model
import pandas as pd
from matplotlib import pyplot as plt

people = ['Ann', 'Betty', 'Charlotte', 'Edith', 'Felicia', 'Georgia', 'Helen']
people_met = {'Ann': ['Betty', 'Charlotte', 'Felicia', 'Georgia'],
              'Betty': ['Ann', 'Charlotte', 'Edith', 'Felicia', 'Helen'],
              'Charlotte': ['Ann', 'Betty', 'Edith'],
              'Edith': ['Betty', 'Charlotte', 'Felicia'],
              'Felicia': ['Ann', 'Betty', 'Edith', 'Helen'],
              'Georgia': ['Ann', 'Helen'],
              'Helen': ['Betty', 'Felicia', 'Georgia']}

model = cp_model.CpModel()
num_vals = 1000

# Arrival time of person i in the castle
s = {i: model.NewIntVar(0, num_vals, 'start_' + i) for i in people}
# Duration of the visit of person i in the castle
e = {i: model.NewIntVar(0, num_vals, 'end_' + i) for i in people}
# Departure time of person i from the castle
d = {i: model.NewIntVar(0, num_vals, 'duration_' + i) for i in people}
# Logic variable that is True (1) is person cannot be included in the visit schedule. False otherwise
v = {i: model.NewBoolVar('v_' + i) for i in people}
# Auxiliary Boolean variables
b1 = {(i, j): model.NewBoolVar(name='b1_' + i + "_" + j) for i in people for j in people if i != j}
b2 = {(i, j): model.NewBoolVar(name='b2_' + i + "_" + j) for i in people for j in people if i != j}
b3 = {(i, j): model.NewBoolVar(name='b3_' + i + "_" + j) for i in people for j in people if i != j}
b4 = {(i, j): model.NewBoolVar(name='b4_' + i + "_" + j) for i in people for j in people if i != j}

# Departure time is equal to arrival time plus duration
for i in people:
    model.Add(s[i] + d[i] == e[i])

for i in people:
    for j in people:
        if i != j:
            if j in people_met[i]:
                # Overlap condition 1
                model.Add(e[i] > s[j]).OnlyEnforceIf(b1[(i, j)])
                model.Add(s[i] < e[j]).OnlyEnforceIf(b1[(i, j)])
                # Overlap condition 2
                model.Add(s[i] < e[j]).OnlyEnforceIf(b2[(i, j)])
                model.Add(s[i] > s[j]).OnlyEnforceIf(b2[(i, j)])
                # At least one of the overlap conditions
                model.AddAtLeastOne([b1[(i, j)], b2[(i, j)], v[i], v[j]])
            else:
                # No overlap condition 1
                model.Add(e[i] <= s[j]).OnlyEnforceIf(b3[(i, j)])
                # No overlap condition 2
                model.Add(s[i] >= e[j]).OnlyEnforceIf(b4[(i, j)])
                # At least one of the non overlap conditions
                model.AddAtLeastOne([b3[(i, j)], b4[(i, j)], v[i], v[j]])

# Duration of person (d_i) is 0 is value v_i is True. If v_i is False, d_i must be strictly positive.
for i in people:
    model.Add(d[i] == 0).OnlyEnforceIf(v[i])
    model.Add(d[i] > 0).OnlyEnforceIf(v[i].Not())

# Objective function is maximizing the number of people included - minimizing the sum of variable v_i.
var_obj = 0
for i in people:
    var_obj += v[i]
model.Minimize(var_obj)

solver = cp_model.CpSolver()
status = solver.Solve(model)

if status == cp_model.OPTIMAL:
    for i in people:
        print(i, solver.Value(s[i]), solver.Value(e[i]), solver.Value(d[i]))
gantt_result_dict = {'Person': [], 'Start': [], 'End': [], 'Duration': []}
for i in people:
    gantt_result_dict['Person'].append(i)
    gantt_result_dict['Start'].append(solver.Value(s[i]))
    gantt_result_dict['End'].append(solver.Value(e[i]))
    gantt_result_dict['Duration'].append(solver.Value(d[i]))
gantt_result_df = pd.DataFrame.from_dict(gantt_result_dict)
print(gantt_result_df)
fig, ax = plt.subplots(1, figsize=(16, 6))
ax.barh(gantt_result_df['Person'], gantt_result_df['Duration'], left=gantt_result_df['Start'])
plt.grid()
plt.show()
