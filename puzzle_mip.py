import pandas as pd
from matplotlib import pyplot as plt
from ortools.linear_solver import pywraplp

people = ['Ann', 'Betty', 'Charlotte', 'Edith', 'Felicia', 'Georgia', 'Helen']
people_met = {'Ann': ['Betty', 'Charlotte', 'Felicia', 'Georgia'],
              'Betty': ['Ann', 'Charlotte', 'Edith', 'Felicia', 'Helen'],
              'Charlotte': ['Ann', 'Betty', 'Edith'],
              'Edith': ['Betty', 'Charlotte', 'Felicia'],
              'Felicia': ['Ann', 'Betty', 'Edith', 'Helen'],
              'Georgia': ['Ann', 'Helen'],
              'Helen': ['Betty', 'Felicia', 'Georgia']}

periods = 6
T = [p for p in range(0, periods)]
solver = pywraplp.Solver('puzzle', pywraplp.Solver.CBC_MIXED_INTEGER_PROGRAMMING)

# 1 if person i is included. 0 otherwise
y = {(i): solver.IntVar(0, 1, "y_{0}".format(i)) for i in people}

# 1 if person i is in the castle at t. 0 otherwise
x = {(i, t): solver.IntVar(0, 1, "x_{0}_{1}".format(i, t)) for i in people for t in T}

# 1 if person i and j are in the castle simultaneously at t. 0 otherwise
z = {(i, j, t): solver.IntVar(0, 1, "z_{0}_{1}_{2}".format(i, j, t))
for i in people for j in people for t in T if i != j}

# 1 if person i arrives in the castle at t. 0 otherwise
w = {(i, t): solver.IntVar(0, 1, "w_{0}_{1}".format(i, t)) for i in people for t in range(0, periods - 1)}

# If a person is included she must have been in the castle at least once
c1 = {i: solver.Add(solver.Sum(x[(i, t)] for t in T) >= y[i]) for i in people}

# If a person is included she must have been in the castle simultaneously with other people she met at least once
c2 = {(i, j): solver.Add(solver.Sum(z[(i, j, t)] for t in T) >= y[i])
      for i in people for j in people_met[i]}

# Two people were simultaneously at t in the castle only if they are both there at t
c3 = {(i, j, t): solver.Add((z[(i, j, t)] >= x[(i, t)] + x[(j, t)] - 1))
      for i in people for j in people for t in T if i != j}

# Two people were simultaneously at t in the castle only if they are both there at t and if they are included
c4 = {(i, j, t): solver.Add(
    (x[(i, t)] + x[(j, t)] + periods * (1 - z[(i, j, t)]) >= y[i] + y[j]))
      for i in people for j in people for t in T if i != j}

# Two people that did not meet cannot be in the castle simultaneously
c5 = {(i, j): solver.Add(solver.Sum(z[(i, j, t)] for t in T) == 0)
      for i in people for j in people if i != j and j not in people_met[i]}

# Defines the arrival time of person
c6 = {(i, t): solver.Add((w[(i, t)] >= x[(i, t + 1)] - x[(i, t)]))
      for i in people for t in range(0, periods - 1)}

# Person cannot be in the castle in period 0 and period T
c7 = {(i): solver.Add(x[(i, 0)] + x[(i, periods - 1)] == 0)
      for i in people}

# If a person was included it has just one arrival time
c8 = {(i): solver.Add(solver.Sum(w[(i, t)] for t in range(0, periods - 1)) == y[i])
      for i in people}

# Objective function - maximizing the number of people included
number_of_people = solver.Sum(y[i] for i in people)

solver.Maximize(number_of_people)
result_status = solver.Solve()

gantt_result_dict = {'Person': [], 'Start': [], 'End': [], 'Duration': []}
duration = {i: 0 for i in people}
start = {i: 0 for i in people}
end = {i: 0 for i in people}
for i in people:
    for t in T:
        if x[(i, t)].solution_value() >= 0.1:
            duration[i] += 1
            if x[(i, t - 1)].solution_value() == 0:
                start[i] = t
    end[i] = start[i] + duration[i]
    gantt_result_dict['Person'].append(i)
    gantt_result_dict['Start'].append(start[i])
    gantt_result_dict['End'].append(end[i])
    gantt_result_dict['Duration'].append(duration[i])
gantt_result_df = pd.DataFrame.from_dict(gantt_result_dict)
print(gantt_result_df)
fig, ax = plt.subplots(1, figsize=(16, 6))
ax.barh(gantt_result_df['Person'], gantt_result_df['Duration'], left=gantt_result_df['Start'])
plt.grid()
plt.show()
