import sys
import os
from collections import OrderedDict, Counter

folder = 'zadanie_1_words'
path = sys.path[0] + '/' + folder

histogram = Counter()
for txt in os.listdir(path):
    f = open(path + '/' + txt)
    output = f.read().lower()
    histogram += Counter(output)

result = ''
ordered_histogram = OrderedDict(sorted(histogram.items(), key=lambda x: x[0]))
for key, value in ordered_histogram.items():
    result += key
    result += str(value)

print(result)
