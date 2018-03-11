import sys

file_name = sys.path[0] + '/zadanie_4_triangle_big.txt'
source = open(file=file_name, mode='r')

triangle = []
for line in source.readlines():
    values_list = line.split()
    values_list = list(map(lambda x: int(x), values_list))
    triangle.append(values_list)

while len(triangle) != 1:
    last_line = triangle.pop()
    results = []
    for x in range(len(last_line)-1):
        results.append(max([last_line[x], last_line[x+1]]))

    for x in range(len(triangle[-1])):
        triangle[-1][x] += results[x]

print(triangle[-1])
