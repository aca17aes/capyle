# ordered_directions = ["N", "NW", "W", "SW", "S", "SE", "E", "NE"]
# boxes = [2, 1, 4, 7, 8, 9, 6, 3]
# length = len(ordered_directions)

# # relax and for now only have the function that returns the integers
# # just like the grids you drew in your notebook

# wind_index = 4

# print(boxes[wind_index:length])
# print(ordered_directions[wind_index:length])

# print("\nBRUH\n")

# # print(zip(boxes,ordered_directions))

# part_1 = boxes[0:wind_index]
# part_2 = boxes[wind_index:length]

# print(part_1)
# print(part_2)

# print(f"\n{part_2 + part_1}")

# # seems to work!

import numpy as np

a = [[1,2,3],[4,5,6],[7,8,9]]
b = [[True,False,True],
	 [False,True,True],
	 [False,True,True]]

a = np.array(a)
b = np.array(b)

print(a*b)
