import sys
from pathlib import Path


import numpy as np

A = np.random.randint(0, 6, (5, 5)) * 10
print(A)
B = A == 50
print(B)
print(np.sum(B))
exit()
## https://github.com/stakahama/sie-eng270-projectexample/blob/main/code/simulategrid.py
print(Path(sys.path[0]).parent)

exit()

from parameters import MazeParameter, NodePos, JsonObjectHandler, convert_params_to_json, save_params, load_params

start = NodePos(1, 1)
end = NodePos(5, 1)

pars = MazeParameter("abc", "abc", start, end)

# print(vars(pars))
# print(convert_params_to_json(pars))
# save_params("jsontest.json", pars)

a = load_params("jsontest.json")
print(a.start_point.x)

